import pygame
import math
import random
from .base_scene import BaseScene
from settings import SCREEN_WIDTH, SCREEN_HEIGHT

class PetalParticle:
    def __init__(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(-50, -10)
        self.speed_y = random.uniform(0.3, 1.0)
        self.drift = random.uniform(-0.3, 0.3)
        self.size = random.randint(4, 7)
        self.alpha = random.randint(100, 200)

    def update(self):
        self.y += self.speed_y
        self.x += self.drift
        if self.y > SCREEN_HEIGHT:
            return False
        return True

    def draw(self, screen):
        surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        pygame.draw.ellipse(surface, (255, 80, 120, self.alpha), (0, 0, self.size, self.size))
        screen.blit(surface, (self.x, self.y))

class GameOverScene(BaseScene):
    def __init__(self, screen, previous_scene):
        super().__init__(screen)
        self.previous_scene = previous_scene
        self.fade_alpha = 0
        self.show_menu = False
        self.selection = 0
        self.last_input_time = 0
        self.particles = []
        self.last_particle_time = 0
        self.bg_image = pygame.image.load("assets/scene/gameover_bg.png").convert()
        self.bg_image = pygame.transform.scale(self.bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.tagline_font = pygame.font.Font("assets/fonts/Cinzel-Regular.ttf", 30)
        self.title_font = pygame.font.Font("assets/fonts/Cinzel-Regular.ttf", 80)
        self.option_font = pygame.font.Font("assets/fonts/Cinzel-Regular.ttf", 42)

    def on_enter(self):
        pygame.mixer.music.fadeout(2000)
        pygame.mixer.music.load("assets/music/gameover_theme.ogg")
        pygame.mixer.music.play()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update(self):
        if self.fade_alpha < 160:
            self.fade_alpha = min(160, self.fade_alpha + 1.5)
        else:
            self.show_menu = True

        if self.show_menu:
            now = pygame.time.get_ticks()
            keys = pygame.key.get_pressed()

            if now - self.last_input_time > 200:
                if keys[pygame.K_UP] or keys[pygame.K_w]:
                    self.selection = (self.selection - 1) % 2
                    self.last_input_time = now
                elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
                    self.selection = (self.selection + 1) % 2
                    self.last_input_time = now
                elif keys[pygame.K_RETURN] or keys[pygame.K_SPACE]:
                    if self.selection == 0:  # Retry
                        pygame.mixer.music.fadeout(1000)
                        pygame.mixer.music.load("assets/music/menu_ambience.ogg")
                        pygame.mixer.music.play(-1)
                        self.previous_scene.retry()
                        self.previous_scene.scene_state = "play"
                        self.previous_scene.game_over_scene = None
                        self.previous_scene.player.is_dead = False
                        self.manager.switch_to(self.previous_scene)
                    elif self.selection == 1:  # Main Menu
                        pygame.mixer.music.fadeout(1000)
                        pygame.mixer.music.load("assets/music/menu_ambience.ogg")
                        pygame.mixer.music.play(-1)
                        from .menu_scene import MenuScene
                        self.manager.switch_to(MenuScene(self.screen))
                elif keys[pygame.K_r]:  # Shortcut for retry
                    pygame.mixer.music.fadeout(1000)
                    pygame.mixer.music.load("assets/music/menu_ambience.ogg")
                    pygame.mixer.music.play(-1)
                    self.previous_scene.retry()
                    self.previous_scene.scene_state = "play"
                    self.previous_scene.game_over_scene = None
                    self.previous_scene.player.is_dead = False
                    self.manager.switch_to(self.previous_scene)

        # spawn particles
        if pygame.time.get_ticks() - self.last_particle_time > 100:
            self.particles.append(PetalParticle())
            self.last_particle_time = pygame.time.get_ticks()

        self.particles = [p for p in self.particles if p.update()]

    def draw(self):
        self.screen.blit(self.bg_image, (0, 0))

        for p in self.particles:
            p.draw(self.screen)

        fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        fade_surface.set_alpha(self.fade_alpha)
        fade_surface.fill((0, 0, 0))
        self.screen.blit(fade_surface, (0, 0))

        if self.show_menu:
            self.draw_menu()

        pygame.display.update()

    def draw_menu(self):
        elapsed = pygame.time.get_ticks() - self.previous_scene.player.death_start_time

        game_over_text = self.title_font.render("Game Over", True, (255, 255, 255))
        retry_color = (255, 180, 180) if self.selection == 0 else (255, 255, 255)
        menu_color = (180, 180, 255) if self.selection == 1 else (255, 255, 255)

        retry_text = self.option_font.render("Retry (R)", True, retry_color)
        menu_text = self.option_font.render("Main Menu (M)", True, menu_color)
        tagline_text = self.tagline_font.render("The final note has fallen...", True, (220, 200, 240))

        shadow_offset = 2
        float_offset = int(5 * math.sin(pygame.time.get_ticks() / 300))

        y_center = SCREEN_HEIGHT // 2
        title_y = y_center - 140
        retry_y = y_center - 30
        menu_y = y_center + 30

        for surf, y in [(game_over_text, title_y), (retry_text, retry_y), (menu_text, menu_y)]:
            x = SCREEN_WIDTH // 2 - surf.get_width() // 2

            shadow = surf.copy()
            shadow.set_alpha(100)
            self.screen.blit(shadow, (x + shadow_offset, y + shadow_offset))

            glow = pygame.transform.rotozoom(surf, 0, 1.1)
            glow.set_alpha(25)
            self.screen.blit(glow, (SCREEN_WIDTH // 2 - glow.get_width() // 2, y))

            self.screen.blit(surf, (x, y))

        self.screen.blit(tagline_text, (SCREEN_WIDTH // 2 - tagline_text.get_width() // 2,
                                        y_center + 100))
