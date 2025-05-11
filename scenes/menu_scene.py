import sys
import os
import pygame
import random
import math
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from .base_scene import BaseScene
from .game_scene import GameScene
from .setting_scene import SettingScene

class FloatingNote:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = random.uniform(0.2, 0.5)
        self.alpha = 255
        self.symbol = random.choice(["♪", "♫", "𝄞"])
        self.font = pygame.font.Font("assets/fonts/NotoMusic-Regular.ttf", random.randint(20, 30))

    def update(self):
        self.y -= self.speed
        self.alpha -= 0.5

    def draw(self, screen):
        if self.alpha > 0:
            surface = self.font.render(self.symbol, True, (255, 200, 255))
            surface.set_alpha(int(self.alpha))
            screen.blit(surface, (self.x, self.y))

class Firefly:
    def __init__(self, width, height):
        self.x = random.randint(0, width)
        self.y = random.randint(height // 2, height)
        self.radius = random.randint(1, 3)
        self.alpha = random.randint(100, 200)
        self.dy = random.uniform(-0.3, -0.1)

    def update(self):
        self.y += self.dy
        self.alpha -= 0.3

    def draw(self, screen):
        if self.alpha > 0:
            s = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (255, 190, 255, int(self.alpha)), (self.radius, self.radius), self.radius)
            screen.blit(s, (self.x, self.y))

class MenuScene(BaseScene):
    def __init__(self, screen):
        super().__init__(screen)
        self.options = ["Start Game", "Settings", "Quit"]
        self.selected = 0

        self.font_path = "assets/fonts/Cinzel-Regular.ttf"
        self.title_font = pygame.font.Font(self.font_path, 72)
        self.option_font = pygame.font.Font(self.font_path, 40)
        self.small_font = pygame.font.Font(self.font_path, 20)

        self.color_selected = (210, 140, 255)
        self.color_unselected = (230, 230, 255)
        self.shadow_color = (0, 0, 0, 100)

        self.bg_image = pygame.image.load("assets/scene/menu_bg.png").convert()
        self.bg_image = pygame.transform.scale(self.bg_image, screen.get_size())

        self.overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 60))
        self.fade_alpha = 255
        self.fade_surface = pygame.Surface(screen.get_size())
        self.fade_surface.fill((0, 0, 0))

        self.notes = []
        self.fireflies = []

        self.quotes = [
            "In silence, her melody sleeps...",
            "Where harmony ends, her journey begins.",
            "The last note lingers in the dark.",
            "The overture fades into memory..."
        ]
        self.quote_index = 0
        self.quote = self.quotes[self.quote_index]
        self.quote_timer = 0
        self.quote_alpha = 255
        self.quote_fadeout = False

        self.glow_phase = 0

        try:
            pygame.mixer.music.load("assets/music/menu_ambience.ogg")
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1)
        except Exception as e:
            print("Music error:", e)

        try:
            self.select_sound = pygame.mixer.Sound("assets/sfx/select.wav")
            self.enter_sound = pygame.mixer.Sound("assets/sfx/enter.wav")
        except Exception as e:
            print("SFX error:", e)

    def on_enter(self):
        self.fade_alpha = 255

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_DOWN, pygame.K_s]:
                    self.selected = (self.selected + 1) % len(self.options)
                    self.select_sound.play()
                elif event.key in [pygame.K_UP, pygame.K_w]:
                    self.selected = (self.selected - 1) % len(self.options)
                    self.select_sound.play()
                elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                    self.enter_sound.play()
                    if self.selected == 0:
                        self.manager.switch_to(GameScene(self.screen))
                    elif self.selected == 1:
                        self.manager.switch_to(SettingScene(self.screen))
                    elif self.selected == 2:
                        self.running = False

    def update(self):
        self.glow_phase += 0.05

        if self.fade_alpha > 0:
            self.fade_alpha = max(0, self.fade_alpha - 8)

        if random.random() < 0.05:
            self.notes.append(FloatingNote(random.randint(0, self.screen.get_width()), self.screen.get_height()))
        if random.random() < 0.05:
            self.fireflies.append(Firefly(self.screen.get_width(), self.screen.get_height()))

        for n in self.notes:
            n.update()
        self.notes = [n for n in self.notes if n.alpha > 0]

        for f in self.fireflies:
            f.update()
        self.fireflies = [f for f in self.fireflies if f.alpha > 0]

        # Subtitle quote animation
        self.quote_timer += 1
        if self.quote_timer >= 420:  # 👈 ปรับจาก 180 → 420 (แสดงนานขึ้น)
            self.quote_fadeout = True
            self.quote_alpha -= 6
            if self.quote_alpha <= 0:
                self.quote_index = (self.quote_index + 1) % len(self.quotes)
                self.quote = self.quotes[self.quote_index]
                self.quote_alpha = 0
                self.quote_fadeout = False
                self.quote_timer = 0
        elif not self.quote_fadeout and self.quote_alpha < 255:
            self.quote_alpha += 4

    def draw_text(self, text, font, color, center_x, y, glow=False, scale=1.0):
        base = font.render(text, True, color)
        base = pygame.transform.rotozoom(base, 0, scale)
        x = center_x - base.get_width() // 2
        shadow = font.render(text, True, self.shadow_color)
        shadow = pygame.transform.rotozoom(shadow, 0, scale)
        if glow:
            for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
                self.screen.blit(shadow, (x + dx, y + dy))
        self.screen.blit(base, (x, y))
        return base.get_width(), base.get_height()

    def draw(self):
        self.screen.blit(self.bg_image, (0, 0))
        self.screen.blit(self.overlay, (0, 0))

        # ❌ ลบ glow ออก (เดิมเคยมีตรงนี้)

        for note in self.notes:
            note.draw(self.screen)
        for f in self.fireflies:
            f.draw(self.screen)

        center_x = self.screen.get_width() // 2
        self.draw_text("Symphony of the Lost", self.title_font, (200, 150, 255), center_x, 80, glow=True)

        start_y = 250
        spacing = 60
        for i, option in enumerate(self.options):
            is_selected = (i == self.selected)
            color = self.color_selected if is_selected else self.color_unselected
            scale = 1.08 if is_selected else 1.0
            w, h = self.draw_text(option, self.option_font, color, center_x, start_y + i * spacing, glow=is_selected, scale=scale)
            if is_selected:
                pygame.draw.rect(self.screen, color, (center_x - w // 2, start_y + i * spacing + h + 4, w, 3))

        # 🛠 Animated subtitle quote
        quote_surface = self.small_font.render(self.quote, True, (240, 240, 255))
        quote_surface.set_alpha(self.quote_alpha)
        slide_offset = int(20 * (1 - self.quote_alpha / 255))
        offset_x = 10   # 👈 ขยับขวาเล็กน้อย
        offset_y = -10  # 👈 ขยับขึ้นเล็กน้อย
        self.screen.blit(quote_surface, (
            center_x - quote_surface.get_width() // 2 + offset_x,
            480 + slide_offset + offset_y
        ))

        if self.fade_alpha > 0:
            self.fade_surface.set_alpha(self.fade_alpha)
            self.screen.blit(self.fade_surface, (0, 0))

        pygame.display.flip()