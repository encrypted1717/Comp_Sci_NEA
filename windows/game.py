import pygame
import logging
from core.window import Window
from core.entity import Entity
from core.config_manager import ConfigManager
from core.button import Button
from core.collision_manager import CollisionManager
from utils.combat_system import CombatSystem
from graphics.map_generation import MapGeneration


class Game(Window):
    def __init__(self, display, renderer, player1, player2):
        super().__init__(display, renderer)

        # Logging Setup
        self.log = logging.getLogger(__name__)
        self.log.info("Initialising Game module")

        # Configs Setup
        self.config_manager = ConfigManager("assets\\game_settings\\config_user.ini")
        self.config = self.config_manager.get_config()

        # Main Setup
        self.combat_system = CombatSystem()
        self.last_frame = None
        self.__setup_players()
        self.__setup_groups()
        self.__setup_map()

    def __setup_players(self):
        font = pygame.font.Font(self.fonts["GothicPixel"], 16)

        self.player1 = Entity((680,  450), "player1")
        self.health1_btn = Button(
            (240, 120),
            (235, 70),
            f"Health: {str(self.player1.health)}",
            font,
            '#000000',
            '#ffffff',
            5,
            border_colour="#000000",
            offset_y=4
        )

        # TODO make health button a percentage meter that reduces as the player loses health
        self.player2 = Entity((1000, 450), "player2")
        self.health2_btn = Button(
            (1560, 120),
            (235, 70),
            f"Health: {str(self.player2.health)}",
            font,
            '#000000',
            '#ffffff',
            5,
            border_colour="#000000",
            offset_y=4
        )

    def __setup_groups(self):
        self.colliders = pygame.sprite.Group()
        self.entities = pygame.sprite.Group(self.player1, self.player2)
        self.collision_manager = CollisionManager(self.entities, self.colliders)
        self.buttons.add(self.health1_btn, self.health2_btn)

    def __setup_map(self):
        self.map = MapGeneration()
        self.map.create_map()
        for tile in self.map.solid_tiles:
            self.colliders.add(tile)

        # Killzone is a death barrier that is slightly larger than the screen
        killzone_padding = 1000
        self.killzone = self.surface.get_rect().inflate(killzone_padding, killzone_padding)

    def event_handler(self, events):
        for entity in self.entities:
            entity.event_handler(events)

        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return "pause", self.last_frame # Necessary for pause menu
        return None

    def draw(self, dt):
        self.dt = dt
        self.surface.fill((128, 128, 128))

        self.colliders.draw(self.surface)
        self.entities.update(dt)
        self.collision_manager.resolve_entity(dt)

        self.__draw_entities()
        self.__update_health_ui()
        super().draw(dt)
        self.__process_combat()

        self.last_frame = self.surface.copy()

    def __draw_entities(self):
        # TODO: health should update to 0 if entity falls off map
        for entity in list(self.entities):
            alive = entity.health > 0 or entity.animation_manager.is_playing()
            if alive and self.killzone.contains(entity.body):
                self.surface.blit(entity.image, entity.img_rect.topleft)
                self.__draw_debug(entity) # TODO Turned on via button
            else:
                entity.health = 0
                self.entities.remove(entity)

    def __draw_debug(self, entity):
        # Collision body
        pygame.draw.rect(self.surface, (255, 0, 0), entity.body, 2)
        # Animation-based sprite bounds/hit box
        pygame.draw.rect(self.surface, (0, 255, 0), entity.sprite_bounds, 2)
        # Collider outlines
        for collider in self.colliders:
            pygame.draw.rect(collider.image, pygame.Color("white"), collider.image.get_rect(), 2)

    def __update_health_ui(self):
        self.health1_btn.update_text(f"Health: {max(self.player1.health, 0)}") # If below 0 then health is 0
        self.health2_btn.update_text(f"Health: {max(self.player2.health, 0)}")

    def __process_combat(self):
        for attacker in self.entities:
            if not attacker.attacking:
                continue

            for defender in self.entities:
                if attacker is not defender:
                    self.combat_system.try_apply_hits(attacker, defender)

            self.__draw_attack_hitbox(attacker)

        self.combat_system.update(self.entities)

    def __draw_attack_hitbox(self, attacker):
        """Debug: draw the active hitbox rect for an attacking entity."""
        attack_data = self.combat_system.attacks.get(attacker.attack_name)
        if not attack_data:
            return

        frame_index = attacker.animation_manager.get_frame_index()
        hitbox_data = attack_data.get("hitbox", {}).get(frame_index)
        if not hitbox_data:
            return

        hitbox = self.combat_system.build_hitbox(attacker, hitbox_data)
        pygame.draw.rect(self.surface, (0, 255, 255), hitbox, 4)