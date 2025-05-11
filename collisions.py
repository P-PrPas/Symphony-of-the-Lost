import pygame

class CollisionHandler:
    def __init__(self, collidables):
        self.static_rects = collidables
        self.dynamic_objects = []

    def add_dynamic(self, dynamic_rects):
        self.dynamic_objects.extend(dynamic_rects)

    def check_collision(self, rect, dx=0, dy=0):
        test_rect = rect.move(dx, dy)
        for obstacle in self.static_rects + self.dynamic_objects:
            if test_rect.colliderect(obstacle):
                return True
        return False

    def remove_dynamic(self, rect_to_remove):
        if rect_to_remove in self.dynamic_objects:
            self.dynamic_objects.remove(rect_to_remove)

    def clear_dynamic(self):
        self.dynamic_objects.clear()