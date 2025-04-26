import pygame
import asyncio
import platform
import base64
from io import BytesIO
import harta  # Exploration mode
import lupta  # Fighting mode

# Debug: Verify module imports
print("combined_game.py: Starting application")
try:
    print("combined_game.py: Imported harta module from:", harta.__file__)
    print("combined_game.py: Imported lupta module from:", lupta.__file__)
except AttributeError as e:
    print(f"combined_game.py: Import error: {e}")
    exit(1)

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Screen dimensions and constants
WIDTH = 800
HEIGHT = 600
MAP_WIDTH, MAP_HEIGHT = 1600, 1200  # Map size for exploration/fighting
PLAYER_SIZE = 50
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Starting Screen")

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
HIGHLIGHT_COLOR = (255, 255, 255, 50)  
BLACK = (0, 0, 0)
GRAY = (150, 150, 150)

# Load background music
if platform.system() == "Emscripten":
    # For Pyodide: Use base64-encoded audio (placeholder)
    base64_string_music = (
        "YOUR_BASE64_ENCODED_MUSIC_FILE_HERE"  # Replace with actual base64 string
    )
    audio_data = base64.b64decode(base64_string_music)
    pygame.mixer.music.load(BytesIO(audio_data))
else:
    # For Visual Studio: Load music from file
    try:
        pygame.mixer.music.load("menu.mp3")  # Your music file path
    except pygame.error:
        print("Music file not found. Please add 'menu.mp3' to your project folder.")
        pygame.mixer.music.load(BytesIO(b""))  # Fallback to empty audio

pygame.mixer.music.play(-1)  # Play music on loop
pygame.mixer.music.set_volume(0.4)  # Initial volume set to 40%

# Fonts
font = pygame.font.SysFont("arial", 36)
small_font = pygame.font.SysFont("arial", 24)  # Smaller font for slider labels

# Load start screen image
if platform.system() == "Emscripten":
    # For Pyodide: Use base64-encoded image
    base64_string_start = (
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAACklEQVR4nGMAAQAABQABDQottAAAAABJRU5ErkJggg=="
    )  # Placeholder (1x1 black pixel)
    img_data_start = base64.b64decode(base64_string_start)
    start_image = pygame.image.load(BytesIO(img_data_start))
else:
    # For Visual Studio: Load image from file
    try:
        start_image = pygame.image.load("main.png")  # Your starting screen image
    except pygame.error:
        # Fallback if image not found
        start_image = pygame.Surface((WIDTH, HEIGHT))
        start_image.fill((100, 100, 100))  # Gray background
        text = font.render("Image not found.", True, WHITE)

# Load settings screen background image
if platform.system() == "Emscripten":
    # For Pyodide: Use base64-encoded image
    base64_string_settings = (
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAACklEQVR4nGMAAQAABQABDQottAAAAABJRU5ErkJggg=="
    )  # Placeholder (1x1 black pixel)
    img_data_settings = base64.b64decode(base64_string_settings)
    settings_image = pygame.image.load(BytesIO(img_data_settings))
