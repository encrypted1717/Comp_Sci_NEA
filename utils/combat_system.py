import pygame


class CombatSystem:
    def __init__(self):
        # Tracks already-landed hits as (attacker_id, attack_id, defender_id).
        # attack_id increments on each new swing, so the same move can't hit
        # the same defender twice within a single swing.
        self.__hit_registry = set()

        # Per-attack config:
        #   damage_attr – name of the attribute on the attacker that holds damage
        #   hitbox      – maps frame_index → (offset_x, offset_y, width, height)
        #                 offset is relative to the attacker's rect centre.
        #                 Only frames that appear as keys here are "active"
        #                 (able to deal damage), so no separate active_frames needed.
        self.attacks = {
            "punch_1": {
                "damage_attr": "punch_1_damage",
                "hitbox": {
                    2: (10, -40, 50, 40),
                    3: (30, -40, 65, 40),
                    4: (55, -40, 75, 40),
                },
            },
            "jump_strike": {
                "damage_attr": "jump_strike_damage",
                "hitbox": {
                    1: (10, -10, 50, 35),
                    2: (20, -10, 65, 35),
                },
            },
        }

    def update(self, entities):
        """Expire hit-registry entries whose attack swing is no longer active.

        Each active swing is identified by (entity_id, attack_id). When an
        entity stops attacking, its swing disappears from active_swings and
        any recorded hits for it are cleared — allowing future swings to land.
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
        """Apply damage if the attacker's hitbox overlaps the defender, once per swing."""
        attack_data  = self.attacks.get(getattr(attacker, "attack_name", None))
        frame_index  = attacker.animation_manager.get_frame_index()
        hitbox_data  = attack_data["hitbox"].get(frame_index) if attack_data else None
        hit_key      = (attacker.entity_id, attacker.attack_id, defender.entity_id)

        # hitbox_data is None when the current frame isn't an active damage frame,
        # or the attack name isn't registered — either way, nothing to do.
        if attacker is defender or not hitbox_data or hit_key in self.__hit_registry:
            return

        if self.build_hitbox(attacker, hitbox_data).colliderect(defender.sprite_bounds):
            defender.health -= getattr(attacker, attack_data["damage_attr"], 0)
            self.__hit_registry.add(hit_key)

    def build_hitbox(self, attacker, hitbox_data):
        """Return a Rect for the attack hitbox, mirrored horizontally if facing left."""
        offset_x, offset_y, width, height = hitbox_data

        # When facing left, flip the offset so the hitbox extends to the left instead
        if attacker.flip_x:
            offset_x = -offset_x - width

        return pygame.Rect(
            attacker.rect.centerx + offset_x,
            attacker.rect.centery + offset_y,
            width, height,
        )