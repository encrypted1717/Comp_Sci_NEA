"""
    Main game window for game.

    This module provides the Game class, which owns a single match between two
    players. It manages the round lifecycle (countdown, combat, round-end, reset),
    entity updates, collision, combat, portal teleportation, HUD rendering, and
    debug visualisation. Game is created fresh for each match by WindowManager.
"""

import pygame
from core import Window, Entity, CPU, ConfigManager, Button, CollisionManager
from utils import CombatSystem, Portal
from graphics import MapGeneration


class Game(Window):
    """
        Active match window that runs the full game loop for one best-of-3 series.

        Inherits from Window for display surface, renderer, button group, and font
        access. Manages two entities (human or CPU), a map, a collision manager,
        a combat system, and all associated HUD labels. Each round resets entities
        and the map while preserving win counts across resets.
    """

    def __init__(self, display, renderer, player1, player2, cpu_difficulty=None):
        """
            Initialise the game window and set up the first round.

            Reads player 1's debug config, creates all HUD labels, then delegates
            to setup helpers for players, controls, sprite groups, and the map.

            Args:
                display: the pygame Surface to render onto.
                renderer: the VirtualRenderer instance shared across all windows.
                player1: (user_id, username) tuple for the logged-in player 1.
                player2: (user_id, username) tuple for player 2, or None if CPU mode.
                cpu_difficulty: None for PvP, or "easy"/"medium"/"hard" for PvCPU.
        """
        super().__init__(display, renderer)

        # Config
        self.config_manager = ConfigManager("assets\\game_settings\\config_user.ini")
        self.config = self.config_manager.get_config()

        # Spawn positions - stored so __reset_round can recreate entities in the same spots
        self.p1_pos = (820,  450)
        self.p2_pos = (1100, 450)

        self.player1_data = player1         # (user_id, username) - used to load config and display names
        self.player2_data = player2         # (user_id, username) or None in CPU mode
        self.cpu_difficulty = cpu_difficulty  # None means PvP; string means PvCPU

        # Round tracking
        self.round = 1
        self.round_label = Button(
            (self.center_x, 70),
            (235, 70),
            f"Round {self.round}",
            pygame.font.Font(self.fonts["GothicPixel"], 16),
            '#000000', '#ffffff', 5,
            border_colour="#000000", offset_y=4
        )
        self.player1_wins = 0
        self.player2_wins = 0
        self.elapsed_time = 0
        self.round_over = False
        self.round_over_timer = 0.0
        self.round_over_delay = 2.5   # seconds to show round result before resetting or going to victory
        self.round_result_text = None  # e.g. "Player 1 - Alice  Wins!" - shown during post-round delay
        self.pending_action = None  # set during draw(), consumed by event_handler() next frame

        # Countdown - runs at the start of every round before input is unlocked.
        # Each entry is (duration_seconds, display_label).
        self.countdown_sequence = [(1.0, "3"), (1.0, "2"), (1.0, "1"), (0.75, "FIGHT!")]
        self.countdown_index = 0
        self.countdown_timer = 0.0
        self.countdown_active = True  # cleared once the full sequence finishes

        # Read player 1's debug toggle - reloaded each time Game is created so config changes are picked up
        player1_config = ConfigManager(f"assets\\game_settings\\users\\config_{player1[0]}.ini").get_config()
        self.debugging = player1_config.get("Game", "Debugging", fallback="Off").strip().lower() == "on"

        self.combat_system = CombatSystem()
        self.last_frame = None  # frozen copy of the previous frame, passed to PauseMenu as its backdrop
        self.portals = {}    # maps entity.entity_id to its active Portal instance
        self.dt = 0

        self.__setup_players()
        self.__load_controls()
        self.__setup_groups()
        self.__setup_map()

    def event_handler(self, events):
        """
            Process input and return a navigation action if one is pending.

            Pending actions (victory, round reset) are set during draw() and consumed
            here on the following frame to keep draw and logic separated. Input is
            frozen during the countdown and during the post-round delay.

            Args:
                events: list of mapped pygame events for this frame.

            Returns:
                A navigation tuple (e.g. ("pause", frame) or ("victory", data)),
                or None if no navigation is needed.
        """
        # Consume any action that was queued during the previous draw() call
        if self.pending_action:
            action = self.pending_action
            self.pending_action = None
            return action

        # Freeze all entity input during countdown and after a round ends
        if not self.round_over and not self.countdown_active:
            for entity in self.entities:
                if isinstance(entity, CPU):
                    entity.update_ai(self.dt)  # CPU drives itself using last frame's dt
                else:
                    entity.event_handler(events)

        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return "pause", self.last_frame  # last_frame is the backdrop shown behind the pause menu
        return None

    def draw(self, dt):
        """
            Render one frame of the game and advance all simulation state.

            Order matters: update physics first, then resolve combat on the same
            frame's animation index, then resolve collisions, then remove dead
            entities before drawing or checking round end.

            Args:
                dt: delta time in seconds since the last frame.
        """
        self.dt = dt  # stored so event_handler can pass it to CPU.update_ai on the same frame

        # Accumulate match time only while combat is live (not during countdown or post-round delay)
        if not self.countdown_active and not self.round_over:
            self.elapsed_time += dt

        self.surface.fill((128, 128, 128))

        self.colliders.draw(self.surface)
        self.entities.update(dt)
        self.__process_combat() # must run after update() so frame index matches animation just set
        self.collision_manager.resolve_entity(dt)

        self.__remove_dead_entities()
        self.__draw_entities()
        self.__check_round_end()

        # Once round_over is set, wait for round_over_delay seconds before acting
        if self.round_over:
            self.round_over_timer += dt
            if self.round_over_timer >= self.round_over_delay:
                p1_name = self.player1_data[1]
                p2_name = self.player2_data[1] if self.player2_data else "CPU"
                print(f"DEBUG victory: player1_data={self.player1_data}, p1_name={repr(p1_name)}")  # add this
                if self.player1_wins >= 2:
                    # Include elapsed_time only for CPU wins so the leaderboard can record it
                    elapsed = round(self.elapsed_time, 2) if self.cpu_difficulty else None
                    self.pending_action = ("victory", ("Player 1", p1_name, elapsed))
                elif self.player2_wins >= 2:
                    self.pending_action = ("victory", ("Player 2", p2_name, None))
                else:
                    self.__reset_round()

        self.__process_portals()
        self.__update_attributes()
        self.__draw_energy()
        self.__tick_countdown(dt)
        self.__draw_overlay()
        super().draw(dt)  # draws self.buttons (HUD labels) on top of everything

        self.last_frame = self.surface.copy()  # snapshot used as pause menu backdrop next

    def __setup_players(self):
        """
            Create player entities and all associated HUD Button labels.

            Uses shared kwargs dicts to avoid repeating common Button arguments.
            Player 2 is a CPU entity when cpu_difficulty is set, otherwise a
            standard human Entity. Called on init and again by __reset_round.
        """
        health_font = pygame.font.Font(self.fonts["GothicPixel"], 16)
        general_font = pygame.font.Font(self.fonts["GothicPixel"], 8)
        wins_font = pygame.font.Font(self.fonts["GothicPixel"], 16)

        # Shared kwargs for each label style - avoids repeating common args on every Button call
        health_kwargs = {
            "font": health_font, "text_colour": '#000000', "rect_colour": '#ffffff',
            "border": 5, "border_colour": "#000000", "offset_y": 4
        }
        energy_kwargs = {
            "text": "", "font": general_font, "text_colour": '#000000',
            "rect_colour": '#ffffff', "border": 3, "border_colour": "#000000", "fill": False
        }
        block_kwargs = {
            "font": general_font, "text_colour": '#000000',
            "rect_colour": '#ffffff', "offset_y": 4, "fill": False
        }
        wins_kwargs = {
            "font": wins_font, "text_colour": '#000000', "rect_colour": '#ffffff',
            "border": 5, "border_colour": "#000000", "offset_y": 4
        }

        # Player 1
        self.player1 = Entity(self.p1_pos, "player1")
        self.health1_label = Button(
            (150, 60),
            (235, 70),
            f"Health: {self.player1.health}",
            **health_kwargs
        )
        self.energy1 = pygame.Rect(33, 105, 235, 40)  # filled rect whose width scales with energy
        self.energy1_frame = Button(
            (149, 125),
            (235, 40),
            **energy_kwargs
        )
        self.block1_label  = Button(
            (105, 170),
            (155, 35),
            f"Blocks Remaining: {self.player1.blocks_remaining}",
            **block_kwargs
        )
        self.p1_wins_label = Button(
            (400, 60),
            (235, 70),
            str(self.player1_wins),
            **wins_kwargs
        )

        # Player 2
        if self.cpu_difficulty:
            self.player2 = CPU(self.p2_pos, "player2", difficulty=self.cpu_difficulty)
            self.player2.set_opponent(self.player1)  # CPU needs a target to make decisions against
        else:
            self.player2 = Entity(self.p2_pos, "player2")

        self.health2_label = Button(
            (1770, 60),
            (235, 70),
            f"Health: {self.player2.health}",
            **health_kwargs
        )
        self.energy2 = pygame.Rect(1653, 105, 235, 40)
        self.energy2_frame = Button(
            (1770, 125),
            (235, 40),
            **energy_kwargs
        )
        self.block2_label = Button(
            (1725, 170),
            (150, 35),
            f"Blocks Remaining: {self.player2.blocks_remaining}",
            **block_kwargs
        )
        self.p2_wins_label = Button(
            (1520, 60),
            (235, 70),
            str(self.player2_wins),
            **wins_kwargs
        )

    def __setup_groups(self):
        """
            Create sprite groups for entities and colliders, and register all HUD buttons.

            Called on init and again by __reset_round after players are recreated.
        """
        self.colliders = pygame.sprite.Group()
        self.entities  = pygame.sprite.Group(self.player1, self.player2)
        self.collision_manager = CollisionManager(self.entities, self.colliders)
        self.buttons.add(
            self.round_label,
            self.p1_wins_label,
            self.p2_wins_label,
            self.health1_label,
            self.health2_label,
            self.energy1_frame,
            self.energy2_frame,
            self.block1_label,
            self.block2_label,
        )

    def __load_controls(self):
        """
            Read saved keybinds from each player's config file and apply them to their entity.

            Player 1 always reads from their own [Player1 Controls] section.
            Player 2: if logged in, reads from their own [Player2 Controls]; otherwise reads
            from player 1's config under [Player2 Controls]. CPU entities are skipped entirely.
        """
        def apply_section(entity, path, section):
            """Parse a config section and call entity.set_bind for each valid entry."""
            config = ConfigManager(path).get_config()
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
                except ValueError:
                    self.log.warning("Skipping malformed bind for action '%s': %s", action, raw)  # silently skip malformed or unrecognised binds

        p1_path = f"assets\\game_settings\\users\\config_{self.player1_data[0]}.ini"
        apply_section(self.player1, p1_path, "Player1 Controls")

        if not self.cpu_difficulty:  # CPU has no keybinds to load
            if self.player2_data:
                p2_path = f"assets\\game_settings\\users\\config_{self.player2_data[0]}.ini"
                apply_section(self.player2, p2_path, "Player2 Controls")
            else:
                apply_section(self.player2, p1_path, "Player2 Controls")

    def __setup_map(self):
        """
            Generate a random map, add its colliders to the group, and define the killzone.

            The killzone is a rect slightly larger than the screen. Any entity whose
            body leaves it is considered fallen and is removed from play.
        """
        self.map = MapGeneration()
        self.map.create_map()
        for tile in self.map.solid_tiles:
            self.colliders.add(tile)

        killzone_padding = 2000  # pixels beyond the screen edge before an entity is culled
        self.killzone = self.surface.get_rect().inflate(killzone_padding, killzone_padding)

    def reload_controls(self):
        """Re-read keybinds from config and reapply to entities. Called after controls are changed in-game."""
        self.__load_controls()
        self.log.info("Controls reloaded")

    def reload_settings(self):
        """Re-read game settings from player 1's config. Called after settings are changed in-game."""
        player1_config = ConfigManager(f"assets\\game_settings\\users\\config_{self.player1_data[0]}.ini").get_config()
        self.debugging = player1_config.get("Game", "Debugging", fallback="Off").strip().lower() == "on"
        self.log.info("Game settings reloaded - debugging=%s", self.debugging)

    def __check_round_end(self):
        """
            Award a round win if one or both entities have been removed, then start the over-delay.

            Only fires once per round - the early return guards against double-triggering.
            Called each frame after __remove_dead_entities so entity count is current.
        """
        if self.round_over or len(self.entities) == 2:
            return  # round still in progress, or already handled

        self.round_over = True
        self.round_over_timer = 0.0

        p1_alive = self.player1 in self.entities
        p2_alive = self.player2 in self.entities
        p2_label = "CPU" if self.cpu_difficulty else "Player 2"

        if p1_alive and not p2_alive:
            self.player1_wins += 1
            self.round_result_text = f"Player 1 - {self.player1_data[1]}  Wins!"
        elif p2_alive and not p1_alive:
            self.player2_wins += 1
            p2_name = self.player2_data[1] if self.player2_data else p2_label
            self.round_result_text = f"{p2_label} - {p2_name} Wins!" if p2_name != "CPU" else f"{p2_name} Wins!"
        else:
            self.round_result_text = "Draw!"

    def __reset_round(self):
        """
            Tear down the current round and start the next one, preserving win counts.

            Clears all portals, empties the button group, then rebuilds players,
            controls, sprite groups, and the map from scratch.
        """
        self.round += 1
        self.round_over = False
        self.round_over_timer = 0.0
        self.round_result_text = None
        self.elapsed_time = 0  # reset for next round so time reflects the full match fresh
        self.countdown_index = 0
        self.countdown_timer = 0.0
        self.countdown_active = True
        self.portals.clear()
        self.buttons.empty()  # cleared so __setup_groups can re-add fresh label instances
        self.__setup_players()
        self.__load_controls()
        self.__setup_groups()
        self.__setup_map()
        self.round_label.update_text(f"Round {self.round}")
        self.p1_wins_label.update_text(f"Wins: {self.player1_wins}")
        self.p2_wins_label.update_text(f"Wins: {self.player2_wins}")

    def __tick_countdown(self, dt):
        """
            Advance the countdown timer and move to the next step when due.

            Clears countdown_active once all steps have elapsed, which unlocks
            entity input in event_handler for the rest of the round.

            Args:
                dt: delta time in seconds since the last frame.
        """
        if not self.countdown_active:
            return
        self.countdown_timer += dt
        duration = self.countdown_sequence[self.countdown_index][0]
        if self.countdown_timer >= duration:
            self.countdown_timer = 0.0
            self.countdown_index += 1
            if self.countdown_index >= len(self.countdown_sequence):
                self.countdown_active = False
                self.countdown_index = 0  # reset so it is safe to index into the sequence again

    def __draw_overlay(self):
        """
            Render the countdown number or round-result text centered on screen with a drop shadow.

            Button was considered here but does not support drop shadows, which are
            the main visual feature of the countdown display. Raw font rendering is
            kept intentionally.
        """
        text  = None
        large = True

        if self.countdown_active:
            label = self.countdown_sequence[self.countdown_index][1]
            text = label
            large = (label != "FIGHT!")  # numbers use the large font; "FIGHT!" uses small
        elif self.round_over and self.round_result_text:
            text = self.round_result_text
            large = False

        if not text:
            return

        # Overlay fonts - created once and reused for both countdown and round-result text.
        font_large = pygame.font.Font(self.fonts["GothicPixel"], 32)  # "3", "2", "1"
        font_small = pygame.font.Font(self.fonts["GothicPixel"], 32)  # "FIGHT!" and results
        font = font_large if large else font_small

        # Shadow
        shadow = font.render(text, True, (0, 0, 0))
        shadow_rect = shadow.get_rect(center=(self.center_x + 4, self.center_y + 4))
        self.surface.blit(shadow, shadow_rect)

        # Main text pass
        surf = font.render(text, True, (255, 255, 255))
        rect = surf.get_rect(center=(self.center_x, self.center_y))
        self.surface.blit(surf, rect)

    def __draw_entities(self):
        """
            Blit each living entity's current frame, plus any active overlay effects and debug visuals.

            Only called after __remove_dead_entities, so every entity in self.entities
            is guaranteed to be alive and inside the killzone at this point.
        """
        for entity in self.entities:
            self.surface.blit(entity.image, entity.img_rect.topleft)

            # Energy charge overlay - a separate sprite sheet drawn on top of the entity's frame.
            if getattr(entity, "energy_charge_overlay", False):
                overlay_frames = entity.animation_manager.animations.get("energy_charge")
                if overlay_frames:
                    frame_list, cooldown = overlay_frames
                    # Time-based frame index so the overlay loops independently while the main animation changes
                    idx = int(pygame.time.get_ticks() / (cooldown * 1000)) % len(frame_list)
                    overlay_img = pygame.transform.flip(frame_list[idx], entity.flip_x, False)
                    self.surface.blit(overlay_img, entity.img_rect.topleft)

            if self.debugging:
                self.__draw_debug(entity)

    def __draw_energy(self):
        """
            Draw both energy bars and their five segment dividers.

            Each bar is a plain rect whose width is scaled by __update_attributes to
            reflect the entity's current energy. Dividers are vertical lines drawn on
            top at even intervals, splitting each bar into activation segments.
        """
        pygame.draw.rect(self.surface, (173, 216, 230), self.energy1)
        pygame.draw.rect(self.surface, (173, 216, 230), self.energy2)
        for i in range(5):  # 5 dividers create 5 equal energy segments
            x1 = int(33 + i * 47.4)
            x2 = int(1888 - i * 47.5)
            pygame.draw.line(self.surface, (0, 0, 0), (x1, 105), (x1, 144), 3)
            pygame.draw.line(self.surface, (0, 0, 0), (x2, 105), (x2, 144), 3)

    def __draw_debug(self, entity):
        """
            Draw debug visualisations for a single entity.

            Renders the physics body (red), animation-based sprite bounds (green),
            and outlines every collider in the scene (white).

            Args:
                entity: the Entity whose debug rects should be drawn.
        """
        pygame.draw.rect(self.surface, (255, 0, 0), entity.body, 2)           # physics collision body
        pygame.draw.rect(self.surface, (0, 255, 0), entity.sprite_bounds, 2)  # animation bounding hitbox
        for collider in self.colliders:
            pygame.draw.rect(collider.image, pygame.Color("white"), collider.image.get_rect(), 2)

    def __remove_dead_entities(self):
        """
            Remove entities that are dead and finished animating, or have left the killzone.

            Iterates a copy of the group so removal during iteration is safe.
            Health is clamped to 0 on removal so HUD labels never show negative values.
        """
        for entity in list(self.entities):
            alive = entity.health > 0 or entity.animation_manager.is_playing()
            if not alive or not self.killzone.contains(entity.body):
                entity.health = 0
                self.entities.remove(entity)

    def __process_combat(self):
        """
            Check all attacking entities against all others and apply any valid hits.

            Must be called immediately after entities.update() so the animation frame
            index used for hitbox lookups matches the frame that was just set.
        """
        for attacker in self.entities:
            if not attacker.attacking:
                continue
            for defender in self.entities:
                if attacker is not defender:
                    self.combat_system.try_apply_hits(attacker, defender)
            if self.debugging:
                self.__draw_attack_hitbox(attacker)

        self.combat_system.update(self.entities)  # tick hit-stun timers and clear expired hits

    def __draw_attack_hitbox(self, attacker):
        """
            Debug: draw the active hitbox rect for an attacking entity in cyan.

            Args:
                attacker: the Entity whose current attack hitbox should be visualised.
        """
        attack_data = self.combat_system.attacks.get(attacker.attack_name)
        if not attack_data:
            return
        frame_index = attacker.animation_manager.get_frame_index()
        hitbox_data = attack_data.get("hitbox", {}).get(frame_index)
        if not hitbox_data:
            return
        hitbox = self.combat_system.build_hitbox(attacker, hitbox_data)
        pygame.draw.rect(self.surface, (0, 255, 255), hitbox, 4)

    def __update_attributes(self):
        """
            Sync all HUD label text and energy bar widths to the current entity state.

            Called once per frame after combat and entity updates so values are always
            current. Health is clamped to 0 so labels never display negative numbers.
        """
        self.health1_label.update_text(f"Health: {max(self.player1.health, 0)}")
        self.health2_label.update_text(f"Health: {max(self.player2.health, 0)}")
        self.energy1.width = int(235 * (self.player1.energy / 100))  # scale bar width to 0-235px
        self.energy2.width = int(235 * (self.player2.energy / 100))
        self.block1_label.update_text(f"Blocks Remaining: {self.player1.blocks_remaining}")
        self.block2_label.update_text(f"Blocks Remaining: {self.player2.blocks_remaining}")

    def __process_portals(self):
        """
            Drive the full portal lifecycle for this frame.

            Checks each entity for a spawn or warp request, then ticks and draws
            all active portals, removing any that have finished closing.
        """
        for entity in self.entities:
            self.__handle_portal_spawn(entity)
            self.__handle_portal_warp(entity)
        self.__update_and_draw_portals()

    def __handle_portal_spawn(self, entity):
        """
            If the entity just requested a portal, place one at their current position.

            Closes any existing portal for this entity before placing the new one.
            Player 1 gets a blue tint; player 2 gets a red tint.

            Args:
                entity: the Entity to check and potentially spawn a portal for.
        """
        if not entity.teleport_requested:
            return
        entity.teleport_requested = False
        entity_id = entity.entity_id
        if entity_id in self.portals:
            self.portals[entity_id].begin_close()  # close old portal before replacing it
        portal_tint = (100, 100, 255) if entity is self.player1 else (255, 80, 80)
        self.portals[entity_id] = Portal(entity.body.midbottom, entity.sprite_scale, portal_tint)
        entity.portal_open = True  # second ability press will now trigger a return warp, not a new portal

    def __handle_portal_warp(self, entity):
        """
            Once the teleport_out animation finishes, warp the entity to the portal.

            Delegates all entity state changes to entity.teleport_to() so this
            method only needs to close the portal and call one method.

            Args:
                entity: the Entity to check for a completed teleport_out animation.
        """
        if entity.teleport_phase != "out" or entity.animation_manager.is_playing():
            return
        portal = self.portals.get(entity.entity_id)
        if portal:
            portal.begin_close()
            entity.teleport_to(portal.position)  # entity owns all its own state transitions

    def __update_and_draw_portals(self):
        """
            Tick and render all active portals, removing finished ones and clearing entity flags.

            Iterates a copy of the dict so entries can be safely deleted mid-loop.
        """
        for entity_id in list(self.portals):
            portal = self.portals[entity_id]
            portal.update(self.dt)
            portal.draw(self.surface)
            if portal.done:
                del self.portals[entity_id]
                # Clear portal_open on the owning entity so they can place a new one
                for entity in self.entities:
                    if entity.entity_id == entity_id:
                        entity.portal_open = False
                        entity.teleport_return_requested = False

    def on_escape(self):
        return None

    def show_back_button(self):
        return False