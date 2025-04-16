from dataclasses import dataclass
import pygame
import random

RADIANT_DURATION = 500  # milliseconds
PARTICLE_LIFETIME = 600
SPARK_LIFETIME = 1000
GLOW_DURATION = 400

@dataclass
class RadiantPulse:
    center: tuple
    start_time: int
    max_radius: int = 80
    color: tuple = (180, 255, 220)

    def draw(self, surface, current_time):
        elapsed = current_time - self.start_time
        if elapsed > RADIANT_DURATION:
            return False

        progress = elapsed / RADIANT_DURATION
        radius = int(progress * self.max_radius)
        alpha = int(255 * (1 - progress))

        pulse_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(pulse_surface, (*self.color[:3], alpha), (radius, radius), radius)
        surface.blit(pulse_surface, (self.center[0] - radius, self.center[1] - radius))
        return True

class NoteParticle:
    def __init__(self, pos, symbol, color):
        self.x, self.y = pos
        self.symbol = symbol
        self.color = color
        self.vx = random.uniform(-1.5, 1.5)
        self.vy = random.uniform(-2.5, -1)
        self.alpha = 255
        self.birth = pygame.time.get_ticks()

    def update(self, current_time):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.1  # gravity-like
        life = current_time - self.birth
        self.alpha = max(0, 255 - int((life / PARTICLE_LIFETIME) * 255))
        return life < PARTICLE_LIFETIME

    def draw(self, surface, font):
        if self.alpha <= 0:
            return
        text = font.render(self.symbol, True, (*self.color, self.alpha))
        surface.blit(text, (self.x, self.y))

class GlowEffect:
    def __init__(self, rect):
        self.rect = rect
        self.start_time = pygame.time.get_ticks()

    def draw(self, surface, current_time):
        elapsed = current_time - self.start_time
        if elapsed > GLOW_DURATION:
            return False
        glow_surface = pygame.Surface((self.rect.width + 10, self.rect.height + 10), pygame.SRCALPHA)
        pygame.draw.rect(glow_surface, (255, 255, 255, 80), glow_surface.get_rect(), border_radius=12)
        surface.blit(glow_surface, (self.rect.x - 5, self.rect.y - 5))
        return True

class SparkParticle:
    def __init__(self, pos):
        self.x, self.y = pos
        self.vx = random.uniform(-0.5, 0.5)
        self.vy = random.uniform(-1.5, -0.5)
        self.radius = random.randint(1, 2)
        self.birth = pygame.time.get_ticks()
        self.alpha = 255

    def update(self, current_time):
        self.x += self.vx
        self.y += self.vy
        life = current_time - self.birth
        self.alpha = max(0, 255 - int((life / SPARK_LIFETIME) * 255))
        return life < SPARK_LIFETIME

    def draw(self, surface):
        if self.alpha > 0:
            pygame.draw.circle(surface, (255, 200, 255, self.alpha), (int(self.x), int(self.y)), self.radius)

class ComboEffectManager:
    def __init__(self):
        self.pulses = []
        self.particles = []
        self.glows = []
        self.sparks = []

    def trigger(self, center, note_symbols_colors, glow_rect=None, color_override=None):
        now = pygame.time.get_ticks()
        self.pulses.append(RadiantPulse(center, now, color=color_override or (180, 255, 220)))

        for sym, color in note_symbols_colors:
            final_color = color_override if color_override else color
            for _ in range(3):
                self.particles.append(NoteParticle(center, sym, final_color))


        if glow_rect:
            self.glows.append(GlowEffect(glow_rect))

        for _ in range(10):
            self.sparks.append(SparkParticle(center))

    def update_and_draw(self, surface, font):
        now = pygame.time.get_ticks()
        self.pulses = [p for p in self.pulses if p.draw(surface, now)]
        self.particles = [p for p in self.particles if p.update(now) or p.draw(surface, font)]
        self.glows = [g for g in self.glows if g.draw(surface, now)]
        self.sparks = [s for s in self.sparks if s.update(now) or s.draw(surface)]

    def draw(self, surface, font):
        self.update_and_draw(surface, font)
