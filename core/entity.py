import logging
import pygame
from graphics.animation_manager import AnimationManager


# TODO add more animations
# TODO support different times of punches/combos using delays/elapsed time between clicks
# TODO fix bug: sprinting anim continues after releasing movement key before removing sprint key
# TODO Add functions for energy
class Entity(pygame.sprite.Sprite):
    def __init__(self, start_position: tuple, sprite_type: str, health=100):
        super().__init__()

        # Logging Setup
        self.__log = logging.getLogger(__name__)
        self.__log.info("Creating an entity: sprite_type = %s pos = %s", sprite_type, start_position)

        # Main Setup
        self.vector = pygame.math.Vector2
        self.sprite = sprite_type
        self.dt = None
        self.flip_x = False

        # Sprite Attributes
        self.entity_id = id(self)
        self.health = health
        self.energy = 0

        # Sprite Creation
        self.sprite_scale = 1.2
        self.frame_size = (int(128 * self.sprite_scale), int(128 * self.sprite_scale))
        body_w, body_h = int(36 * self.sprite_scale), int(72 * self.sprite_scale)
        self.body = pygame.Rect(0, 0, body_w, body_h)  # Collision Box
        self.position = self.vector(start_position)
        self.body.midbottom = (int(self.position.x), int(self.position.y))  # Position anchor is MIDBOTTOM (feet)
        self.rect = self.body
        self.image = pygame.Surface(self.frame_size, pygame.SRCALPHA)
        self.img_rect = self.image.get_rect(midbottom=self.body.midbottom)
        self.sprite_bounds = self.image.get_bounding_rect().move(self.img_rect.topleft)  # Dynamic Hitbox based on animation

        # Physics
        self.velocity = self.vector(0, 0)
        self.acceleration = self.vector(0, 0)
        self.horizontal_acceleration = 2250.0
        self.horizontal_friction = 11
        self.sprint_force = 1500
        self.jump_force = 650
        self.double_jump_force = 450
        self.down_force = 1500
        self.gravity = 1250
        self.on_ground = False
        self.jumps_remaining = 2
        self.air_time = 0.0
        self.double_jump_delay = 0.01

        # Combat
        self.punch_1_damage = 6
        self.jump_strike_damage = 0
        self.attacking = False
        self.attack_name = None
        self.attack_id = 0
        self.combos = 0

        # Input
        self.keys = None
        self.binds = self._default_binds()

        # Animations
        # TODO update system so the scale can be updated and doesnt need to be stated at every load of animation
        self.animation_manager = AnimationManager()
        self._load_animations()

        # Priority levels — a playing animation can only be interrupted by something strictly higher.
        #   0  idle / movement   (walk, sprint, default, stop_sprint)
        #   1  airborne          (jump, double_jump)
        #   2  committed actions (crouch, charging, attacks, death)
        self.animation_priority = {
            "default": 0,
            "walk": 0,
            "sprint": 1,
            "stop_sprint": 2,
            "jump": 2,
            "double_jump": 2,
            "crouch": 3,
            "activate": 3,
            "punch_1": 3,
            "jump_strike": 3,
            "death": 4,
        }
        self.animation_manager.set_animation("default")
        self.__log.info("Entity created: id = %s sprite_type = %s", id(self), sprite_type)

    def _default_binds(self) -> dict:
        if self.sprite == "player1":
            return {
                "left": ("key", pygame.K_a),
                "right": ("key", pygame.K_d),
                "jump": ("key", pygame.K_w),
                "down": ("key", pygame.K_s),
                "sprint": ("key", pygame.K_LSHIFT),
                "punch": ("key", pygame.K_SPACE),  # ("mouse", 1) left click
                "activate": ("key", pygame.K_e),
            }
        elif self.sprite == "player2":
            return {
                "left": ("key", pygame.K_LEFT),
                "right": ("key", pygame.K_RIGHT),
                "jump": ("key", pygame.K_UP),
                "down": ("key", pygame.K_DOWN),
                "sprint": ("key", pygame.K_RSHIFT),
                "punch": ("key", pygame.K_RETURN),
                "activate": ("key", pygame.K_KP0),
            }
        return {}

    def _load_animations(self) -> None:
        load = self.animation_manager.load_animation
        address_fight = "assets\\characters\\default\\fighting\\Animations\\"
        address_move = "assets\\characters\\default\\movement\\Animations\\"
        address_other = "assets\\characters\\default\\other\\Animations\\"

        load("default", address_fight + "punch_1.png", scale=self.sprite_scale, frame_indices=[0])
        load("punch_1", address_fight + "punch_1.png", scale=self.sprite_scale, cooldown=0.035)
        load("activate", address_fight + "skill_charging.png", scale=self.sprite_scale, cooldown=0.12)  # Make this a skill activation not a charging anim
        load("jump", address_move + "upward_jump.png", scale=self.sprite_scale, frame_indices=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 3, 2, 1, 0], cooldown=0.04)
        load("double_jump", address_move + "double_jump.png", scale=self.sprite_scale, cooldown=0.04)
        load("walk", address_move + "walking.png", scale=self.sprite_scale)
        load("sprint", address_move + "running.png", scale=self.sprite_scale)
        load("stop_sprint", address_move + "stop_running.png", scale=self.sprite_scale)
        load("crouch", address_move + "crouch.png", scale=self.sprite_scale, cooldown=0.035)
        load("jump_strike", address_move + "jump_strike.png", scale=self.sprite_scale)
        load("death", address_other + "death.png", scale=self.sprite_scale)

    def update(self, dt):
        self.dt = dt
        self.air_time = 0.0 if self.on_ground else self.air_time + dt

        # Physics Update
        self.velocity.y += self.gravity * dt
        self.acceleration.x -= self.velocity.x * self.horizontal_friction
        self.velocity += self.acceleration * dt
        self.position += self.velocity * dt + 0.5 * self.acceleration * (dt ** 2)

        # Update Body
        self.body.midbottom = (int(self.position.x), int(self.position.y))
        self.rect = self.body

        # Update Animation
        self.animation_manager.update(dt)
        self.image = pygame.transform.flip(self.animation_manager.get_frame(), self.flip_x, False)
        self.sync_img_rect_to_body()

        # Clear attack state once animation finishes
        if self.attacking and not self.animation_manager.is_playing():
            self.attacking = False
            self.attack_name = None

    def event_handler(self, events):
        self.acceleration = self.vector(0, 0)

        if self.health > 0:
            inp = self.__get_input_state(events)
            self.apply_actions(inp)
            self.apply_movement(inp)
            self.select_animation(inp)
        else:
            self.animation_manager.set_animation("death", loop=False, restart=False)

    def __get_input_state(self, events) -> dict:
        self.keys = pygame.key.get_pressed()

        state = {
            "left": self.__is_held("left"),
            "right": self.__is_held("right"),
            "down": self.__is_held("down"),
            "sprint": self.__is_held("sprint"),
            "jump": False,
            "punch": False,
            "activate": False,
        }

        for event in events:
            for action in ("jump", "punch", "activate"):
                dev, bind = self.binds[action]
                if dev == "key" and event.type == pygame.KEYDOWN and event.key == bind:
                    state[action] = True
                elif dev == "mouse" and event.type == pygame.MOUSEBUTTONDOWN and event.button == bind:
                    state[action] = True

        return state

    def __is_held(self, action: str) -> bool:
        device, code = self.binds[action]
        if device == "key":
            return bool(self.keys[code])
        if device == "mouse":
            buttons = pygame.mouse.get_pressed(5)
            idx = code - 1  # event mouse buttons start at 1, index starts at 0
            if not 0 <= idx < len(buttons):
                self.__log.warning("Bind uses mouse button %s, but only %s buttons are tracked", code, len(buttons))
                return False
            return buttons[idx]
        return False

    def apply_actions(self, inp):
        """
        Handles one-shot actions: jump and attack.
        Later: dash, interact, swap weapon, parry, etc.
        """
        if inp["jump"]:
            if self.jumps_remaining == 2:
                self.velocity.y = -self.jump_force
                self.jumps_remaining -= 1
                self.on_ground = False
            elif self.jumps_remaining == 1 and self.air_time >= self.double_jump_delay:
                self.velocity.y = -self.double_jump_force
                self.jumps_remaining -= 1
                self.on_ground = False

        if inp["punch"]:
            self.attacking = True
            self.attack_name = "punch_1" if self.on_ground else "jump_strike"
            self.attack_id += 1

        if inp["activate"]:
            self.energy = 0

    def apply_movement(self, inp):
        if self.animation_manager.current_animation_name == "crouch":
            self.acceleration.y += self.down_force  # Extra downward force when crouching

        axis = (1 if inp["right"] else 0) - (1 if inp["left"] else 0)
        if axis == 0:
            self.acceleration.x = 0.0
            return

        self.flip_x = (axis < 0)
        accel = self.horizontal_acceleration + (self.sprint_force if (inp["sprint"] and not inp["down"]) else 0.0)
        self.acceleration.x = axis * accel

    def select_animation(self, inp):
        current = self.animation_manager.get_name()
        requested = None
        loop = False
        restart = False

        # apply_actions() already decremented jumps_remaining each check is 1 less
        if inp["jump"]:
            if self.jumps_remaining == 1:
                requested = "jump"
                restart = True
            elif self.jumps_remaining == 0:
                requested = "double_jump"
                restart = True

        elif inp["punch"]:
            requested = self.attack_name
            restart = True

        elif inp["down"]:
            requested = "crouch"

        elif inp["activate"]:
            requested = "activate"

        else:
            axis = (1 if inp["right"] else 0) - (1 if inp["left"] else 0)
            if axis != 0:
                if inp["sprint"]:
                    requested = "sprint"
                    loop = True
                elif current == "sprint":
                    requested = "stop_sprint"
                else:
                    requested = "walk"
                    loop = True
            else:
                requested = "default"

        if requested is None:
            return

        if self.animation_manager.is_playing():
            if self.animation_priority.get(requested) < self.animation_priority.get(current):
                return

        self.animation_manager.set_animation(requested, loop=loop, restart=restart)

    def set_bind(self, action: str, device: str, code: int):
        self.binds[action] = (device, code)

    def set_body_size(self, w: int, h: int):
        midbottom = self.body.midbottom
        self.body.size = (w, h)
        self.body.midbottom = midbottom

    def sync_img_rect_to_body(self):
        """
        Align the visible pixels of the current image to the physics body anchor.
        This prevents left/right flipping causing horizontal offsets due to the transparent padding (bounding rect)
        """
        bounds = self.image.get_bounding_rect()
        self.img_rect = self.image.get_rect()
        self.img_rect.topleft = (
            self.body.midbottom[0] - bounds.midbottom[0],
            self.body.midbottom[1] - bounds.midbottom[1],
        )
        self.sprite_bounds = bounds.move(self.img_rect.topleft)