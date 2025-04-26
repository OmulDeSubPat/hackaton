import pygame
import platform
from lupta import Enemy
import math

print("harta.py loaded")

# Constants
WIDTH, HEIGHT = 600,800
PLAYER_SIZE = 50
PLAYER_COLOR = (0, 255, 0)
MAP_WIDTH, MAP_HEIGHT = 10000, 10000  # Match the 20,000x20,000 map.png
GRID_SPACING = 500  # Adjusted for larger map
FPS = 60
HEALTH_BAR_WIDTH = 50
HEALTH_BAR_HEIGHT = 10
HEALTH_BAR_COLOR = (0, 255, 0)
HEALTH_BAR_BG_COLOR = (255, 0, 0)
DODGE_DURATION = 18
DODGE_DISTANCE = 100
DODGE_COOLDOWN = 60

# Camera class to handle scrolling
class Camera:
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, rect):
        return pygame.Rect(rect.x - self.camera.x, rect.y - self.camera.y, rect.width, rect.height)

    def update(self, target):
        x = -target.rect.centerx + int(WIDTH / 2)
        y = -target.rect.centery + int(HEIGHT / 2)
        x = min(0, x)
        y = min(0, y)
        x = max(-(MAP_WIDTH - WIDTH), x)
        y = max(-(MAP_HEIGHT - HEIGHT), y)
        self.camera = pygame.Rect(-x, -y, self.width, self.height)

