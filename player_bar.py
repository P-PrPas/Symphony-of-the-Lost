import pygame
import random
import math


class FloatingNote:
    def __init__(self, x, y, speed, lifespan):
        self.x = x
        self.y = y
        self.speed = speed
        self.lifespan = lifespan
        self.age = 0
        self.alpha = 255
        self.exploded = False
        self.fragments = []

    def update(self, dt):
        self.age += dt
        if self.age >= self.lifespan and not self.exploded:
            self.exploded = True
            for _ in range(6):
                angle = random.uniform(0, 2 * math.pi)
                self.fragments.append({
                    "x": self.x,
                    "y": self.y,
                    "dx": math.cos(angle) * 0.05,
                    "dy": math.sin(angle) * 0.05,
                    "life": 0
                })

        if not self.exploded:
            self.y -= self.speed * dt / 16
            self.alpha = max(0, 255 - int(255 * (self.age / self.lifespan)))
        else:
            for frag in self.fragments:
                frag["x"] += frag["dx"] * dt
                frag["y"] += frag["dy"] * dt
                frag["life"] += dt

    def draw(self, surface):
        if not self.exploded:
            note_surface = pygame.Surface((10, 20), pygame.SRCALPHA)
            color = (255, 255, 255, self.alpha)
            pygame.draw.circle(note_surface, color, (5, 5), 3)
            pygame.draw.line(note_surface, color, (5, 5), (5, 18), 2)
            surface.blit(note_surface, (self.x, self.y))
        else:
            for frag in self.fragments:
                if frag["life"] < 800:
                    pygame.draw.circle(surface, (255, 200, 200, max(0, 255 - int(frag["life"] / 3))),
                                       (int(frag["x"]), int(frag["y"])), 2)


class BoxAura:
    def __init__(self, x, y, w, h, count=20):
        self.particles = []
        for i in range(count):
            pos = i / count
            self.particles.append({
                "progress": pos,
                "speed": random.uniform(0.0002, 0.00035),
            })
        self.rect = pygame.Rect(x, y, w, h)

    def update(self, dt):
        for p in self.particles:
            p["progress"] = (p["progress"] + p["speed"] * dt) % 1

    def draw(self, screen):
        for p in self.particles:
            prog = p["progress"]
            x, y, w, h = self.rect
            perimeter = 2 * (w + h)
            dist = prog * perimeter

            if dist <= w:
                px = x + dist
                py = y
            elif dist <= w + h:
                px = x + w
                py = y + (dist - w)
            elif dist <= w + h + w:
                px = x + (w - (dist - w - h))
                py = y + h
            else:
                px = x
                py = y + (h - (dist - w - h - w))

            pygame.draw.circle(screen, (255, 160, 240, 80), (int(px), int(py)), 2)


