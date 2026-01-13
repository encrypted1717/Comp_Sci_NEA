import pygame
from core.button import Button
from graphics.parallax_background import Background
from core.window import Window

class MainMenu(Window):
    def __init__(self, display):
        super().__init__(display)
        # Setup parallax background
        self.bg = Background()
        self.bg.resize((self.display_width, self.display_height)) # Can be used once again when resolution changes
        # Setup buttons
        self.buttons = pygame.sprite.Group()
        self.center_x = self.rs.x(960)
        self.button_width = self.rs.x(255)
        self.button_height = self.rs.y(70)
        # noinspection PyTypeChecker
        self.buttons.add(
            Button(
                (self.center_x, self.rs.y(500)),
                (self.button_width, self.button_height),
                "Start",
                pygame.font.Font(self.fonts["OldeTome"], self.rs.u(43)),
                "#ffffff",
                "#000000",
                self.rs.u(5),
                border_colour = "#ffffff",
                fill = False,
                offset_y = self.rs.u(4),
                action = "start",
                hover_text_colour = "#000000",
                hover_rect_colour = "#ffffff",
                hover_border_colour = "#000000",
                fill_on_hover = True
            ),
            Button(
                (self.center_x, self.rs.y(590)),
                (self.button_width, self.button_height),
                "Controls",
                pygame.font.Font(self.fonts["OldeTome"], self.rs.u(43)),
                "#ffffff",
                "#000000",
                self.rs.u(5),
                border_colour = "#ffffff",
                fill = False,
                offset_y = self.rs.u(4),
                action = "controls",
                hover_text_colour = "#000000",
                hover_rect_colour = "#ffffff",
                hover_border_colour = "#000000",
                fill_on_hover = True
            ),
            Button(
                (self.center_x, self.rs.y(680)),
                (self.button_width, self.button_height),
                "Settings",
                pygame.font.Font(self.fonts["OldeTome"], self.rs.u(43)),
                "#ffffff",
                "#000000",
                self.rs.u(5),
                border_colour = "#ffffff",
                fill = False,
                offset_y = self.rs.u(4),
                action = "settings",
                hover_text_colour = "#000000",
                hover_rect_colour = "#ffffff",
                hover_border_colour = "#000000",
                fill_on_hover = True
            ),
            Button(
                (self.center_x, self.rs.y(770)),
                (self.button_width, self.button_height),
                "Exit",
                pygame.font.Font(self.fonts["OldeTome"], self.rs.u(43)),
                "#ffffff",
                "#000000",
                self.rs.u(5),
                border_colour = "#ffffff",
                fill = False,
                offset_y = self.rs.u(4),
                action = "exit",
                hover_text_colour = "#000000",
                hover_rect_colour = "#ffffff",
                hover_border_colour = "#000000",
                fill_on_hover = True
            ),
        )

    def event_handler(self, events):
        for event in events:
            for btn in self.buttons:
                action = btn.handle_event(event)
                if action is not None:
                    return action
        return None

    def draw(self, dt):
        self.bg.update(dt)
        self.bg.draw(self.display)
        super().draw(dt)