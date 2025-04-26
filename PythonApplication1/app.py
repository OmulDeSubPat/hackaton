import pygame
import platform
import base64
from io import BytesIO
import harta  # Exploration mode
import lupta  # Fighting mode

# Debug: Verify module imports
print("app.py: Starting application")
try:
    print("app.py: Imported harta module from:", harta.__file__)
    print("app.py: Imported lupta module from:", lupta.__file__)
except AttributeError as e:
    print(f"app.py: Import error: {e}")
    exit(1)

pygame.init()

# Constants
WIDTH = 800
HEIGHT = 600
WHITE = (255, 255, 255)
HIGHLIGHT_COLOR = (255, 255, 255, 50)  # Semi-transparent highlight
FPS = 60
MAP_WIDTH, MAP_HEIGHT = 1600, 1200  # Map size
PLAYER_SIZE = 50

try:
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Starting Screen")
except Exception as e:
    print(f"app.py: Failed to initialize screen: {e}")
    exit(1)

font = pygame.font.SysFont("arial", 36)
debug_font = pygame.font.SysFont("arial", 20)

if platform.system() == "Emscripten":
    base64_string = (
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAACklEQVR4nGMAAQAABQABDQottAAAAABJRU5ErkJggg=="
    )  # Placeholder (1x1 black pixel)
    img_data = base64.b64decode(base64_string)
    start_image = pygame.image.load(BytesIO(img_data))
else:
    try:
        start_image = pygame.image.load("image.png")  # Replace with your image
    except pygame.error:
        print("app.py: image.png not found, using gray background")
        start_image = pygame.Surface((WIDTH, HEIGHT))
        start_image.fill((100, 100, 100))  # Gray background

BUTTON_WIDTH = 368
BUTTON_HEIGHT = 72
BUTTON_X = WIDTH // 2 - BUTTON_WIDTH // 2  # Center horizontally

# Define button rectangles
new_game_rect = pygame.Rect(BUTTON_X, 167, BUTTON_WIDTH, BUTTON_HEIGHT)  # NEW GAME
continue_rect = pygame.Rect(BUTTON_X, 261, BUTTON_WIDTH, BUTTON_HEIGHT)  # CONTINUE
settings_rect = pygame.Rect(BUTTON_X, 351, BUTTON_WIDTH, BUTTON_HEIGHT)  # SETTINGS
exit_rect = pygame.Rect(BUTTON_X, 444, BUTTON_WIDTH, BUTTON_HEIGHT)      # EXIT

