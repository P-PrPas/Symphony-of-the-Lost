import pygame
from enum import Enum

class NoteType(Enum):
    WHOLE = {
        "key": pygame.K_a,
        "symbol": "\U0001D15D",  # 𝅝
        "weight": 4.0,
        "color": (255, 245, 170),
        "cost": 20
    }
    HALF = {
        "key": pygame.K_s,
        "symbol": "\U0001D15E",  # 𝅗𝅥
        "weight": 2.0,
        "color": (140, 230, 255),
        "cost": 10
    }
    QUARTER = {
        "key": pygame.K_d,
        "symbol": "\U0001D15F",  # 𝅘𝅥
        "weight": 1.0,
        "color": (255, 170, 90),
        "cost": 5
    }
    EIGHTH = {
        "key": pygame.K_f,
        "symbol": "\U0001D160",  # 𝅘𝅥𝅮
        "weight": 0.5,
        "color": (255, 100, 200),
        "cost": 2
    }


