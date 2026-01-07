import pygame
from core.entity import Entity
from core.config_manager import ConfigManager
from core.button import Button
from core.collider import Collider
from core.collision_manager import CollisionManager


class Game:
    # noinspection PyTypeChecker
    def __init__(self, display):
        # Main Setup
        self.display = display
        self.dt = 0 # Seconds
        self.events = None
        # Fonts
        self.front_font = pygame.font.Font("assets\\fonts\\OldeTome\\OldeTome.ttf", 56)
        self.num_font = pygame.font.Font("assets\\fonts\\Number_Font_Osadam\\Gothic_pixel_font.ttf", 16)

        # Setup configurations
        self.config_manager = ConfigManager()
        self.config = self.config_manager.get_config()
        self.config_manager.open_file("assets\\game_settings\\config_user.ini")
        # Player1 setup
        self.player1 = Entity((680, 450), "player1")
        self.health1_btn = Button((240, 120), (235, 70), f"Health: {str(self.player1.health)}", self.num_font, '#000000', '#ffffff', 5, border_colour = "#000000", offset_y=4)
        # Player2 setup
        self.player2 = Entity((1000, 450), "player2")
        # Setup static objects
        self.ground = Collider(pygame.Rect(0, 1080, 1920, 100), "ground")
        # Setup groups
        self.colliders = pygame.sprite.Group()
        self.colliders.add(self.ground)
        self.entities = pygame.sprite.Group()
        self.entities.add(self.player1)
        self.entities.add(self.player2)
        self.buttons = pygame.sprite.Group()
        self.buttons.add(self.health1_btn)

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
        self.collision_manager.resolve_entity(self.dt)
        for entity in self.entities:
            self.display.blit(entity.image, entity.img_rect.topleft)
            pygame.draw.rect(self.display,(255, 0, 0), entity.rect, 5) # collision/hit box
        self.buttons.draw(self.display)