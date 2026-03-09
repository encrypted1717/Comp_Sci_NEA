"""
    Base window class for game.

    This module provides the Window class, which acts as the foundation for every
    screen in the game. It owns the display surface reference, renderer, button
    group, font registry, and the optional auto back button. All concrete screens
    inherit from Window and override on_escape, show_back_button, handle_action,
    and draw as needed.
"""

import logging
import pygame
from core import Button


class Window:
    """
        Base class for all game screens and menus.

        Window provides the shared infrastructure that every screen needs: a
        reference to the pygame display and virtual renderer surface, a sprite
        group for buttons, a font registry, and center-coordinate helpers.
        It also conditionally creates a Back button based on the values returned
        by on_escape and show_back_button, which subclasses can override.

        Subclasses should override:
            on_escape - return value determines ESC behaviour and back button presence.
            show_back_button - whether the auto back button is shown.
            handle_action - route button action strings to screen-specific logic.
            draw - render screen content before calling super().draw(dt).
    """

    def __init__(self, display, renderer):
        # Logging setup
        self.log = logging.getLogger(type(self).__module__)  # Named after the subclass module so log output is traceable to the right file
        self.log.info("Initialising %s module", type(self).__name__)

        # Main setup
        self.display = display    # Real pygame display surface - used when the window surface needs to be swapped out
        self.renderer = renderer  # VirtualRenderer instance shared across all windows
        self.surface = self.renderer.virtual_surface  # All drawing targets the virtual surface, not the real display directly
        self.design_width, self.design_height = self.renderer.design_size  # Fixed virtual resolution (1920x1080) used for all layout calculations
        self.events = None  # Unused by base class but available to subclasses that need direct event access
        self.dt = 0         # Delta time in seconds, updated each frame via draw() and available to subclasses

        # Center coordinate helpers - derived once here so subclasses don't have to recalculate
        self.center_x = self.design_width / 2
        self.center_y = self.design_height / 2

        # Font registry - maps readable names to file paths so subclasses reference fonts by name, not path
        self.fonts = {
            "OldeTome": "assets\\fonts\\OldeTome\\OldeTome.ttf",
            "GothicPixel": "assets\\fonts\\Number_Font_Osadam\\Gothic_pixel_font.ttf"
        }

        self.buttons = pygame.sprite.Group()  # All buttons for this window - updated and drawn each frame by draw()

        # Conditionally create the auto back button based on subclass overrides.
        # Both conditions must be true: on_escape must return "back" (not None or another action),
        # and show_back_button must return True. This allows subclasses to suppress the button
        # independently of ESC behaviour.
        if self.on_escape() == "back" and self.show_back_button():
            self._back_btn = Button(
                (150, 90), (160, 60), "Back",
                pygame.font.Font(self.fonts["OldeTome"], 37),
                "#ffffff", "#000000", 5,
                border_colour="#000000", offset_y=4,
                action="back",
                hover_text_colour="#000000",
                hover_rect_colour="#ffffff",
                hover_border_colour="#000000",
                fill_on_hover=True
            )
            self.buttons.add(self._back_btn)
        else:
            self._back_btn = None  # Stored as None so subclasses can safely check without AttributeError

    def event_handler(self, events):
        """
            Process all events for this frame and return a navigation action if one occurs.

            Iterates every event and every button in the group. ESC is checked first
            and delegates to on_escape. Button clicks are routed through handle_action.
            The first non-None result from either is returned immediately, stopping
            further processing for that frame.

            Args:
                events: list of mapped pygame events from the current frame.

            Returns:
                A navigation action string or tuple if an interaction triggered one,
                or None if nothing actionable occurred this frame.
        """
        for event in events:
            # ESC key - delegate to on_escape so subclasses can override the behaviour per screen
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                result = self.on_escape()
                if result is not None:
                    return result  # Return immediately - only one action per frame

            # Check every button in the group against this event
            for btn in self.buttons:
                action = btn.handle_event(event)
                if action:
                    result = self.handle_action(action)
                    if result is not None:
                        return result  # Return immediately - only one action per frame

        return None

    def draw(self, dt):
        """
            Update and draw all buttons onto the virtual surface.

            Called once per frame by WindowManager. Subclasses should do their own
            drawing first (e.g. filling the background, drawing entities), then call
            super().draw(dt) so buttons are always rendered on top.

            Args:
                dt: delta time in seconds since the last frame.
        """
        self.dt = dt  # Store so subclasses can access dt outside of draw if needed
        mouse_pos = self.renderer.get_virtual_mouse_pos()  # Virtual coordinates so hover detection works at any window size
        self.buttons.update(mouse_pos, dt)  # Advance cursor blink timers, key repeat, and hover state for all buttons
        self.buttons.draw(self.surface)     # Blit every button's current image onto the virtual surface

    def on_escape(self):
        """
            Define what happens when ESC is pressed.

            Also controls whether the auto back button is created in __init__ -
            if this returns "back", the button is shown (subject to show_back_button).
            Subclasses should override this to return None to disable ESC entirely,
            or return a different action string for custom ESC behaviour.

            Returns:
                "back" by default so most screens return to the previous window.
        """
        return "back"  # Sensible default - most windows want ESC to go back

    def show_back_button(self):
        """
            Control whether the auto back button is created in __init__.

            Evaluated once during construction alongside on_escape. Returning False
            suppresses the button even if on_escape returns "back", which is useful
            for root screens (e.g. login) where there is nowhere to go back to.

            Returns:
                True by default so most screens show the back button.
        """
        return True  # Default: show the auto back button

    def handle_action(self, action):
        """
            Route a button action string to screen-specific logic.

            The base implementation simply passes the action through unchanged,
            which lets strings like "back", "settings", and "controls" propagate
            directly to WindowManager without any subclass override needed.
            Subclasses override this to intercept specific actions and return
            None to consume them, or return a tuple for complex navigation.

            Args:
                action: the action string (or tuple) returned by a button.

            Returns:
                The action unchanged by default, so WindowManager receives it.
        """
        return action  # Default: pass through unchanged to WindowManager

    def set_display(self, new_display):
        """
            Swap in a new display surface and update all renderer and surface references.

            Called by WindowManager whenever the pygame display is recreated, for
            example after the player changes resolution or display mode in settings,
            or when the window is resized. All three references must be updated
            together to keep drawing and mouse mapping consistent.

            Args:
                new_display: the new pygame display Surface to render onto.
        """
        self.display = new_display                      # Update local reference so this window's display is current
        self.renderer.set_window_surface(new_display)  # Notify renderer so scaling and letterbox offsets are recalculated
        self.surface = self.renderer.virtual_surface   # Re-fetch virtual surface in case renderer recreated it