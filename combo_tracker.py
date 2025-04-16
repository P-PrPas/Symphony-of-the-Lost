from collections import deque
import pygame

class ComboTracker:
    def __init__(self, timeout_ms=3000):
        self.combo = deque()
        self.total_weight = 0.0
        self.timeout_ms = timeout_ms
        self.last_input_time = 0
        self.alert = False
        self.success = False
        self.success_timer = 0
        self.alert_timer = 0
        self.cooldown_timer = 0

    def add_note(self, note_type, current_time):
        if self.cooldown_timer > 0:
            return "cooldown"

        note_weight = note_type.value["weight"]
        self.combo.append(note_type)
        self.total_weight += note_weight
        self.last_input_time = current_time
        self.alert = False
        self.success = False

        if self.total_weight == 4.0:
            self.success = True
            self.success_timer = 60
            self.cooldown_timer = 30
            return "trigger"

        elif self.total_weight > 4.0:
            self.reset()
            self.alert = True
            self.alert_timer = 30
            self.cooldown_timer = 30
            return "overflow"

        return "continue"

    def update(self, current_time):
        if self.combo and current_time - self.last_input_time > self.timeout_ms:
            self.reset()

        if self.success_timer > 0:
            self.success_timer -= 1
            if self.success_timer == 0:
                self.reset()

        if self.alert_timer > 0:
            self.alert_timer -= 1
            if self.alert_timer == 0:
                self.alert = False

        if self.cooldown_timer > 0:
            self.cooldown_timer -= 1

    def reset(self):
        self.combo.clear()
        self.total_weight = 0.0
        self.alert = False
        self.success = False
        self.success_timer = 0

    def get_combo_symbols(self):
        return [note.value["symbol"] for note in self.combo]

    def get_combo_colors(self):
        return [note.value["color"] for note in self.combo]


    def is_alerting(self):
        return self.alert

    def is_success(self):
        return self.success

    def get_combo(self):
        return self.combo.copy()

    def get_last_note_type(self):
        return self.combo[-1] if self.combo else None

    def draw(self, screen, font):
        bar_width = 500
        bar_height = 80
        padding = 20
        bar_x = screen.get_width() - bar_width - padding
        bar_y = screen.get_height() - bar_height - 40

        pygame.draw.rect(screen, (70, 50, 90), (bar_x, bar_y, bar_width, bar_height), border_radius=15)

        x = bar_x + 20
        for note in self.combo:
            symbol = note.value["symbol"]
            color = note.value["color"]
            text = font.render(symbol, True, color)
            screen.blit(text, (x, bar_y + (bar_height - text.get_height()) // 2))
            x += text.get_width() + 25

        if self.success:
            pygame.draw.rect(screen, (0, 255, 100), (bar_x - 5, bar_y - 5, bar_width + 10, bar_height + 10), 3,
                             border_radius=20)
        elif self.alert:
            pygame.draw.rect(screen, (255, 50, 50), (bar_x - 5, bar_y - 5, bar_width + 10, bar_height + 10), 3,
                             border_radius=20)