import pygame
import os
from enemy_profiles import ENEMY_PROFILES
from settings import SHOW_ENEMY_HP_BAR, SHOW_HITBOX_ENEMY
from math import sqrt
import random
from exp_star import EXPStar

SPRITE_SIZE = 64
ANIMATION_DELAY = 120

global_exp_stars = []


class Enemy:
    def __init__(self, x, y, enemy_type, sprite_folder, collision_handler,
                 hp, atk, speed, scale, hitbox_offset, hitbox_size, frame_config, exp, attack_cooldown, attack_range):
        self.x, self.y = x, y
        self.type = enemy_type
        self.max_hp = hp
        self.hp = hp
        self.atk = atk
        self.speed = speed
        self.scale = scale
        self.hitbox_offset = hitbox_offset
        self.hitbox_size = hitbox_size
        self.attack_range = attack_range
        self.buffer_range = 10 if self.type == "melee" else 0

        self.collision_handler = collision_handler
        self.frame_config = frame_config
        self.animations = self.load_animations(sprite_folder)
        self.current_animation = "walk"
        self.direction = "down"
        self.frame = 0
        self.animation_timer = 0
        self.playing_hurt = False
        self.playing_death = False
        self.playing_attack = False
        self.has_damaged = False
        self.hurt_start_time = 0
        self.attack_cooldown = attack_cooldown
        self.last_attack_time = 0
        self.exp = exp
        self.player = None
        self.image = self.animations[self.current_animation][self.direction][self.frame]
        self.rect = self.image.get_rect(topleft=(self.x, self.y))
        self.pos_x = float(self.rect.x)
        self.pos_y = float(self.rect.y)

        self.hitbox = pygame.Rect(
            self.rect.x + self.hitbox_offset[0],
            self.rect.y + self.hitbox_offset[1],
            self.hitbox_size[0],
            self.hitbox_size[1]
        )

        self.alive = True
        self.exp_given = False

        self.hp_bar = EnemyHPBar(self)

    def load_animations(self, folder):
        animations = {}
        for anim_type, frame_count in self.frame_config.items():
            animations[anim_type] = {d: [] for d in ["up", "down", "left", "right"]}
            sheet = pygame.image.load(os.path.join(folder, f"{anim_type}.png")).convert_alpha()

            for i in range(frame_count):
                for j, direction in enumerate(["down", "left", "right", "up"]):
                    sprite = sheet.subsurface((i * SPRITE_SIZE, j * SPRITE_SIZE, SPRITE_SIZE, SPRITE_SIZE))
                    sprite = pygame.transform.scale(sprite, (SPRITE_SIZE * self.scale, SPRITE_SIZE * self.scale))
                    animations[anim_type][direction].append(sprite)

        return animations

    def move_towards_player(self):
        print(
            f"[DEBUG] Attempting to move. Alive: {self.alive}, Hurt: {self.playing_hurt}, Death: {self.playing_death}")
        if not self.alive or self.playing_death or self.playing_hurt:
            return

        if not self.player:
            print("[DEBUG] Player reference is None.")
            return

        dx = self.player.rect.centerx - self.rect.centerx
        dy = self.player.rect.centery - self.rect.centery
        distance = sqrt(dx ** 2 + dy ** 2)

        print(
            f"[DEBUG] Distance to player: {distance:.2f}, Attack range: {self.attack_range}, Cooldown: {pygame.time.get_ticks() - self.last_attack_time}")

        if abs(dx) > abs(dy):
            self.direction = "right" if dx > 0 else "left"
        else:
            self.direction = "down" if dy > 0 else "up"

        # ✅ Enemy will keep moving if not in attack animation
        #    And will fallback to reposition if too close
        should_move = False
        if distance > self.attack_range * 1.15 and not self.playing_attack:
            should_move = True
        elif distance < self.attack_range * 0.75 and not self.playing_attack:
            # Fallback: too close, back away slightly
            dx = -dx
            dy = -dy
            should_move = True

        if should_move:
            direction_x = dx / distance
            direction_y = dy / distance

            self.pos_x += direction_x * self.speed
            self.pos_y += direction_y * self.speed

            self.rect.x = int(self.pos_x)
            self.rect.y = int(self.pos_y)

            self.hitbox.topleft = (
                self.rect.x + self.hitbox_offset[0],
                self.rect.y + self.hitbox_offset[1]
            )
        else:
            now = pygame.time.get_ticks()
            if now - self.last_attack_time >= self.attack_cooldown and not self.playing_attack:
                self.playing_attack = True
                self.current_animation = "attack"
                self.frame = 0
                self.animation_timer = 0
                self.last_attack_time = now

    def update_animation(self, dt):
        self.animation_timer += dt
        if self.animation_timer >= ANIMATION_DELAY:
            self.animation_timer = 0
            frames = self.animations[self.current_animation][self.direction]

            self.frame += 1
            print(
                f"[DEBUG] Animation Frame Update | Animation: {self.current_animation}, Frame: {self.frame}/{len(frames)}")

            if self.frame >= len(frames):
                self.frame = 0

                if self.current_animation == "hurt":
                    self.playing_hurt = False
                    self.current_animation = "walk"
                    print("[DEBUG] Hurt animation ended. Returning to walk.")

                elif self.current_animation == "death":
                    self.alive = False
                    self.image = None
                    print("[DEBUG] Death animation ended. Enemy marked as dead.")
                    if not self.exp_given:
                        self.spawn_exp(self.player)
                        self.exp_given = True
                    return

                elif self.current_animation == "attack":
                    self.playing_attack = False
                    self.current_animation = "walk"
                    self.has_damaged = False
                    print("[DEBUG] Attack animation ended. Returning to walk.")

            # ดาเมจเกิด frame สุดท้ายของ attack
            if self.current_animation == "attack" and self.frame == len(frames) - 1:
                if not self.has_damaged:
                    dx = self.player.rect.centerx - self.rect.centerx
                    dy = self.player.rect.centery - self.rect.centery
                    distance = sqrt(dx ** 2 + dy ** 2)
                    print(f"[DEBUG] Melee attack check: distance={distance}, range={self.attack_range}")
                    if distance <= self.attack_range * 1.15:
                        print("[HIT] Enemy attacked player")
                        self.player.take_damage(self.atk)
                    self.has_damaged = True

        if self.current_animation != "death" or self.alive:
            self.image = self.animations[self.current_animation][self.direction][self.frame]

    def spawn_exp(self, player):
        global global_exp_stars
        pieces = random.randint(4, 6)
        for _ in range(pieces):
            offset_x = random.randint(-10, 10)
            offset_y = random.randint(-10, 10)
            star = EXPStar(self.rect.centerx + offset_x, self.rect.centery + offset_y, self.exp // pieces, player)
            global_exp_stars.append(star)

    def update(self, player_rect, dt, player):
        if self.alive:

            if not self.player:
                self.player = player  # ✅ fallback สำรอง
            print(f"[DEBUG] Enemy Update | Alive: {self.alive}, Animation: {self.current_animation}, Hurt: {self.playing_hurt}")
            self.update_animation(dt)
            self.move_towards_player()

    def take_damage(self, amount):
        print(
            f"[DEBUG] take_damage called | HP: {self.hp}, Playing Hurt: {self.playing_hurt}, Playing Death: {self.playing_death}")

        if self.playing_hurt or self.playing_death:
            print("[DEBUG] Ignored damage due to current animation state.")
            return
        self.hp -= amount
        print(f"[DEBUG] Damage applied. New HP: {self.hp}")
        if self.hp <= 0:
            self.hitbox = pygame.Rect(0, 0, 0, 0)
            self.collision_handler.remove_dynamic(self.hitbox)
            self.playing_death = True
            self.current_animation = "death"
            self.frame = 0
            self.animation_timer = 0
            self.image = self.animations["death"][self.direction][self.frame]
            print("[DEBUG] Enemy is dying. Switching to death animation.")
        else:
            self.current_animation = "hurt"
            self.playing_hurt = True
            self.hurt_start_time = pygame.time.get_ticks()
            self.frame = 0
            self.animation_timer = 0
            self.image = self.animations["hurt"][self.direction][self.frame]
            print("[DEBUG] Enemy is hurt. Switching to hurt animation.")

    def is_dead(self):
        return not self.alive

    def draw(self, screen):
        if (self.alive or self.current_animation == "death") and self.image:
            screen.blit(self.image, self.rect)
            if SHOW_HITBOX_ENEMY and self.alive:
                pygame.draw.rect(screen, (255, 0, 0), self.hitbox, 2)
            if self.alive:
                self.hp_bar.draw(screen)




class EnemyManager:
    def __init__(self, collision_handler):
        self.enemies = []
        self.collision_handler = collision_handler

    def create_enemy_from_profile(self, x, y, enemy_type, sprite_name):
        profile = ENEMY_PROFILES[sprite_name]
        sprite_folder = os.path.join("assets/enemies", sprite_name)
        return Enemy(
            x, y, enemy_type, sprite_folder, self.collision_handler,
            hp=profile["hp"],
            atk=profile["atk"],
            speed=profile["speed"],
            scale=profile["scale"],
            hitbox_offset=profile["hitbox_offset"],
            hitbox_size=profile["hitbox_size"],
            frame_config=profile["frame_config"],
            exp = profile["exp"],
            attack_cooldown = profile["attack_cooldown"],
            attack_range=profile["attack_range"]
        )

    def spawn_from_data(self, data_list, player=None):
        self.enemies.clear()
        for data in data_list:
            try:
                enemy = self.create_enemy_from_profile(data["x"], data["y"], data["type"], data["sprite"])
                if player:
                    enemy.player = player
                self.enemies.append(enemy)
                print(f"[OK] Spawned enemy {data['type']} using {data['sprite']} at ({data['x']},{data['y']})")
            except Exception as e:
                print(f"[ERROR] Failed to create enemy {data}: {e}")

    def set_alpha(self, alpha):
        for enemy in self.enemies:
            if hasattr(enemy, "image"):
                enemy.image.set_alpha(alpha)

    def update_all(self, player_rect, dt, player):
        for enemy in self.enemies:
            enemy.update(player_rect, dt, player)

    def draw_all(self, screen, debug=False):
        for enemy in self.enemies:
            enemy.draw(screen)

    def all_defeated(self):
        return all(enemy.is_dead() for enemy in self.enemies)


class EnemyHPBar:
    def __init__(self, enemy, width=50, height=6, offset_y=-50):
        self.enemy = enemy
        self.width = width
        self.height = height
        self.offset_y = offset_y
        self.border_color = (255, 255, 255)
        self.bg_color = (60, 60, 60)
        self.hp_color = (200, 50, 50)

    def draw(self, screen):
        if not SHOW_ENEMY_HP_BAR or not self.enemy.alive:
            return

        x = self.enemy.rect.centerx - self.width // 2
        y = self.enemy.rect.top - self.offset_y

        ratio = max(0, self.enemy.hp / self.enemy.max_hp)
        inner_width = int(self.width * ratio)

        pygame.draw.rect(screen, self.bg_color, (x, y, self.width, self.height))
        pygame.draw.rect(screen, self.border_color, (x, y, self.width, self.height), 1)
        pygame.draw.rect(screen, self.hp_color, (x + 1, y + 1, inner_width - 2, self.height - 2))
