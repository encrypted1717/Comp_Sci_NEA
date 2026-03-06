"""
    AI opponent utilities for game.

    This module provides the CPU class, which simulates a human player by running
    a decision-making loop and feeding its choices into the same input pipeline
    used by human-controlled entities. Behaviour is tuned per difficulty level.
"""

import random
import logging
import pygame
from core.entity import Entity


class CPU(Entity):
    """
        AI-controlled entity that simulates player input using decision-making logic.

        The CPU observes its opponent every `reaction_time` seconds and decides
        on a set of actions (move, jump, attack, block, abilities). Those decisions
        are then translated into a synthetic input dict and fed into the standard
        apply_actions / apply_movement / select_animation pipeline inherited from Entity,
        so the AI behaves identically to a human-controlled entity at the physics level.

        Difficulty settings
        -------------------
        Easy   - slow reactions, low attack / block rates, rarely uses abilities
        Medium - moderate reactions, balanced aggression, occasional special moves
        Hard   - fast reactions, high aggression and block rate, uses abilities often
    """

    def __init__(self,
                 start_position: tuple,
                 sprite_type: str,
                 health: int = 100,
                 difficulty: str = "medium"
                 ):
        """
            Initialise the CPU entity and configure its difficulty settings.

            Calls the parent Entity constructor to set up physics, animation,
            and combat state, then layers AI-specific attributes on top.

            Args:
                start_position: (x, y) pixel coordinates for the entity's spawn point.
                sprite_type: key used to load the correct sprite sheets for this character.
                health: starting health value.
                difficulty: one of "easy", "medium", or "hard". Falls back to "medium" if unrecognised.
        """
        super().__init__(start_position, sprite_type, health)

        self.__log = logging.getLogger(__name__)
        self.__log.info("CPU entity created: difficulty=%s", difficulty)

        # Each difficulty tier defines thresholds and probability weights that control how aggressively and accurately the CPU plays.
        self.difficulty_settings = {
            "easy": {
                "reaction_time": 0.65,  # seconds between decisions
                "attack_chance": 0.30,  # probability of punching when in range
                "block_chance": 0.15,   # probability of blocking when opponent is attacking
                "jump_chance": 0.10,    # random jump probability per decision tick
                "sprint_chance": 0.20,  # probability of sprinting while chasing
                "ability_chance": 0.02, # probability of using an ability per tick
                "attack_range": 160,    # pixels - start attacking below this distance
                "preferred_range": 220, # pixels - move toward opponent beyond this
                "retreat_range": 60,    # pixels - back away below this
            },
            "medium": {
                "reaction_time": 0.35,
                "attack_chance": 0.55,
                "block_chance": 0.35,
                "jump_chance": 0.20,
                "sprint_chance": 0.40,
                "ability_chance": 0.05,
                "attack_range": 150,
                "preferred_range": 170,
                "retreat_range": 55,
            },
            "hard": {
                "reaction_time": 0.12,
                "attack_chance": 0.80,
                "block_chance": 0.60,
                "jump_chance": 0.35,
                "sprint_chance": 0.65,
                "ability_chance": 0.12,
                "attack_range": 155,
                "preferred_range": 150,
                "retreat_range": 50,
            },
        }

        self.difficulty = difficulty
        self.settings = self.difficulty_settings.get(difficulty.lower())

        self._opponent = None
        self._reaction_timer = 0.0    # Accumulates dt each frame until a new decision is due
        self._cached_input = {
            "left":         False,
            "right":        False,
            "jump":         False,
            "down":         False,
            "sprint":       False,
            "punch":        False,
            "block":        False,
            "main_ability": False,
            "side_ability": False,
        }  # Holds the input dict until the next decision changes it

    def set_opponent(self, opponent: Entity) -> None:
        """
            Register the entity the CPU will target.

            Must be called before update_ai, otherwise the CPU will skip all
            decision-making each frame.

            Args:
                opponent: the Entity instance the CPU should track and react to.
        """
        self._opponent = opponent

    def update_ai(self, dt: float) -> None:
        """
            Advance the CPU's AI for one frame.

            This is the drop-in replacement for Entity.event_handler when the
            entity is AI-controlled. It should be called once per frame in place
            of event_handler. The method ticks the reaction timer, fires a new
            decision when the timer expires, then executes that decision through
            the standard Entity action and movement pipeline.

            Args:
                dt: delta time in seconds since the last frame.
        """
        self.acceleration = pygame.math.Vector2(0, 0)  # Reset acceleration so last frame's input doesn't carry over

        # No target registered yet - nothing to react to
        if self._opponent is None:
            return

        # Accumulate time and only re-evaluate decisions once the reaction window has elapsed, simulating human reaction delay rather than updating every single frame.
        self._reaction_timer += dt
        if self._reaction_timer >= self.settings["reaction_time"]:
            self._reaction_timer = 0.0
            self._cached_input = self._make_decision()

        # Run the cached input dict through the same pipeline a human player's keypresses would use.
        self.apply_actions(self._cached_input)
        self.apply_movement(self._cached_input)
        self.select_animation(self._cached_input)

    def event_handler(self, events) -> None:
        """
            Entity.event_handler not needed as it was designed for humans

            Args:
                events: list of pygame events (ignored).
        """
        pass

    def _make_decision(self) -> dict:
        """
            Observe the opponent and build a ready-to-use input dict for this reaction window.

            Reads the opponent's current position and attack state, applies distance-based
            positioning logic and probability rolls, then resolves move intent into left/right
            booleans - all in one pass. The returned dict is cached in self._cached_input
            and reused every frame until the next reaction window fires.

            Returns:
                A dict of input booleans keyed by action name, in the same format
                that apply_actions, apply_movement, and select_animation expect.
        """
        opp = self._opponent
        settings = self.settings

        dx = opp.position.x - self.position.x  # - or + = opponent on left or right of AI
        dist = abs(dx) # Raw distance

        move_toward = move_away = False
        jump = down = sprint = punch = block = main_ability = side_ability = False

        # Chase if the opponent is beyond the preferred engagement range, or retreat if they are uncomfortably close.
        if dist > settings["preferred_range"]:
            move_toward = True
            if random.random() < settings["sprint_chance"]:  # Randomly sprint while closing the gap
                sprint = True
        elif dist < settings["retreat_range"]:
            move_away = True

        # Attack
        if dist <= settings["attack_range"]:
            if random.random() < settings["attack_chance"]:
                punch = True
            # Slide attack: sprint + crouch + punch while very close and on the ground
            if self.on_ground and dist < 90 and random.random() < 0.25:
                sprint = True
                down = True
                punch = True

        # Jump to reach an airborne opponent or as an unpredictable dodge.
        opp_above = (opp.position.y - self.position.y) < -30  # Negative y means opponent is higher on screen
        if opp_above or random.random() < settings["jump_chance"]:
            jump = True

        # Only consider blocking when the opponent is actively in an attack animation.
        if opp.attacking and random.random() < settings["block_chance"]:
            block = True
            punch = False  # Blocking and punching are mutually exclusive

        # Each ability must have enough energy, then apply a probability roll. Side ability is rarer (40% of the base chance).
        if self.energy >= self.main_energy_consumption and random.random() < settings["ability_chance"]:
            main_ability = True
        if self.energy >= self.side_energy_consumption and random.random() < settings["ability_chance"] * 0.4:
            side_ability = True

        # Resolve direction
        left = right = False
        if move_toward:
            right, left = (True, False) if dx > 0 else (False, True)
        elif move_away:
            right, left = (False, True) if dx > 0 else (True, False)

        return {
            "left":         left,
            "right":        right,
            "jump":         jump,
            "down":         down,
            "sprint":       sprint,
            "punch":        punch,
            "block":        block,
            "main_ability": main_ability,
            "side_ability": side_ability,
        }