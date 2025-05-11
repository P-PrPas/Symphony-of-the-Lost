from settings import SHOW_HITBOX_PLAYER
import pygame
import math
import random
import os
from damage_label import FloatingDamageText

class SkillEffect(pygame.sprite.Sprite):
    def __init__(self, skill_data, origin_source, direction, current_time):
        super().__init__()
        self.skill_data = skill_data
        self.direction = direction
        self.frames = []
        self.frame_index = 0
        self.animation_speed = getattr(skill_data, "animation_speed_override", 80)
        self.duration_override = getattr(skill_data, "duration_override", None)
        self.last_update = current_time
        self.spawn_time = current_time
        self.scale = getattr(skill_data, 'scale', 3)
        self.damage = skill_data.damage
        self.follow_caster = skill_data.follow_caster

        # 💡 รองรับทั้ง entity และ position
        if self.follow_caster:
            self.origin_entity = origin_source
            self.origin_pos = None
        else:
            self.origin_entity = None
            self.origin_pos = origin_source  # (x, y)

        self.load_frames(skill_data.animation_path, skill_data.frames, direction)

        if self.frames:
            self.image = self.frames[self.frame_index]
        else:
            self.image = pygame.Surface((1, 1), pygame.SRCALPHA)

        self.rect = self.image.get_rect()
        self.set_position(direction)

        self.already_hit = set()



    def load_frames(self, sprite_path, num_frames, direction):
        if not sprite_path or not os.path.isfile(sprite_path):
            self.frames = []
            return
        sheet = pygame.image.load(sprite_path).convert_alpha()
        frame_width = 64
        frame_height = 64
        directions_map = {"right": 0, "left": 1, "up": 2, "down": 3}
        row = directions_map.get(direction, 3)

        self.frames = []
        for i in range(num_frames):
            x = i * frame_width
            y = row * frame_height
            frame_rect = pygame.Rect(x, y, frame_width, frame_height)
            frame_surface = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
            frame_surface.blit(sheet, (0, 0), frame_rect)

            scaled = pygame.transform.scale(
                frame_surface,
                (int(frame_width * self.scale), int(frame_height * self.scale))
            )
            self.frames.append(scaled)

    def set_position(self, direction):
        if self.follow_caster:
            ox, oy = self.origin_entity.rect.center
        else:
            ox, oy = self.origin_pos

        offsets = self.skill_data.effect_offsets or {}
        dx, dy = offsets.get(direction, (0, 0))
        self.rect.topleft = (ox + dx, oy + dy)

        raw_hitbox = self.skill_data.hitbox_sizes
        width, height = raw_hitbox.get(direction, (50, 50)) if isinstance(raw_hitbox, dict) else raw_hitbox
        cx, cy = self.rect.center
        self.hitbox = pygame.Rect(cx - width // 2, cy - height // 2, width, height)

    def update(self, current_time):
        if current_time - self.last_update >= self.animation_speed:
            self.frame_index += 1
            if self.frame_index >= len(self.frames):
                if self.duration_override:
                    if not hasattr(self, "_linger_start"):
                        self._linger_start = current_time
                    elif current_time - self._linger_start >= self.duration_override:
                        self.kill()
                    return
                else:
                    self.kill()
                    return
            self.image = self.frames[self.frame_index]
            self.last_update = current_time

        # ✅ อัปเดตตำแหน่งต่อเมื่อ follow_caster = True
        if self.follow_caster:
            self.set_position(self.direction)

    def draw(self, screen):
        screen.blit(self.image, self.rect.topleft)

        if SHOW_HITBOX_PLAYER:
            pygame.draw.rect(screen, (255, 0, 0), self.hitbox, 2)

import pygame
import math
import random


class Projectile:
    def __init__(self, x, y, direction, speed, skill_data):
        self.start_x = x
        self.start_y = y
        self.x = x
        self.y = y
        self.dir = direction
        self.speed = speed
        self.skill_data = skill_data
        self.is_max_combo = getattr(skill_data, "is_max_combo", False)
        self.damage = skill_data.damage
        self.max_range = 600
        self.alive = True

        self.base_radius = 16
        self.glow_color = (220, 160, 255, 60)
        self.trail_color = (240, 180, 255)
        self.note_color = (180, 220, 255)

        self.angle = 0
        self.pulse = 0
        self.font = pygame.font.Font("assets/fonts/Cinzel-Regular.ttf", 36)
        self.note_surface = self.font.render("𝄞", True, self.note_color)

        self.trail = []

        if direction == "up": self.dx, self.dy = 0, -1
        elif direction == "down": self.dx, self.dy = 0, 1
        elif direction == "left": self.dx, self.dy = -1, 0
        elif direction == "right": self.dx, self.dy = 1, 0
        else: self.dx, self.dy = 0, 0

    def update(self, dt):
        self.x += self.dx * self.speed * dt / 16
        self.y += self.dy * self.speed * dt / 16

        if random.random() < 0.6:
            self.trail.append([self.x, self.y, random.randint(3, 5), 200])
        self.trail = [t for t in self.trail if t[3] > 0]
        for t in self.trail:
            t[3] -= 12

        self.angle += 3
        self.pulse = 3 * math.sin(pygame.time.get_ticks() * 0.008)

        dist = math.hypot(self.x - self.start_x, self.y - self.start_y)
        if dist > self.max_range:
            self.alive = False

    def check_collision(self, enemies, effect_manager):
        for enemy in enemies:
            if enemy.hitbox.collidepoint(self.x, self.y) and not enemy.is_dead():
                enemy.take_damage(self.damage)
                self.alive = False
                effect_manager.spawn_impact(self.x, self.y)
                break

    def draw(self, screen):
        self.base_radius = 16 if not self.is_max_combo else 28
        self.note_surface = self.font.render("𝄞", True, (180, 220, 255) if not self.is_max_combo else (255, 100, 255))

        for i in range(2, 0, -1):
            glow_surface = pygame.Surface((60, 60), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface,
                (self.glow_color[0], self.glow_color[1], self.glow_color[2], self.glow_color[3] // i),
                (30, 30), self.base_radius + i * 4 + int(self.pulse))
            screen.blit(glow_surface, (self.x - 30, self.y - 30), special_flags=pygame.BLEND_RGBA_ADD)

        for tx, ty, size, alpha in self.trail:
            alpha = max(0, min(255, int(alpha)))
            trail_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(trail_surf, (*self.trail_color, alpha), (size, size), size)
            screen.blit(trail_surf, (tx - size, ty - size), special_flags=pygame.BLEND_RGBA_ADD)

        rotated = pygame.transform.rotate(self.note_surface, self.angle)
        rect = rotated.get_rect(center=(self.x, self.y))
        screen.blit(rotated, rect.topleft)

class CrescendoEffect:
    def __init__(self, player, duration):
        self.player = player
        self.duration = duration
        self.start_time = pygame.time.get_ticks()
        self.finished = False
        self.particles = []
        self.orbit_angle = 0.0
        self.spawn_interval = 50  # ms
        self.last_spawn_time = self.start_time

    def update(self):
        now = pygame.time.get_ticks()

        # 🎯 ครบระยะ → หยุด
        if now - self.start_time >= self.duration:
            self.finished = True
            return

        # 🎇 spawn particle ใหม่เรื่อย ๆ
        if now - self.last_spawn_time >= self.spawn_interval:
            self.last_spawn_time = now
            cx, cy = self.player.rect.center
            radius = 36  # ระยะล้อมรอบ
            speed = 0.2

            self.orbit_angle = (self.orbit_angle + 0.25) % (2 * math.pi)
            angle = self.orbit_angle + random.uniform(-0.2, 0.2)
            x = cx + math.cos(angle) * radius
            y = cy + math.sin(angle) * radius
            dx = random.uniform(-speed, speed)
            dy = random.uniform(-speed, speed)
            size = random.randint(2, 4)
            color = (200, 50, 50)
            lifetime = random.randint(400, 700)
            self.particles.append([x, y, dx, dy, lifetime, size, color])

        # 🎐 update movement
        self.particles = [
            [x + dx, y + dy, dx, dy, lifetime - 16, size, color]
            for x, y, dx, dy, lifetime, size, color in self.particles if lifetime > 0
        ]

    def draw(self, screen):
        for x, y, _, _, lifetime, size, color in self.particles:
            alpha = max(0, min(180, int(lifetime / 600 * 140)))
            glow_radius = size + 3

            # 🌫️ Glow เบา
            glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*color, int(alpha * 0.25)), (glow_radius, glow_radius), glow_radius)
            screen.blit(glow_surf, (x - glow_radius, y - glow_radius), special_flags=pygame.BLEND_RGBA_MULT)

            # 💡 Core particle
            pygame.draw.circle(screen, (*color, alpha), (int(x), int(y)), size)

