import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pygame

class BaseScene:
    def __init__(self, screen):
        self.screen = screen
        self.running = True
        self.manager = None

    def on_enter(self):
        pass

    def handle_events(self):
        raise NotImplementedError

    def update(self):
        raise NotImplementedError

    def draw(self):
        raise NotImplementedError