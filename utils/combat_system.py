import pygame


class CombatSystem:
    def __init__(self):
        # Tracks "already hit" per (attacker_id, attack_id, defender_id)
        self.__hit_registry = set()

        # Attack definitions (can tweak)
        # active_frames: which animation frame indices can deal damage
        # hitbox: (offset_x, offset_y, w, h) relative to attacker rect center
        self.attacks = {
            "punch_1": {
                "damage_attr": "punch_1_damage",
                "active_frames": {2, 3, 4},
                "hitbox": {
                    2: (20, -40, 50, 40),
                    3: (40, -40, 65, 40),
                    4: (55, -40, 75, 40)
                }
            },
            "jump_strike": {
                "damage_attr": "jump_strike_damage",
                "active_frames": {1, 2},
                "hitbox": {
                    2: (20, -40, 50, 40),
                    3: (40, -40, 65, 40),
                    4: (55, -40, 75, 40)
                }
            }
        }

    def update(self, entities):
        """
        if attacker not attacker, clean set
        """
        active_attack_keys = set()
        for entity in entities:
            if getattr(entity, "attacking", False):
                active_attack_keys.add((entity.entity_id, entity.attack_id))

        # Keep only hits that belong to currently active attacks
        # Equivalent to looping through each key and checking if its its active or not. if not then remove it from hit registry
        self.__hit_registry = {
            key for key in self.__hit_registry
            if (key[0], key[1]) in active_attack_keys
        }

    # TODO Clean code by simplifying the if... returns
    def try_apply_hits(self, attacker, defender):
        if attacker is defender:
            return

        attack_name = getattr(attacker, "attack_name", None)
        if not attack_name or not getattr(attacker, "attacking", False):
            return

        attack_data = self.attacks.get(attack_name)
        if not attack_data:
            return

        frame_index = attacker.animation_manager.get_frame_index()
        if frame_index not in attack_data["active_frames"]:
            return

        # Already hit this defender?
        hit_key = (attacker.entity_id, attacker.attack_id, defender.entity_id)
        if hit_key in self.__hit_registry:
            return

        hitbox_data = attack_data.get("hitbox", {}).get(frame_index)
        if not hitbox_data:
            return

        hitbox = self.build_hitbox(attacker, hitbox_data)

        if hitbox.colliderect(defender.rect):
            damage = getattr(attacker, attack_data["damage_attr"], 0)
            defender.health -= damage
            self.__hit_registry.add(hit_key)

    def build_hitbox(self, attacker, hitbox_data):
        offset_x, offset_y, width, height = hitbox_data

        # Flip hitbox horizontally if facing left
        if attacker.flip_x:
            offset_x = -offset_x - width

        # Anchor everything to the centre of the attacker's rect
        x = attacker.rect.centerx + offset_x
        y = attacker.rect.centery + offset_y
        return pygame.Rect(x, y, width, height)