# Unified Player class
class Player:
    def __init__(self):
        self.rect = pygame.Rect(MAP_WIDTH // 2, MAP_HEIGHT // 2, PLAYER_SIZE, PLAYER_SIZE)
        self.speed = 5
        self.health = 100
        self.max_health = 100
        self.attack_cooldown = 0
        self.is_blocking = False

    def handle_movement(self, keys_pressed):
        moved = False
        key_status = []
        dx, dy = 0, 0  # Movement vector
        # Apply speed penalty when blocking
        current_speed = 2 if self.is_blocking else self.speed

        if keys_pressed[pygame.K_w]:
            print("app.py: W pressed: Moving up")
            dy -= current_speed
            key_status.append("W")
        if keys_pressed[pygame.K_s]:
            print("app.py: S pressed: Moving down")
            dy += current_speed
            key_status.append("S")
        if keys_pressed[pygame.K_a]:
            print("app.py: A pressed: Moving left")
            dx -= current_speed
            key_status.append("A")
        if keys_pressed[pygame.K_d]:
            print("app.py: D pressed: Moving right")
            dx += current_speed
            key_status.append("D")

        # Normalize movement vector to ensure consistent speed
        if dx != 0 or dy != 0:
            import math
            length = math.sqrt(dx**2 + dy**2)
            if length > 0:
                dx = dx * current_speed / length
                dy = dy * current_speed / length
                self.rect.x += dx
                self.rect.y += dy
                moved = True

        # Keep player within map boundaries
        self.rect.x = max(0, min(self.rect.x, MAP_WIDTH - PLAYER_SIZE))
        self.rect.y = max(0, min(self.rect.y, MAP_HEIGHT - PLAYER_SIZE))

        return moved, key_status

    def attack(self, enemy, mouse_buttons):
        if mouse_buttons[0] and self.attack_cooldown <= 0:  # Left click
            import math
            dx = self.rect.centerx - enemy.rect.centerx
            dy = self.rect.centery - enemy.rect.centery
            distance = math.sqrt(dx**2 + dy**2)
            if distance <= 100:  # Attack range
                print("app.py: Player attacks!")
                enemy.take_damage(10)  # Deal 10 damage
                self.attack_cooldown = 60  # 1-second cooldown at 60 FPS
                return True
        return False

    def block(self, mouse_buttons):
        self.is_blocking = mouse_buttons[2]  # Right click
        if self.is_blocking:
            print("app.py: Player blocking!")
        return self.is_blocking

    def update(self):
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

# Game variables
running = True
clock = pygame.time.Clock()
game_state = "menu"
player = Player()  # Shared player object

def update_loop():
    global running, game_state, player
    print("app.py: Entering update_loop")

    while running:
        if game_state == "menu":
            mouse_pos = pygame.mouse.get_pos()
            new_game_hovered = new_game_rect.collidepoint(mouse_pos)
            continue_hovered = continue_rect.collidepoint(mouse_pos)
            settings_hovered = settings_rect.collidepoint(mouse_pos)
            exit_hovered = exit_rect.collidepoint(mouse_pos)

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print("app.py: Quit event received")
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
                    if new_game_hovered:
                        print("app.py: New Game Started! (Fighting Mode)")
                        game_state = "fighting"
                        pygame.display.set_caption("Fighting Mode")
                    if continue_hovered:
                        print("app.py: Continue Game! (Exploration Mode)")
                        game_state = "exploring"
                        pygame.display.set_caption("Exploration Mode")
                    if settings_hovered:
                        print("app.py: Settings Opened! (Not implemented)")
                        # Add settings screen later
                    if exit_hovered:
                        print("app.py: Exit selected")
                        running = False

            # Draw everything
            screen.blit(start_image, (0, 0))  # Background image

            # Draw hover highlights
            highlight_surface = pygame.Surface((BUTTON_WIDTH, BUTTON_HEIGHT), pygame.SRCALPHA)
            highlight_surface.fill(HIGHLIGHT_COLOR)

            if new_game_hovered:
                screen.blit(highlight_surface, new_game_rect)
            if continue_hovered:
                screen.blit(highlight_surface, continue_rect)
            if settings_hovered:
                screen.blit(highlight_surface, settings_rect)
            if exit_hovered:
                screen.blit(highlight_surface, exit_rect)

            # Draw debug info
            debug_text = debug_font.render(f"State: {game_state}", True, (255, 0, 0))
            screen.blit(debug_text, (10, HEIGHT - 30))

            pygame.display.flip()

        elif game_state == "exploring":
            print("app.py: Entering exploration mode")
            try:
                result = harta.play_game(screen, clock, player)
                if result == "switch_to_fighting":
                    print("app.py: Switching to fighting mode")
                    game_state = "fighting"
                    pygame.display.set_caption("Fighting Mode")
                elif result == "return_to_menu":
                    print("app.py: Player died, returning to menu")
                    player = Player()  # Reset player
                    game_state = "menu"
                    pygame.display.set_caption("Starting Screen")
                elif not result or not running:
                    print("app.py: Exiting exploration mode")
                    game_state = "menu"
                    pygame.display.set_caption("Starting Screen")
            except Exception as e:
                print(f"app.py: Error in exploration mode: {str(e)}")
                running = False

        elif game_state == "fighting":
            print("app.py: Entering fighting mode")
            try:
                result = lupta.play_game(screen, clock, player)
                if result == "switch_to_exploring":
                    print("app.py: Switching to exploration mode")
                    game_state = "exploring"
                    pygame.display.set_caption("Exploration Mode")
                elif result == "return_to_menu":
                    print("app.py: Player died, returning to menu")
                    player = Player()  # Reset player
                    game_state = "menu"
                    pygame.display.set_caption("Starting Screen")
                elif not result or not running:
                    print("app.py: Exiting fighting mode")
                    game_state = "menu"
                    pygame.display.set_caption("Starting Screen")
            except Exception as e:
                print(f"app.py: Error in fighting mode: {str(e)}")
                running = False

        clock.tick(FPS)

def main():
    print("app.py: Starting main loop")
    try:
        update_loop()
    except Exception as e:
        print(f"app.py: Main loop error: {str(e)}")
    finally:
        pygame.quit()
        print("app.py: Pygame quit")

# Run the program
if platform.system() == "Emscripten":
    main()
else:
    if __name__ == "__main__":
        main()