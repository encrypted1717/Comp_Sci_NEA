import pygame
from core.button import Button


class ControlsMenu(Button):
    def __init__(self, window):
        super().__init__()
        self.window = window

    def event_handler(self):
        return "controls"