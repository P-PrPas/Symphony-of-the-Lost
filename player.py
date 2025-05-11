import pygame
import os
from settings import (PLAYER_SPEED, SPRINT_SPEED, SPRITE_SIZE, ANIMATION_DELAY, DASH_SPEED,
                      DASH_DURATION, DASH_COOLDOWN, SHOW_HITBOX_PLAYER)
from combo_tracker import ComboTracker
from combo_effect import ComboEffectManager
from note_type import NoteType
from key_manager import KeyPressManager
from skills_database import skill_database
from exp_star import EXPStar
import random
import math



class Player:
    def __init__(self, x, y, collision_handler, skill_effect_manager):
        self.animations = self.load_animations("assets/sprites/test sprite")
        self.current_animation = "idle"
        self.image = self.animations[self.current_animation]["down"][0]

        HITBOX_WIDTH = 60
        HITBOX_HEIGHT = 120
        self.rect = pygame.Rect(x, y, HITBOX_WIDTH, HITBOX_HEIGHT)

        self.hitbox_offset_x = (SPRITE_SIZE * 2.5 - HITBOX_WIDTH) // 2
        self.hitbox_offset_y = int((SPRITE_SIZE * 2.5 - HITBOX_HEIGHT) // 1.5)

        self.speed = PLAYER_SPEED
        self.direction = "down"
        self.frame = 0
        self.animation_timer = 0

        self.is_sprinting = False
        self.is_dashing = False
        self.current_skill = None
        self.dash_timer = 0
        self.last_dash_time = -DASH_COOLDOWN
        self.shift_pressed = False

        self.collision_handler = collision_handler
        self.combo_tracker = ComboTracker()
        self.combo_effects = ComboEffectManager()
        self.key_manager = KeyPressManager()
        self.skill_effect_manager = skill_effect_manager

        self.last_attack_time = 0
        self.damage_timer = -99999
        self.damage_duration = 300  # milliseconds
        self.damage_shake_offset = [0, 0]

        self.is_dead = False
        self.death_start_time = None
        self.start_game_over = False

        self.level = 1
        self.exp = 0
        self.max_exp = self.level * 5
        self.exp_stars = []
        self.hp = 10
        self.max_hp = 10 + (self.level - 1) * 2

        self.barrier_active = False
        self.barrier_end_time = 0
        self.barrier_sound = pygame.mixer.Sound("assets/SFX/barrier_activate.wav")

        self.soundquake_charging = False
        self.soundquake_start_time = 0
        self.soundquake_glow = False
        self.charge_flash_timer = 0

        self.skill_cooldowns = {}

    def get_max_hp(self):
        return self.max_hp

    def load_animations(self, folder, frame_override=None):
        animations = {}
        SCALE_FACTOR = 2.5

        for animation_name in os.listdir(folder):
            if animation_name.endswith(".png"):
                anim_key = animation_name.split(".")[0]
                sheet_path = os.path.join(folder, animation_name)

                if not os.path.exists(sheet_path):
                    print(f"[WARN] Missing sprite: {sheet_path}")
                    continue

                sheet = pygame.image.load(sheet_path).convert_alpha()
                sheet_width = sheet.get_width()
                max_frames = sheet_width // SPRITE_SIZE
                frame = frame_override if frame_override else max_frames

                animations[anim_key] = {"up": [], "down": [], "left": [], "right": []}
                for i in range(frame):
                    # ป้องกันการอ่านเกินขอบภาพ
                    if (i + 1) * SPRITE_SIZE > sheet_width:
                        print(f"[WARN] Skipping frame {i} in '{anim_key}' — exceeds sheet width")
                        break
                    animations[anim_key]["up"].append(
                        self.get_scaled_sprite(sheet, i, 3, SCALE_FACTOR))
                    animations[anim_key]["down"].append(
                        self.get_scaled_sprite(sheet, i, 0, SCALE_FACTOR))
                    animations[anim_key]["left"].append(
                        self.get_scaled_sprite(sheet, i, 1, SCALE_FACTOR))
                    animations[anim_key]["right"].append(
                        self.get_scaled_sprite(sheet, i, 2, SCALE_FACTOR))

        return animations
    def load_single_animation(self, path, frames):
        animations = {"up": [], "down": [], "left": [], "right": []}
        SCALE_FACTOR = 2.5
        sheet = pygame.image.load(path).convert_alpha()

        for i in range(frames):
            animations["up"].append(self.get_scaled_sprite(sheet, i, 3, SCALE_FACTOR))
            animations["down"].append(self.get_scaled_sprite(sheet, i, 0, SCALE_FACTOR))
            animations["left"].append(self.get_scaled_sprite(sheet, i, 1, SCALE_FACTOR))
            animations["right"].append(self.get_scaled_sprite(sheet, i, 2, SCALE_FACTOR))

        return {os.path.splitext(os.path.basename(path))[0]: animations}

    def get_scaled_sprite(self, sheet, frame, row, scale):
        sprite = sheet.subsurface((frame * SPRITE_SIZE, row * SPRITE_SIZE, SPRITE_SIZE, SPRITE_SIZE))
        return pygame.transform.scale(sprite, (int(SPRITE_SIZE * scale), int(SPRITE_SIZE * scale)))

    def set_animation(self, anim_name, frame_override=None):
        if anim_name not in self.animations or self.direction not in self.animations[anim_name]:
            if anim_name in skill_database:
                skill = skill_database[anim_name]
                if os.path.isfile(skill.animation_path):
                    self.animations[anim_name] = self.load_single_animation(
                        skill.animation_path,
                        frame_override or skill.frames
                    )[anim_name]
                else:
                    self.animations.update(
                        self.load_animations(skill.animation_path, frame_override or skill.frames)
                    )

        if anim_name in self.animations and anim_name != self.current_animation:
            self.current_animation = anim_name
            self.frame = 0
            self.animation_timer = 0
            self.image = self.animations[anim_name][self.direction][0]

    def gain_exp(self, amount):
        self.exp += amount
        self.check_level_up()

    def check_level_up(self):
        while self.exp >= self.max_exp:
            self.exp -= self.max_exp
            self.level += 1
            self.max_exp = self.level * 5
            print(f"[LEVEL UP] New level: {self.level}")

    def update_exp_stars(self, screen):
        for star in self.exp_stars[:]:
            star.update()
            star.draw(screen)
            if star.check_collision():
                self.gain_exp(star.amount)
                self.exp_stars.remove(star)

    def move(self, keys, dt, current_time):
        shift_now = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        moving = keys[pygame.K_UP] or keys[pygame.K_DOWN] or keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]

        if self.is_dashing:
            pass
        elif self.is_sprinting and moving:
            self.set_animation("run", 9)
        elif moving:
            self.set_animation("walk", 4)
        else:
            self.set_animation("idle", 4)

        if self.is_dashing:
            speed = DASH_SPEED
        elif self.is_sprinting and not self.is_dashing:
            speed = SPRINT_SPEED
        else:
            speed = PLAYER_SPEED

        dx, dy = 0, 0
        if keys[pygame.K_UP]:
            dy = -speed
            self.direction = "up"
        elif keys[pygame.K_DOWN]:
            dy = speed
            self.direction = "down"
        if keys[pygame.K_LEFT]:
            dx = -speed
            self.direction = "left"
        elif keys[pygame.K_RIGHT]:
            dx = speed
            self.direction = "right"

        if dx != 0 and not self.collision_handler.check_collision(self.rect, dx, 0):
            self.rect.x += dx
        if dy != 0 and not self.collision_handler.check_collision(self.rect, 0, dy):
            self.rect.y += dy

        if shift_now and not self.shift_pressed and moving and current_time - self.last_dash_time >= DASH_COOLDOWN:
            self.start_dash(current_time)

        self.shift_pressed = shift_now

    def start_dash(self, current_time):
        self.is_dashing = True
        self.dash_timer = current_time
        self.last_dash_time = current_time

    def start_death(self):
        self.is_dead = True
        self.death_image = pygame.transform.rotate(self.image, 90)
        self.death_start_time = pygame.time.get_ticks()
        self.start_game_over = True

    def take_damage(self, amount):
        if self.is_dead or self.barrier_active:
            return
        self.hp -= amount
        self.damage_timer = pygame.time.get_ticks()
        if self.hp <= 0:
            self.start_death()

    def update_death_effect(self):
        if not self.is_dead or self.image is None:
            return None, (0, 0), 255

        elapsed = pygame.time.get_ticks() - self.death_start_time
        duration = 1000  # milliseconds
        progress = min(elapsed / duration, 1.0)

        scale = 1.0 - 0.2 * progress
        fade_alpha = int(255 * (1 - progress))
        offset_y = int(10 * progress)

        sprite = pygame.transform.rotozoom(self.death_image, 0, scale)
        sprite.set_alpha(fade_alpha)

        return sprite, (self.rect.x - self.hitbox_offset_x, self.rect.y - self.hitbox_offset_y + offset_y), fade_alpha

    def update_dash(self, current_time):
        if self.is_dashing and current_time - self.dash_timer >= DASH_DURATION:
            self.is_dashing = False

    def handle_soundquake_input(self, keys, current_time):
        import pygame
        from skill_effect import SoundquakeEffect
        from skills_database import skill_database

        A = pygame.K_a
        skill = skill_database.get("soundquake")
        if not skill:
            return

        # 👉 เพิ่มตรงนี้: ห้ามเริ่มชาร์จถ้า cooldown ยังไม่หมด
        if keys[A] and not self.soundquake_charging:
            if self.is_skill_on_cooldown(skill, current_time):
                return  # ❌ หยุดทันทีถ้า cooldown
            self.soundquake_charging = True
            self.soundquake_start_time = current_time
            self.soundquake_glow = False
            self.charge_flash_timer = 0

        elif not keys[A] and self.soundquake_charging:
            elapsed = current_time - self.soundquake_start_time
            charge_ratio = min(elapsed / skill.charge_time, 1.0)

            damage = int(skill.damage + charge_ratio * skill.bonus_damage)
            radius = int(skill.radius + charge_ratio * skill.radius_bonus)
            cooldown = int(skill.cooldown + charge_ratio * 1000)

            effect = SoundquakeEffect(
                origin=self.rect.center,
                radius=radius,
                damage=damage,
                charge_ratio=charge_ratio,
                font=pygame.font.Font("assets/fonts/NotoMusic-Regular.ttf", 36),
                note_char="𝄝"
            )

            self.skill_effect_manager.add_effect(effect)
            self.combo_tracker.add_note(NoteType.WHOLE, current_time)
            self.skill_cooldowns[skill.name] = current_time + cooldown
            self.soundquake_charging = False
            return

        if self.soundquake_charging:
            elapsed = current_time - self.soundquake_start_time
            if elapsed >= skill.charge_time:
                self.soundquake_glow = True
            if elapsed - self.charge_flash_timer >= 1000 and elapsed < skill.charge_time:
                self.charge_flash_timer = elapsed
                self.flash_color = (120, 180, 255)
                self.flash_timer = current_time

    def handle_input(self, keys, current_time):
        # mapping: NoteType → skill_name
        note_to_skill = {
            NoteType.QUARTER: "strike_beat",
            NoteType.EIGHTH: "note_flurry",
            NoteType.HALF: "sound_barrier",
            NoteType.WHOLE: "soundquake"
            # เพิ่ม mapping เพิ่มเติมในอนาคตได้เลย
        }
        if self.key_manager.is_new_press(pygame.K_f, keys):
            skill = skill_database.get("note_flurry")
            if skill and not self.is_skill_on_cooldown(skill, current_time):
                self.current_skill = skill
                self.skill_cooldowns[skill.name] = current_time
                self.skill_effect_manager.cast_note_flurry(self)
                self.combo_tracker.add_note(NoteType.EIGHTH, current_time)

        if self.key_manager.is_new_press(pygame.K_s, keys):
            skill = skill_database.get("sound_barrier")
            if skill and not self.is_skill_on_cooldown(skill, current_time):
                self.current_skill = skill
                self.skill_cooldowns[skill.name] = current_time
                self.barrier_active = True
                self.barrier_end_time = current_time + skill.duration
                self.barrier_sound.play()
                self.combo_tracker.add_note(NoteType.HALF, current_time)

        self.handle_soundquake_input(keys, current_time)

        for note in NoteType:
            if self.key_manager.is_new_press(note.value["key"], keys):
                if note == NoteType.WHOLE:
                    continue

                skill_name = note_to_skill.get(note)
                skill = skill_database.get(skill_name) if skill_name else None

                # ✅ ถ้า note นี้มี skill mapping
                if skill:
                    if self.is_skill_on_cooldown(skill, current_time):
                        print(f"[Cooldown] {skill.name} is on cooldown.")
                        return  # ❌ ไม่ใช้ skill, ไม่เพิ่ม note เข้าคอมโบ

                    # ✅ ใช้ skill ได้
                    self.current_skill = skill
                    self.set_animation(skill.name, frame_override=skill.frames)
                    self.skill_effect_manager.spawn(skill, self, self.direction, current_time)
                    self.skill_cooldowns[skill.name] = current_time

                    # ✅ เพิ่มคอมโบเฉพาะเมื่อ skill ถูกใช้จริง
                    self.combo_tracker.add_note(note, current_time)

                else:
                    # 🟢 ถ้าเป็น note ที่ไม่มี skill (เช่น future feature), ยอมให้เพิ่มคอมโบได้
                    self.combo_tracker.add_note(note, current_time)

    def is_skill_on_cooldown(self, skill, current_time):
        last_used = self.skill_cooldowns.get(skill.name, -99999)
        return current_time - last_used < skill.cooldown

    def update(self, current_time, enemy_manager):
        if self.is_dead:
            return
        self.combo_tracker.update(current_time)
        self.skill_effect_manager.update(current_time)
        combo = list(self.combo_tracker.get_combo())
        # heal check
        if len(combo) == 2 and all(n == NoteType.HALF for n in combo):
            skill = skill_database.get("heal_note")
            if skill and not self.is_skill_on_cooldown(skill, current_time):
                self.skill_cooldowns[skill.name] = current_time
                heal_amount = abs(skill.damage)
                self.hp = min(self.hp + heal_amount, self.get_max_hp())
                pygame.mixer.Sound("assets/SFX/heal.wav").play()
                self.skill_effect_manager.spawn_heal_effect(self)
                print(f"[Heal] Player healed for {heal_amount} HP.")
                self.combo_tracker.reset()
        self.skill_effect_manager.check_skill_hits(enemy_manager.enemies)
        if self.barrier_active and current_time >= self.barrier_end_time:
            self.barrier_active = False
        self.update_animation(16)
        # super slash check
        if len(combo) == 4 and all(n == NoteType.QUARTER for n in combo):
            base_skill = skill_database.get("strike_beat")
            if base_skill and not self.is_skill_on_cooldown(base_skill, current_time):
                import copy
                big_slash = copy.deepcopy(base_skill)
                big_slash.name = "Strike Beat MAX"
                big_slash.damage = base_skill.damage * 2
                big_slash.scale = 4

                # ✅ ปรับ offset ใหม่ให้เหมาะกับ scale
                base_scale = 3  # scale เดิมของ skill effect
                scaled_offsets = {
                    dir: (int(dx * big_slash.scale / base_scale), int(dy * big_slash.scale / base_scale))
                    for dir, (dx, dy) in base_skill.effect_offsets.items()
                }
                big_slash.effect_offsets = scaled_offsets
                big_slash.hitbox_sizes = dict(base_skill.hitbox_sizes)
                big_slash.follow_caster = base_skill.follow_caster

                #big_slash.animation_speed_override = 130
                #big_slash.duration_override = 500

                self.skill_cooldowns[big_slash.name] = current_time
                self.set_animation("strike_beat", frame_override=base_skill.frames)
                self.skill_effect_manager.spawn(big_slash, self, self.direction, current_time)
                print("[Combo MAX] Triggered 4x QUARTER Slash!")
                self.combo_tracker.reset()
        # Super Projectile
        if len(combo) == 8 and all(n == NoteType.EIGHTH for n in combo):
            base_skill = skill_database.get("note_flurry")
            if base_skill and not self.is_skill_on_cooldown(base_skill, current_time):
                import copy
                big_flurry = copy.deepcopy(base_skill)
                big_flurry.name = "Note Flurry MAX"
                big_flurry.damage = base_skill.damage * 2
                big_flurry.is_max_combo = True  # ✅ ใช้ flag นี้เพื่อบอก Projectile ให้เปลี่ยนลักษณะ
                self.skill_cooldowns[big_flurry.name] = current_time

                if base_skill.animation_path:
                    self.set_animation("note_flurry", frame_override=base_skill.frames)
                self.skill_effect_manager.cast_note_flurry(self, override_skill=big_flurry)
                print("[Combo MAX] Triggered 8x EIGHTH Shot!")
                self.combo_tracker.reset()
        # Crescendo check
        if combo == [NoteType.HALF, NoteType.QUARTER, NoteType.EIGHTH, NoteType.EIGHTH]:
            skill = skill_database.get("crescendo")
            if skill and not self.is_skill_on_cooldown(skill, current_time):
                self.skill_cooldowns[skill.name] = current_time
                self.attack_boost_end_time = current_time + skill.duration
                self.skill_effect_manager.spawn_crescendo_effect(self)
                print("[Buff] Crescendo activated! 2x attack power for 5 seconds.")
                self.combo_tracker.reset()

    def draw_combo_ui(self, screen, font, margin=60, spacing=28, height_offset=120):
        symbols = self.combo_tracker.get_combo_symbols()
        colors = self.combo_tracker.get_combo_colors()

        target_height = 72
        base_y = screen.get_height() - margin - height_offset

        total_width = 0
        scaled_data = []

        for symbol, color in reversed(list(zip(symbols, colors))):
            surface = font.render(symbol, True, color)
            scale = target_height / surface.get_height()
            new_width = int(surface.get_width() * scale)
            scaled_surface = pygame.transform.smoothscale(surface, (new_width, target_height))
            total_width += new_width + spacing
            scaled_data.append((scaled_surface, new_width, color))

        bar_padding_x = 35
        bar_padding_y = 20
        bar_height = target_height + bar_padding_y * 2
        bar_width = total_width + bar_padding_x * 2
        bar_x = screen.get_width() - margin - bar_width
        bar_y = base_y - bar_padding_y

        glow_color = (100, 70, 160)
        glow_rect = pygame.Rect(bar_x - 2, bar_y - 2, bar_width + 4, bar_height + 4)
        pygame.draw.rect(screen, glow_color, glow_rect, border_radius=12)

        self.combo_effects.update_and_draw(screen, font)

        bar_color = (60, 40, 100)
        border_color = (180, 160, 255)
        pygame.draw.rect(screen, bar_color, (bar_x, bar_y, bar_width, bar_height), border_radius=10)
        pygame.draw.rect(screen, border_color, (bar_x, bar_y, bar_width, bar_height), width=2, border_radius=10)

        pattern_color = (90, 70, 120)
        for i in range(5):
            y = bar_y + int(bar_height * (0.2 + 0.15 * i))
            pygame.draw.line(screen, pattern_color, (bar_x + 10, y), (bar_x + bar_width - 10, y), 1)

        x = bar_x + bar_padding_x
        for surface, w, _ in reversed(scaled_data):
            y = bar_y + bar_padding_y
            screen.blit(surface, (x, y))
            x += w + spacing

        if self.combo_tracker.is_alerting():
            pygame.draw.rect(screen, (255, 100, 100), (bar_x, bar_y, bar_width, bar_height), width=4, border_radius=12)

            if not hasattr(self, "_combo_overflow_shown") or not self._combo_overflow_shown:
                self._combo_overflow_shown = True
                center = (bar_x + bar_width // 2, bar_y + bar_height // 2)
                symbols = self.combo_tracker.get_combo_symbols()
                colors = self.combo_tracker.get_combo_colors()
                symbol_color_pairs = list(zip(symbols, colors))

                self.combo_effects.trigger(center, symbol_color_pairs,
                                           glow_rect=pygame.Rect(bar_x, bar_y, bar_width, bar_height),
                                           color_override=(255, 50, 50))  # สีแดงพิเศษ
        elif self.combo_tracker.is_success():
            pygame.draw.rect(screen, (80, 255, 120), (bar_x, bar_y, bar_width, bar_height), width=4, border_radius=12)

            if not hasattr(self, "_combo_success_shown") or not self._combo_success_shown:
                self._combo_success_shown = True
                center = (bar_x + bar_width // 2, bar_y + bar_height // 2)
                symbols = self.combo_tracker.get_combo_symbols()
                colors = self.combo_tracker.get_combo_colors()
                symbol_color_pairs = list(zip(symbols, colors))

                self.combo_effects.trigger(center, symbol_color_pairs,
                                           glow_rect=pygame.Rect(bar_x, bar_y, bar_width, bar_height))

        else:
            self._combo_success_shown = False
            self._combo_overflow_shown = False

    def draw_exp_bar(self, screen):
        bar_width = 200
        bar_height = 16
        margin = 20

        x = margin
        y = screen.get_height() - bar_height - margin

        # Background
        pygame.draw.rect(screen, (50, 50, 50), (x, y, bar_width, bar_height))
        pygame.draw.rect(screen, (255, 255, 255), (x, y, bar_width, bar_height), 2)

        # Fill
        exp_ratio = min(1.0, self.exp / self.max_exp)
        fill_width = int(bar_width * exp_ratio)
        pygame.draw.rect(screen, (255, 230, 70), (x + 2, y + 2, fill_width - 4, bar_height - 4))

        # Text
        font = pygame.font.SysFont(None, 24)
        exp_text = font.render(f"EXP: {self.exp} / {self.max_exp}  Lv.{self.level}", True, (255, 255, 255))
        screen.blit(exp_text, (x + bar_width + 10, y - 2))

    def draw_barrier_effect(self, screen):
        if not self.barrier_active:
            return

        t = pygame.time.get_ticks()
        center = self.rect.center
        base_radius = max(self.rect.width, self.rect.height) // 2 + 10
        pulse = 1.0 + 0.05 * math.sin(t / 200.0)
        radius = int(base_radius * pulse)

        # 🟣 ชั้น aura glow (ม่วงฟ้านุ่มแบบเข้าธีม)
        aura_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(
            aura_surf,
            (130, 110, 255, 70),  # โทนม่วงฟ้า + เข้มขึ้นเล็กน้อย
            (radius, radius),
            radius
        )
        aura_surf.set_alpha(100)
        screen.blit(aura_surf, aura_surf.get_rect(center=center))

        # 🔵 ขอบ core โปร่ง + highlight
        core_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(core_surf, (255, 255, 255, 35), (radius, radius), radius - 2)
        pygame.draw.circle(core_surf, (180, 140, 255, 90), (radius, radius), radius - 3, 2)
        screen.blit(core_surf, (center[0] - radius, center[1] - radius))

        # ✨ ประกายเล็กหมุนวน (sparkles)
        for i in range(6):
            angle = math.radians((360 / 6) * i + (t / 10 % 360))
            sparkle_x = int(center[0] + math.cos(angle) * (radius - 4))
            sparkle_y = int(center[1] + math.sin(angle) * (radius - 4))
            pygame.draw.circle(screen, (255, 255, 255, 80), (sparkle_x, sparkle_y), 2)

        # 🎵 โน้ตดนตรีหมุนรอบ barrier
        note_font = pygame.font.Font("assets/fonts/NotoMusic-Regular.ttf", 18)
        symbols = ["𝄞", "♪", "𝅘𝅥", "♩"]
        orbit_r = radius - 8
        for i, sym in enumerate(symbols):
            angle = t * 0.002 + (2 * math.pi * i / len(symbols))
            nx = center[0] + math.cos(angle) * orbit_r
            ny = center[1] + math.sin(angle) * orbit_r
            note = note_font.render(sym, True, (210, 180, 255))
            note.set_alpha(140)
            screen.blit(note, note.get_rect(center=(nx, ny)))

    def draw_buff_ui(self, screen, font):
        active_buffs = []
        now = pygame.time.get_ticks()

        # 📌 ตรวจสอบบัฟ Crescendo
        if hasattr(self, "attack_boost_end_time") and now < self.attack_boost_end_time:
            remaining = (self.attack_boost_end_time - now) / 1000
            active_buffs.append(("ATK x2", remaining, 5.0))  # name, remaining, max_time

        if not active_buffs:
            return

        margin = 20
        bar_width = 220
        bar_height = 30
        spacing = 12

        # ✅ ขยับขึ้นเหนือ Combo Tracker ชัดเจน
        base_y = screen.get_height() - 270
        base_x = screen.get_width() - margin - bar_width

        for i, (buff_name, remaining, max_time) in enumerate(active_buffs):
            y = base_y - i * (bar_height + spacing)

            # 🔲 พื้นหลังโปร่ง
            bg_surf = pygame.Surface((bar_width, bar_height), pygame.SRCALPHA)
            bg_surf.fill((60, 40, 60, 220))
            screen.blit(bg_surf, (base_x, y))

            # 🔴 วงกลมไอคอนจำลอง
            icon_radius = 10
            icon_x = base_x + 14
            icon_y = y + bar_height // 2
            pygame.draw.circle(screen, (180, 50, 50), (icon_x, icon_y), icon_radius)

            # ✏️ x2 ตัวใหญ่ในวงกลม
            icon_text = font.render("×2", True, (255, 255, 255))
            icon_rect = icon_text.get_rect(center=(icon_x, icon_y))
            screen.blit(icon_text, icon_rect)

            # 🏷 ชื่อบัฟ (อยู่ขวา icon)
            label = font.render(buff_name, True, (255, 220, 220))
            screen.blit(label, (base_x + 30, y + 5))

            # 📊 Gradient bar
            time_w = int(bar_width * (remaining / max_time))
            bar_x = base_x
            bar_y = y + bar_height - 6
            bar_h = 5

            # วาด gradient จากแดง → ส้มอ่อน
            for i in range(time_w):
                t = i / bar_width
                r = int(200 + 55 * t)
                g = int(60 + 120 * t)
                b = int(60 * (1 - t))
                pygame.draw.line(screen, (r, g, b), (bar_x + i, bar_y), (bar_x + i, bar_y + bar_h))

            # ขอบบาร์ (optional)
            pygame.draw.rect(screen, (255, 255, 255, 50), (bar_x, bar_y, bar_width, bar_h), 1)

    def draw_cooldowns(self, screen, font, current_time):
        spacing = 36
        margin = 20
        screen_height = screen.get_height()

        cooldown_entries = []

        for skill_key, skill in skill_database.items():
            last_used = self.skill_cooldowns.get(skill.name, -99999)
            remaining = (skill.cooldown - (current_time - last_used)) / 1000
            total_cooldown = skill.cooldown / 1000

            # แสดงเฉพาะ skill ที่ cooldown ยังไม่หมด หรือเพิ่งหมดไม่นาน
            if remaining > 0 or (0 <= remaining > -2):
                cooldown_entries.append((skill.name, remaining, total_cooldown))

        for i, (name, remaining, total) in enumerate(reversed(cooldown_entries)):
            show_text = f"{name}: {remaining:.1f}s" if remaining > 0 else f"{name}: Ready"
            color = (200, 60, 60) if remaining > 0 else (30, 220, 30)
            outline_color = (255, 255, 255)

            text_surf = font.render(show_text, True, color)
            text_w, text_h = text_surf.get_size()
            x = margin
            offset_y = 40
            y = screen_height - margin - offset_y - (i + 1) * spacing

            # --- 🔲 วาดพื้นหลังโปร่งใส ---
            bg_rect = pygame.Surface((text_w + 12, text_h + 14), pygame.SRCALPHA)
            bg_rect.fill((0, 0, 0, 140))  # RGBA
            screen.blit(bg_rect, (x - 6, y - 6))

            # --- 🖋 วาดขอบข้อความ (outline) ---
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx != 0 or dy != 0:
                        outline_surf = font.render(show_text, True, outline_color)
                        screen.blit(outline_surf, (x + dx, y + dy))

            # --- ✏️ วาดข้อความจริง ---
            screen.blit(text_surf, (x, y))

            # --- 📊 วาด bar cooldown (เฉพาะตอน cooldown เหลือ) ---
            if remaining > 0:
                bar_w = text_w
                bar_h = 6
                bar_x = x
                bar_y = y + text_h + 4

                fill_ratio = max(0.0, min(1.0, remaining / total))
                fill_w = int(bar_w * fill_ratio)

                pygame.draw.rect(screen, (60, 60, 60), (bar_x, bar_y, bar_w, bar_h))  # พื้นหลัง bar
                pygame.draw.rect(screen, (200, 60, 60), (bar_x, bar_y, fill_w, bar_h))  # เติม bar

    def update_animation(self, dt):
        self.animation_timer += dt
        if self.animation_timer >= ANIMATION_DELAY:
            self.animation_timer = 0
            self.frame += 1
            frames_list = self.animations[self.current_animation].get(self.direction, [])
            if not frames_list:
                print(f"[ERROR] No frames found for {self.current_animation} - {self.direction}")
                return
            else:
                self.frame %= len(frames_list)
            self.image = frames_list[self.frame]

    def draw(self, screen):
        if self.is_dead:
            sprite, pos, alpha = self.update_death_effect()
            if sprite and alpha > 0:
                screen.blit(sprite, pos)
            return

        offset_x = self.rect.x - self.hitbox_offset_x
        offset_y = self.rect.y - self.hitbox_offset_y

        draw_image = self.image
        current_time = pygame.time.get_ticks()
        under_damage = current_time - self.damage_timer < self.damage_duration

        if under_damage:
            tinted = draw_image.copy()
            red_tint = pygame.Surface(tinted.get_size(), pygame.SRCALPHA)
            red_tint.fill((255, 100, 100, 100))
            tinted.blit(red_tint, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            shake_x = random.randint(-2, 2)
            shake_y = random.randint(-2, 2)
            screen.blit(tinted, (offset_x + shake_x, offset_y + shake_y))
        else:
            screen.blit(draw_image, (offset_x, offset_y))

        self.skill_effect_manager.draw_crescendo_only(screen)

        self.draw_barrier_effect(screen)
        self.skill_effect_manager.draw(screen)

        if SHOW_HITBOX_PLAYER:
            pygame.draw.rect(screen, (0, 255, 0), self.rect, 2)