class SymphonicHealthBar:
    def __init__(self, max_hp, current_hp=None, pos=(20, 20), size=(320, 50)):
        self.max_hp = max_hp
        self.current_hp = current_hp if current_hp is not None else max_hp
        self.last_hp = self.current_hp
        self.pos = list(pos)
        self.base_pos = list(pos)
        self.size = size
        self.font = pygame.font.SysFont("georgia", 22, bold=True)
        self.label_font = pygame.font.SysFont("georgia", 20, bold=True)

        self.notes = []
        self.last_note_spawn = 0
        self.aura = BoxAura(pos[0], pos[1], size[0], size[1])

        self.shake_timer = 0
        self.shake_intensity = 0

    def update(self, current_hp, dt):
        if current_hp < self.current_hp:
            self.shake_timer = 300
            self.shake_intensity = 3
        self.last_hp = self.current_hp
        self.current_hp = max(0, min(current_hp, self.max_hp))
        self.last_note_spawn += dt
        self.aura.update(dt)

        if self.current_hp / self.max_hp <= 0.2:
            self.shake_timer = max(self.shake_timer, 100)
            self.shake_intensity = 1

        if self.shake_timer > 0:
            self.shake_timer -= dt
            self.pos[0] = self.base_pos[0] + random.randint(-self.shake_intensity, self.shake_intensity)
            self.pos[1] = self.base_pos[1] + random.randint(-self.shake_intensity, self.shake_intensity)
        else:
            self.pos = self.base_pos[:]

        if self.current_hp / self.max_hp > 0.3 and self.last_note_spawn > 500:
            spawn_area = pygame.Rect(self.pos[0] + 10, self.pos[1] + 8, self.size[0] - 20, self.size[1] - 16)
            center_exclude = pygame.Rect(self.pos[0] + self.size[0] // 2 - 40, self.pos[1], 80, self.size[1])
            for _ in range(10):
                px = random.randint(spawn_area.left, spawn_area.right)
                py = random.randint(spawn_area.top, spawn_area.bottom)
                if not center_exclude.collidepoint(px, py):
                    self.notes.append(FloatingNote(px, py, speed=random.uniform(0.05, 0.2), lifespan=1500))
                    break
            self.last_note_spawn = 0

        for note in self.notes[:]:
            note.update(dt)
            if note.exploded and all(f["life"] > 800 for f in note.fragments):
                self.notes.remove(note)

    def draw(self, screen):
        x, y = self.pos
        w, h = self.size
        ratio = self.current_hp / self.max_hp
        bar_width = int(w * ratio)

        if ratio > 0.7:
            bar_color = (160, 100, 220)
            glow = (180, 130, 230)
        elif ratio > 0.3:
            bar_color = (180, 80, 140)
            glow = (200, 100, 160)
        else:
            bar_color = (220, 50, 60)
            glow = (255, 70, 70)

        glow_surface = pygame.Surface((w + 10, h + 10), pygame.SRCALPHA)
        pygame.draw.rect(glow_surface, (*glow, 80), glow_surface.get_rect(), border_radius=16)
        screen.blit(glow_surface, (x - 5, y - 5))

        pygame.draw.rect(screen, (20, 10, 30), (x, y, w, h), border_radius=12)
        pygame.draw.rect(screen, (255, 255, 255), (x, y, w, h), 2, border_radius=12)
        pygame.draw.rect(screen, bar_color, (x + 3, y + 3, bar_width - 6, h - 6), border_radius=10)

        for note in self.notes:
            note.draw(screen)

        self.aura.draw(screen)

        label_text = self.label_font.render("HP", True, (255, 255, 255))
        screen.blit(label_text, (x + 12, y + h // 2 - label_text.get_height() // 2))

        hp_text = self.font.render(f"{int(self.current_hp)} / {int(self.max_hp)}", True, (255, 255, 255))
        screen.blit(hp_text, (x + w // 2 - hp_text.get_width() // 2, y + h // 2 - hp_text.get_height() // 2))


class SymphonicStaminaBar:
    def __init__(self, max_stamina, current_stamina=None, pos=(20, 80), size=(320, 40)):
        self.max_stamina = max_stamina
        self.current_stamina = current_stamina if current_stamina is not None else max_stamina
        self.last_stamina = self.current_stamina
        self.pos = list(pos)
        self.base_pos = list(pos)
        self.size = size
        self.font = pygame.font.SysFont("georgia", 20, bold=True)
        self.label_font = pygame.font.SysFont("georgia", 18, bold=True)

        self.notes = []
        self.last_note_spawn = 0
        self.aura = BoxAura(pos[0], pos[1], size[0], size[1])

        self.shake_timer = 0
        self.shake_intensity = 0

    def update(self, current_stamina, dt):
        if current_stamina < self.current_stamina:
            self.shake_timer = 300
            self.shake_intensity = 2
        self.last_stamina = self.current_stamina
        self.current_stamina = max(0, min(current_stamina, self.max_stamina))
        self.last_note_spawn += dt
        self.aura.update(dt)

        if self.current_stamina / self.max_stamina <= 0.2:
            self.shake_timer = max(self.shake_timer, 100)
            self.shake_intensity = 1

        if self.shake_timer > 0:
            self.shake_timer -= dt
            self.pos[0] = self.base_pos[0] + random.randint(-self.shake_intensity, self.shake_intensity)
            self.pos[1] = self.base_pos[1] + random.randint(-self.shake_intensity, self.shake_intensity)
        else:
            self.pos = self.base_pos[:]

        if self.current_stamina / self.max_stamina > 0.3 and self.last_note_spawn > 600:
            spawn_area = pygame.Rect(self.pos[0] + 10, self.pos[1] + 6, self.size[0] - 20, self.size[1] - 12)
            center_exclude = pygame.Rect(self.pos[0] + self.size[0] // 2 - 40, self.pos[1], 80, self.size[1])
            for _ in range(10):
                px = random.randint(spawn_area.left, spawn_area.right)
                py = random.randint(spawn_area.top, spawn_area.bottom)
                if not center_exclude.collidepoint(px, py):
                    self.notes.append(FloatingNote(px, py, speed=random.uniform(0.04, 0.12), lifespan=1200))
                    break
            self.last_note_spawn = 0

        for note in self.notes[:]:
            note.update(dt)
            if note.exploded and all(f["life"] > 800 for f in note.fragments):
                self.notes.remove(note)

    def draw(self, screen):
        x, y = self.pos
        w, h = self.size
        ratio = self.current_stamina / self.max_stamina
        bar_width = int(w * ratio)

        if ratio > 0.7:
            bar_color = (100, 200, 255)
            glow = (150, 220, 255)
        elif ratio > 0.3:
            bar_color = (80, 160, 220)
            glow = (120, 180, 230)
        else:
            bar_color = (60, 100, 180)
            glow = (100, 140, 200)

        glow_surface = pygame.Surface((w + 10, h + 10), pygame.SRCALPHA)
        pygame.draw.rect(glow_surface, (*glow, 70), glow_surface.get_rect(), border_radius=14)
        screen.blit(glow_surface, (x - 5, y - 5))

        pygame.draw.rect(screen, (10, 10, 25), (x, y, w, h), border_radius=10)
        pygame.draw.rect(screen, (255, 255, 255), (x, y, w, h), 2, border_radius=10)
        pygame.draw.rect(screen, bar_color, (x + 3, y + 3, bar_width - 6, h - 6), border_radius=8)

        for note in self.notes:
            note.draw(screen)

        self.aura.draw(screen)

        label_text = self.label_font.render("Stamina", True, (255, 255, 255))
        screen.blit(label_text, (x + 12, y + h // 2 - label_text.get_height() // 2))

        st_text = self.font.render(f"{int(self.current_stamina)} / {int(self.max_stamina)}", True, (255, 255, 255))
        screen.blit(st_text, (x + w // 2 - st_text.get_width() // 2, y + h // 2 - st_text.get_height() // 2))