class SoundquakeEffect:
    def __init__(self, origin, radius, damage, charge_ratio, font, note_char):
        self.origin = origin
        self.radius = radius
        self.damage = damage
        self.charge_ratio = charge_ratio
        self.font = font
        self.note_char = note_char
        self.spawn_time = pygame.time.get_ticks()
        self.duration = 600  # milliseconds
        self.alpha_decay_rate = 255 / self.duration
        self.notes = []
        self.rotation = 0
        self.generate_notes()
        self.alive = True  # ✅ สำคัญ

    def generate_notes(self):
        num_notes = int(5 + self.charge_ratio * 5)
        for i in range(num_notes):
            angle = (2 * math.pi * i) / num_notes
            self.notes.append({
                "angle": angle + random.uniform(-0.1, 0.1),
                "radius_offset": random.randint(-10, 10),
                "speed": random.uniform(1.5, 3.0),
                "char": self.note_char,
                "size": random.randint(16, 24)
            })

    def update(self, dt):
        self.rotation += dt * 0.005  # radians

    def draw(self, surface):
        now = pygame.time.get_ticks()
        elapsed = now - self.spawn_time
        if elapsed > self.duration:
            self.alive = False
            return False

        alpha = max(0, 255 - int(elapsed * self.alpha_decay_rate))
        x, y = self.origin

        # 🎆 Glow ขยายเป็นชั้น ๆ
        for i in range(6, 0, -1):
            r = int(self.radius * (i / 6))
            glow_surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (120, 100, 255, int(alpha * (i / 6))), (r, r), r)
            surface.blit(glow_surf, (x - r, y - r), special_flags=pygame.BLEND_PREMULTIPLIED)

        # 🎵 วาดโน้ตหมุนรอบ
        for note in self.notes:
            angle = note["angle"] + self.rotation * note["speed"]
            note_radius = self.radius + note["radius_offset"]
            nx = x + int(note_radius * math.cos(angle))
            ny = y + int(note_radius * math.sin(angle))
            txt = self.font.render(note["char"], True, (190, 150, 255))
            txt.set_alpha(alpha)
            surface.blit(txt, txt.get_rect(center=(nx, ny)))

        return True

    def check_collision(self, enemies, manager):
        for enemy in enemies:
            distance = math.hypot(enemy.rect.centerx - self.origin[0], enemy.rect.centery - self.origin[1])
            if distance < self.radius:
                enemy.take_damage(self.damage)

