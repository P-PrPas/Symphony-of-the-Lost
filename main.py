import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, BG_COLOR
from player import Player
from collisions import CollisionHandler
from map import Map
from enemy import EnemyManager
from player_bar import SymphonicHealthBar, SymphonicStaminaBar
from stamina_system import StaminaSystem


pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
font = pygame.font.Font("assets/fonts/NotoMusic-Regular.ttf", 72)
pygame.display.set_caption("Symphony of the Lost")
clock = pygame.time.Clock()
stamina = StaminaSystem()


screen_width = SCREEN_WIDTH
screen_height = SCREEN_HEIGHT
boundary_thickness = 10
current_map = Map("castle_hall", (SCREEN_WIDTH, SCREEN_HEIGHT))

collision_handler = CollisionHandler(current_map.get_collision_rects())

player = Player(500, 700, collision_handler)
player_hp_bar = SymphonicHealthBar(max_hp=10)
stamina_bar = SymphonicStaminaBar(max_stamina=50)

enemy_manager = EnemyManager(collision_handler)
enemy_manager.spawn_from_data(current_map.enemy_data)

running = True
while running:
    dt = clock.tick(FPS)
    current_time = pygame.time.get_ticks()
    stamina.is_sprinting = player.is_sprinting
    stamina.is_dashing = player.is_dashing
    stamina.update(dt, current_time)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if current_map.has_enemies and not current_map.cleared:
        if enemy_manager.all_defeated():
            current_map.mark_cleared()

    result = current_map.check_transition(player.rect)
    if result:
        target_map = result["target_map"]
        new_map = Map(target_map, (SCREEN_WIDTH, SCREEN_HEIGHT))
        current_map.fade(screen)
        current_map = new_map
        enemy_manager = EnemyManager(collision_handler)
        enemy_manager.spawn_from_data(current_map.enemy_data)
        current_map.fade(screen)

        new_x, new_y = result["player_pos"]
        if new_x is not None:
            player.rect.x = new_x
        if new_y is not None:
            player.rect.y = new_y

        collision_handler = CollisionHandler(current_map.get_collision_rects())
        player.collision_handler = collision_handler
        enemy_rects = [enemy.hitbox for enemy in enemy_manager.enemies if not enemy.is_dead()]
        collision_handler.add_dynamic(enemy_rects)

    keys = pygame.key.get_pressed()
    player.move(keys, dt, current_time)
    player.update_dash(current_time)
    player.update_animation(dt)
    player_hp_bar.update(player.hp, dt)
    stamina_bar.update(stamina.current_stamina, dt)

    screen.fill(BG_COLOR)
    current_map.draw(screen)

    enemy_manager.update_all(player.rect, dt)
    enemy_manager.draw_all(screen)

    player.draw(screen)
    player_hp_bar.draw(screen)

    player.handle_input(pygame.key.get_pressed(), pygame.time.get_ticks())
    player.update(pygame.time.get_ticks())
    player.draw_combo_ui(screen, font)

    stamina_bar.draw(screen)
    pygame.display.update()

pygame.quit()
