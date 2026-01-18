import pygame
from core.window import Window
from core.button import Button


class ExitMenu(Window):
    def __init__(self, display):
        super().__init__(display)
        # noinspection PyTypeChecker
        self.buttons.add(
            Button(
                (self.center_x, self.center_y),
                (self.rs.x(550), self.rs.y(120)),
                "Are you sure you want to exit",
                pygame.font.Font(self.fonts["OldeTome"], self.rs.u(43)),
                "#ffffff",
                '#000000',
                self.rs.u(5),
                border_colour = "#ffffff",
                offset_y = self.rs.y(4),
                action = "exit",
                hover_text_colour = "#000000",
                hover_rect_colour = "#ffffff",
                hover_border_colour = "#000000"
            ),
            Button(
                (self.rs.x(150), self.rs.y(120)),
                (self.rs.x(175), self.rs.y(70)),
                "Back",
                pygame.font.Font(self.fonts["OldeTome"], self.rs.u(43)),
                "#ffffff",
                "#000000",
                self.rs.u(5),
                border_colour = "#ffffff",
                offset_y = self.rs.y(4),
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
        self.dt = dt
        mouse_pos = pygame.mouse.get_pos()
        self.buttons.update(mouse_pos)
        self.buttons.draw(self.display)