class HealEffect:
    def __init__(self, target_rect):
        self.particles = []
        for _ in range(25):
            angle = random.uniform(0, 2 * math.pi)
            radius = random.uniform(10, 40)
            speed = random.uniform(0.5, 1.5)
            dx = math.cos(angle) * speed
            dy = math.sin(angle) * speed
            size = random.randint(2, 5)
            color = (180, 255, 180)
            lifetime = random.randint(500, 1000)
            self.particles.append([target_rect.centerx, target_rect.centery, dx, dy, lifetime, size, color])
        self.finished = False

    def update(self):
        self.particles = [
            [x + dx, y + dy, dx, dy, lifetime - 16, size, color]
            for x, y, dx, dy, lifetime, size, color in self.particles if lifetime > 0
        ]
        if not self.particles:
            self.finished = True

    def draw(self, screen):
        for x, y, _, _, lifetime, size, color in self.particles:
            alpha = max(0, min(255, int(lifetime / 1000 * 255)))
            surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*color, alpha), (size, size), size)
            screen.blit(surf, (x - size, y - size))

class ImpactEffect:
    def __init__(self, x, y):
        self.particles = []
        for _ in range(10):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1.0, 3.5)
            dx = math.cos(angle) * speed
            dy = math.sin(angle) * speed
            lifetime = random.randint(300, 500)
            size = random.randint(3, 6)
            color = (255, 200, 255)
            self.particles.append([x, y, dx, dy, lifetime, size, color])
        self.start_time = pygame.time.get_ticks()
        self.finished = False

    def update(self):
        now = pygame.time.get_ticks()
        self.particles = [
            [x + dx, y + dy, dx, dy, lifetime - 16, size, color]
            for x, y, dx, dy, lifetime, size, color in self.particles if lifetime > 0
        ]
        if not self.particles:
            self.finished = True

    def draw(self, screen):
        for x, y, dx, dy, lifetime, size, color in self.particles:
            alpha = max(0, min(255, int(lifetime / 500 * 255)))
            surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*color, alpha), (size, size), size)
            screen.blit(surf, (x - size, y - size))


