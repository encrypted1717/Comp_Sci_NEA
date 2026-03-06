import pygame
from core.window import Window
from core.button import Button


class GameSetup(Window):
    def __init__(self, display, renderer):
        super().__init__(display, renderer)

        # Setup Buttons
        self.__create_buttons()
        self.buttons.add(
            self.__player_vs_cpu_label,
            self.__player_vs_player_label,
            self.__easy_btn,
            self.__medium_btn,
            self.__hard_btn
        )

    def draw(self, dt):
        self.surface.fill((255, 255, 255))  # White background
        super().draw(dt)

    def __create_buttons(self):
        font = pygame.font.Font(self.fonts["OldeTome"], 40)
        small_font = pygame.font.Font(self.fonts["OldeTome"], 34)

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

        # Difficulty buttons sit beneath the PvCPU card
        btn_y = 595   # just below the card
        btn_w = 110
        btn_h = 52
        spacing = 15
        base_x  = (self.center_x - 400) - btn_w - spacing  # left-align trio under card

        self.__easy_btn = Button(
            (base_x, btn_y),
            (btn_w, btn_h),
            "Easy",
            small_font,
            "#ffffff",
            "#2a7a2a",   # green fill
            4,
            border_colour="#1a5a1a",
            offset_y=3,
            action=("game", "cpu", "easy"),
            hover_text_colour="#ffffff",
            hover_rect_colour="#1a5a1a",
            hover_border_colour="#1a5a1a",
            fill_on_hover=True
        )

        self.__medium_btn = Button(
            (base_x + btn_w + spacing, btn_y),
            (btn_w, btn_h),
            "Medium",
            small_font,
            "#ffffff",
            "#a07020",   # amber fill
            4,
            border_colour="#805010",
            offset_y=3,
            action=("game", "cpu", "medium"),
            hover_text_colour="#ffffff",
            hover_rect_colour="#805010",
            hover_border_colour="#805010",
            fill_on_hover=True
        )

        self.__hard_btn = Button(
            (base_x + (btn_w + spacing) * 2, btn_y),
            (btn_w, btn_h),
            "Hard",
            small_font,
            "#ffffff",
            "#8a1a1a",   # red fill
            4,
            border_colour="#6a0a0a",
            offset_y=3,
            action=("game", "cpu", "hard"),
            hover_text_colour="#ffffff",
            hover_rect_colour="#6a0a0a",
            hover_border_colour="#6a0a0a",
            fill_on_hover=True
        )

        self.__player_vs_player_label = Button(
            (self.center_x + 400, 400),
            (350, 350),
            "Player vs Player",
            font,
            '#ffffff',
            '#000000',
            5,
            offset_y=4,
            action=("game", "pvp"),
            border_colour="#000000",
            hover_text_colour="#000000",
            hover_rect_colour="#ffffff",
            hover_border_colour="#000000",
            fill_on_hover=True
        )