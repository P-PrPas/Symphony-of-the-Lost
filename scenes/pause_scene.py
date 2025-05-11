import pygame
from .base_scene import BaseScene
from settings import SCREEN_WIDTH, SCREEN_HEIGHT
from .setting_scene import SettingScene


class PauseScene(BaseScene):
    def __init__(self, screen, game_scene):
        super().__init__(screen)
        self.screen = screen
        self.game_scene = game_scene
        self.running = True

        self.title_font = pygame.font.Font("assets/fonts/NotoMusic-Regular.ttf", 72)
        self.menu_font = pygame.font.Font("assets/fonts/NotoMusic-Regular.ttf", 36)
        self.subtitle_font = pygame.font.Font("assets/fonts/Cinzel-Regular.ttf", 24)

        self.options = ["Resume", "Settings", "Back to Menu"]
        self.selected_index = 0

        self.select_sound = pygame.mixer.Sound("assets/sfx/select.wav")
        self.enter_sound = pygame.mixer.Sound("assets/sfx/enter.wav")

        self.quotes = [
            "Music rests between battles.",
            "The melody pauses, but never ends.",
            "Every silence has meaning.",
        ]
        self.quote_index = 0
        self.last_quote_switch = pygame.time.get_ticks()
        self.quote_delay = 7000

        self.paused_music_volume = pygame.mixer.music.get_volume()
        pygame.mixer.music.fadeout(500)

    def handle_events(self):
        from .menu_scene import MenuScene

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.select_sound.play()
                    self.selected_index = (self.selected_index - 1) % len(self.options)
                elif event.key == pygame.K_DOWN:
                    self.select_sound.play()
                    self.selected_index = (self.selected_index + 1) % len(self.options)
                elif event.key == pygame.K_RETURN:
                    self.enter_sound.play()
                    selected = self.options[self.selected_index]
                    if selected == "Resume":
                        pygame.mixer.music.play(-1, fade_ms=500)  # Resume music with fade in
                        pygame.mixer.music.set_volume(self.paused_music_volume)
                        self.manager.switch_to(self.game_scene)
                    elif selected == "Settings":
                        from .setting_scene import SettingScene
                        setting = SettingScene(self.screen, previous_scene=self)
                        setting.manager = self.manager
                        self.manager.switch_to(setting)
                    elif selected == "Back to Menu":
                        pygame.mixer.music.fadeout(500)
                        self.manager.switch_to(MenuScene(self.screen))

    def update(self):
        result = self.handle_events()
        if result:
            return result

        now = pygame.time.get_ticks()
        if now - self.last_quote_switch > self.quote_delay:
            self.quote_index = (self.quote_index + 1) % len(self.quotes)
            self.last_quote_switch = now

        self.draw()
        return None

    def draw(self):
        # วาดฉากเกมหยุดไว้เบื้องหลัง
        self.game_scene.draw_static()

        # Overlay มืด
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        # หัวข้อ
        title_text = self.title_font.render("Paused", True, (200, 160, 255))
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 150))
        self.screen.blit(title_text, title_rect)

        # เมนูตัวเลือก
        option_spacing = 65  # ระยะห่างแต่ละบรรทัดให้มากขึ้น
        for i, option in enumerate(self.options):
            is_selected = i == self.selected_index
            color = (255, 255, 255) if not is_selected else (180, 140, 255)
            text = self.menu_font.render(option, True, color)
            scale = 1.05 if is_selected else 1.0
            text = pygame.transform.rotozoom(text, 0, scale)
            rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20 + i * option_spacing))

            if is_selected:
                padding_x, padding_y = 16, 10
                box_rect = pygame.Rect(rect.left - padding_x, rect.top - padding_y,
                                       rect.width + padding_x * 2, rect.height + padding_y * 2)
                pygame.draw.rect(self.screen, (180, 140, 255), box_rect, 2)

            self.screen.blit(text, rect)

        # Subtitle / Quote
        quote = self.quotes[self.quote_index]
        alpha = 255
        now = pygame.time.get_ticks()
        progress = (now - self.last_quote_switch) / self.quote_delay
        if progress > 0.8:
            alpha = int(255 * (1 - (progress - 0.8) / 0.2))
        elif progress < 0.2:
            alpha = int(255 * (progress / 0.2))

        quote_surf = self.subtitle_font.render(quote, True, (200, 160, 255))
        quote_surf.set_alpha(alpha)
        quote_x = SCREEN_WIDTH // 2 - quote_surf.get_width() // 2 - 20
        quote_y = SCREEN_HEIGHT - 80
        self.screen.blit(quote_surf, (quote_x, quote_y))

        pygame.display.update()
