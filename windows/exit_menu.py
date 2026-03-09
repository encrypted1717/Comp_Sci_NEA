"""
    Exit confirmation menu window.

    This module provides the ExitMenu class, which is displayed when the player
    chooses to exit from the main menu or pause menu. It prompts the player to
    choose between logging out and returning to the login screen, or quitting
    the application entirely.
"""

import pygame
from core import Window, Button


class ExitMenu(Window):
    """
        Confirmation overlay presented when the player chooses to exit.

        Offers two distinct exit paths: logging out of the current session
        and returning to the login screen, or quitting the application entirely.
        ESC and the auto back button are both available to dismiss the menu.
    """

    def __init__(self, display: pygame.Surface, renderer) -> None:
        """
            Initialise the exit menu.

            Args:
                display: the pygame display surface.
                renderer: the renderer managing the virtual surface and scaling.
        """
        super().__init__(display, renderer)
        # Create buttons
        self.__create_buttons()
        self.buttons.add(
            self.question_label,
            self.log_out_btn,
            self.exit_btn
        )

    def handle_action(self, action: str) -> str | None:
        """
            Handle button actions specific to the exit menu.

            Intercepts the "exit" action to post a QUIT event rather than
            returning it up the chain. All other actions pass through unchanged.

            Args:
                action: the action string returned by a button.

            Returns:
                None if the app is quitting, otherwise the action string.
        """
        if action == "exit":
            pygame.event.post(pygame.event.Event(pygame.QUIT))  # Triggers the main loop to shut down cleanly
            return None
        return action  # "back" and "logout" are handled by WindowManager

    def draw(self, dt: float) -> None:
        """
            Draw the exit menu.

            Args:
                dt: delta time passed since the last frame.
        """
        self.surface.fill((255, 255, 255))
        super().draw(dt)

    def __create_buttons(self) -> None:
        """Create and store all labels and buttons displayed in the exit menu."""
        small_font  = pygame.font.Font(self.fonts["OldeTome"], 34)
        option_font = pygame.font.Font(self.fonts["OldeTome"], 43)

        # Shared hover styling — both option buttons invert colours on hover
        hover_kwargs = {
            "hover_text_colour": "#000000",
            "hover_rect_colour": "#ffffff",
            "hover_border_colour": "#000000"
        }

        self.question_label = Button(
            (self.center_x, self.center_y - 130),
            (550, 90),
            "What would you like to do?",
            small_font,
            "#ffffff", "#000000", 5,
            border_colour="#ffffff",
            offset_y=4,
        )

        self.log_out_btn = Button(
            (self.center_x - 200, self.center_y),
            (340, 90),
            "Log Out",
            option_font,
            "#ffffff", "#000000", 5,
            border_colour="#ffffff",
            offset_y=4,
            action="logout",  # "logout" clears player session and resets to the login screen
            **hover_kwargs
        )

        self.exit_btn = Button(
            (self.center_x + 200, self.center_y),
            (340, 90),
            "Exit Game",
            option_font,
            "#ffffff", "#000000", 5,
            border_colour="#ffffff",
            offset_y=4,
            action="exit",  # "exit" posts a QUIT event, handled in handle_action above
            **hover_kwargs
        )