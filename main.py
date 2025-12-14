import pygame
import time
import logging
from core.window_manager import WindowManager
from core.config_manager import ConfigManager


def get_settings():
    config_manager = ConfigManager()
    if config_manager.open_file("assets\\game_settings\\config_user.ini"):
        config = config_manager.get_config()
        width = config.getint("Graphics", "Screen_Width")
        height = config.getint("Graphics", "Screen_Height")
        #fps = config.getint("Window", "FPS")
    else:
        width, height = pygame.display.get_desktop_sizes()[0]
        config_manager.set_value({"Graphics": {"Screen_Width": screen_width, "Screen_Height": screen_height}})
        config_manager.open_file("assets\\game_settings\\config_default.ini")
        config = config_manager.get_config()
        #fps = config.getint("Window", "FPS")
    return width, height

def main():
    logging.basicConfig(
        level=logging.DEBUG,
        filename='utils\\debug.log',
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %I:%M:%S %p'
    )
    log = logging.getLogger(__name__)
    log.info("Starting game")
    pygame.init() #initiating pygame
    clock = pygame.time.Clock() #tool to control tick speed/fps/physics
    prev_time = time.time()
    screen_width, screen_height = get_settings() #check if user settings are already created
    fps = 60
    window = pygame.display.set_mode((screen_width, screen_height))
    log.info("Screen setup with resolution: %s x %s", screen_width, screen_height)

    # WindowManager handles everything to do with the windows (i.e. switching/creating/deleting windows)
    manager = WindowManager(window)
    running = True

    while running:
        clock.tick(60)  # Sets tick speed and fps
        # Calc delta time in milliseconds
        now = time.time()
        dt = now - prev_time
        prev_time = now

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False

        window.fill((255, 255, 255)) # Clear screen with white background
        manager.set_window(events)
        manager.draw(dt)
        pygame.display.flip()

if __name__ == "__main__":
    main()