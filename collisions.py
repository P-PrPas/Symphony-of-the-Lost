import pygame

class CollisionHandler:
    def __init__(self, collidables):
        self.static_rects = collidables
        self.dynamic_rects = []

    def add_dynamic(self, rects):
        self.dynamic_rects = rects

    def check_collision(self, rect, dx=0, dy=0):
        test_rect = rect.move(dx, dy)
        for obstacle in self.static_rects + self.dynamic_rects:
            if test_rect.colliderect(obstacle):
                return True
        return False

