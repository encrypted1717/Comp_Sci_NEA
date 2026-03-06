"""
    Combat resolution system for the game.

    This module provides the CombatSystem class, which handles hitbox construction,
    hit detection, damage application, and block logic between entities each frame.
    A hit registry prevents the same swing from landing on the same defender more
    than once, and is automatically cleared when a swing ends.
"""

import pygame


class CombatSystem:
    """
    Stateful combat resolver shared across all entities in a round.

    Owns the hit registry and the per-attack hitbox and damage configuration.
    game.py calls update() once per frame to expire stale registry entries,
    then calls try_apply_hits() for each attacker-defender pair.
    """
    def __init__(self):
        """Initialise the hit registry and define all attack hitbox configurations."""
        # Tracks already-landed hits as (attacker_id, attack_id, defender_id).
        self.__hit_registry = set()

        # Per-attack config:
        #   damage_attr - name of the attribute on the attacker that holds damage
        #   hitbox - (offset_x, offset_y, width, height), offset is relative to the attacker's rect centre.
        self.attacks = {
            "punch_1": {
                "damage_attr": "punch_1_damage",
                "hitbox": {
                    2: (0, -40, 50, 50),
                    3: (20, -40, 45, 50),
                    4: (20, -40, 45, 50),
                },
            },
            "punch_2": {
                "damage_attr": "punch_2_damage",
                "hitbox": {
                    0: (0, -40, 50, 50),
                    1: (15, -40, 75, 50),
                    2: (20, -40, 75, 50),
                }
            },
            "jump_strike": {
                "damage_attr": "jump_strike_damage",
                "hitbox": {
                    0: (0, -5, 35, 40),
                    1: (10, -5, 50, 45),
                    2: (20, -5, 65, 50)
                },
            },
            "energy_punch": {
                "damage_attr": "energy_punch_damage",
                "hitbox": {
                    3: (10, -35, 70, 60),
                    4: (20, -45, 90, 85),
                    5: (25, -55, 120, 115),
                    6: (30, -65, 140, 135),
                    7: (55, -75, 150, 145),
                },
            },
            "slide_attack": {
                "damage_attr": "slide_attack_damage",
                # Hitbox sits low (near feet) and extends forward - adjust frame indices
                "hitbox": {
                    2: (-10, 0, 65, 50),
                    3: (-20, 0, 95, 50),
                    4: (-20, 0, 115, 50),
                    5: (-20, 0, 130, 50),
                },
            },
        }

    def update(self, entities):
        """
        Expire hit-registry entries whose attack swing is no longer active.

        Each active swing is identified by (entity_id, attack_id). When an
        entity stops attacking, its swing disappears from active_swings and
        any recorded hits for it are cleared, allowing future swings to land.

        Args:
            entities: all active entity instances in the current round.
        """
        active_swings = {
            (e.entity_id, e.attack_id)
            for e in entities
            if getattr(e, "attacking", False)
        }
        self.__hit_registry = {
            key for key in self.__hit_registry
            if (key[0], key[1]) in active_swings
        }

    def try_apply_hits(self, attacker, defender):
        """
        Apply damage if the attacker's hitbox overlaps the defender, once per swing.

        Checks whether the current animation frame is an active damage frame for
        the attacker's current attack. If the hitbox collides with the defender and
        the hit hasn't already been registered this swing, applies damage or consumes
        a block, then handles any launch effects for special attacks.

        Args:
            attacker: the entity currently performing an attack.
            defender: the entity to test collision against.
        """
        attack_data = self.attacks.get(getattr(attacker, "attack_name", None))
        frame_index = attacker.animation_manager.get_frame_index()
        hitbox_data = attack_data["hitbox"].get(frame_index) if attack_data else None
        hit_key = (attacker.entity_id, attacker.attack_id, defender.entity_id)

        # hitbox_data is None when the current frame isn't an active damage frame, or the attack name isn't registered — either way, nothing to do.
        if attacker is defender or not hitbox_data or hit_key in self.__hit_registry:
            return

        if self.build_hitbox(attacker, hitbox_data).colliderect(defender.sprite_bounds):
            if defender.is_blocking and defender.blocks_remaining > 0:
                # Block absorbs the hit - consume one block and reset the regen timer
                defender.blocks_remaining -= 1
                defender.block_regen_timer = 0.0
            else:
                # Either not blocking, or block is broken - take full damage and trigger hurt
                damage = getattr(attacker, attack_data["damage_attr"], 0)
                attacker.energy += 10
                defender.take_hit(damage)
            # Slide attack launches defender straight up regardless of block
            if attacker.attack_name == "slide_attack":
                defender.velocity.y = -defender.jump_force * 1.5
                defender.on_ground = False
            # Energy punch launches defender diagonally backwards and upward, ignores block
            elif attacker.attack_name == "energy_punch":
                direction = -1 if attacker.flip_x else 1
                defender.velocity.x = direction * 3000
                defender.velocity.y = -900
                defender.on_ground = False
            self.__hit_registry.add(hit_key)

    def build_hitbox(self, attacker, hitbox_data):
        """
        Return a Rect for the attack hitbox, mirrored horizontally if facing left.

        The offset is relative to the attacker's rect centre. When the attacker
        is facing left (flip_x is True), the x offset is negated and shifted by
        the hitbox width so it extends in the correct direction.

        Args:
            attacker:    the entity performing the attack.
            hitbox_data: (offset_x, offset_y, width, height) for the current frame.

        Returns:
            A pygame.Rect representing the active hitbox in world coordinates.
        """
        offset_x, offset_y, width, height = hitbox_data

        # When facing left, flip the offset so the hitbox extends to the left instead
        if attacker.flip_x:
            offset_x = -offset_x - width

        return pygame.Rect(
            attacker.rect.centerx + offset_x,
            attacker.rect.centery + offset_y,
            width, height,
        )