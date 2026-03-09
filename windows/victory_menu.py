"""
    Victory screen window displayed at the end of a match.

    This module provides the VictoryMenu class, which is shown once a winner
    has been determined in a best-of-3 series. It announces the winning player
    and offers options to play again or return to the main menu.
"""

import pygame
from core import Window, Button


class VictoryMenu(Window):
    """
        End-of-match screen that announces the winner and offers next steps.

        Displays the winning player's label and username, and presents two
        options: starting a new game setup or exiting to the main menu.
        ESC is intentionally disabled on this screen.
    """

    def __init__(self, display: pygame.Surface, renderer, winner: tuple) -> None:
        """
            Initialise the victory menu.

            Args:
                display: the pygame display surface.
                renderer: the renderer managing the virtual surface and scaling.
                winner: a tuple of (player_label, username, elapsed_time) identifying the winner,
                        e.g. ("Player 1", "Alice", 42.5). elapsed_time is None for PvP matches.
        """
        super().__init__(display, renderer)
        # Main setup
        self._winner = winner  # Stored as (player_label, username) set by the game on win condition
        # Create buttons
        self.__create_buttons()
        self.buttons.add(
            self.victory_label,
            self.win_label,
            self.prompt_label,  # Fixed: was created but never added, so never rendered
            self.play_button,
            self.exit_button
        )

    def on_escape(self) -> None:
        """Disable ESC on the victory screen — the player must make an explicit choice."""
        return None

    def draw(self, dt: float) -> None:
        """
            Draw the victory screen.

            Args:
                dt: delta time passed since the last frame.
        """
        self.surface.fill((255, 255, 255))
        super().draw(dt)

    def __create_buttons(self) -> None:
        """Create and store all labels and buttons displayed on the victory screen."""
        username = self._winner[1]
        player_label = self._winner[0]

        menu_font  = pygame.font.Font(self.fonts["GothicPixel"], 20)
        small_font = pygame.font.Font(self.fonts["GothicPixel"], 14)
        title_font = pygame.font.Font(self.fonts["GothicPixel"], 22)

        # Shared hover styling — interactive buttons invert colours on hover
        hover_kwargs = {
            "hover_text_colour": "#000000",
            "hover_rect_colour": "#ffffff",
            "hover_border_colour": "#000000",
        }

        self.victory_label = Button(
            (self.center_x, 120), (235, 70),
            "Victory",
            title_font, "#ffffff", "#000000",
            offset_y=4
        )

        self.win_label = Button(
            (self.center_x, self.center_y - 270),
            (510, 110),
            f"{player_label} - {username}  wins!!",  # player_label is e.g. "Player 1", username is their login name
            menu_font,
            "#ffffff",
            "#000000",
            offset_y=4,
        )

        self.prompt_label = Button(
            (self.center_x, self.center_y - 130),
            (550, 90),
            "What would you like to do?",
            small_font,
            "#ffffff",
            "#000000",
            3,
            border_colour="#ffffff",
            offset_y=4,
        )

        self.play_button = Button(
            (self.center_x - 200, self.center_y),
            (340, 90),
            "Play Again",
            small_font,
            "#ffffff",
            "#000000",
            5,
            border_colour="#ffffff",
            offset_y=4,
            action="setup",  # "setup" pushes the game setup screen so players can choose mode again
            **hover_kwargs
        )

        self.exit_button = Button(
            (self.center_x + 200, self.center_y),
            (340, 90),
            "Exit to Main Menu",
            small_font,
            "#ffffff",
            "#000000",
            3,
            border_colour="#ffffff",
            offset_y=4,
            action="main",  # "main" triggers a hard reset of the window stack back to the main menu
            **hover_kwargs
        )