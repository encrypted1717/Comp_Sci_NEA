import pygame
from core.button import Button


class ExitMenu:
    def __init__(self, display):
        self.dt = None
        self.display = display
        self.events = None
        self.font = pygame.font.Font("assets\\fonts\\OldeTome\\OldeTome.ttf", 43)
        self.buttons = pygame.sprite.Group()
        # noinspection PyTypeChecker
        self.buttons.add(
            Button((960, 540), (550, 120), "Are you sure you want to exit", self.font, "#ffffff", '#000000', 5, border_colour = "#ffffff", offset_y = 4, action = "exit", hover_text_colour = "#000000", hover_rect_colour = "#ffffff", hover_border_colour = "#000000"),
            Button((150, 120), (175, 70), "Back", self.font, "#ffffff", "#000000", 5, border_colour = "#ffffff", offset_y = 4, action = "main_menu", hover_text_colour = "#000000", hover_rect_colour = "#ffffff", hover_border_colour = "#000000")
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