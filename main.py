"""
    Entry point for the game.

    This module initialises pygame, sets up the display and renderer, and runs
    the main game loop. It handles event processing, delta time, window management,
    and applies per-user display settings once player 1 has logged in.
"""

import pygame
import logging
import shutil
from core import WindowManager
from utils import ConfigManager
from graphics import VirtualRenderer


def get_settings(path: str, logger: logging.Logger) -> tuple[int, int, str, int, bool]:
    """
        Load display settings from a user config file.

        If the config file does not exist, a fresh copy is made from the default
        config before loading. If the stored resolution is "Default", the current
        desktop resolution is substituted and written back to the file.

        Args:
            path: path to the user's config .ini file.
            logger: logger instance for warnings and info.

        Returns:
            A tuple of (width, height, display_mode, framerate, vsync).
    """
    default_path = "assets\\game_settings\\config_default.ini"
    config_manager = ConfigManager(path)

    if not config_manager.file_read:
        logger.warning("Could not open config file at: %s — copying from default", path)
        shutil.copy(default_path, path)
        config_manager = ConfigManager(path)  # Reload now the file exists

    config = config_manager.get_config()
    desktop_w, desktop_h = pygame.display.get_desktop_sizes()[0]

    raw_width = config.get("Graphics", "Screen_Width")
    raw_height = config.get("Graphics", "Screen_Height")
    width  = int(raw_width)  if raw_width  != "Default" else desktop_w  # Fall back to desktop size if unset
    height = int(raw_height) if raw_height != "Default" else desktop_h

    display_mode = config.get("Window", "Display_Mode")
    fps = config.get("Window", "FPS")
    vsync = False

    # Write the resolved resolution back so "Default" is only used once
    if raw_width == "Default" or raw_height == "Default":
        config_manager.set_values({"Graphics": {"Screen_Width": width, "Screen_Height": height}})

    framerate = 0 if fps.lower() == "unlimited" else int(fps)  # 0 = uncapped in pygame clock
    return width, height, display_mode, framerate, vsync


def get_display(width: int, height: int, mode: str, logger: logging.Logger, vsync: bool = False) -> tuple[pygame.Surface, int]:
    """
        Create and return a pygame display surface with the given settings.

        Args:
            width: window width in pixels.
            height: window height in pixels.
            mode: display mode string — "Windowed", "Borderless_Windowed", or "Fullscreen".
            logger: logger instance for info and errors.
            vsync: whether to enable vertical sync.

        Returns:
            A tuple of (display surface, pygame flags integer).

        Raises:
            ValueError: if an unrecognised display mode is provided.
    """
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
    display = pygame.display.set_mode((width, height), flags, vsync=False)
    logger.info("Display setup: %s x %s  mode=%s  vsync=%s", width, height, mode, vsync)
    return display, flags


def apply_user_settings(user_id: int, renderer: VirtualRenderer, manager: WindowManager, log: logging.Logger) -> tuple[pygame.Surface, int, int, str]:
    """
        Load and apply player 1's saved display settings after login.

        Reads the user's config file, recreates the display surface, and
        notifies both the renderer and window manager of the change.

        Args:
            user_id: the logged-in player 1's database ID, used to locate their config file.
            renderer: the active VirtualRenderer instance.
            manager: the active WindowManager instance.
            log: logger instance for info messages.

        Returns:
            A tuple of (display surface, flags, framerate, user_settings_path).
    """
    path = f"assets\\game_settings\\users\\config_{user_id}.ini"
    w, h, mode, framerate, vsync = get_settings(path, log)
    display, flags = get_display(w, h, mode, log, vsync)
    renderer.set_window_surface(display)
    manager.update_display(display)
    return display, flags, framerate, path


def main() -> None:
    """Initialise the game and run the main loop until the player quits."""
    # Setup logging — all modules share this root config
    logging.basicConfig(
        level=logging.DEBUG,
        filename='assets\\data\\debug.log',
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %I:%M:%S %p'
    )
    log = logging.getLogger(__name__)
    log.info("Starting game")

    pygame.init()
    clock = pygame.time.Clock()

    # Safe default display before any user config is loaded — applied once player 1 logs in
    framerate = 60
    user_settings_path = None  # Remains None until player 1 completes login
    display, flags = get_display(1280, 720, "Windowed", log, vsync=False)

    renderer = VirtualRenderer(display, design_size=(1920, 1080))
    manager  = WindowManager(display, renderer)

    running = True
    while running:
        dt = clock.tick(framerate) / 1000.0  # ms → seconds for physics and animation

        raw_events = pygame.event.get()
        for event in raw_events:
            if event.type == pygame.QUIT:
                running = False

            # Persist the new window size to the user's config when the window is resized
            if event.type == pygame.WINDOWRESIZED and user_settings_path:
                cfg = ConfigManager(user_settings_path)
                cfg.set_values({"Graphics": {"Screen_Width": event.x, "Screen_Height": event.y}})

        # Remap mouse events from window pixels into virtual coordinates, discarding any in letterbox bars
        events = [e for e in (renderer.map_event_to_virtual(e) for e in raw_events) if e is not None]

        renderer.clear_frame()

        # Update the active window; on first login swap in player 1's display settings
        state = manager.update_window(events)
        if state and state[0] == "update_display":
            display, flags, framerate, user_settings_path = apply_user_settings(state[1], renderer, manager, log)
            log.info("Settings applied for user_id=%s", state[1])

        manager.draw(dt)

        renderer.draw()
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()