import pygame
import os
from settings import (PLAYER_SPEED, SPRINT_SPEED, SPRITE_SIZE, ANIMATION_DELAY, DASH_SPEED,
                      DASH_DURATION, DASH_COOLDOWN, SHOW_HITBOX_PLAYER)
from combo_tracker import ComboTracker
from combo_effect import ComboEffectManager
from note_type import NoteType
from key_manager import KeyPressManager
from skills_database import skill_database



class Player:
    def __init__(self, x, y, collision_handler):
        self.animations = self.load_animations("assets/sprites/test sprite")
        self.current_animation = "idle"
        self.image = self.animations[self.current_animation]["down"][0]

        HITBOX_WIDTH = 50
        HITBOX_HEIGHT = 95
        self.rect = pygame.Rect(x, y, HITBOX_WIDTH, HITBOX_HEIGHT)

        self.hitbox_offset_x = (SPRITE_SIZE * 5 - HITBOX_WIDTH) // 2
        self.hitbox_offset_y = (SPRITE_SIZE * 5 - HITBOX_HEIGHT) // 2

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

        self.hp = 10

    def load_animations(self, folder, frame_override=None):
        animations = {}
        SCALE_FACTOR = 5
        if frame_override == None:
            frame = 6
        else:
            frame = frame_override

        for animation_name in os.listdir(folder):
            if animation_name.endswith(".png"):
                anim_key = animation_name.split(".")[0]
                sheet = pygame.image.load(os.path.join(folder, animation_name)).convert_alpha()

                animations[anim_key] = {
                    "up": [], "down": [], "left": [], "right": []
                }
                for i in range(frame):
                    animations[anim_key]["up"].append(
                        self.get_scaled_sprite(sheet, i, 3, SCALE_FACTOR))
                    animations[anim_key]["down"].append(
                        self.get_scaled_sprite(sheet, i, 0, SCALE_FACTOR))
                    animations[anim_key]["left"].append(
                        self.get_scaled_sprite(sheet, i, 1, SCALE_FACTOR))
                    animations[anim_key]["right"].append(
                        self.get_scaled_sprite(sheet, i, 2, SCALE_FACTOR))

        print("Loaded animations:", animations.keys())
        return animations

    def get_scaled_sprite(self, sheet, frame, row, scale):
        sprite = sheet.subsurface((frame * SPRITE_SIZE, row * SPRITE_SIZE, SPRITE_SIZE, SPRITE_SIZE))
        return pygame.transform.scale(sprite, (int(SPRITE_SIZE * scale), int(SPRITE_SIZE * scale)))

    def set_animation(self, anim_name, frame_override=None):
        if anim_name not in self.animations and anim_name in skill_database:
            if frame_override:
                self.animations[anim_name] = \
                self.load_animations(skill_database[anim_name].animation_path, frame_override)[
                    anim_name]
            skill = skill_database[anim_name]
            self.animations[anim_name] = self.load_animations(skill.animation_path, frame_override=skill.frames)[
                anim_name]

        if anim_name in self.animations and anim_name != self.current_animation:
            self.current_animation = anim_name
            self.frame = 0
            self.animation_timer = 0
            self.image = self.animations[self.current_animation][self.direction][self.frame]

        self.frame = 0


    def move(self, keys, dt, current_time):
        shift_now = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        moving = keys[pygame.K_UP] or keys[pygame.K_DOWN] or keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]

        if self.is_dashing:
            pass
        elif self.is_sprinting and moving:
            self.set_animation("run", 9)
        elif moving:
            self.set_animation("walk", 6)
        else:
            self.set_animation("idle", 13)

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

    def update_dash(self, current_time):
        if self.is_dashing and current_time - self.dash_timer >= DASH_DURATION:
            self.is_dashing = False

    def handle_input(self, keys, current_time):
        for note in NoteType:
            if self.key_manager.is_new_press(note.value["key"], keys):
                result = self.combo_tracker.add_note(note, current_time)
                if note == NoteType.QUARTER:  # Strike Beat
                    if "strike_beat" not in self.animations:
                        self.current_skill = skill_database["strike_beat"]
                        self.animations["strike_beat"] = \
                        self.load_animations(self.current_skill.animation_path, frame_override=self.current_skill.frames)["strike_beat"]
                    self.set_animation("strike_beat")
                    print("Setting strike_beat animation")


                if result == "trigger":
                    print("🎯 TRIGGER")

                    # === Trigger Combo Effect ===
                    # ดึงตำแหน่ง Combo UI
                    margin = 60
                    spacing = 15
                    height_offset = 80
                    symbols = self.combo_tracker.get_combo_symbols()
                    colors = self.combo_tracker.get_combo_colors()

                    target_height = 48
                    total_width = 0
                    for symbol, color in reversed(list(zip(symbols, colors))):
                        surface = pygame.font.SysFont(None, 48).render(symbol, True, color)
                        scale = target_height / surface.get_height()
                        new_width = int(surface.get_width() * scale)
                        total_width += new_width + spacing

                    bar_padding_x = 25
                    bar_padding_y = 12
                    bar_height = target_height + bar_padding_y * 2
                    bar_width = total_width + bar_padding_x * 2
                    bar_x = 1920 - margin - bar_width
                    bar_y = 1080 - margin - height_offset - bar_padding_y
                    bar_center = (bar_x + bar_width // 2, bar_y + bar_height // 2)
                    bar_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)

                    symbol_color_pairs = list(zip(symbols, colors))
                    self.combo_effects.trigger(bar_center, symbol_color_pairs, glow_rect=bar_rect)


    def update(self, current_time):
        self.combo_tracker.update(current_time)
        self.update_animation(16)

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

    def update_animation(self, dt):
        self.animation_timer += dt
        if self.animation_timer >= ANIMATION_DELAY:
            self.animation_timer = 0
            self.frame = (self.frame + 1) % len(self.animations[self.current_animation][self.direction])
            self.image = self.animations[self.current_animation][self.direction][self.frame]
        if self.current_skill and self.frame >= self.current_skill.frames:
            self.current_skill = None
            self.set_animation("idle", 13)
        print(f"Updating animation: {self.current_animation}, frame: {self.frame}")

    def draw(self, screen):
        screen.blit(self.image, (self.rect.x - self.hitbox_offset_x, self.rect.y - self.hitbox_offset_y))
        if SHOW_HITBOX_PLAYER:
            pygame.draw.rect(screen, (0, 255, 0), self.rect, 2)

