import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pygame
import math
from .base_scene import BaseScene
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, BG_COLOR
from player import Player
from collisions import CollisionHandler
from map import Map
from map_profiles import MAP_PROFILES
from enemy import EnemyManager, global_exp_stars
from player_bar import SymphonicHealthBar, SymphonicStaminaBar
from stamina_system import StaminaSystem
from skill_effect import SkillEffectManager


class GameScene(BaseScene):

    def __init__(self, screen):
        super().__init__(screen)
        self.font = pygame.font.Font("assets/fonts/NotoMusic-Regular.ttf", 72)
        self.cooldown_font = pygame.font.SysFont("Arial", 20)
        pygame.display.set_caption("Symphony of the Lost")
        self.clock = pygame.time.Clock()
        self.stamina = StaminaSystem()
        self.skill_effect_manager = SkillEffectManager()
        self.fade_alpha = 0
        self.fade_speed = 5
        self.current_map = Map("tutorial_hall", (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.cutscene_mode = self.current_map.cutscene_mode
        self.collision_handler = CollisionHandler(self.current_map.get_collision_rects())
        self.player = Player(500, 800, self.collision_handler, self.skill_effect_manager)
        self.player_hp_bar = SymphonicHealthBar(max_hp=10)
        self.stamina_bar = SymphonicStaminaBar(max_stamina=50)
        self.enemy_manager = EnemyManager(self.collision_handler)
        if self.cutscene_mode:
            self.enemy_spawn_pending = True
            self.enemy_fade_in = False
            self.enemy_fade_timer = 0
            self.enemy_manager.set_alpha(0)
        else:
            self.enemy_manager.spawn_from_data(self.current_map.enemy_data, self.player)
            self.enemy_manager.set_alpha(255)
            self.enemy_spawn_pending = False
        self.running = True
        self.scene_state = "play"
        self.game_over_scene = None
        self.death_time = None
        self.death_fade_alpha = 0

        self.enemy_fade_in = False
        self.enemy_fade_timer = 0
        self.enemy_fade_duration = 500


    def handle_map_transition(self):
        result = self.current_map.check_transition(self.player.rect)
        if result:
            target_map = result["target_map"]
            new_map = Map(target_map, (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.current_map.fade(self.screen)
            self.current_map = new_map
            self.enemy_manager = EnemyManager(self.collision_handler)
            self.enemy_manager.spawn_from_data(self.current_map.enemy_data, self.player)
            self.skill_effect_manager.check_skill_hits(self.enemy_manager.enemies)
            self.current_map.fade(self.screen)

            new_x, new_y = result["player_pos"]
            if new_x is not None:
                self.player.rect.x = new_x
            if new_y is not None:
                self.player.rect.y = new_y

            self.collision_handler = CollisionHandler(self.current_map.get_collision_rects())
            self.player.collision_handler = self.collision_handler
            enemy_rects = [e.hitbox for e in self.enemy_manager.enemies if not e.is_dead()]
            self.collision_handler.add_dynamic(enemy_rects)

    def update(self):
        dt = self.clock.tick(FPS)
        current_time = pygame.time.get_ticks()

        # ✅ Cutscene logic block (ก่อน input event)
        if self.cutscene_mode:
            self.current_map.update_npcs(dt)

            for npc in self.current_map.npc_list:
                npc.update(dt)
                if not npc.dialog_active and not npc.fading_out and npc.dialog_index == 0:
                    npc.start_fade_out()
                    self.enemy_fade_in = True
                    self.enemy_fade_timer = 0

            if self.enemy_fade_in:
                if self.enemy_spawn_pending:
                    self.enemy_manager.spawn_from_data(self.current_map.enemy_data, self.player)
                    self.enemy_spawn_pending = False

                self.enemy_fade_timer += dt
                alpha = int(255 * min(1, self.enemy_fade_timer / self.enemy_fade_duration))
                self.enemy_manager.set_alpha(alpha)

                if self.enemy_fade_timer >= self.enemy_fade_duration:
                    self.cutscene_mode = False
                    self.enemy_fade_in = False

            return

        if self.player.is_dead:
            if self.death_time is None:
                self.death_time = current_time
                self.death_fade_alpha = 0
            self.death_fade_alpha = min(255, (current_time - self.death_time) * 255 // 1500)

            if current_time - self.death_time >= 1500 and self.game_over_scene is None:
                from .gameover_scene import GameOverScene
                self.game_over_scene = GameOverScene(self.screen, self)
                self.game_over_scene.manager = self.manager
                self.manager.switch_to(self.game_over_scene)

            return

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    from .pause_scene import PauseScene
                    pause_scene = PauseScene(self.screen, self)
                    pause_scene.manager = self.manager
                    self.manager.switch_to(pause_scene)

                elif event.key == pygame.K_e:
                    for npc in self.current_map.npc_list:
                        if npc.is_near_player(self.player.rect):
                            npc.toggle_dialog()

                elif event.key == pygame.K_RETURN:
                    for npc in self.current_map.npc_list:
                        if npc.dialog_active:
                            npc.advance_dialog()

        self.handle_map_transition()
        self.current_map.update_npcs(dt)

        keys = pygame.key.get_pressed()
        self.player.move(keys, dt, current_time)
        self.player.update_dash(current_time)
        self.stamina.update(dt, current_time)
        self.player_hp_bar.update(self.player.hp, dt)
        self.stamina_bar.update(self.stamina.current_stamina, dt)

        for star in global_exp_stars[:]:
            star.update()
            if star.check_collision():
                self.player.gain_exp(star.amount)
                global_exp_stars.remove(star)

        self.enemy_manager.update_all(self.player.rect, dt, self.player)
        self.collision_handler.dynamic_objects = [e.hitbox for e in self.enemy_manager.enemies if not e.is_dead()]
        self.player.handle_input(keys, current_time)
        self.player.update(current_time, self.enemy_manager)
        self.skill_effect_manager.update_projectiles(self.screen, self.enemy_manager.enemies, dt)

        if self.current_map.has_enemies and not self.current_map.cleared:
            if self.enemy_manager.all_defeated():
                self.current_map.mark_cleared()

    def retry(self):
        self.current_map = Map(self.current_map.name, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.collision_handler = CollisionHandler(self.current_map.get_collision_rects())
        start_x, start_y = MAP_PROFILES[self.current_map.name].get("starting_pos", (500, 700))
        self.player = Player(start_x, start_y, self.collision_handler, self.skill_effect_manager)
        self.player.is_dead = False
        self.player_hp_bar = SymphonicHealthBar(max_hp=10)
        self.enemy_manager = EnemyManager(self.collision_handler)
        self.enemy_manager.spawn_from_data(self.current_map.enemy_data, self.player)
        self.collision_handler.clear_dynamic()
        enemy_rects = [e.hitbox for e in self.enemy_manager.enemies if not e.is_dead()]
        self.collision_handler.add_dynamic(enemy_rects)
        print("[DEBUG] Dynamic collision count:", len(self.collision_handler.dynamic_objects))
        self.fade_alpha = 0
        self.game_over_scene = None

    def draw(self):
        self.screen.fill(BG_COLOR)
        self.current_map.draw(self.screen)
        self.current_map.draw_npcs(self.screen)

        for star in global_exp_stars[:]:
            star.draw(self.screen)

        self.enemy_manager.draw_all(self.screen)

        # ✅ วาด skill effects (main effects)
        self.skill_effect_manager.draw(self.screen)

        # ✅ projectile และ impact (ตัวนี้ถูกวาดตอน update_projectiles แล้ว)
        self.skill_effect_manager.update_projectiles(self.screen, self.enemy_manager.enemies, 0)

        self.player.draw(self.screen)
        self.player_hp_bar.draw(self.screen)
        self.stamina_bar.draw(self.screen)
        self.player.draw_exp_bar(self.screen)
        self.player.draw_combo_ui(self.screen, self.font)
        self.player.draw_cooldowns(self.screen, self.cooldown_font, pygame.time.get_ticks())
        self.player.draw_buff_ui(self.screen, self.cooldown_font)

        for npc in self.current_map.npc_list:
            if npc.dialog_active:
                npc.draw_dialog(self.screen)

        pygame.display.update()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                from .pause_scene import PauseScene
                pause_scene = PauseScene(self.screen, self)
                pause_scene.manager = self.manager
                self.manager.switch_to(pause_scene)

    def draw_static(self):
        self.screen.fill((0, 0, 0))
        self.current_map.draw(self.screen)
        for star in global_exp_stars:
            star.draw(self.screen)
        self.enemy_manager.draw_all(self.screen)
        self.player.draw(self.screen)
        self.player_hp_bar.draw(self.screen)
        self.stamina_bar.draw(self.screen)
        self.player.draw_exp_bar(self.screen)


if __name__ == "__main__":
    game = Game()
    game.run()