class SkillEffectManager:
    def __init__(self):
        self.effects = pygame.sprite.Group()
        self.damage_texts = []
        self.projectiles = []
        self.impact_effects = []
        self.heal_effects = []
        self.crescendo_effects = []

    def spawn(self, skill, origin_entity, direction, current_time):
        if not skill.animation_path:
            return
        if skill.follow_caster:
            effect = SkillEffect(skill, origin_entity, direction, current_time)
        else:
            effect = SkillEffect(skill, origin_entity.rect.center, direction, current_time)
        self.effects.add(effect)

    def spawn_heal_effect(self, player):
        self.heal_effects.append(HealEffect(player.rect))

    def spawn_crescendo_effect(self, player):
        self.crescendo_effects.append(CrescendoEffect(player, duration=5000))

    def cast_note_flurry(self, player, override_skill=None):
        from skills_database import skill_database
        skill = override_skill or skill_database["note_flurry"]
        proj = Projectile(player.rect.centerx, player.rect.centery, player.direction, 8, skill)
        self.projectiles.append(proj)

    def update_projectiles(self, screen, enemies, dt):
        for proj in self.projectiles[:]:
            if hasattr(proj, "check_collision"):
                proj.check_collision(enemies, self)
                proj.update(dt)
                proj.draw(screen)
                if not proj.alive:
                    self.projectiles.remove(proj)
            elif isinstance(proj, SoundquakeEffect):
                proj.update(dt, enemies)
                proj.draw(screen)
                if not proj.active:
                    self.projectiles.remove(proj)

        for effect in self.impact_effects[:]:
            effect.update()
            effect.draw(screen)
            if effect.finished:
                self.impact_effects.remove(effect)
    def check_skill_hits(self, enemies):
        for effect in self.effects:
            for enemy in enemies:
                if not enemy.alive:
                    continue
                if enemy in effect.already_hit:
                    continue  # ข้ามศัตรูที่โดนไปแล้ว
                if effect.hitbox.colliderect(enemy.hitbox):
                    enemy.take_damage(effect.damage)
                    effect.already_hit.add(enemy)
                    # 🎯 เพิ่มเลข damage popup ตรงกลาง enemy
                    center = enemy.rect.center
                    self.damage_texts.append(FloatingDamageText(effect.damage, (center[0], center[1] - 30)))

    def spawn_impact(self, x, y):
        self.impact_effects.append(ImpactEffect(x, y))

    def add_effect(self, effect):
        """
        เพิ่มเอฟเฟกต์แบบ custom (เช่น SoundquakeEffect ที่ไม่ใช่ Sprite)
        """
        self.projectiles.append(effect)

    def update(self, current_time: int):
        self.effects.update(current_time)
        for eff in self.heal_effects:
            eff.update()
        self.heal_effects = [e for e in self.heal_effects if not e.finished]

        for eff in self.crescendo_effects:
            eff.update()
        self.crescendo_effects = [e for e in self.crescendo_effects if not e.finished]

        # อัปเดต damage texts
        for dmg_text in self.damage_texts:
            dmg_text.update()
        self.damage_texts = [d for d in self.damage_texts if not d.is_expired()]

    def draw_crescendo_only(self, screen):
        for eff in self.crescendo_effects:
            eff.draw(screen)

    def draw(self, screen):
        for effect in self.effects:
            effect.draw(screen)
        for eff in self.heal_effects:
            eff.draw(screen)

        for dmg_text in self.damage_texts:
            dmg_text.draw(screen)