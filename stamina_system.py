import pygame


class StaminaSystem:
    def __init__(self, max_stamina=50, regen_rate=5, dash_cost=10, regen_cooldown=1000):
        self.max_stamina = max_stamina
        self.current_stamina = max_stamina
        self.regen_rate = regen_rate
        self.dash_cost = dash_cost
        self.regen_cooldown = regen_cooldown

        self.last_stamina_use = 0
        self.last_dash_time = 0

        self.is_sprinting = False
        self.is_dashing = False

    def update(self, dt, current_time):
        if self.is_dashing and current_time - self.last_dash_time > 500:
            self.use_stamina(self.dash_cost)
            self.last_dash_time = current_time

        if current_time - self.last_stamina_use > self.regen_cooldown:
            regen_amount = self.regen_rate * (dt / 1000)
            self.current_stamina = min(self.max_stamina, self.current_stamina + regen_amount)

    def can_dash(self):
        return self.current_stamina >= self.dash_cost

    def use_stamina(self, amount):
        self.current_stamina = max(0, self.current_stamina - amount)
        self.last_stamina_use = pygame.time.get_ticks()

    def get_stamina_ratio(self):
        return self.current_stamina / self.max_stamina

    def get_color_state(self):
        if self.is_dashing:
            return (100, 255, 255), (160, 255, 255)
        elif self.is_sprinting:
            return (60, 160, 220), (100, 200, 240)
        else:
            return (80, 140, 200), (120, 180, 230)
