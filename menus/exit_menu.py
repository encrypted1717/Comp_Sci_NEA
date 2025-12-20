import pygame
from core.button import Button


class ExitMenu(Button):
    def __init__(self, display):
        super().__init__()
        self.dt = None
        self.display = display
        self.events = None
        self.font = pygame.font.Font("assets\\fonts\\OldeTome\\OldeTome.ttf", 43)
        self.confirmation_btn = self.create_rect((960, 540), (550, 120), '#ffffff', '#000000', "Are you sure you want to exit", self.font, 0, offset_y=4)
        self.back_btn = self.create_rect((150, 120), (175, 70), '#ffffff', '#000000', "Back", self.font, 0, offset_y=4)
        self.buttons = [self.confirmation_btn, self.back_btn]

    def event_handler(self, events):
        self.events = events
        for event in self.events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # if user left clicks mouse
                if self.confirmation_btn["rect"].collidepoint(event.pos):  # if colliding with any menu buttons... open that menu
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
                if self.back_btn["rect"].collidepoint(event.pos):
                    return "main_menu"
            # check_click = print(event.pos, event.button)
        return None

    def draw(self, dt):
        self.dt = dt
        for btn in self.buttons:
            pygame.draw.rect(self.display, btn["rect_colour"], btn["rect"], btn["border"])
            self.display.blit(btn["text_surf"], btn["text_rect"])