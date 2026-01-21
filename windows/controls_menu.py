import pygame
from core.window import Window


class ControlsMenu(Window):
    def __init__(self, display, renderer):
        super().__init__(display, renderer)

    def event_handler(self, events):
        return "main_menu"

    def draw(self, dt):
        super().draw()