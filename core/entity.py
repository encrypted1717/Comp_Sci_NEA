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
        self.is_moving = False
        self.velocity = self.vector(0, 0)
        self.acceleration = self.vector(0, 0)
        self.horizontal_acceleration = 2250.0
        self.horizontal_friction = 11
        self.sprint_force = 1450
        self.slide_force = 650
        self.jump_force = 650
        self.double_jump_force = 450
        self.down_force = 1500
        self.gravity = 1250
        self.on_ground = False
        self.jumps_remaining = 2
        self.jump_anim = None
        self.air_time = 0.0
        self.can_activate = False
        self.energy_timer = 0.0
        self.energy_consumption = 20
        self.energy_delay = 2 # seconds
        self.double_jump_delay = 0.01

        # Combat
        self.punch_1_damage = 6
        self.jump_strike_damage = 0
        self.slide_attack_damage = 10
        self.attacking = False
        self.attack_name = None
        self.attack_id = 0
        self.combos = 0
        self.max_blocks = 2
        self.blocks_remaining = self.max_blocks
        self.is_blocking = False
        self.block_regen_timer = 0.0
        self.block_regen_delay = 5.0  # seconds after last blocked hit before blocks reset

        # Input
        self.keys = None
        # Input
        self.keys = None
        self.binds = {
            "left": ("none", None),
            "right": ("none", None),
            "jump": ("none", None),
            "down": ("none", None),
            "sprint": ("none", None),
            "punch": ("none", None),
            "block": ("none", None),
            "activate": ("none", None),
        }

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
            "sprint": 0,
            "stop_sprint": 1,
            "jump": 1,
            "double_jump": 1,
            "block": 2,
            "crouch": 2,
            "activate": 2,
            "punch_1": 2,
            "jump_strike": 2,
            "slide_attack": 2,
            "death": 3
        }
        self.animation_manager.set_animation("default")
        self.__log.info("Entity created: id = %s sprite_type = %s", id(self), sprite_type)

    def _load_animations(self) -> None:
        load = self.animation_manager.load_animation
        path_fight = "assets\\characters\\default\\fighting\\animations\\"
        path_move = "assets\\characters\\default\\movement\\animations\\"
        path_other = "assets\\characters\\default\\other\\animations\\"

        load("default", path_fight + "punch_1.png", scale=self.sprite_scale, frame_indices=[0])
        load("punch_1", path_fight + "punch_1.png", scale=self.sprite_scale, cooldown=0.035)
        load("punch_2", path_fight + "punch_2.png", scale=self.sprite_scale)
        load("block", path_fight + "block.png", scale=self.sprite_scale, cooldown=0.15)
        load("activate", path_fight + "skill_charging.png", scale=self.sprite_scale, cooldown=0.12)  # Make this a skill activation not a charging anim
        load("jump", path_move + "upward_jump.png", scale=self.sprite_scale, frame_indices=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 3, 2, 1, 0], cooldown=0.04)
        load("double_jump", path_move + "double_jump.png", scale=self.sprite_scale, cooldown=0.04)
        load("walk", path_move + "walking.png", scale=self.sprite_scale)
        load("sprint", path_move + "running.png", scale=self.sprite_scale, cooldown=0.08)
        load("stop_sprint", path_move + "stop_running.png", scale=self.sprite_scale)
        load("crouch", path_move + "crouch.png", scale=self.sprite_scale, cooldown=0.035)
        load("jump_strike", path_move + "jump_strike.png", scale=self.sprite_scale)
        load("slide_attack", path_fight + "slide_attack.png", scale=self.sprite_scale)
        load("death", path_other + "death.png", scale=self.sprite_scale)

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

        # Update Attributes
        self.energy_timer += dt
        if self.energy_timer >= self.energy_delay:
            self.energy = min(self.energy + 10, 100)  # cap at 100
            self.energy_timer = 0.0

        # Block regen — reset blocks after not being hit for block_regen_delay seconds
        if self.blocks_remaining < self.max_blocks:
            self.block_regen_timer += dt
            if self.block_regen_timer >= self.block_regen_delay:
                self.blocks_remaining = self.max_blocks
                self.block_regen_timer = 0.0

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
            "block": self.__is_held("block"),
            "jump": False,
            "punch": False,
            "activate": False, # activates set ability
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
        return False # for unbinded keys

    def apply_actions(self, inp):
        """
        Handles one-shot actions: jump and attack.
        Later: dash, interact, swap weapon, parry, etc.
        """
        self.jump_anim = None
        if inp["jump"]:
            if self.jumps_remaining == 2:
                self.velocity.y = -self.jump_force
                self.jumps_remaining -= 1
                self.on_ground = False
                self.jump_anim = "jump"
            elif self.jumps_remaining == 1 and self.air_time >= self.double_jump_delay and not self.on_ground:
                self.velocity.y = -self.double_jump_force
                self.jumps_remaining -= 1
                self.jump_anim = "double_jump"

        if inp["punch"]:
            self.attacking = True
            if inp["sprint"] and inp["down"] and self.on_ground and self.is_moving:
                self.attack_name = "slide_attack"
            elif self.on_ground:
                self.attack_name = "punch_1"
            else:
                self.attack_name = "jump_strike"
            self.attack_id += 1

        if inp["activate"]:
            if self.energy >= self.energy_consumption and self.animation_manager.get_name() != "activate":
                self.can_activate = True
                self.energy -= self.energy_consumption
            else:
                self.can_activate = False
            if self.can_activate:
                pass # run ability

        self.is_blocking = inp["block"] and self.blocks_remaining > 0


    def apply_movement(self, inp):
        if inp["down"] and not self.on_ground:
            self.acceleration.y += self.down_force  # Extra downward force when crouching

        axis = (1 if inp["right"] else 0) - (1 if inp["left"] else 0)
        if axis == 0:
            self.acceleration.x = 0.0
            self.is_moving = False
            return
        self.is_moving = True
        self.flip_x = (axis < 0)
        sprint_force = self.sprint_force if inp["sprint"] else 0.0
        slide_force = self.slide_force if self.attacking and self.attack_name == "slide_attack" else 0.0
        accel = self.horizontal_acceleration + sprint_force + slide_force
        self.acceleration.x = axis * accel

    def select_animation(self, inp):
        current = self.animation_manager.get_name()
        requested = None
        loop = False
        restart = False

        # apply_actions() already decremented jumps_remaining each check is 1 less
        if self.jump_anim:
            requested = self.jump_anim
            restart = True

        elif inp["punch"]:
            requested = self.attack_name
            restart = True

        elif inp["down"] and not inp["sprint"]:
            requested = "crouch"

        elif self.is_blocking:
            requested = "block"

        elif self.can_activate:
            self.can_activate = False
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