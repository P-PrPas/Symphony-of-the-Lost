import pygame
import os
from map_profiles import MAP_PROFILES

class Map:
    def __init__(self, name: str, screen_size: tuple, map_dir="assets/background"):
        self.name = name
        self.screen_width, self.screen_height = screen_size
        self.map_dir = map_dir
        self.image = None
        self.collision_rects = []
        self.transition_zones = {}
        self.barrier_rects = []
        self.has_enemies = False
        self.cleared = True
        self.enemy_data = []
        self.scaled_image = None
        self.load()

    def load(self):
        image_path = os.path.join(self.map_dir, f"{self.name}.png")
        self.image = pygame.image.load(image_path).convert()
        self.scaled_image = pygame.transform.scale(self.image, (self.screen_width, self.screen_height))

        profile = MAP_PROFILES.get(self.name, {})
        self.collision_rects = [pygame.Rect(*r) for r in profile.get("collision_rects", [])]

        self.transition_zones = {
            direction: {
                "zone": pygame.Rect(0, 540, 50, 540) if direction == "left" else pygame.Rect(1870, 540, 50, 540),
                "target_map": data["target_map"],
                "player_pos": data["player_pos"]
            }
            for direction, data in profile.get("transitions", {}).items()
        }

        self.has_enemies = profile.get("has_enemies", False)
        self.cleared = not self.has_enemies
        self.enemy_data = profile.get("enemy_data", [])

        if profile.get("barriers", False) and not self.cleared:
            self.barrier_rects.append(pygame.Rect(0, 540, 50, 540))
            self.barrier_rects.append(pygame.Rect(1870, 540, 50, 540))

    def draw(self, screen):
        screen.blit(self.scaled_image, (0, 0))

    def get_collision_rects(self):
        return self.collision_rects + (self.barrier_rects if not self.cleared else [])

    def check_transition(self, player_rect):
        if self.has_enemies and not self.cleared:
            return None

        for data in self.transition_zones.values():
            if player_rect.colliderect(data["zone"]):
                return {
                    "target_map": data["target_map"],
                    "player_pos": data["player_pos"]
                }
        return None

    @staticmethod
    def fade(screen, color=(0, 0, 0), speed=10):
        fade = pygame.Surface(screen.get_size())
        fade.fill(color)
        for alpha in range(0, 255, speed):
            fade.set_alpha(alpha)
            screen.blit(fade, (0, 0))
            pygame.display.update()
            pygame.time.delay(5)

    def transition_to(self, screen, new_map_name, screen_size):
        Map.fade(screen)
        new_map = Map(new_map_name, screen_size, self.map_dir)
        Map.fade(screen, speed=-10)
        return new_map

    def mark_cleared(self):
        self.cleared = True
        self.barrier_rects.clear()