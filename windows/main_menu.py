"""
    Main menu window displayed after player 1 has logged in.

    This module provides the MainMenu class, which serves as the hub for all
    navigation in the game. It shows the logged-in player names, provides access
    to game setup, controls, settings, leaderboard, and exit, and allows player 2
    to log in from this screen.
"""

import pygame
from core.window import Window
from core.button import Button
from graphics.parallax_background import Background


class MainMenu(Window):
    """
        Central navigation hub shown after player 1 logs in.

        Displays a scrolling parallax background behind a vertical menu of options.
        Player 1's username is always shown in the top-left. If player 2 is logged in
        their username appears top-right; otherwise a login button is shown instead.
        ESC and the auto back button are disabled — the main menu is the root screen.
    """

    def __init__(self, display: pygame.Surface, renderer, player1: tuple[int, str], player2: tuple[int, str] | None) -> None:
        """
            Initialise the main menu.

            Args:
                display: the pygame display surface.
                renderer: the renderer managing the virtual surface and scaling.
                player1: (user_id, username) of the logged-in player 1.
                player2: (user_id, username) of player 2, or None if not yet logged in.
        """
        super().__init__(display, renderer)
        self.player1_ID, self.player1_username = player1
        self.player2_ID, self.player2_username = player2 if player2 is not None else (None, None)  # Unpack safely even when player 2 is absent

        # Parallax background scrolls behind the menu
        self.bg = Background()
        self.bg.resize((self.design_width, self.design_height))

        self.__create_buttons()

        # Show either player 2's name label or the login button depending on whether they are logged in
        if self.player2_ID:
            self.buttons.add(self.p2_label)
        else:
            self.buttons.add(self.p2_btn)

        self.buttons.add(
            self.p1_label,
            self.__start_btn,
            self.__leaderboard_btn,
            self.__controls_btn,
            self.__settings_btn,
            self.__exit_btn
        )

    def on_escape(self) -> None:
        """Disable ESC — the main menu is the root screen with no parent to return to."""
        return None

    def show_back_button(self) -> bool:
        """Suppress the auto back button — there is no previous screen from the main menu."""
        return False

    def handle_action(self, action: str) -> tuple | str:
        """
            Handle actions specific to the main menu.

            Intercepts the player 2 login button action and wraps it with the
            player number so WindowManager knows which login slot to fill.
            All other actions pass through unchanged.

            Args:
                action: the action string returned by a button.

            Returns:
                ("login", 2) when the player 2 login button is pressed,
                otherwise the action string unchanged.
        """
        if action == "login":
            return "login", 2  # Tell WindowManager to open a login screen for player 2
        return action

    def draw(self, dt: float) -> None:
        """
            Draw the scrolling background then the menu buttons.

            Args:
                dt: delta time in seconds since the last frame.
        """
        self.bg.update(dt)
        self.bg.draw(self.surface)
        super().draw(dt)

    def __create_buttons(self) -> None:
        """Create and store all player labels and navigation buttons for the main menu."""
        menu_font  = pygame.font.Font(self.fonts["OldeTome"], 43)
        player_font = pygame.font.Font(self.fonts["GothicPixel"], 16)
        menu_width = 255
        height     = 70
        player_width = 175

        # Button width scales with username length so long names don't overflow their label
        player1_offset = 22 * len(self.player1_username)
        player2_offset = 22 * len(self.player2_username) if self.player2_ID is not None else 0

        # Shared styling for all interactive centre-column menu buttons
        menu_btn_kwargs = {
            "font": menu_font,
            "text_colour": "#ffffff",
            "rect_colour": "#000000",
            "border": 5,
            "border_colour": "#ffffff",
            "fill": False,
            "offset_y": 4,
            "hover_text_colour": "#000000",
            "hover_rect_colour": "#ffffff",
            "hover_border_colour": "#000000",
            "fill_on_hover": True
        }

        # Shared styling for the static player name labels (non-interactive)
        player_kwargs = {
            "font": player_font,
            "text_colour": "#ffffff",
            "rect_colour": "#000000",
            "border": 5,
            "border_colour": "#ffffff",
            "fill": False,
            "offset_y": 4
        }

        # Player 1 label anchored to the top-left, expanding right with username length
        self.p1_label = Button(
            (150 + (player1_offset // 2), 90),
            (player_width + player1_offset, height),
            f"Player 1: {self.player1_username}",
            **player_kwargs
        )

        # Player 2 label anchored to the top-right, expanding left with username length
        self.p2_label = Button(
            (1770 - (player2_offset // 2), 90),
            (player_width + player2_offset, height),
            f"Player 2: {self.player2_username}",
            **player_kwargs
        ) if self.player2_ID is not None else None  # Only created when player 2 is logged in

        # Shown in place of p2_label when player 2 has not yet logged in
        self.p2_btn = Button(
            (1693, 90),
            (329, height),
            "Login as Player 2",
            player_font,
            "#ffffff", "#000000", 5,
            border_colour="#ffffff",
            fill=False,
            offset_y=4,
            action="login",
            hover_text_colour="#000000",
            hover_rect_colour="#ffffff",
            hover_border_colour="#000000",
            fill_on_hover=True
        ) if self.player2_ID is None else None  # Only created when player 2 is absent

        self.__start_btn = Button(
            (self.center_x, 360),
            (menu_width, height),
            "Start",
            action="setup",
            **menu_btn_kwargs
        )

        self.__leaderboard_btn = Button(
            (self.center_x, 450),
            (menu_width, height),
            "Leaderboard",
            action="leaderboard",
            **menu_btn_kwargs
        )

        self.__controls_btn = Button(
            (self.center_x, 540),
            (menu_width, height),
            "Controls",
            action="controls",
            **menu_btn_kwargs
        )

        self.__settings_btn = Button(
            (self.center_x, 630),
            (menu_width, height),
            "Settings",
            action="settings",
            **menu_btn_kwargs
        )

        self.__exit_btn = Button(
            (self.center_x, 720),
            (menu_width, height),
            "Exit",
            action="exit",
            **menu_btn_kwargs
        )