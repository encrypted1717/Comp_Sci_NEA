import pygame
import logging
from core.window import Window
from core.button import Button
from core.config_manager import ConfigManager
from graphics.parallax_background import Background


class MainMenu(Window):
    def __init__(self, display, renderer, player1: tuple, player2: tuple | None):
        super().__init__(display, renderer)

        # Logging Setup
        self.log = logging.getLogger(__name__)
        self.log.info("Initialising Main Menu module")
        # Main Setup
        self.player1_ID, self.player1_username = player1
        self.player2_ID, self.player2_username = player2 if player2 is not None else (None, None)
        # Setup parallax background
        self.bg = Background()
        self.bg.resize((self.display_width, self.display_height)) # Resize to virtual resolution (1920 x 1080)
        # Setup buttons

        self.player1_label = None
        self.player2_label = None
        self.__start_btn = None
        self.__controls_btn = None
        self.__settings_btn = None
        self.__exit_btn = None

        self.__create_buttons()

        if self.player2_ID: # If player 2 is logged in
            self.buttons.add(self.player2_label)
        else:
            self.buttons.add(self.player2_btn)

        self.buttons.add(
            self.player1_label,
            self.__start_btn,
            self.__leaderboard_btn,
            self.__controls_btn,
            self.__settings_btn,
            self.__exit_btn
        )

    def event_handler(self, events):
        for event in events:
            for btn in self.buttons:
                action = btn.handle_event(event)
                if action == "login":
                    return (action, 2)
                if action:
                    return action
        return None

    def draw(self, dt):
        self.bg.update(dt)
        self.bg.draw(self.surface) # Draw to virtual surface
        super().draw(dt)

    def __create_buttons(self):
        menu_font = pygame.font.Font(self.fonts["OldeTome"], 43)
        player_font = pygame.font.Font(self.fonts["GothicPixel"], 16)
        menu_width = 255
        height = 70
        player_width = 175
        player1_offset = 22 * len(self.player1_username)
        player2_offset = 22 * len(self.player2_username) if self.player2_ID is not None else 0

        self.player1_label = Button(
            (150 + (player1_offset // 2), 90),
            (player_width + player1_offset, height),
            f"Player 1: {self.player1_username}",
            player_font,
            "#ffffff",
            "#000000",
            5,
            border_colour="#ffffff",
            fill=False,
            offset_y=4
        )

        self.player2_label = Button(
            (1770 - (player2_offset // 2), 90),
            (player_width + player2_offset, height),
            f"Player 2: {self.player2_username}",
            player_font,
            "#ffffff",
            "#000000",
            5,
            border_colour="#ffffff",
            fill=False,
            offset_y=4
        ) if self.player2_ID is not None else None

        self.player2_btn = Button(
            (1693, 90),
            (329, height),
            f"Login as Player 2",
            player_font,
            "#ffffff",
            "#000000",
            5,
            border_colour="#ffffff",
            fill=False,
            offset_y=4,
            action="login",
            hover_text_colour="#000000",
            hover_rect_colour="#ffffff",
            hover_border_colour="#000000",
            fill_on_hover=True
        ) if self.player2_ID is None else None

        self.__start_btn = Button(
            (self.center_x, 360),
            (menu_width, height),
            "Start",
            menu_font,
            "#ffffff",
            "#000000",
            5,
            border_colour="#ffffff",
            fill=False,
            offset_y=4,
            action="setup",
            hover_text_colour="#000000",
            hover_rect_colour="#ffffff",
            hover_border_colour="#000000",
            fill_on_hover=True
        )
        self.__leaderboard_btn = Button(
            (self.center_x, 450),
            (menu_width, height),
            "Leaderboard",
            menu_font,
            "#ffffff",
            "#000000",
            5,
            border_colour="#ffffff",
            fill=False,
            offset_y=4,
            action="leaderboard",
            hover_text_colour="#000000",
            hover_rect_colour="#ffffff",
            hover_border_colour="#000000",
            fill_on_hover=True
        )
        self.__controls_btn = Button(
            (self.center_x, 540),
            (menu_width, height),
            "Controls",
            menu_font,
            "#ffffff",
            "#000000",
            5,
            border_colour="#ffffff",
            fill=False,
            offset_y=4,
            action="controls",
            hover_text_colour="#000000",
            hover_rect_colour="#ffffff",
            hover_border_colour="#000000",
            fill_on_hover=True
        )

        self.__settings_btn = Button(
            (self.center_x, 630),
            (menu_width, height),
            "Settings",
            menu_font,
            "#ffffff",
            "#000000",
            5,
            border_colour="#ffffff",
            fill=False,
            offset_y=4,
            action="settings",
            hover_text_colour="#000000",
            hover_rect_colour="#ffffff",
            hover_border_colour="#000000",
            fill_on_hover=True
        )

        self.__exit_btn = Button(
            (self.center_x, 720),
            (menu_width, height),
            "Exit",
            menu_font,
            "#ffffff",
            "#000000",
            5,
            border_colour="#ffffff",
            fill=False,
            offset_y=4,
            action="exit",
            hover_text_colour="#000000",
            hover_rect_colour="#ffffff",
            hover_border_colour="#000000",
            fill_on_hover=True
        )
