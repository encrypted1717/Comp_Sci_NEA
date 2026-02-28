import pygame
import logging
from core.window import Window
from core.button import Button


class GameSetup(Window):
    def __init__(self, display, renderer, player1, player2):
        super().__init__(display, renderer)

        # Setup Logging
        self.log = logging.getLogger(__name__)
        self.log.info("Initialising Login Menu module")

        # Setup Buttons
        self.__create_buttons()
        self.buttons.add(
            self.__back_btn,
            self.__player_vs_cpu_label,
            self.__player_vs_player_label
        )

    def event_handler(self, events):
        for event in events:
            # kb press down
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return "back"
            for btn in self.buttons:
                action = btn.handle_event(event)

                if action:
                    return action

        return None

    def draw(self, dt):
        self.surface.fill((255, 255, 255))  # White background
        super().draw(dt)

    def __create_buttons(self):
        font = pygame.font.Font(self.fonts["OldeTome"], 40)
        self.__back_btn = Button(
            (150, 120),
            (160, 60),
            "Back",
            pygame.font.Font(self.fonts["OldeTome"], 37),
            "#ffffff",
            '#000000',
            5,
            border_colour="#000000",
            offset_y=4,
            action="back",
            hover_text_colour="#000000",
            hover_rect_colour="#ffffff",
            hover_border_colour="#000000",
            fill_on_hover=True
        )

        self.__player_vs_cpu_label = Button(
            (self.center_x - 400, 400),
            (350, 350),
            "Player vs CPU",
            font,
            '#ffffff',
            '#000000',
            5,
            offset_y=4,
            action="game",
            border_colour="#000000",
            hover_text_colour="#000000",
            hover_rect_colour="#ffffff",
            hover_border_colour="#000000",
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
            action="game",
            border_colour="#000000",
            hover_text_colour="#000000",
            hover_rect_colour="#ffffff",
            hover_border_colour="#000000",
            fill_on_hover=True
        )


