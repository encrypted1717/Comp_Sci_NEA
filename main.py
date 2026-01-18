import pygame
import time
import logging
from core.window_manager import WindowManager
from core.config_manager import ConfigManager


# TODO fix logic as it is a bit off as after checking if files couldn't be open it doesn't make sense to attempt to open the path again
def get_settings(path, logger):
    config_manager = ConfigManager(path)
    if config_manager.file_read:
        config = config_manager.get_config()
        width = config.getint("Graphics", "Screen_Width")
        height = config.getint("Graphics", "Screen_Height")
        display_mode = config.get("Window", "Display_Mode")
        fps = config.getint("Window", "FPS")
    # TODO get default values not python set values through the programming
    else:
        logger.warning("Could not open config file in path: %s", path)
        width, height = pygame.display.get_desktop_sizes()[0]
        display_mode = "Fullscreen"
        fps = 60
        config_manager.set_values({
            "Graphics": {"Screen_Width": width, "Screen_Height": height},
            "Window": {"Display_Mode": display_mode, "FPS": fps}
        })
        #config = config_manager.get_config()
    return width, height, display_mode, fps

def get_display(width, height, mode, logger):
    if mode == "Windowed":
        # Width and height reduced to show top bar of window
        width -= 150
        height -= 200
        flags = pygame.RESIZABLE
    elif mode == "Borderless_Windowed":
        flags = pygame.NOFRAME
    elif mode in ("Fullscreen", "Default"):
        flags = pygame.FULLSCREEN
    else:
        logger.error("Unknown display mode: %s", mode)
        raise ValueError(f"Unknown mode: {mode}")

    pygame.display.set_caption("Game")
    display = pygame.display.set_mode((width, height), flags)
    logger.info("Display setup with resolution: %s x %s", width, height)
    logger.info("Display mode: %s", mode)
    return display

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
    clock = pygame.time.Clock() # Controls tick speed
    prev_time = time.time()

    user_settings_path = "assets\\game_settings\\config_user.ini"
    display_width, display_height, display_mode, fps = get_settings(user_settings_path, log) #check if user settings are already created
    log.info("Settings have been loaded")

    display = get_display(display_width, display_height, display_mode, log)
    manager = WindowManager(display)  # WindowManager handles everything to do with the windows (i.e. switching/creating/deleting windows)

    running = True
    while running:
        clock.tick(fps)  # Sets tick speed and fps

        # Calc delta time in milliseconds
        now = time.time()
        dt = now - prev_time
        prev_time = now

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False

        display.fill((255, 255, 255)) # Clear screen with white background

        # Update window and check whether a change in settings has taken place
        state = manager.update_window(events)
        if state == "update_display":
            display_width, display_height, display_mode, fps = get_settings(user_settings_path, log)
            log.info("Settings have been reloaded")
            display = get_display(display_width, display_height, display_mode, log)
            manager.update_display(display)

        manager.draw(dt)
        pygame.display.flip()
    pygame.quit()

if __name__ == "__main__":
    main()