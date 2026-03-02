import pygame
import logging
from core.window import Window
from core.entity import Entity
from core.config_manager import ConfigManager
from core.button import Button
from core.collision_manager import CollisionManager
from utils.combat_system import CombatSystem
from utils.portal import Portal
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
        self.player1_data = player1  # (user_id, username)
        self.player2_data = player2  # (user_id, username) or None
        self.combat_system = CombatSystem()
        self.last_frame = None
        self.portals = {}  # Maps each entity's unique id (entity.entity_id) to their active Portal instance
        self.__setup_players()
        self.__load_controls()
        self.__setup_groups()
        self.__setup_map()

    def __setup_players(self):
        font = pygame.font.Font(self.fonts["GothicPixel"], 16)
        block_font = pygame.font.Font(self.fonts["GothicPixel"], 8)

        self.player1 = Entity((820,  450), "player1")
        self.health1_label = Button(
            (150, 60),
            (235, 70),
            f"Health: {str(self.player1.health)}",
            font,
            '#000000',
            '#ffffff',
            5,
            border_colour="#000000",
            offset_y=4
        )
        self.energy1 = pygame.Rect(33, 105, 235, 40)
        self.energy1_frame = Button(
            (149, 125),
            (237, 40),
            "",
            block_font,
            '#000000',
            '#ffffff',
            3,
            border_colour="#000000",
            fill=False
        )
        self.block1_label = Button(
            (105, 170),
            (155, 35),
            f"Blocks Remaining: {str(self.player1.blocks_remaining)}",
            block_font,
            '#000000',
            '#ffffff',
            offset_y=4,
            fill=False
        )

        # TODO make health button a percentage meter that reduces as the player loses health
        self.player2 = Entity((1100, 450), "player2")
        self.health2_label = Button(
            (1770, 60),
            (235, 70),
            f"Health: {str(self.player2.health)}",
            font,
            '#000000',
            '#ffffff',
            5,
            border_colour="#000000",
            offset_y=4
        )
        self.energy2 = pygame.Rect(1653, 105, 235, 40)
        self.energy2_frame = Button(
            (1770, 125),
            (235, 40),
            "",
            block_font,
            '#000000',
            '#ffffff',
            5,
            border_colour="#000000",
            fill=False
        )
        self.block2_label = Button(
            (1725, 170),
            (150, 35),
            f"Blocks Remaining: {str(self.player2.blocks_remaining)}",
            block_font,
            '#000000',
            '#ffffff',
            offset_y=4,
            fill=False
        )

    def __setup_groups(self):
        self.colliders = pygame.sprite.Group()
        self.entities = pygame.sprite.Group(self.player1, self.player2)
        self.collision_manager = CollisionManager(self.entities, self.colliders)
        self.buttons.add(
            self.health1_label,
            self.health2_label,
            self.energy1_frame,
            self.energy2_frame,
            self.block1_label,
            self.block2_label

        )

    def __load_controls(self):
        """
        Read saved keybinds from each player's config and apply them to their entity.
        P1 always uses their own [Player1 Controls].
        P2: if logged in, their own [Player1 Controls]; else player1's [Player2 Controls].
        """

        def apply_section(entity, path, section):
            config_manager = ConfigManager(path)
            config = config_manager.get_config()
            for action, raw in config.items(section):
                try:
                    if raw.lower() == "none":
                        entity.set_bind(action.lower(), "none", None)
                        continue
                    parts = [p.strip() for p in raw.split(",", 1)]
                    if len(parts) == 2:
                        device, value = parts[0].lower(), parts[1].strip()
                        code = int(value) if device == "mouse" else pygame.key.key_code(value)
                        entity.set_bind(action.lower(), device, code)
                except Exception:
                    pass

        p1_path = f"assets\\game_settings\\users\\config_{self.player1_data[0]}.ini"
        apply_section(self.player1, p1_path, "Player1 Controls")

        if self.player2_data:
            p2_path = f"assets\\game_settings\\users\\config_{self.player2_data[0]}.ini"
            apply_section(self.player2, p2_path, "Player1 Controls")
        else:
            apply_section(self.player2, p1_path, "Player2 Controls")

    def __setup_map(self):
        self.map = MapGeneration()
        self.map.create_map()
        for tile in self.map.solid_tiles:
            self.colliders.add(tile)

        # Killzone is a death barrier that is slightly larger than the screen
        killzone_padding = 1000
        self.killzone = self.surface.get_rect().inflate(killzone_padding, killzone_padding)

    def reload_controls(self):
        """Re-read keybinds from config and reapply to entities. Called after controls are changed in-game."""
        self.__load_controls()
        self.log.info("Controls reloaded")

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
        self.__process_portals()
        self.__update_attributes()
        self.__draw_energy()
        super().draw(dt)
        self.__process_combat()

        self.last_frame = self.surface.copy()

    def __draw_entities(self):
        # TODO: health should update to 0 if entity falls off map
        for entity in self.entities:
            alive = entity.health > 0 or entity.animation_manager.is_playing()
            if alive and self.killzone.contains(entity.body):
                self.surface.blit(entity.image, entity.img_rect.topleft)
                # Energy charge overlay — drawn on top of the entity's normal frame
                # The sprite sheet contains only the effect, no player, so it stacks cleanly
                if getattr(entity, "energy_charge_overlay", False):
                    overlay_frames = entity.animation_manager.animations.get("energy_charge")
                    if overlay_frames:
                        frame_list, cooldown = overlay_frames
                        # Drive a looping frame index that respects the animation's own cooldown
                        idx = int(pygame.time.get_ticks() / (cooldown * 1000)) % len(frame_list)
                        overlay_img = pygame.transform.flip(frame_list[idx], entity.flip_x, False)
                        self.surface.blit(overlay_img, entity.img_rect.topleft)
                self.__draw_debug(entity) # TODO Turned on via button
            else:
                entity.health = 0
                self.entities.remove(entity)

    def __process_portals(self):
        """Entry point called every draw frame — delegates to focused helper functions."""
        for entity in self.entities:
            self.__handle_portal_spawn(entity)
            self.__handle_portal_warp(entity)
        self.__update_and_draw_portals()

    def __handle_portal_spawn(self, entity):
        """If the entity just pressed the side ability, place a portal at their current position."""
        if not entity.teleport_requested:
            return
        entity.teleport_requested = False
        entity_id = entity.entity_id  # unique integer id for this entity, used as the dict key
        # Close any existing portal for this entity before placing a new one
        if entity_id in self.portals:
            self.portals[entity_id].begin_close()
        # Player 1 gets a blue tint, player 2 gets a red tint
        portal_tint = (100, 100, 255) if entity is self.player1 else (255, 80, 80)
        position = (entity.body.midbottom[0], entity.body.midbottom[1] + 30)
        self.portals[entity_id] = Portal(position, entity.sprite_scale, portal_tint)
        entity.portal_open = True  # tells entity a portal exists so second press triggers return, not open

    def __handle_portal_warp(self, entity):
        """Once teleport_out anim finishes, warp the entity to the portal and begin teleport_in."""
        if entity.teleport_phase != "out" or entity.animation_manager.is_playing():
            return
        entity_id = entity.entity_id
        portal = self.portals.get(entity_id)
        if portal:
            entity.position.x = portal.position[0]
            entity.position.y = portal.position[1]
            entity.body.midbottom = portal.position
            entity.velocity = entity.vector(0, 0)
            portal.begin_close()
        entity.teleport_phase = "in"
        entity.teleport_just_started = True  # tells select_animation to start teleport_in on this frame only
        entity.teleport_return_requested = False
        entity.portal_open = False  # portal is closing, entity can open a new one after this

    def __update_and_draw_portals(self):
        """Tick and render all active portals, removing any that have finished closing."""
        for entity_id in list(self.portals):  # list() so we can safely delete during iteration
            portal = self.portals[entity_id]
            portal.update(self.dt)
            portal.draw(self.surface)
            if portal.done:
                del self.portals[entity_id]
                # Find the entity that owns this portal and clear their portal_open flag
                for entity in self.entities:
                    if entity.entity_id == entity_id:
                        entity.portal_open = False
                        entity.teleport_return_requested = False

    def __draw_energy(self):
        pygame.draw.rect(self.surface, (173, 216, 230), self.energy1)
        pygame.draw.rect(self.surface, (173, 216, 230), self.energy2)
        for activation in range(5):
            x1 = int(33 + activation * 47.4)
            x2 = int(1888 - activation * 47.5)
            pygame.draw.line(self.surface, (0, 0, 0), (x1, 105), (x1, 144), 3)
            pygame.draw.line(self.surface, (0, 0, 0), (x2, 105), (x2, 144), 3)

    def __draw_debug(self, entity):
        # Collision body
        pygame.draw.rect(self.surface, (255, 0, 0), entity.body, 2)
        # Animation-based sprite bounds/hit box
        pygame.draw.rect(self.surface, (0, 255, 0), entity.sprite_bounds, 2)
        # Collider outlines
        for collider in self.colliders:
            pygame.draw.rect(collider.image, pygame.Color("white"), collider.image.get_rect(), 2)

    def __update_attributes(self):
        self.health1_label.update_text(f"Health: {max(self.player1.health, 0)}") # If below 0 then health is 0
        self.health2_label.update_text(f"Health: {max(self.player2.health, 0)}")
        self.energy1.width = int(235 * (self.player1.energy/100))
        self.energy2.width = int(235 * (self.player2.energy/100))
        self.block1_label.update_text(f"Blocks Remaining: {self.player1.blocks_remaining}")
        self.block2_label.update_text(f"Blocks Remaining: {self.player2.blocks_remaining}")

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