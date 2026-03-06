"""
    Pause menu window for the game.

    This module provides the PauseMenu class, which is displayed when the player
    pauses the game mid-match. It renders a blurred snapshot of the game frame
    as its background, and presents options to continue, adjust controls/settings,
    return to the main menu, or exit.
"""

import pygame
from core.window import Window
from core.button import Button


class PauseMenu(Window):
    """
        Overlay menu displayed when the game is paused.

        The PauseMenu renders a blurred version of the last rendered game frame
        behind its buttons, giving the impression of an in-game overlay. It
        provides navigation to continue the game, access controls or settings,
        return to the main menu, or exit.
    """

    def __init__(self, display: pygame.Surface, renderer, background_surface: pygame.Surface) -> None:
        """
            Initialise the pause menu.

            Args:
                display: the pygame display surface.
                renderer: the renderer managing the virtual surface and scaling.
                background_surface: a snapshot of the game frame to display blurred behind the menu.
        """
        super().__init__(display, renderer)
        # Main setup
        self.log.info("Game has been paused")
        self.background_surface = background_surface  # Saved game frame used as the blurred backdrop
        # Create buttons
        self.__create_buttons()
        self.buttons.add(
            self.continue_btn,
            self.controls_btn,
            self.settings_btn,
            self.main_menu_btn,
            self.exit_btn
        )

    def draw(self, dt: float) -> None:
        """
            Draw the pause menu, blurring the background game frame before rendering buttons.

            Args:
                dt: delta time passed since the last frame.
        """
        # Blur the captured game frame to visually indicate the game is paused
        blurred = pygame.transform.box_blur(self.background_surface, radius=7)
        self.surface.blit(blurred, (0, 0))

        super().draw(dt)

    def __create_buttons(self) -> None:
        """Create and store all buttons displayed in the pause menu."""
        font = pygame.font.Font(self.fonts["OldeTome"], 43)
        width = 400
        height = 70

        # Shared arguments
        kwargs = {
            "dimensions": (width, height),
            "font": font,
            "text_colour": "#ffffff",
            "rect_colour": "#000000",
            "border": 5,
            "border_colour": "#000000",
            "fill": True,
            "offset_y": 4,
            "hover_text_colour": "#000000",
            "hover_rect_colour": "#ffffff",
            "hover_border_colour": "#000000",
            "fill_on_hover": True
        }

        self.continue_btn = Button(
            (self.center_x, 370), # Even though these arguments don't need to declare i.e position=, in this case you do because dimensions breaks the order
            text="Continue",
            action="back",  # "back" pops the pause menu off the stack and resumes the game
            **kwargs
        )

        self.controls_btn = Button(
            (self.center_x, 460),
            text="Controls",
            action="controls",
            **kwargs
        )

        self.settings_btn = Button(
            (self.center_x, 550),
            text="Settings",
            action="settings",
            **kwargs
        )

        self.main_menu_btn = Button(
            (self.center_x, 640),
            text="Return to main menu",
            action="main",  # "main" triggers a hard reset of the window stack back to the main menu
            **kwargs
        )

        self.exit_btn = Button(
            (self.center_x, 730),
            text="Exit",
            action="exit",
            **kwargs
        )

    def show_back_button(self):
        return False