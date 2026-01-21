import pygame
import time
import logging
from core.window_manager import WindowManager
from core.config_manager import ConfigManager
from graphics.virtual_renderer import VirtualRenderer


def get_settings(path, logger):
    config_manager = ConfigManager(path)
    # check if user settings are already created
    if config_manager.file_read:
        config = config_manager.get_config()
        width = config.getint("Graphics", "Screen_Width")
        height = config.getint("Graphics", "Screen_Height")
        display_mode = config.get("Window", "Display_Mode")
        fps = config.get("Window", "FPS")
    # TODO get default values not python set values through the programming
    else:
        logger.warning("Could not open config file in path: %s", path)
        width, height = pygame.display.get_desktop_sizes()[0]
        display_mode = "Fullscreen"
        fps = "60"
        config_manager.set_values({
            "Graphics": {"Screen_Width": width, "Screen_Height": height},
            "Window": {"Display_Mode": display_mode, "FPS": fps}
        })
    framerate = 0 if fps.lower() == "unlimited" else int(fps)
    return width, height, display_mode, framerate

def get_display(width, height, mode, logger):
    if mode == "Windowed":
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
    return display, flags

def main():
    # Setup Logging
    logging.basicConfig(
        level=logging.DEBUG,
        filename='utils\\debug.log',
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %I:%M:%S %p'
    )
    log = logging.getLogger(__name__)
    log.info("Starting game")
    # Setup Pygame
    pygame.init()
    clock = pygame.time.Clock()
    prev_time = time.time() # Calc elapsed time
    # Retrieve settings
    user_settings_path = "assets\\game_settings\\config_user.ini"
    display_width, display_height, display_mode, framerate = get_settings(user_settings_path, log)
    log.info("Settings have been loaded")
    # Setup virtual and actual display and passed to manager
    display, flags = get_display(display_width, display_height, display_mode, log)
    renderer = VirtualRenderer(display, design_size=(1920, 1080))
    manager = WindowManager(display, renderer) # WindowManager handles everything to do with the windows (i.e. switching/creating/deleting windows)

    running = True
    while running:
        clock.tick(framerate)  # Sets tick speed/fps

        # Calc delta time in milliseconds
        now = time.time()
        dt = now - prev_time
        prev_time = now

        # Get events for window before mapping such as resizing/quit
        raw_events = pygame.event.get()
        for event in raw_events:
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.VIDEORESIZE:
                display = pygame.display.set_mode((event.w, event.h), flags)
                renderer.set_window_surface(display)
                manager.update_display(display)

                cfg = ConfigManager(user_settings_path)
                cfg.set_values({"Graphics": {"Screen_Width": event.w, "Screen_Height": event.h}})

        # Map events into virtual coordinates for game/UI
        events = []
        for e in raw_events:
            mapped = renderer.map_event_to_virtual(e)
            if mapped is not None:
                events.append(mapped)

        # Start a virtual frame
        renderer.clear_frame()

        # Update window and apply settings changes
        state = manager.update_window(events)
        if state == "update_display":
            display_width, display_height, display_mode, framerate = get_settings(user_settings_path, log)
            log.info("Settings have been reloaded")

            display, flags = get_display(display_width, display_height, display_mode, log)
            renderer.set_window_surface(display)
            manager.update_display(display)

        manager.draw(dt)

        # Present scaled and letterboxed output
        renderer.draw()
        pygame.display.flip()
    pygame.quit()

if __name__ == "__main__":
    main()