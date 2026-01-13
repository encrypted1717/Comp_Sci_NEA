import pygame
from graphics.resolution_scaler import ResolutionScaler
from core.button import Button


class Window:
    def __init__(self, display):
        self.display = display
        self.display_width, self.display_height = self.display.get_size()
        self.rs = ResolutionScaler((self.display_width, self.display_height), (1920, 1080))
        self.Button = Button
        self.events = None
        self.dt = 0
        self.fonts = {
            "OldeTome" : "assets\\fonts\\OldeTome\\OldeTome.ttf",
            "GothicPixel" : "assets\\fonts\\Number_Font_Osadam\\Gothic_pixel_font.ttf"
        }
        self.buttons = pygame.sprite.Group()

    def draw(self, dt):
        self.dt = dt
        self.buttons.update(pygame.mouse.get_pos())
        self.buttons.draw(self.display)  # keep loading buttons