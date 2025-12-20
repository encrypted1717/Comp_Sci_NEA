import pygame
from core.entity import Entity
from core.config_manager import ConfigManager
from core.button import Button
from core.collider import Collider
from core.collision_manager import CollisionManager


class Game(Button):
    # noinspection PyTypeChecker
    def __init__(self, display):
        super().__init__()
        # Main Setup
        self.display = display
        self.dt = 0 # Seconds
        self.events = None
        # Setup configurations
        self.config_manager = ConfigManager()
        self.config = self.config_manager.get_config()
        self.config_manager.open_file("assets\\game_settings\\config_user.ini")
        # Player setup
        self.player = Entity((680, 450))
        # Setup static objects
        self.ground = Collider(pygame.Rect(0, 1080, 1920, 100), "ground")
        # Setup collisions
        self.colliders = pygame.sprite.Group()
        self.colliders.add(self.ground)

        self.entities = pygame.sprite.Group()
        self.entities.add(self.player)

        self.collision_manager = CollisionManager(self.entities, self.colliders)

        # Map setup

    def event_handler(self, events):
        self.events = events
        for entity in self.entities:
            entity.event_handler(self.events)
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
        self.colliders.draw(self.display)
        self.entities.update(self.dt)
        self.collision_manager.resolve_entity()
        self.entities.draw(self.display)
        for entity in self.entities:
            pygame.draw.rect(self.display,(255, 0, 0), entity.rect, 5)