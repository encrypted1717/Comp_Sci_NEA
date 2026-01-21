import pygame
from core.window import Window
from core.button import Button

class PauseMenu(Window):
    def __init__(self, display, renderer, background_surface):
        super().__init__(display, renderer)
        self.background_surface = background_surface
        self.button_width = 255
        self.button_height = 70
        self.buttons.add(
            Button(
                (self.center_x, 370),
                (self.button_width, self.button_height),
                "Continue",
                pygame.font.Font(self.fonts["OldeTome"], 43),
                "#ffffff",
                "#000000",
                5,
                border_colour="#000000",
                fill=True,
                offset_y=4,
                action="start",
                hover_text_colour="#000000",
                hover_rect_colour="#ffffff",
                hover_border_colour="#000000",
                fill_on_hover=True
            ),
            Button(
                (self.center_x, 460),
                (self.button_width, self.button_height),
                "Controls",
                pygame.font.Font(self.fonts["OldeTome"], 43),
                "#ffffff",
                "#000000",
                5,
                border_colour="#000000",
                fill=True,
                offset_y=4,
                action="controls",
                hover_text_colour="#000000",
                hover_rect_colour="#ffffff",
                hover_border_colour="#000000",
                fill_on_hover=True
            ),
            Button(
                (self.center_x, 550),
                (self.button_width, self.button_height),
                "Settings",
                pygame.font.Font(self.fonts["OldeTome"], 43),
                "#ffffff",
                "#000000",
                5,
                border_colour="#000000",
                fill=True,
                offset_y=4,
                action="settings",
                hover_text_colour="#000000",
                hover_rect_colour="#ffffff",
                hover_border_colour="#000000",
                fill_on_hover=True
            ),
            Button(
                (self.center_x, 640),
                (self.button_width, self.button_height),
                "Exit",
                pygame.font.Font(self.fonts["OldeTome"], 43),
                "#ffffff",
                "#000000",
                5,
                border_colour="#000000",
                fill=True,
                offset_y=4,
                action="exit",
                hover_text_colour="#000000",
                hover_rect_colour="#ffffff",
                hover_border_colour="#000000",
                fill_on_hover=True
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
        blurred = pygame.transform.box_blur(self.background_surface, radius=5)
        self.surface.blit(blurred, (0, 0))
        super().draw(dt)
