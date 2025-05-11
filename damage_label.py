import pygame

class FloatingDamageText:
    def __init__(self, text, pos, color=(255, 0, 0), lifetime=600, rise_speed=0.3):
        self.text = str(text)
        self.x, self.y = pos
        self.color = color
        self.lifetime = lifetime  # milliseconds
        self.rise_speed = rise_speed
        self.start_time = pygame.time.get_ticks()
        self.font = pygame.font.SysFont("Arial", 28, bold=True)

    def update(self):
        self.y -= self.rise_speed

    def is_expired(self):
        return pygame.time.get_ticks() - self.start_time > self.lifetime

    def draw(self, screen):
        alpha = max(0, 255 - int((pygame.time.get_ticks() - self.start_time) / self.lifetime * 255))
        text_surface = self.font.render(self.text, True, self.color)
        text_surface.set_alpha(alpha)

        # ✅ สร้างขอบขาว
        outline_color = (255, 255, 255)
        outline_surfaces = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx != 0 or dy != 0:
                    s = self.font.render(self.text, True, outline_color)
                    s.set_alpha(alpha)
                    outline_surfaces.append((s, (self.x + dx, self.y + dy)))

        # วาดขอบก่อน
        for surf, pos in outline_surfaces:
            screen.blit(surf, pos)

        # วาดตัวเลขหลักทับตรงกลาง
        screen.blit(text_surface, (self.x, self.y))

