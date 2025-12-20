import pygame
from core.button import Button


class ControlsMenu(Button):
    def __init__(self, display):
        super().__init__()
        self.events = None
        self.dt = None
        self.display = display

    def event_handler(self, events):
        self.events = events
        return "main_menu"

    def draw(self, dt):
        self.dt = dt