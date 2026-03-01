import pygame
import time
import logging

from pygame.constants import FULLSCREEN

from core.window_manager import WindowManager
from core.config_manager import ConfigManager
from graphics.virtual_renderer import VirtualRenderer

def get_settings(path, logger):
    config_manager = ConfigManager(path)
    config = config_manager.get_config()
    desktop_w, desktop_h = pygame.display.get_desktop_sizes()[0]

    # Check if user settings are already created
    if config_manager.file_read:
        width = config.getint("Graphics", "Screen_Width")
        height = config.getint("Graphics", "Screen_Height")
        display_mode = config.get("Window", "Display_Mode")
        fps = config.get("Window", "FPS")
    else:
        logger.warning("Could not open config file in path: %s", path)

        default_settings_path = "assets\\game_settings\\config_default.ini"
        default_config_manager = ConfigManager(default_settings_path)
        default_config = default_config_manager.get_config()

        raw_width = default_config.get("Graphics", "Screen_Width")
        raw_height = default_config.get("Graphics", "Screen_Height")
        width = int(raw_width) if raw_width != "Default" else desktop_w
        height = int(raw_height) if raw_height != "Default" else desktop_h

        display_mode = default_config.get("Window", "Display_Mode")
        fps = default_config.get("Window", "FPS")

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
    logger.info("Display setup: %s x %s  mode=%s", width, height, mode)
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

    # Pre-login display (safe default, no user config yet)
    framerate = 60
    user_settings_path = None # Set once player logs in
    display, flags = get_display(1280, 720, "Windowed", log)

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
                # Only persist size if player 1 is already logged in
                if user_settings_path:
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

        # Update window and apply settings changes // once player 1 logs in, apply their display settings
        state = manager.update_window(events)
        if state and state[0] == "update_display":
            user_id = state[1]
            user_settings_path = f"assets\\game_settings\\users\\config_{user_id}.ini"
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