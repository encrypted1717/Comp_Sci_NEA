import pygame
from core.window import Window
from core.entity import Entity
from core.config_manager import ConfigManager
from core.button import Button
from core.collision_manager import CollisionManager
from utils.combat_system import CombatSystem
from graphics.map_generation import MapGeneration


class Game(Window):
    def __init__(self, display, renderer):
        super().__init__(display, renderer)
        # Main Setup
        self.combat_system = CombatSystem()
        # Setup configurations
        self.config_manager = ConfigManager("assets\\game_settings\\config_user.ini")
        self.config = self.config_manager.get_config()
        # Setup Pause frame
        self.last_frame = None
        # Player1 setup
        self.player1 = Entity((680, 450), "player1")
        self.health1_btn = Button(
            (240, 120),
            (235, 70),
            f"Health: {str(self.player1.health)}",
            pygame.font.Font(self.fonts["GothicPixel"], 16),
            '#000000',
            '#ffffff',
            5,
            border_colour = "#000000",
            offset_y = 4
        )

        # Player2 setup
        self.player2 = Entity((1000, 450), "player2")
        # TODO make health button have a percentage type meter that reduces as the player loses health... do this by making the health button invisible fill and then have another rect beneath it be a still colour and make rect reduce size by percentage of total health
        self.health2_btn = Button(
            (1560, 120),
            (235, 70),
            f"Health: {str(self.player2.health)}",
            pygame.font.Font(self.fonts["GothicPixel"], 16),
            '#000000',
            '#ffffff',
            5,
            border_colour = "#000000",
            offset_y = 4
        )
        # Setup groups
        self.colliders = pygame.sprite.Group()
        self.entities = pygame.sprite.Group(self.player1, self.player2)
        self.buttons.add(self.health1_btn, self.health2_btn)

        self.collision_manager = CollisionManager(self.entities, self.colliders)

        # Map setup
        self.map = MapGeneration()
        self.map.create_map()
        for tile in self.map.solid_tiles:
            self.colliders.add(tile)

    def event_handler(self, events):
        for entity in self.entities:
            entity.event_handler(events)

        for event in events:
            #kb press down
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return "pause", self.last_frame
        return None

    def draw(self, dt):
        self.dt = dt
        self.surface.fill((128, 128, 128))  # White background
        '''pygame.image.load(
            "assets\\images\\background\\parallax_mountain_pack\\layers\\parallax-mountain-trees.png"
        ).convert_alpha()
        self.surface.fill()'''
        # Draw to virtual surface
        self.colliders.draw(self.surface)
        self.entities.update(self.dt)
        self.collision_manager.resolve_entity(self.dt)

        for entity in self.entities:
            if entity.health > 0 or entity.animation_manager.is_playing():
                self.surface.blit(entity.image, entity.img_rect.topleft)
                #pygame.draw.rect(self.surface,(255, 0, 0), entity.rect, 5) # Collision/hit box
            else:
                # TODO update health to
                self.entities.remove(entity)

        self.health1_btn.update_text(f"Health: {self.player1.health if self.player1.health > 0 else 0}")
        self.health2_btn.update_text(f"Health: {self.player2.health if self.player2.health > 0 else 0}")
        super().draw(self.dt)

        for attacker in self.entities:
            if attacker.attacking:
                for defender in self.entities:
                    if attacker is defender:
                        continue
                    self.combat_system.try_apply_hits(attacker, defender)

                '''# Debug: draw attacker hitbox if attacking
                attack_data = self.combat_system.attacks.get(attacker.attack_name)
                frame_index = attacker.animation_manager.get_frame_index()

                # Frame-based hitboxes
                hitbox_data = attack_data.get("hitbox", {}).get(frame_index)
                if not hitbox_data:
                    continue

                hitbox = self.combat_system.build_hitbox(attacker, hitbox_data)
                pygame.draw.rect(self.surface, (0, 255, 0), hitbox, 10)'''

        self.combat_system.update(self.entities)
        self.last_frame = self.surface.copy()