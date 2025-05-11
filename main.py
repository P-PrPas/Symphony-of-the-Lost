import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pygame
from scene_manager import SceneManager
from scenes.menu_scene import MenuScene
from settings import SCREEN_WIDTH, SCREEN_HEIGHT

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    manager = SceneManager(MenuScene(screen))
    manager.run()
    pygame.quit()

if __name__ == "__main__":
    main()
