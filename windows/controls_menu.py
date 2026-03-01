import pygame
from core.window import Window


class ControlsMenu(Window):
    def __init__(self, display, renderer, player1, player2):
        super().__init__(display, renderer)



    def event_handler(self, events):
        for event in events:
            # kb press down
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return "back"
            for btn in self.buttons:
                action = btn.handle_event(event)
                if action == "":
                    pass
                elif action:
                    return action
        return None

    def draw(self, dt):
        super().draw(dt)