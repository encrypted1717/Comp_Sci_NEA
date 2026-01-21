import pygame
from core.window import Window
from core.button import Button
from graphics.parallax_background import Background


class MainMenu(Window):
    def __init__(self, display, renderer):
        super().__init__(display, renderer)
        # Setup parallax background
        self.bg = Background()
        self.bg.resize((self.display_width, self.display_height)) # Resize to virtual resolution (1920 x 1080)
        # Setup buttons
        self.button_width = 255
        self.button_height = 70
        self.buttons.add(
            Button(
                (self.center_x, 500),
                (self.button_width, self.button_height),
                "Start",
                pygame.font.Font(self.fonts["OldeTome"], 43),
                "#ffffff",
                "#000000",
                5,
                border_colour = "#ffffff",
                fill = False,
                offset_y = 4,
                action = "start",
                hover_text_colour = "#000000",
                hover_rect_colour = "#ffffff",
                hover_border_colour = "#000000",
                fill_on_hover = True
            ),
            Button(
                (self.center_x, 590),
                (self.button_width, self.button_height),
                "Controls",
                pygame.font.Font(self.fonts["OldeTome"], 43),
                "#ffffff",
                "#000000",
                5,
                border_colour = "#ffffff",
                fill = False,
                offset_y = 4,
                action = "controls",
                hover_text_colour = "#000000",
                hover_rect_colour = "#ffffff",
                hover_border_colour = "#000000",
                fill_on_hover = True
            ),
            Button(
                (self.center_x, 680),
                (self.button_width, self.button_height),
                "Settings",
                pygame.font.Font(self.fonts["OldeTome"], 43),
                "#ffffff",
                "#000000",
                5,
                border_colour = "#ffffff",
                fill = False,
                offset_y = 4,
                action = "settings",
                hover_text_colour = "#000000",
                hover_rect_colour = "#ffffff",
                hover_border_colour = "#000000",
                fill_on_hover = True
            ),
            Button(
                (self.center_x, 770),
                (self.button_width, self.button_height),
                "Exit",
                pygame.font.Font(self.fonts["OldeTome"], 43),
                "#ffffff",
                "#000000",
                5,
                border_colour = "#ffffff",
                fill = False,
                offset_y = 4,
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
        self.bg.draw(self.surface) # Draw to virtual surface
        super().draw(dt)