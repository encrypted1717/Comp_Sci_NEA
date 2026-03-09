"""
    Settings menu window for configuring display options.

    This module provides the SettingsMenu class, which lets player 1 adjust
    graphics and window settings including resolution, display mode, FPS cap,
    vsync, and debugging overlay. Changes are held in memory until the player
    presses Apply, at which point they are written to the user's config file
    and the display is updated.
"""

import pygame
from core.window import Window
from core.button import Button
from core.config_manager import ConfigManager


# TODO: Introduce more settings (e.g. audio, keybind display style)
class Settings(Window):
    """
        In-game settings screen for display and window configuration.

        Reads current settings from player 1's config file on open. Each setting
        has a cycling or toggle button that updates an in-memory value. The Apply
        button only appears once a change has been made, and writes all values back
        to the config and triggers a display update when pressed.
    """

    def __init__(self, display: pygame.Surface, renderer, user: tuple[int, str]) -> None:
        """
            Initialise the settings menu.

            Args:
                display: the pygame display surface.
                renderer: the renderer managing the virtual surface and scaling.
                user: (user_id, username) of the logged-in player 1, used to locate their config file.
        """
        super().__init__(display, renderer)

        # Always read from player 1's config — only their display settings affect this machine
        user_id = user[0]
        self.config_manager = ConfigManager(f"assets\\game_settings\\users\\config_{user_id}.ini")
        self.config = self.config_manager.get_config()

        self.changed = False  # Tracks whether any setting has been modified since last apply

        # Load current values from config to initialise button labels
        self.debugging = self.config.get("Game", "Debugging")
        self.resolutions = pygame.display.list_modes()  # All modes supported by the display hardware
        self.resolution = self.display.get_size()  # Read from the live window, not the config, to reflect actual state
        self.display_modes = ("Fullscreen", "Borderless_Windowed", "Windowed")
        self.display_mode = self.config.get("Window", "Display_Mode")
        self.fps_values = ("30", "60", "120", "144", "165", "185", "240", "360", "Unlimited")  # "Unlimited" maps to 0 in pygame clock
        self.fps = self.config.get("Window", "FPS")
        self.vsync = self.config.get("Window", "Vsync")

        self._create_buttons()
        self.buttons.add(
            self.__graphics_label,
            self.__resolution_label,
            self.__resolution_btn,
            self.__display_mode_label,
            self.__display_mode_btn,
            self.__fps_label,
            self.__fps_btn,
            self.__debugging_label,
            self.__debugging_btn,
            self.__vsync_label,
            self.__vsync_btn
        )

    def event_handler(self, events: list) -> str | None:
        """
            Sync the Apply button visibility before delegating to the base event loop.

            The Apply button is only shown once at least one setting has been changed,
            and hidden again after changes are written.

            Args:
                events: the list of pygame events for this frame.

            Returns:
                An action string or None, as returned by the base event handler.
        """
        # Show apply button as soon as any setting changes; hide it again after applying
        if self.changed and not self.buttons.has(self.__apply_btn):
            self.buttons.add(self.__apply_btn)
        elif not self.changed and self.buttons.has(self.__apply_btn):
            self.buttons.remove(self.__apply_btn)
        return super().event_handler(events)

    def handle_action(self, action: str) -> str | None:
        """
            Handle all settings button actions.

            Cycling buttons advance through their respective value lists.
            Toggle buttons flip between "On" and "Off". The apply action
            writes all current values to the config and triggers a display reload.

            Args:
                action: the action string returned by a button.

            Returns:
                "update_display" when Apply is pressed, None for all setting
                changes, or the action string unchanged for anything else.
        """
        if action == "cycle_resolution":
            self.resolution = self.__cycle_setting(self.resolution, self.resolutions)
            self.__resolution_btn.update_text(f"{self.resolution[0]} x {self.resolution[1]}")
            return None

        if action == "cycle_display_modes":
            self.display_mode = self.__cycle_setting(self.display_mode, self.display_modes)
            self.__display_mode_btn.update_text(self.display_mode)
            return None

        if action == "cycle_fps":
            if self.vsync == "On":
                # Cycling fps while vsync is on - disable vsync first to avoid the mismatch crash
                self.vsync = "Off"
                self.__vsync_btn.update_text(self.vsync)
            self.fps = self.__cycle_setting(self.fps, self.fps_values)
            self.__fps_btn.update_text(self.fps)
            return None

        if action == "toggle_debugging":
            self.debugging = "Off" if self.debugging == "On" else "On"
            self.__debugging_btn.update_text(self.debugging)
            self.changed = True  # No guard needed — assigning True to True is essentially free
            return None

        if action == "toggle_vsync":
            self.vsync = "Off" if self.vsync == "On" else "On"
            if self.vsync == "On":
                # Snap fps to the monitor's refresh rate so vsync has a matching target
                hz = str(pygame.display.get_current_refresh_rate())
                self.fps = hz if hz in self.fps_values else self.fps_values[1]  # fall back to 60 if hz isn't in the list
                self.__fps_btn.update_text(self.fps)
            self.__vsync_btn.update_text(self.vsync)
            self.changed = True
            return None

        if action == "apply":
            self.config_manager.set_values({
                "Graphics": {
                    "Screen_Width":  self.resolution[0],
                    "Screen_Height": self.resolution[1]
                },
                "Window": {
                    "Display_Mode": self.display_mode,
                    "FPS":          self.fps,
                    "Vsync":        self.vsync
                },
                "Game": {
                    "Debugging": self.debugging
                }
            })
            self.buttons.remove(self.__apply_btn)
            self.changed = False
            return "update_display"  # Tells WindowManager to recreate the display with the new settings

        return action

    def draw(self, dt: float) -> None:
        """
            Draw the settings menu.

            Args:
                dt: delta time in seconds since the last frame.
        """
        self.surface.fill((255, 255, 255))
        super().draw(dt)

    def __cycle_setting(self, setting, values: tuple | list):
        """
            Advance a setting to the next value in its list, wrapping around at the end.

            If the current value is not found in the list (e.g. an unsupported resolution
            was stored in the config), falls back to the first value rather than raising.

            Args:
                setting: the current value of the setting.
                values: the ordered sequence of valid values to cycle through.

            Returns:
                The next value in the sequence.
        """
        if not values:
            return setting  # Nothing to cycle through — leave unchanged

        try:
            current_index = values.index(setting)
        except ValueError:
            current_index = -1  # Unknown value — wraps to index 0 on the next line

        # Modulo wraps the index back to 0 once it passes the end of the list,
        # so the last item cycles back to the first, giving infinite looping
        next_index  = (current_index + 1) % len(values)
        new_setting = values[next_index]

        self.changed = True
        return new_setting

    def _create_buttons(self) -> None:
        """Create and store all labels, setting buttons, and the apply button."""
        title_font = pygame.font.Font(self.fonts["OldeTome"], 56)
        label_font = pygame.font.Font(self.fonts["OldeTome"], 37)
        btn_font   = pygame.font.Font(self.fonts["GothicPixel"], 16)

        # Shared styling for all interactive setting buttons — inverts colours on hover
        btn_kwargs = {
            "font": btn_font,
            "text_colour": "#000000",
            "rect_colour": "#ffffff",
            "border": 5,
            "border_colour": "#000000",
            "offset_y": 4,
            "hover_text_colour": "#ffffff",
            "hover_rect_colour": "#000000",
            "hover_border_colour": "#ffffff",
            "fill_on_hover": True
        }

        # Shared styling for all non-interactive row labels on the left column
        label_kwargs = {
            "font": label_font,
            "text_colour": "#ffffff",
            "rect_colour": "#000000",
            "offset_y": 4
        }

        self.__graphics_label = Button(
            (self.center_x, 70),
            (350, 70),
            "Graphics",
            title_font,
            "#ffffff",
            "#000000",
            offset_y=4
        )

        self.__resolution_label = Button((780, 350),  (300, 60), "Resolution",   **label_kwargs)
        self.__resolution_btn   = Button(
            (1180, 350),
            (380, 60),
            f"{self.resolution[0]} x {self.resolution[1]}",  # Initialised from the live window size
            action="cycle_resolution",
            **btn_kwargs
        )

        self.__display_mode_label = Button((780, 440), (300, 60), "Display_Mode", **label_kwargs)
        self.__display_mode_btn   = Button(
            (1180, 440), (380, 60),
            self.display_mode,
            action="cycle_display_modes", **btn_kwargs
        )

        self.__fps_label = Button((780, 530), (300, 60), "FPS", **label_kwargs)
        self.__fps_btn   = Button(
            (1180, 530), (380, 60),
            self.fps,
            action="cycle_fps", **btn_kwargs
        )

        self.__debugging_label = Button((780, 620), (300, 60), "Debugging", **label_kwargs)
        self.__debugging_btn   = Button(
            (1180, 620), (380, 60),
            self.debugging,
            action="toggle_debugging", **btn_kwargs
        )

        self.__vsync_label = Button((780, 710), (300, 60), "Vsync", **label_kwargs)
        self.__vsync_btn   = Button(
            (1180, 710), (380, 60),
            self.vsync,
            action="toggle_vsync", **btn_kwargs
        )

        # Apply button is created here but not added to self.buttons yet —
        # event_handler adds it dynamically once self.changed becomes True
        self.__apply_btn = Button(
            (1770, 960), (160, 60),
            "Apply",
            action="apply", **btn_kwargs
        )