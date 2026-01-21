import pygame
from core.window import Window
from core.button import Button


class ExitMenu(Window):
    def __init__(self, display, renderer):
        super().__init__(display, renderer)
        self.buttons.add(
            Button(
                (self.center_x, self.center_y),
                (550, 120),
                "Are you sure you want to exit",
                pygame.font.Font(self.fonts["OldeTome"], 43),
                "#ffffff",
                '#000000',
                5,
                border_colour = "#ffffff",
                offset_y = 4,
                action = "exit",
                hover_text_colour = "#000000",
                hover_rect_colour = "#ffffff",
                hover_border_colour = "#000000"
            ),
            Button(
                (150, 120),
                (175, 70),
                "Back",
                pygame.font.Font(self.fonts["OldeTome"], 43),
                "#ffffff",
                "#000000",
                5,
                border_colour = "#ffffff",
                offset_y = 4,
                action = "main_menu",
                hover_text_colour = "#000000",
                hover_rect_colour = "#ffffff",
                hover_border_colour = "#000000"
            )
        )

    def event_handler(self, events):
        for event in events:
            for btn in self.buttons:
                action = btn.handle_event(event)
                if action is None:
                    continue
                if action == "exit":
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
                    return None
                return action
        return None

    def draw(self, dt):
        self.surface.fill((255, 255, 255))
        super().draw(dt)