else:
    # For Visual Studio: Load image from file
    try:
        settings_image = pygame.image.load("settings.png")  # Your settings background image
    except pygame.error:
        # Fallback if image not found
        settings_image = pygame.Surface((WIDTH, HEIGHT))
        settings_image.fill((100, 100, 100))  # Gray background
        text = font.render("Settings image not found.", True, WHITE)
        settings_image.blit(text, (WIDTH // 4, HEIGHT // 2))

# Scale images to fit screen
start_image = pygame.transform.scale(start_image, (WIDTH, HEIGHT))
settings_image = pygame.transform.scale(settings_image, (WIDTH, HEIGHT))

# Button hitboxes for starting screen
BUTTON_WIDTH = 368
BUTTON_HEIGHT = 72
BUTTON_X = WIDTH // 2 - BUTTON_WIDTH // 2  # Center horizontally
new_game_rect = pygame.Rect(BUTTON_X, 167, BUTTON_WIDTH, BUTTON_HEIGHT)  # NEW GAME
continue_rect = pygame.Rect(BUTTON_X, 261, BUTTON_WIDTH, BUTTON_HEIGHT)  # CONTINUE
settings_rect = pygame.Rect(BUTTON_X, 351, BUTTON_WIDTH, BUTTON_HEIGHT)  # SETTINGS
exit_rect = pygame.Rect(BUTTON_X, 444, BUTTON_WIDTH, BUTTON_HEIGHT)      # EXIT  
fullscreen_rect = pygame.Rect(140, 150, BUTTON_WIDTH, BUTTON_HEIGHT)  # FULLSCREEN
controls_rect = pygame.Rect(140, 240, 300, 36)  # CONTROLS

# Button hitbox for settings screen (Back button)
BACK_BUTTON_WIDTH = 150
BACK_BUTTON_HEIGHT = 50
back_button_rect = pygame.Rect(WIDTH - BACK_BUTTON_WIDTH - 20, HEIGHT - BACK_BUTTON_HEIGHT - 20, BACK_BUTTON_WIDTH, BACK_BUTTON_HEIGHT)

# Slider properties for settings screen
SLIDER_WIDTH = 260
SLIDER_WIDTH1 = 470
SLIDER_HEIGHT = 10
SLIDER_HANDLE_WIDTH = 10
SLIDER_HANDLE_HEIGHT = 30

# Brightness Slider (x=167, y=505)
brightness_slider_x = 167
brightness_slider_y = 505
brightness_slider_rect = pygame.Rect(brightness_slider_x, brightness_slider_y, SLIDER_WIDTH1, SLIDER_HEIGHT)
brightness_handle_rect = pygame.Rect(brightness_slider_x + SLIDER_WIDTH1 - SLIDER_HANDLE_WIDTH, brightness_slider_y - (SLIDER_HANDLE_HEIGHT - SLIDER_HEIGHT) // 2, SLIDER_HANDLE_WIDTH, SLIDER_HANDLE_HEIGHT)
brightness_value = 100  # Initial value set to maximum (0 to 100)

# SFX Slider (x=367, y=350)
sfx_slider_x = 367
sfx_slider_y = 350
sfx_slider_rect = pygame.Rect(sfx_slider_x, sfx_slider_y, SLIDER_WIDTH, SLIDER_HEIGHT)
sfx_handle_rect = pygame.Rect(sfx_slider_x, sfx_slider_y - (SLIDER_HANDLE_HEIGHT - SLIDER_HEIGHT) // 2, SLIDER_HANDLE_WIDTH, SLIDER_HANDLE_HEIGHT)
sfx_value = 0  # Initial value (0 to 100)

# Volume Slider (x=367, y=309)
volume_slider_x = 367
volume_slider_y = 309
volume_slider_rect = pygame.Rect(volume_slider_x, volume_slider_y, SLIDER_WIDTH, SLIDER_HEIGHT)
volume_handle_rect = pygame.Rect(volume_slider_x + int((40 / 100) * (SLIDER_WIDTH - SLIDER_HANDLE_WIDTH)), volume_slider_y - (SLIDER_HANDLE_HEIGHT - SLIDER_HEIGHT) // 2, SLIDER_HANDLE_WIDTH, SLIDER_HANDLE_HEIGHT)
volume_value = 40  # Initial value set to 40 to match pygame.mixer.music.set_volume(0.4)

# Unified Player class (from second script)
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
            print("combined_game.py: W pressed: Moving up")
            dy -= current_speed
            key_status.append("W")
        if keys_pressed[pygame.K_s]:
            print("combined_game.py: S pressed: Moving down")
            dy += current_speed
            key_status.append("S")
        if keys_pressed[pygame.K_a]:
            print("combined_game.py: A pressed: Moving left")
            dx -= current_speed
            key_status.append("A")
        if keys_pressed[pygame.K_d]:
            print("combined_game.py: D pressed: Moving right")
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
                print("combined_game.py: Player attacks!")
                enemy.take_damage(10)  # Deal 10 damage
                self.attack_cooldown = 60  # 1-second cooldown at 60 FPS
                return True
        return False

    def block(self, mouse_buttons):
        self.is_blocking = mouse_buttons[2]  # Right click
        if self.is_blocking:
            print("combined_game.py: Player blocking!")
        return self.is_blocking

    def update(self):
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

# Game variables
running = True
clock = pygame.time.Clock()
FPS = 60
game_state = "start"  # Start with the starting screen (equivalent to "menu" in second script)
dragging_brightness = False  # Track if brightness slider is being dragged
dragging_sfx = False  # Track if SFX slider is being dragged
dragging_volume = False  # Track if volume slider is being dragged
is_fullscreen = False  # Track if fullscreen is toggled on/off
player = Player()  # Shared player object for exploration and fighting modes

def draw_button(surface, rect, hovered):
    """Draw a highlight effect for buttons."""
    if hovered:
        highlight_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        highlight_surface.fill(HIGHLIGHT_COLOR)
        surface.blit(highlight_surface, rect)

def draw_slider(surface, slider_rect, handle_rect, value, label):
    """Draw only the slider handle, hiding the label and value."""
    pygame.draw.rect(surface, RED, handle_rect)

def draw_tick(surface, rect):
    """Draw a white tick (checkmark) at x=183, y=185 relative to the button's top-left corner."""
    tick_start = (168, 181)          # Starting point
    tick_mid = (188, 196)           # Middle point (bottom-right)
    tick_end = (199, 180)           # End point (middle-left)
    pygame.draw.line(surface, RED, tick_start, tick_mid, 5)  # First part of the tick
    pygame.draw.line(surface, RED, tick_mid, tick_end, 5)    # Second part of the tick

def apply_brightness(surface, brightness_value):
    """Apply a brightness effect by overlaying a semi-transparent black surface."""
    brightness_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    alpha = int(255 - (brightness_value * 2.55))
    brightness_surface.fill((0, 0, 0, alpha))  # Black with variable alpha
    surface.blit(brightness_surface, (0, 0))

def update_loop():
    global running, game_state, brightness_value, sfx_value, volume_value, dragging_brightness, dragging_sfx, dragging_volume, is_fullscreen, player

    # Get mouse position
    mouse_pos = pygame.mouse.get_pos()
    mouse_pressed = pygame.mouse.get_pressed()[0]  # Left mouse button

    if game_state == "start":
        # Starting screen
        new_game_hovered = new_game_rect.collidepoint(mouse_pos)
        continue_hovered = continue_rect.collidepoint(mouse_pos)
        settings_hovered = settings_rect.collidepoint(mouse_pos)
        exit_hovered = exit_rect.collidepoint(mouse_pos)

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
                if new_game_hovered:
                    print("combined_game.py: New Game Started! (Fighting Mode)")
                    game_state = "fighting"
                    pygame.display.set_caption("Fighting Mode")
                if continue_hovered:
                    print("combined_game.py: Continue Game! (Exploration Mode)")
                    game_state = "exploring"
                    pygame.display.set_caption("Exploration Mode")
                if settings_hovered:
                    game_state = "settings"  # Switch to settings screen
                if exit_hovered:
                    running = False

        # Draw starting screen
        screen.blit(start_image, (0, 0))  # Background image
        draw_button(screen, new_game_rect, new_game_hovered)
        draw_button(screen, continue_rect, continue_hovered)
        draw_button(screen, settings_rect, settings_hovered)
        draw_button(screen, exit_rect, exit_hovered)

    elif game_state == "settings":
        # Settings screen
        back_hovered = back_button_rect.collidepoint(mouse_pos)
        fullscreen_hovered = fullscreen_rect.collidepoint(mouse_pos)
        controls_hovered = controls_rect.collidepoint(mouse_pos)
        brightness_handle_hovered = brightness_handle_rect.collidepoint(mouse_pos)
        sfx_handle_hovered = sfx_handle_rect.collidepoint(mouse_pos)
        volume_handle_hovered = volume_handle_rect.collidepoint(mouse_pos)

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:   
                if back_hovered:
                    game_state = "start"
                if fullscreen_hovered:
                    is_fullscreen = not is_fullscreen  # Toggle fullscreen state
                    try:
                        pygame.display.toggle_fullscreen()  # Toggle fullscreen mode
                    except pygame.error as e:
                        print(f"combined_game.py: Failed to toggle fullscreen: {e}")
                    print("combined_game.py: Toggled Fullscreen! State:", is_fullscreen)
                if controls_hovered:
                    print("combined_game.py: Opened Controls!")  # Placeholder
                if brightness_handle_hovered:
                    dragging_brightness = True
                if sfx_handle_hovered:
                    dragging_sfx = True
                if volume_handle_hovered:
                    dragging_volume = True
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                dragging_brightness = False
                dragging_sfx = False
                dragging_volume = False

        # Update sliders if dragging
        if dragging_brightness and mouse_pressed:
            new_x = max(brightness_slider_rect.x, min(mouse_pos[0] - SLIDER_HANDLE_WIDTH // 2, brightness_slider_rect.x + SLIDER_WIDTH1 - SLIDER_HANDLE_WIDTH))
            brightness_handle_rect.x = new_x
            brightness_value = ((new_x - brightness_slider_rect.x) / (SLIDER_WIDTH1 - SLIDER_HANDLE_WIDTH)) * 100
            print(f"combined_game.py: Brightness: {int(brightness_value)}")
        if dragging_sfx and mouse_pressed:
            new_x = max(sfx_slider_rect.x, min(mouse_pos[0] - SLIDER_HANDLE_WIDTH // 2, sfx_slider_rect.x + SLIDER_WIDTH - SLIDER_HANDLE_WIDTH))
            sfx_handle_rect.x = new_x
            sfx_value = ((new_x - sfx_slider_rect.x) / (SLIDER_WIDTH - SLIDER_HANDLE_WIDTH)) * 100
            print(f"combined_game.py: SFX: {int(sfx_value)}")
        if dragging_volume and mouse_pressed:
            new_x = max(volume_slider_rect.x, min(mouse_pos[0] - SLIDER_HANDLE_WIDTH // 2, volume_slider_rect.x + SLIDER_WIDTH - SLIDER_HANDLE_WIDTH))
            volume_handle_rect.x = new_x
            volume_value = ((new_x - volume_slider_rect.x) / (SLIDER_WIDTH - SLIDER_HANDLE_WIDTH)) * 100
            print(f"combined_game.py: Volume: {int(volume_value)}")
            pygame.mixer.music.set_volume(volume_value / 100)  # Update music volume

        # Draw settings screen
        screen.blit(settings_image, (0, 0))  
        # Draw sliders (only the handles)
        draw_slider(screen, brightness_slider_rect, brightness_handle_rect, brightness_value, "Brightness")
        draw_slider(screen, sfx_slider_rect, sfx_handle_rect, sfx_value, "SFX")
        draw_slider(screen, volume_slider_rect, volume_handle_rect, volume_value, "Volume")
        # Draw buttons
        pygame.draw.rect(screen, BLACK, back_button_rect)
        back_text = font.render("Back", True, RED)
        back_text_rect = back_text.get_rect(center=back_button_rect.center)
        screen.blit(back_text, back_text_rect)
        draw_button(screen, back_button_rect, back_hovered)
        draw_button(screen, fullscreen_rect, fullscreen_hovered)
        # Draw tick on Fullscreen button if toggled on
        if is_fullscreen:
            draw_tick(screen, fullscreen_rect)
        draw_button(screen, controls_rect, controls_hovered)

    elif game_state == "exploring":
        print("combined_game.py: Entering exploration mode")
        try:
            result = harta.play_game(screen, clock, player)
            if result == "switch_to_fighting":
                print("combined_game.py: Switching to fighting mode")
                game_state = "fighting"
                pygame.display.set_caption("Fighting Mode")
            elif result == "return_to_menu":
                print("combined_game.py: Player died, returning to menu")
                player = Player()  # Reset player
                game_state = "start"
                pygame.display.set_caption("Starting Screen")
            elif not result or not running:
                print("combined_game.py: Exiting exploration mode")
                game_state = "start"
                pygame.display.set_caption("Starting Screen")
        except Exception as e:
            print(f"combined_game.py: Error in exploration mode: {str(e)}")
            running = False

    elif game_state == "fighting":
        print("combined_game.py: Entering fighting mode")
        try:
            result = lupta.play_game(screen, clock, player)
            if result == "switch_to_exploring":
                print("combined_game.py: Switching to exploration mode")
                game_state = "exploring"
                pygame.display.set_caption("Exploration Mode")
            elif result == "return_to_menu":
                print("combined_game.py: Player died, returning to menu")
                player = Player()  # Reset player
                game_state = "start"
                pygame.display.set_caption("Starting Screen")
            elif not result or not running:
                print("combined_game.py: Exiting fighting mode")
                game_state = "start"
                pygame.display.set_caption("Starting Screen")
        except Exception as e:
            print(f"combined_game.py: Error in fighting mode: {str(e)}")
            running = False

    # Apply brightness overlay to the entire screen (applies to all states)
    apply_brightness(screen, brightness_value)

    pygame.display.flip()

async def main():
    global running
    while running:
        update_loop()  # Update screen
        clock.tick(FPS)  # Control frame rate
        await asyncio.sleep(1.0 / FPS)  # Yield control

# Run the program
if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())