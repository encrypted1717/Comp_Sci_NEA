import pygame
from core.entity import Entity
from core.config_manager import ConfigManager
from core.button import Button


class Game(Button):
    def __init__(self, window):
        super().__init__()
        # Main Setup
        self.window = window
        self.dt = 0 # Seconds
        self.events = None
        # Player setup
        self.player = Entity((680, 540))
        # Setup configurations
        self.config_manager = ConfigManager()
        self.config = self.config_manager.get_config()
        self.config_manager.open_file("assets\\game_settings\\config_user.ini")

    def event_handler(self, events):
        self.events = events
        self.player.event_handler(self.events)
        for event in self.events:
            #kb press down
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "main_menu"

            #kb up
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_ESCAPE:
                    return "main_menu"
        return None

    def draw(self, dt):
        self.dt = dt
        self.player.update(self.dt)
        self.player.draw(self.window)
        # Needed to avoid truncation error