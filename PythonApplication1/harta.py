import pygame
import platform
from lupta import Enemy  # Import Enemy class from lupta.py

# Debug: Confirm module is loaded
print("harta.py loaded")

# Constants
WIDTH, HEIGHT = 800, 600  # Screen size
PLAYER_SIZE = 50          # Player square size
PLAYER_COLOR = (0, 255, 0)  # Green player
MAP_WIDTH, MAP_HEIGHT = 1600, 1200  # Map size
MAP_COLOR = (255, 255, 255)  # White map
GRID_COLOR = (0, 0, 0)    # Black grid lines
GRID_SPACING = 100        # Grid lines every 100 pixels
FPS = 60
HEALTH_BAR_WIDTH = 50
HEALTH_BAR_HEIGHT = 10
HEALTH_BAR_COLOR = (0, 255, 0)  # Green health
HEALTH_BAR_BG_COLOR = (255, 0, 0)  # Red background
DODGE_DURATION = 18       # 0.3 seconds at 60 FPS (18 frames)
DODGE_DISTANCE = 100      # 1 tile (100 pixels)
DODGE_COOLDOWN = 60       # 1 second at 60 FPS (60 frames)

def play_game(screen, clock, player):
    """Main game loop for exploration mode"""
    print("harta.py: Entering play_game")
    print(f"harta.py: Player position: ({player.rect.x}, {player.rect.y})")
    
    # Create white map surface with grid lines
    map_surface = pygame.Surface((MAP_WIDTH, MAP_HEIGHT))
    map_surface.fill(MAP_COLOR)
    for x in range(0, MAP_WIDTH, GRID_SPACING):
        pygame.draw.line(map_surface, GRID_COLOR, (x, 0), (x, MAP_HEIGHT), 2)  # Thicker lines
    for y in range(0, MAP_HEIGHT, GRID_SPACING):
        pygame.draw.line(map_surface, GRID_COLOR, (0, y), (MAP_WIDTH, y), 2)  # Thicker lines

    font = pygame.font.SysFont("arial", 24)
    debug_font = pygame.font.SysFont("arial", 20)  # Define debug_font
    enemy = Enemy()  # Create a dummy enemy
    enemy.rect.x, enemy.rect.y = 300, 300  # Initial position near player

    # Dodge state
    is_dodging = False
    dodge_timer = 0
    dodge_direction = None  # Will be 'up', 'down', 'left', 'right'
    last_direction = 'right'  # Default direction if no movement
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
                        return "switch_to_fighting"  # Signal to switch modes
                    if event.key == pygame.K_SPACE and not is_dodging and dodge_cooldown <= 0:
                        print("harta.py: Space pressed, starting dodge")
                        is_dodging = True
                        dodge_timer = DODGE_DURATION
                        dodge_direction = last_direction  # Use last movement direction
                        is_invincible = True
                        print(f"harta.py: Dodging {dodge_direction}, invincible: {is_invincible}")
        except Exception as e:
            print(f"harta.py: Event handling error: {str(e)}")
            return False

        # Update player movement
        moved, key_status = player.handle_movement(keys_pressed)
        if moved:
            print(f"harta.py: Player moved to: ({player.rect.x}, {player.rect.y})")
            # Update last direction based on keys pressed
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
                # Move player a fraction of the dodge distance each frame
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
                # End dodge
                is_dodging = False
                is_invincible = False
                dodge_cooldown = DODGE_COOLDOWN
                print(f"harta.py: Dodge ended, invincible: {is_invincible}, cooldown: {dodge_cooldown}")

        # Update dodge cooldown
        if dodge_cooldown > 0:
            dodge_cooldown -= 1

        # Keep player within map boundaries
        player.rect.x = max(0, min(player.rect.x, MAP_WIDTH - PLAYER_SIZE))
        player.rect.y = max(0, min(player.rect.y, MAP_HEIGHT - PLAYER_SIZE))

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

        # Calculate camera offset
        camera_x = player.rect.x - WIDTH // 2 + PLAYER_SIZE // 2
        camera_y = player.rect.y - HEIGHT // 2 + PLAYER_SIZE // 2
        camera_x = max(0, min(camera_x, MAP_WIDTH - WIDTH))
        camera_y = max(0, min(camera_y, MAP_HEIGHT - HEIGHT))

        # Draw map
        try:
            screen.blit(map_surface, (-camera_x, -camera_y))

            # Highlight player's current grid cell
            grid_x = (player.rect.x // GRID_SPACING) * GRID_SPACING
            grid_y = (player.rect.y // GRID_SPACING) * GRID_SPACING
            pygame.draw.rect(screen, (255, 255, 0), 
                            (grid_x - camera_x, grid_y - camera_y, GRID_SPACING, GRID_SPACING), 2)

            # Draw player
            pygame.draw.rect(screen, PLAYER_COLOR, 
                            (player.rect.x - camera_x, player.rect.y - camera_y, PLAYER_SIZE, PLAYER_SIZE))

            # Draw enemy
            if enemy.alive:
                print("harta.py: Drawing enemy at", (enemy.rect.x, enemy.rect.y))
                pygame.draw.rect(screen, (0, 0, 255), 
                                (enemy.rect.x - camera_x, enemy.rect.y - camera_y, PLAYER_SIZE, PLAYER_SIZE))

            # Draw health bars
            # Player health bar
            health_ratio = player.health / player.max_health
            pygame.draw.rect(screen, HEALTH_BAR_BG_COLOR, 
                            (player.rect.x - camera_x, player.rect.y - camera_y - 20, HEALTH_BAR_WIDTH, HEALTH_BAR_HEIGHT))
            pygame.draw.rect(screen, HEALTH_BAR_COLOR, 
                            (player.rect.x - camera_x, player.rect.y - camera_y - 20, HEALTH_BAR_WIDTH * health_ratio, HEALTH_BAR_HEIGHT))
            health_text = font.render(f"{int(player.health)}/{player.max_health}", True, (0, 0, 0))
            screen.blit(health_text, (player.rect.x - camera_x, player.rect.y - camera_y - 40))

            # Enemy health bar
            if enemy.alive:
                health_ratio = enemy.health / enemy.max_health
                pygame.draw.rect(screen, HEALTH_BAR_BG_COLOR, 
                                (enemy.rect.x - camera_x, enemy.rect.y - camera_y - 20, HEALTH_BAR_WIDTH, HEALTH_BAR_HEIGHT))
                pygame.draw.rect(screen, HEALTH_BAR_COLOR, 
                                (enemy.rect.x - camera_x, enemy.rect.y - camera_y - 20, HEALTH_BAR_WIDTH * health_ratio, HEALTH_BAR_HEIGHT))
                health_text = font.render(f"{int(enemy.health)}/{enemy.max_health}", True, (0, 0, 0))
                screen.blit(health_text, (enemy.rect.x - camera_x, enemy.rect.y - camera_y - 40))

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