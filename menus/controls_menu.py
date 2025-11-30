import pygame
from core.button import Button


class ControlsMenu(Button):
    def __init__(self, window):
        super().__init__()
        self.events = None
        self.dt = None
        self.window = window

    def event_handler(self, events):
        self.events = events
        return "main_menu"

    def draw(self, dt):
        self.dt = dt