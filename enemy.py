import pygame
import os
from math import sqrt
from enemy_profiles import ENEMY_PROFILES
from settings import SHOW_ENEMY_HP_BAR, SHOW_HITBOX_ENEMY

SPRITE_SIZE = 64
ANIMATION_DELAY = 120


class Enemy:
    def __init__(self, x, y, enemy_type, sprite_folder, collision_handler,
                 hp, atk, speed, scale, hitbox_offset, hitbox_size):
        self.x, self.y = x, y
        self.type = enemy_type
        self.max_hp = hp
        self.hp = hp
        self.hp_bar = EnemyHPBar(self)
        self.atk = atk
        self.speed = speed
        self.scale = scale
        self.hitbox_offset = hitbox_offset
        self.hitbox_size = hitbox_size
        self.attack_range = 50 if self.type == "melee" else 200

        self.collision_handler = collision_handler
        self.animations = self.load_animations(sprite_folder)
        self.current_animation = "walk"
        self.direction = "down"
        self.frame = 0
        self.animation_timer = 0

        self.image = self.animations[self.current_animation][self.direction][self.frame]
        self.rect = self.image.get_rect(topleft=(self.x, self.y))

        self.hitbox = pygame.Rect(
            self.rect.x + self.hitbox_offset[0],
            self.rect.y + self.hitbox_offset[1],
            self.hitbox_size[0],
            self.hitbox_size[1]
        )

        self.alive = True

    def load_animations(self, folder):
        animations = {"walk": {"up": [], "down": [], "left": [], "right": []}}
        sheet = pygame.image.load(os.path.join(folder, "walk.png")).convert_alpha()

        for i in range(8):
            for j, direction in enumerate(["down", "left", "right", "up"]):
                sprite = sheet.subsurface((i * SPRITE_SIZE, j * SPRITE_SIZE, SPRITE_SIZE, SPRITE_SIZE))
                sprite = pygame.transform.scale(sprite, (SPRITE_SIZE * self.scale, SPRITE_SIZE * self.scale))
                animations["walk"][direction].append(sprite)

        return animations

    def move_towards_player(self, player_rect):
        if not self.alive:
            return

        dx = player_rect.centerx - self.rect.centerx
        dy = player_rect.centery - self.rect.centery
        distance = sqrt(dx ** 2 + dy ** 2)

        if distance > self.attack_range:
            direction_x = dx / distance
            direction_y = dy / distance

            new_x = self.rect.x + direction_x * self.speed
            new_y = self.rect.y + direction_y * self.speed

            x_rect = self.rect.move(direction_x * self.speed, 0)
            if not self.collision_handler.check_collision(self.rect, direction_x * self.speed, 0) \
                    and not x_rect.colliderect(player_rect):
                self.rect.x = new_x

            y_rect = self.rect.move(0, direction_y * self.speed)
            if not self.collision_handler.check_collision(self.rect, 0, direction_y * self.speed) \
                    and not y_rect.colliderect(player_rect):
                self.rect.y = new_y

            if abs(dx) > abs(dy):
                self.direction = "right" if dx > 0 else "left"
            else:
                self.direction = "down" if dy > 0 else "up"

        self.hitbox.topleft = (
            self.rect.x + self.hitbox_offset[0],
            self.rect.y + self.hitbox_offset[1]
        )

    def update_animation(self, dt):
        self.animation_timer += dt
        if self.animation_timer >= ANIMATION_DELAY:
            self.animation_timer = 0
            self.frame = (self.frame + 1) % len(self.animations[self.current_animation][self.direction])
            self.image = self.animations[self.current_animation][self.direction][self.frame]

    def update(self, player_rect, dt):
        if not self.alive:
            return
        self.move_towards_player(player_rect)
        self.update_animation(dt)

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            self.alive = False

    def is_dead(self):
        return not self.alive

    def draw(self, screen):
        if self.alive:
            screen.blit(self.image, self.rect)
            if SHOW_HITBOX_ENEMY:
                pygame.draw.rect(screen, (255, 0, 0), self.hitbox, 2)
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
            hitbox_size=profile["hitbox_size"]
        )

    def spawn_from_data(self, data_list):
        self.enemies.clear()
        for data in data_list:
            try:
                enemy = self.create_enemy_from_profile(data["x"], data["y"], data["type"], data["sprite"])
                self.enemies.append(enemy)
            except Exception as e:
                print(f"[ERROR] Failed to create enemy {data}: {e}")

    def update_all(self, player_rect, dt):
        for enemy in self.enemies:
            enemy.update(player_rect, dt)

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
        if not SHOW_ENEMY_HP_BAR:
            return

        x = self.enemy.rect.centerx - self.width // 2
        y = self.enemy.rect.top - self.offset_y

        ratio = max(0, self.enemy.hp / self.enemy.max_hp)
        inner_width = int(self.width * ratio)

        # พื้นหลัง + ขอบ
        pygame.draw.rect(screen, self.bg_color, (x, y, self.width, self.height))
        pygame.draw.rect(screen, self.border_color, (x, y, self.width, self.height), 1)

        # แถบเลือด
        pygame.draw.rect(screen, self.hp_color, (x + 1, y + 1, inner_width - 2, self.height - 2))