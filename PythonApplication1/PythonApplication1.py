import pygame
import asyncio
import platform
import base64
from io import BytesIO


pygame.init()

WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Starting Screen")


WHITE = (255, 255, 255)
HIGHLIGHT_COLOR = (255, 255, 255, 50)  #Semi-transparent yellow


font = pygame.font.SysFont("arial", 36)


if platform.system() == "Emscripten":
    # For Pyodide: Use base64-encoded image
    # Replace this with your image's base64 string
    base64_string = (
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAACklEQVR4nGMAAQAABQABDQottAAAAABJRU5ErkJggg=="
    )  # Placeholder (1x1 black pixel)
    img_data = base64.b64decode(base64_string)
    start_image = pygame.image.load(BytesIO(img_data))
else:
    # For Visual Studio: Load image from file
    try:
        start_image = pygame.image.load("image.png")  # Replace with your image file name
    except pygame.error:
        # Fallback if image not found
        start_image = pygame.Surface((WIDTH, HEIGHT))
        start_image.fill((100, 100, 100))  # Gray background
        text = font.render("Image not found. Press Enter.", True, WHITE)
        


BUTTON_WIDTH = 368
BUTTON_HEIGHT = 72
BUTTON_X = WIDTH // 2 - BUTTON_WIDTH // 2  # Center horizontally
new_game_rect = pygame.Rect(BUTTON_X, 167, BUTTON_WIDTH, BUTTON_HEIGHT)  # NEW GAME
continue_rect = pygame.Rect(BUTTON_X, 261, BUTTON_WIDTH, BUTTON_HEIGHT)  # CONTINUE
settings_rect = pygame.Rect(BUTTON_X, 351, BUTTON_WIDTH, BUTTON_HEIGHT)  # SETTINGS
exit_rect = pygame.Rect(BUTTON_X, 444, BUTTON_WIDTH, BUTTON_HEIGHT)       #EXIT
# Game variables
running = True
clock = pygame.time.Clock()
FPS = 60

def update_loop():
    global running

    # Get mouse position
    mouse_pos = pygame.mouse.get_pos()
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
                print("New Game Started!")  
            if continue_hovered:
                print("Continue Game!")  
            if settings_hovered:
                print("Settings Opened!")  
            if exit_hovered:
                 running = False
    # Draw everything
    screen.blit(start_image, (0, 0))  # Background image

    # Draw hover effects
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