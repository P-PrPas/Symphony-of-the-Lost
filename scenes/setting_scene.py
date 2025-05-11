import sys
import os
import pygame
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from .base_scene import BaseScene
from settings_manager import SettingsManager

class SettingScene(BaseScene):
    def __init__(self, screen, previous_scene=None):
        super().__init__(screen)
        self.previous_scene = previous_scene

        self.manager_settings = SettingsManager
        self.settings = self.manager_settings.load()
        self.default_settings = {
            "SHOW_ENEMY_HP_BAR": False,
            "SHOW_HITBOX_PLAYER": False,
            "SHOW_HITBOX_ENEMY": False,
            "MASTER_VOLUME": 1.0,
            "MUSIC_VOLUME": 0.5,
            "SFX_VOLUME": 0.5
        }
        self.options = [
            ("SHOW_ENEMY_HP_BAR", self.settings["SHOW_ENEMY_HP_BAR"]),
            ("SHOW_HITBOX_PLAYER", self.settings["SHOW_HITBOX_PLAYER"]),
            ("SHOW_HITBOX_ENEMY", self.settings["SHOW_HITBOX_ENEMY"]),
            ("MASTER_VOLUME", self.settings["MASTER_VOLUME"]),
            ("MUSIC_VOLUME", self.settings["MUSIC_VOLUME"]),
            ("SFX_VOLUME", self.settings["SFX_VOLUME"]),
            ("RESET_DEFAULTS", None),
            ("BACK", None),
        ]
        self.selected = 0

        self.bg_image = pygame.image.load("assets/scene/menu_bg.png").convert()
        self.bg_image = pygame.transform.scale(self.bg_image, screen.get_size())
        self.overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 120))

        self.title_font = pygame.font.Font("assets/fonts/Cinzel-Regular.ttf", 64)
        self.option_font = pygame.font.Font("assets/fonts/Cinzel-Regular.ttf", 36)
        self.subtitle_font = pygame.font.Font("assets/fonts/Cinzel-Regular.ttf", 24)

        self.select_sound = pygame.mixer.Sound("assets/sfx/select.wav")
        self.enter_sound = pygame.mixer.Sound("assets/sfx/enter.wav")
        self.update_volumes()

        self.quotes = [
            "Only silence can reveal the truth.",
            "Even echoes fade in the void.",
            "The last note lingers in the dark.",
        ]
        self.quote_index = 0
        self.last_quote_switch = pygame.time.get_ticks()
        self.quote_delay = 8000
        self.running = True

    def update_volumes(self):
        pygame.mixer.music.set_volume(self.settings["MUSIC_VOLUME"] * self.settings["MASTER_VOLUME"])
        vol = self.settings["SFX_VOLUME"] * self.settings["MASTER_VOLUME"]
        self.select_sound.set_volume(vol)
        self.enter_sound.set_volume(vol)

    def on_enter(self):
        pass

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                key, val = self.options[self.selected]
                if event.key in [pygame.K_DOWN, pygame.K_s]:
                    self.select_sound.play()
                    self.selected = (self.selected + 1) % len(self.options)
                elif event.key in [pygame.K_UP, pygame.K_w]:
                    self.select_sound.play()
                    self.selected = (self.selected - 1) % len(self.options)
                elif event.key == pygame.K_LEFT:
                    if key in ["MASTER_VOLUME", "MUSIC_VOLUME", "SFX_VOLUME"]:
                        self.select_sound.play()
                        self.settings[key] = max(0.0, round(self.settings[key] - 0.05, 2))
                        self.manager_settings.save(self.settings)
                        self.options[self.selected] = (key, self.settings[key])
                        self.update_volumes()
                elif event.key == pygame.K_RIGHT:
                    if key in ["MASTER_VOLUME", "MUSIC_VOLUME", "SFX_VOLUME"]:
                        self.select_sound.play()
                        self.settings[key] = min(1.0, round(self.settings[key] + 0.05, 2))
                        self.manager_settings.save(self.settings)
                        self.options[self.selected] = (key, self.settings[key])
                        self.update_volumes()
                elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                    self.enter_sound.play()
                    if key == "BACK":
                        if self.previous_scene:
                            self.previous_scene.manager = self.manager
                            self.manager.switch_to(self.previous_scene)
                        else:
                            from .menu_scene import MenuScene
                            self.manager.switch_to(MenuScene(self.screen))
                    elif key == "RESET_DEFAULTS":
                        self.settings.update(self.default_settings)
                        self.manager_settings.save(self.settings)
                        for i, (k, _) in enumerate(self.options):
                            if k in self.settings:
                                self.options[i] = (k, self.settings[k])
                        self.update_volumes()
                    elif key not in ["MASTER_VOLUME", "MUSIC_VOLUME", "SFX_VOLUME"]:
                        new_val = not val
                        self.settings[key] = new_val
                        self.manager_settings.save(self.settings)
                        self.options[self.selected] = (key, new_val)

    def update(self):
        result = self.handle_events()
        if result:
            return result

        now = pygame.time.get_ticks()
        if now - self.last_quote_switch > self.quote_delay:
            self.quote_index = (self.quote_index + 1) % len(self.quotes)
            self.last_quote_switch = now

    def draw_slider(self, x, y, value, width=200, height=12):
        bar_rect = pygame.Rect(x, y, width, height)
        fill_rect = pygame.Rect(x, y, int(width * value), height)
        pygame.draw.rect(self.screen, (80, 80, 80), bar_rect, border_radius=6)
        pygame.draw.rect(self.screen, (180, 120, 255), fill_rect, border_radius=6)

    def draw(self):
        self.screen.blit(self.bg_image, (0, 0))
        self.screen.blit(self.overlay, (0, 0))

        title_surface = self.title_font.render("Settings", True, (220, 180, 255))
        self.screen.blit(title_surface, (self.screen.get_width()//2 - title_surface.get_width()//2, 48))

        start_y = 160
        spacing = 60
        for i, (key, val) in enumerate(self.options):
            is_selected = (i == self.selected)
            if key == "BACK":
                text = "← Back"
            elif key == "RESET_DEFAULTS":
                text = "Reset to Defaults"
            elif isinstance(val, bool):
                text = f"{key.replace('_', ' ').title()}: {'ON' if val else 'OFF'}"
            elif isinstance(val, float):
                text = f"{key.replace('_', ' ').title()}: {int(val * 100)}%"

            color = (255, 255, 255) if is_selected else (200, 200, 200)
            glow = 1.1 if is_selected else 1.0
            font_surface = self.option_font.render(text, True, color)
            font_surface = pygame.transform.rotozoom(font_surface, 0, glow)
            x = self.screen.get_width() // 2 - font_surface.get_width() // 2
            y = start_y + i * spacing

            if is_selected:
                pygame.draw.rect(self.screen, (180, 120, 255), (x - 12, y - 4, font_surface.get_width() + 24, font_surface.get_height() + 8), 2)

            self.screen.blit(font_surface, (x, y))

            if isinstance(val, float):
                slider_x = self.screen.get_width() // 2 - 100
                slider_y = y + font_surface.get_height() + 10
                self.draw_slider(slider_x, slider_y, val)

        # animated quote
        quote = self.quotes[self.quote_index]
        alpha = 255
        now = pygame.time.get_ticks()
        interval = self.quote_delay
        progress = (now - self.last_quote_switch) / interval
        if progress > 0.8:
            alpha = int(255 * (1 - (progress - 0.8) / 0.2))
        elif progress < 0.2:
            alpha = int(255 * (progress / 0.2))

        quote_surf = self.subtitle_font.render(quote, True, (200, 160, 255))
        quote_surf.set_alpha(alpha)
        quote_x = self.screen.get_width() // 2 - quote_surf.get_width() // 2 - 20
        quote_y = self.screen.get_height() - 80
        self.screen.blit(quote_surf, (quote_x, quote_y))

        pygame.display.flip()
