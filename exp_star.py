import pygame
from math import sin, sqrt, pi
import time

class EXPStar:
    def __init__(self, x, y, amount, player):
        self.x = x
        self.y = y
        self.amount = amount
        self.player = player
        self.radius = 6
        self.base_radius = 6
        self.color = (255, 230, 50)
        self.speed = 3
        self.spawn_time = time.time()

    def update(self):
        dx = self.player.rect.centerx - self.x
        dy = self.player.rect.centery - self.y
        dist = max(1, sqrt(dx ** 2 + dy ** 2))
        self.x += self.speed * dx / dist
        self.y += self.speed * dy / dist

    def draw(self, screen):
        pulse = 1 + 0.3 * sin((time.time() - self.spawn_time) * 6 * pi)  # pulsating effect
        radius = int(self.base_radius * pulse)

        # Outer glow
        for glow_radius in range(radius + 6, radius, -2):
            alpha = max(20, 255 - (glow_radius - radius) * 30)
            glow_surface = pygame.Surface((glow_radius*2, glow_radius*2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (*self.color, alpha), (glow_radius, glow_radius), glow_radius)
            screen.blit(glow_surface, (self.x - glow_radius, self.y - glow_radius))

        # Core
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), radius)

    def check_collision(self):
        dist = sqrt((self.player.rect.centerx - self.x) ** 2 + (self.player.rect.centery - self.y) ** 2)
        return dist < self.radius + 20
