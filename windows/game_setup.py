"""
    Game setup screen for game.

    This module provides the GameSetup class, which presents the mode-selection
    screen between the main menu and an active match. It lets the player choose
    between Player vs CPU (with a difficulty selection) and Player vs Player.
    Button actions are passed back to WindowManager as tuples so it can configure
    the match before pushing the game window.
"""

import pygame
from core import Window, Button

class GameSetup(Window):
    """
        Mode-selection screen shown before a match begins.

        Inherits from Window for display surface, renderer, button group, and font
        access. Presents two cards - Player vs CPU and Player vs Player - with
        difficulty buttons nested beneath the CPU card. All navigation is handled
        by returning action tuples through the inherited event_handler.

        Button actions emitted:
            ("game", "pvp")               - start a Player vs Player match.
            ("game", "cpu", "easy")       - start a CPU match on easy difficulty.
            ("game", "cpu", "medium")     - start a CPU match on medium difficulty.
            ("game", "cpu", "hard")       - start a CPU match on hard difficulty.
    """

    def __init__(self, display, renderer):
        """
            Initialise the setup screen and register all buttons.

            Creates mode-card labels and difficulty buttons, then adds them all
            to the inherited button group so they are updated and drawn each frame.

            Args:
                display: the pygame Surface to render onto.
                renderer: the VirtualRenderer instance shared across all windows.
        """
        super().__init__(display, renderer)

        # Build all buttons before registering them so every reference is valid
        self.__create_buttons()

        # Register every button with the inherited group so they receive events and are drawn
        self.buttons.add(
            self.__player_vs_cpu_label,
            self.__player_vs_player_label,
            self.__easy_btn,
            self.__medium_btn,
            self.__hard_btn
        )

    def draw(self, dt):
        """
            Clear the screen and draw all buttons for this frame.

            Fills with white before calling super().draw(dt) so buttons are always
            rendered on top of a clean background.

            Args:
                dt: delta time in seconds since the last frame.
        """
        self.surface.fill((255, 255, 255)) # white background applied before buttons are drawn on top
        super().draw(dt)

    def __create_buttons(self):
        """
            Instantiate all mode-card labels and difficulty buttons.

            Positions the difficulty trio directly beneath the Player vs CPU card,
            using a shared base_x so the three buttons stay aligned as a group.
            Fonts are created here and discarded after construction since Button
            stores a rendered copy internally.
        """
        font = pygame.font.Font(self.fonts["OldeTome"], 40) # used for the two large mode-card labels
        small_font = pygame.font.Font(self.fonts["OldeTome"], 34) # used for the smaller difficulty buttons

        # Player vs CPU card - acts as a label only, difficulty buttons handle actual navigation
        self.__player_vs_cpu_label = Button(
            (self.center_x - 400, 370),
            (350, 200),
            "Player vs CPU",
            font,
            '#ffffff',
            '#000000',
            5,
            offset_y=4,
            border_colour="#000000"
        )

        # Difficulty button layout - trio sits just below the Player vs CPU card
        btn_y = 595 # vertical position, placing the row directly under the card
        btn_w = 110
        btn_h = 52
        spacing = 15
        base_x = (self.center_x - 400) - btn_w - spacing # left-aligns the trio under the card

        # Easy button - green colouring to signal low difficulty
        self.__easy_btn = Button(
            (base_x, btn_y),
            (btn_w, btn_h),
            "Easy",
            small_font,
            "#ffffff",
            "#2a7a2a", # green fill
            4,
            border_colour="#1a5a1a",
            offset_y=3,
            action=("game", "cpu", "easy"), # tuple consumed by WindowManager to start a CPU match
            hover_text_colour="#ffffff",
            hover_rect_colour="#1a5a1a",
            hover_border_colour="#1a5a1a",
            fill_on_hover=True
        )

        # Medium button - amber colouring to signal moderate difficulty
        self.__medium_btn = Button(
            (base_x + btn_w + spacing, btn_y), # offset one button-width right of easy
            (btn_w, btn_h),
            "Medium",
            small_font,
            "#ffffff",
            "#a07020", # amber fill
            4,
            border_colour="#805010",
            offset_y=3,
            action=("game", "cpu", "medium"),
            hover_text_colour="#ffffff",
            hover_rect_colour="#805010",
            hover_border_colour="#805010",
            fill_on_hover=True
        )

        # Hard button - red colouring to signal high difficulty
        self.__hard_btn = Button(
            (base_x + (btn_w + spacing) * 2, btn_y), # offset two button-widths right of easy
            (btn_w, btn_h),
            "Hard",
            small_font,
            "#ffffff",
            "#8a1a1a", # red fill
            4,
            border_colour="#6a0a0a",
            offset_y=3,
            action=("game", "cpu", "hard"),
            hover_text_colour="#ffffff",
            hover_rect_colour="#6a0a0a",
            hover_border_colour="#6a0a0a",
            fill_on_hover=True
        )

        # Player vs Player card - interactive, navigates directly to a PvP match on click
        self.__player_vs_player_label = Button(
            (self.center_x + 400, 400),
            (350, 350),
            "Player vs Player",
            font,
            '#ffffff',
            '#000000',
            5,
            offset_y=4,
            action=("game", "pvp"), # tuple consumed by WindowManager to start a PvP match
            border_colour="#000000",
            hover_text_colour="#000000",
            hover_rect_colour="#ffffff",
            hover_border_colour="#000000",
            fill_on_hover=True
        )