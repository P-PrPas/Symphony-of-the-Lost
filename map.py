import pygame
import os
from map_profiles import MAP_PROFILES
from npc_profile import NPC_PROFILES
from npc import NPC
from enemy import EnemyManager

class Map:
    def __init__(self, name: str, screen_size: tuple, map_dir="assets/background"):
        self.name = name
        self.screen_width, self.screen_height = screen_size
        self.map_dir = map_dir
        self.image = None
        self.collision_rects = []
        self.transition_zones = {}
        self.barrier_rects = []
        self.npc_list = []
        self.has_enemies = False
        self.cleared = True
        self.enemy_data = []
        self.enemy_manager = EnemyManager(None)
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

        if profile.get("has_npc", False) and profile.get("has_enemies", False):
            self.cutscene_mode = True
            self.enemy_manager.set_alpha(0)
        else:
            self.cutscene_mode = False
            self.enemy_manager.set_alpha(255)


        npc_names = profile.get("npcs", [])
        all_npc_data = NPC_PROFILES.get(self.name, [])
        self.npc_list = [
            NPC(
                n["name"],
                n["x"],
                n["y"],
                n["sprite_folder"],
                n["dialog"],
                n.get("scale", 1),
                tuple(n.get("frame_size", (32, 32)))  # 👈 default to 48x48
            )
            for n in all_npc_data
            if n["name"] in npc_names
        ]

    def draw(self, screen):
        screen.blit(self.scaled_image, (0, 0))

    def is_cutscene_mode(self):
        return self.has_enemies and any(npc.dialog_lines for npc in self.npc_list)


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

    def update_npcs(self, dt):
        for npc in self.npc_list:
            npc.update(dt)

    def draw_npcs(self, screen):
        for npc in self.npc_list:
            npc.draw(screen)

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