def play_game(screen, clock, player):
    print("harta.py: Entering play_game")
    print(f"harta.py: Player position: ({player.rect.x}, {player.rect.y})")

    # Load the entire map image
    try:
        map_surface = pygame.image.load("map2.png")
        print(f"harta.py: Loaded map.png with size: {map_surface.get_size()}")
        if map_surface.get_width() != MAP_WIDTH or map_surface.get_height() != MAP_HEIGHT:
            print(f"harta.py: Warning: map.png size ({map_surface.get_width()}x{map_surface.get_height()}) does not match expected {MAP_WIDTH}x{MAP_HEIGHT}")
    except pygame.error as e:
        print(f"harta.py: Failed to load map.png: {e}")
        # Fallback to a white surface if the image fails to load
        map_surface = pygame.Surface((MAP_WIDTH, MAP_HEIGHT))
        map_surface.fill((255, 255, 255))

    # Initialize camera
    camera = Camera(WIDTH, HEIGHT)
    camera.update(player)

    font = pygame.font.SysFont("arial", 24)
    debug_font = pygame.font.SysFont("arial", 20)
    enemy = Enemy()
    enemy.rect.x, enemy.rect.y = 19000, 19000

    # Dodge state
    is_dodging = False
    dodge_timer = 0
    dodge_direction = None
    last_direction = 'right'
    is_invincible = False
    dodge_cooldown = 0

    running = True
    while running:
        pygame.event.pump()
        keys_pressed = pygame.key.get_pressed()
        mouse_buttons = pygame.mouse.get_pressed()

        try:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print("harta.py: Quit event received")
                    return False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        print("harta.py: ESC pressed, returning to menu")
                        return False
                    if event.key == pygame.K_f:
                        print("harta.py: F pressed, switching to fighting mode")
                        return "switch_to_fighting"
                    if event.key == pygame.K_SPACE and not is_dodging and dodge_cooldown <= 0:
                        print("harta.py: Space pressed, starting dodge")
                        is_dodging = True
                        dodge_timer = DODGE_DURATION
                        dodge_direction = last_direction
                        is_invincible = True
                        print(f"harta.py: Dodging {dodge_direction}, invincible: {is_invincible}")
        except Exception as e:
            print(f"harta.py: Event handling error: {str(e)}")
            return False

        # Update player movement
        moved, key_status = player.handle_movement(keys_pressed)
        if moved:
            print(f"harta.py: Player moved to: ({player.rect.x}, {player.rect.y})")
            if keys_pressed[pygame.K_w]:
                last_direction = 'up'
            elif keys_pressed[pygame.K_s]:
                last_direction = 'down'
            elif keys_pressed[pygame.K_a]:
                last_direction = 'left'
            elif keys_pressed[pygame.K_d]:
                last_direction = 'right'

        # Handle dodge movement
        if is_dodging:
            dodge_timer -= 1
            if dodge_timer > 0:
                fraction = 1.0 / DODGE_DURATION
                if dodge_direction == 'up':
                    player.rect.y -= DODGE_DISTANCE * fraction
                elif dodge_direction == 'down':
                    player.rect.y += DODGE_DISTANCE * fraction
                elif dodge_direction == 'left':
                    player.rect.x -= DODGE_DISTANCE * fraction
                elif dodge_direction == 'right':
                    player.rect.x += DODGE_DISTANCE * fraction
            else:
                is_dodging = False
                is_invincible = False
                dodge_cooldown = DODGE_COOLDOWN
                print(f"harta.py: Dodge ended, invincible: {is_invincible}, cooldown: {dodge_cooldown}")

        if dodge_cooldown > 0:
            dodge_cooldown -= 1

       

        # Update enemy
        enemy.move_towards_player(player)
        enemy.attack_player(player, is_invincible)
        enemy.update()

        # Update player combat
        attack_active = player.attack(enemy, mouse_buttons)
        block_active = player.block(mouse_buttons)
        player.update()

        # Check game over
        if player.health <= 0:
            print("harta.py: Player defeated!")
            return "return_to_menu"

        # Update camera
        camera.update(player)

        # Draw everything
        try:
            # Draw the map
            screen.fill((0, 0, 0))  # Clear screen
            screen.blit(map_surface, (-camera.camera.x, -camera.camera.y))

          

            # Draw player
            player_rect = camera.apply(player.rect)
            pygame.draw.rect(screen, PLAYER_COLOR, player_rect)

            # Draw enemy
            if enemy.alive:
                print("harta.py: Drawing enemy at", (enemy.rect.x, enemy.rect.y))
                enemy_rect = camera.apply(enemy.rect)
                pygame.draw.rect(screen, (0, 0, 255), enemy_rect)

            # Draw health bars
            # Player health bar
            health_ratio = player.health / player.max_health
            pygame.draw.rect(screen, HEALTH_BAR_BG_COLOR,
                            (player_rect.x, player_rect.y - 20, HEALTH_BAR_WIDTH, HEALTH_BAR_HEIGHT))
            pygame.draw.rect(screen, HEALTH_BAR_COLOR,
                            (player_rect.x, player_rect.y - 20, HEALTH_BAR_WIDTH * health_ratio, HEALTH_BAR_HEIGHT))
            health_text = font.render(f"{int(player.health)}/{player.max_health}", True, (0, 0, 0))
            screen.blit(health_text, (player_rect.x, player_rect.y - 40))

            # Enemy health bar
            if enemy.alive:
                health_ratio = enemy.health / enemy.max_health
                pygame.draw.rect(screen, HEALTH_BAR_BG_COLOR,
                                (enemy_rect.x, enemy_rect.y - 20, HEALTH_BAR_WIDTH, HEALTH_BAR_HEIGHT))
                pygame.draw.rect(screen, HEALTH_BAR_COLOR,
                                (enemy_rect.x, enemy_rect.y - 20, HEALTH_BAR_WIDTH * health_ratio, HEALTH_BAR_HEIGHT))
                health_text = font.render(f"{int(enemy.health)}/{enemy.max_health}", True, (0, 0, 0))
                screen.blit(health_text, (enemy_rect.x, enemy_rect.y - 40))

            # Draw instructions, debug, and coordinates
            text = font.render("WASD to move, Left Click to attack, Right Click to block, Space to dodge, F to switch, ESC to menu", True, (0, 0, 0))
            screen.blit(text, (10, 10))
            key_text = font.render(f"Keys: {', '.join(key_status) if key_status else 'None'}, Attack: {attack_active}, Block: {block_active}, Dodge: {is_dodging}, CD: {dodge_cooldown}, Enemy Attack: {enemy.is_attacking}", True, (0, 0, 0))
            screen.blit(key_text, (10, 40))
            coord_text = font.render(f"Pos: ({player.rect.x}, {player.rect.y})", True, (0, 0, 0))
            screen.blit(coord_text, (10, 70))
            debug_text = debug_font.render(f"Exploration Mode Active, Invincible: {is_invincible}", True, (255, 0, 0))
            screen.blit(debug_text, (10, HEIGHT - 30))

            pygame.display.flip()
        except Exception as e:
            print(f"harta.py: Rendering error: {str(e)}")
            return False

        clock.tick(FPS)

    print("harta.py: Exiting play_game")
    return True