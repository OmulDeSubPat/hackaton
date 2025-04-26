import pygame
import platform

print("lupta.py: Module loaded")

# Constants
WIDTH, HEIGHT = 600,800
PLAYER_SIZE = 50
PLAYER_COLOR = (255, 0, 0)
ENEMY_SIZE = 50
ENEMY_COLOR = (0, 0, 255)
ENEMY_POS = (300, 300)
HEALTH_BAR_WIDTH = 50
HEALTH_BAR_HEIGHT = 10
HEALTH_BAR_COLOR = (0, 255, 0)
HEALTH_BAR_BG_COLOR = (255, 0, 0)
FPS = 60
MAP_WIDTH, MAP_HEIGHT = 10000, 10000
GRID_SPACING = 500  # Adjusted for larger map
DODGE_DURATION = 18
DODGE_DISTANCE = 100
DODGE_COOLDOWN = 60

class Enemy:
    def __init__(self):
        self.rect = pygame.Rect(ENEMY_POS[0], ENEMY_POS[1], ENEMY_SIZE, ENEMY_SIZE)
        self.health = 100
        self.max_health = 100
        self.alive = True
        self.speed = 4
        self.attack_range = 100
        self.attack_cooldown = 0
        self.attack_damage = 10
        self.is_attacking = False

    def take_damage(self, damage):
        if self.alive:
            self.health -= damage
            print(f"lupta.py: Enemy takes {damage} damage, health: {self.health}")
            if self.health <= 0:
                self.health = 0
                self.alive = False
                print("lupta.py: Enemy defeated!")

    def move_towards_player(self, player):
        if not self.alive:
            return
        import math
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance > self.attack_range:
            if distance > 0:
                dx = dx * self.speed / distance
                dy = dy * self.speed / distance
                self.rect.x += dx
                self.rect.y += dy
                print(f"lupta.py: Enemy moving to ({self.rect.x}, {self.rect.y})")
            
            self.rect.x = max(0, min(self.rect.x, MAP_WIDTH - ENEMY_SIZE))
            self.rect.y = max(0, min(self.rect.y, MAP_HEIGHT - ENEMY_SIZE))

    def attack_player(self, player, is_invincible):
        if not self.alive or self.attack_cooldown > 0:
            self.is_attacking = False
            return False
        import math
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance <= self.attack_range:
            self.is_attacking = True
            self.attack_cooldown = 60
            if not player.is_blocking and not is_invincible:
                player.health -= self.attack_damage
                print(f"lupta.py: Enemy attacks player, player health: {player.health}")
                return True
            else:
                print(f"lupta.py: Enemy attack blocked or player invincible")
                return False
        self.is_attacking = False
        return False

    def update(self):
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

def play_game(screen, clock, player):
    print("lupta.py: Entering play_game")
    print(f"lupta.py: Player position: ({player.rect.x}, {player.rect.y})")
    enemy = Enemy()

    # Load the map directly
    try:
        map_surface = pygame.image.load("map.png")
    except pygame.error as e:
        print(f"lupta.py: Failed to load map.png: {e}")
        map_surface = pygame.Surface((MAP_WIDTH, MAP_HEIGHT))
        map_surface.fill((255, 255, 255))  # Fallback to white surface

    # Verify map size
    map_width, map_height = map_surface.get_size()
    if map_width != MAP_WIDTH or map_height != MAP_HEIGHT:
        print(f"lupta.py: Warning: Expected map size {MAP_WIDTH}x{MAP_HEIGHT}, got {map_width}x{map_height}")

    font = pygame.font.SysFont("arial", 24)
    debug_font = pygame.font.SysFont("arial", 20)

    # Dodge state
    is_dodging = False
    dodge_timer = 0
    dodge_direction = None
    last_direction = 'right'
    is_invincible = False
    dodge_cooldown = 0

    running = True
    while running:
        print("lupta.py: Fighting mode active")
        pygame.event.pump()
        mouse_buttons = pygame.mouse.get_pressed()
        keys_pressed = pygame.key.get_pressed()

        try:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print("lupta.py: Quit event received")
                    return False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        print("lupta.py: ESC pressed, returning to menu")
                        return False
                    if event.key == pygame.K_f:
                        print("lupta.py: F pressed, switching to exploration mode")
                        return "switch_to_exploring"
                    if event.key == pygame.K_SPACE and not is_dodging and dodge_cooldown <= 0:
                        print("lupta.py: Space pressed, starting dodge")
                        is_dodging = True
                        dodge_timer = DODGE_DURATION
                        dodge_direction = last_direction
                        is_invincible = True
                        print(f"lupta.py: Dodging {dodge_direction}, invincible: {is_invincible}")
        except Exception as e:
            print(f"lupta.py: Event handling error: {str(e)}")
            return False

        # Update player movement
        moved, key_status = player.handle_movement(keys_pressed)
        if moved:
            print(f"lupta.py: Player moved to: ({player.rect.x}, {player.rect.y})")
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
                print(f"lupta.py: Dodge ended, invincible: {is_invincible}, cooldown: {dodge_cooldown}")

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
            print("lupta.py: Player defeated!")
            return "return_to_menu"

        # Calculate camera offset
        camera_x = player.rect.x - WIDTH // 2 + PLAYER_SIZE // 2
        camera_y = player.rect.y - HEIGHT // 2 + PLAYER_SIZE // 2
        camera_x = max(0, min(camera_x, MAP_WIDTH - WIDTH))
        camera_y = max(0, min(camera_y, MAP_HEIGHT - HEIGHT))

        # Draw everything
        try:
            # Draw map
            screen.blit(map_surface, (-camera_x, -camera_y))

           

            # Draw player
            pygame.draw.rect(screen, PLAYER_COLOR, 
                            (player.rect.x - camera_x, player.rect.y - camera_y, PLAYER_SIZE, PLAYER_SIZE))

            # Draw enemy
            if enemy.alive:
                print("lupta.py: Drawing enemy at", (enemy.rect.x, enemy.rect.y))
                pygame.draw.rect(screen, ENEMY_COLOR, 
                                (enemy.rect.x - camera_x, enemy.rect.y - camera_y, ENEMY_SIZE, ENEMY_SIZE))

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
            action_text = font.render(f"Keys: {', '.join(key_status) if key_status else 'None'}, Attack: {attack_active}, Block: {block_active}, Dodge: {is_dodging}, CD: {dodge_cooldown}, Enemy Attack: {enemy.is_attacking}", True, (0, 0, 0))
            screen.blit(action_text, (10, 40))
            coord_text = font.render(f"Pos: ({player.rect.x}, {player.rect.y})", True, (0, 0, 0))
            screen.blit(coord_text, (10, 70))
            debug_text = debug_font.render(f"Fighting Mode Active, Invincible: {is_invincible}", True, (255, 0, 0))
            screen.blit(debug_text, (10, HEIGHT - 30))

            pygame.display.flip()
        except Exception as e:
            print(f"lupta.py: Rendering error: {str(e)}")
            return False

        clock.tick(FPS)

    print("lupta.py: Exiting play_game")
    return True