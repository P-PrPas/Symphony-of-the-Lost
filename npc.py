import pygame
import os

class NPC:
    def __init__(self, name, x, y, sprite_folder, dialog, scale=1, frame_size=(48, 48)):
        self.name = name
        self.x = x
        self.y = y
        self.dialog_lines = dialog if isinstance(dialog, list) else [dialog]
        self.dialog_index = 0
        self.dialog_active = False

        self.sprite_folder = sprite_folder
        self.scale = scale
        self.frame_width, self.frame_height = frame_size

        self.idle_frames = self.load_idle_frames()
        self.current_frame = 0
        self.frame_timer = 0
        self.frame_rate = 200
        self.image = self.idle_frames[0]
        self.rect = self.image.get_rect()
        self.rect.bottomleft = (self.x, self.y)

        # Sound
        self.select_sound = pygame.mixer.Sound("assets/SFX/select.wav")
        self.select_sound.set_volume(0.5)

        # Dialog box
        self.dialog_box_surface = pygame.Surface((1800, 150), pygame.SRCALPHA)
        self.dialog_font = pygame.font.SysFont("Arial", 28)

        # Fade out
        self.alpha = 255
        self.fading_out = False
        self.fade_timer = 0
        self.fade_duration = 500

    def load_idle_frames(self):
        path = os.path.join("assets", self.sprite_folder, "idle.png")
        sheet = pygame.image.load(path).convert_alpha()
        frame_count = sheet.get_width() // self.frame_width
        frames = []
        for i in range(frame_count):
            frame = sheet.subsurface(
                pygame.Rect(i * self.frame_width, 0, self.frame_width, self.frame_height)
            ).copy()
            if self.scale != 1:
                frame = pygame.transform.scale(
                    frame,
                    (int(self.frame_width * self.scale), int(self.frame_height * self.scale))
                )
            frames.append(frame)
        return frames

    def start_fade_out(self):
        self.fading_out = True
        self.fade_timer = 0

    def update(self, dt):
        self.frame_timer += dt
        if self.frame_timer >= self.frame_rate:
            self.frame_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.idle_frames)
            self.image = self.idle_frames[self.current_frame]
            self.rect = self.image.get_rect()
            self.rect.bottomleft = (self.x, self.y)

        if self.fading_out:
            self.fade_timer += dt
            fade_ratio = min(1, self.fade_timer / self.fade_duration)
            self.alpha = int(255 * (1 - fade_ratio))
            if self.alpha <= 0:
                self.dialog_active = False
                self.fading_out = False
                self.alpha = 0

    def draw(self, screen):
        img = self.image.copy()
        img.set_alpha(self.alpha)
        screen.blit(img, self.rect)
        if self.dialog_active:
            self.draw_dialog(screen)

    def draw_dialog(self, screen):
        self.dialog_box_surface.fill((0, 0, 0, 230))
        pygame.draw.rect(self.dialog_box_surface, (255, 255, 255), (0, 0, 1800, 150), 2)

        if self.dialog_index < len(self.dialog_lines):
            line = self.dialog_lines[self.dialog_index]
            text = self.dialog_font.render(f"{self.name}: {line}", True, (255, 255, 255))
            self.dialog_box_surface.blit(text, (20, 40))

            hint_font = pygame.font.SysFont("Arial", 20)
            hint_text = hint_font.render("Press Enter", True, (200, 200, 200))
            hint_x = self.dialog_box_surface.get_width() - hint_text.get_width() - 20
            hint_y = self.dialog_box_surface.get_height() - hint_text.get_height() - 10
            self.dialog_box_surface.blit(hint_text, (hint_x, hint_y))

        screen.blit(self.dialog_box_surface, (60, 870))

    def is_near_player(self, player_rect, distance=80):
        return self.rect.colliderect(player_rect.inflate(distance, distance))

    def toggle_dialog(self):
        self.dialog_active = not self.dialog_active
        if self.dialog_active:
            self.dialog_index = 0
            self.select_sound.play()

    def advance_dialog(self):
        self.select_sound.play()
        self.dialog_index += 1
        if self.dialog_index >= len(self.dialog_lines):
            self.dialog_active = False
            self.dialog_index = 0