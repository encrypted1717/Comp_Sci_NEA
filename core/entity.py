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
        self.main_energy_consumption = 100
        self.side_energy_consumption = 20
        self.energy_delay = 2 # seconds
        self.double_jump_delay = 0.01

        # Combat
        self.punch_1_damage = 6
        self.punch_2_damage = 8
        self.jump_strike_damage = 10
        self.slide_attack_damage = 10
        self.energy_punch_damage = 25
        self.energy_punch_phase = None     # None | "activating" | "charging" | "striking"
        self.energy_charge_overlay = False  # True while energy_charge anim should render as an overlay
        self.attacking = False
        self.attack_name = None
        self.attack_id = 0
        self.last_punch = 2  # starts at 2 so first punch is punch_1
        self.combos = 0
        self.punch_combo_step = 0
        self.punch_cooldown_timer = 0.0
        self.punch_cooldown_duration = 0.5
        self.jump_strike_cooldown_timer = 0.0
        self.jump_strike_cooldown_duration = 0.4  # seconds between air jump strikes
        self._attack_just_started = False  # True only on the frame an attack begins
        self.is_taking_damage = False
        self.taking_damage_timer = 0.0
        self.taking_damage_duration = 0.45
        self.taking_damage_speed_multiplier = 0.35
        self.max_blocks = 2
        self.blocks_remaining = self.max_blocks
        self.is_blocking = False
        self.block_regen_timer = 0.0
        self.block_regen_delay = 5.0  # seconds after last blocked hit before blocks reset
        self.guard_broken = False
        self.guard_break_timer = 0.0
        self.guard_break_duration = 1.3  # seconds movement is locked after guard breaks
        self.side_ability = "teleport"
        self.main_ability = "energy_punch"

        # Teleport state — managed cooperatively with game.py
        self.teleport_phase = None         # None | "out" | "in"
        self.teleport_requested = False    # game.py reads this to spawn a portal at current pos
        self.portal_open = False           # set True by game.py once a portal exists, False once it closes
        self.teleport_return_requested = False  # game.py reads this to execute the warp
        self.teleport_just_started = False  # True only on the frame teleport_out or teleport_in begins

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
            "main_ability": ("none", None),
            "side_ability": ("none", None),
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
            "punch_2": 2,
            "jump_strike": 2,
            "slide_attack": 2,
            "taking_damage": 2,
            "energy_charge": 2,
            "energy_punch": 2,
            "teleport_in": 2,
            "teleport_out": 2,
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
        load("taking_damage", path_other + "taking_damage.png", scale=self.sprite_scale)
        load("punch_1", path_fight + "punch_1.png", scale=self.sprite_scale, cooldown=0.075) #0.05
        load("punch_2", path_fight + "punch_2.png", scale=self.sprite_scale, cooldown=0.075)
        load("energy_charge", path_other + "energy_charge.png", scale=self.sprite_scale)
        load("energy_punch", path_other + "energy_punch.png", scale=self.sprite_scale)
        load("teleport_in", path_other + "teleport_in.png", scale=self.sprite_scale)
        load("teleport_out", path_other + "teleport_out.png", scale=self.sprite_scale)
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

        # Death takes priority over everything — lock into death anim and skip all other logic
        if self.health <= 0:
            self.animation_manager.set_animation("death", loop=False, restart=False)
            return

        # Reset on_ground each frame so collision_manager is the sole authority on grounded state.
        # Without this, walking off a ledge keeps on_ground=True for one extra frame.
        self.on_ground = False
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

        # Guard break — trigger 2 second movement lock when blocks hit 0
        if self.blocks_remaining == 0 and not self.guard_broken:
            self.guard_broken = True
            self.guard_break_timer = 0.0
        if self.guard_broken:
            self.guard_break_timer += dt
            if self.guard_break_timer >= self.guard_break_duration:
                self.guard_broken = False
                self.blocks_remaining = self.max_blocks  # Restore blocks so guard_broken isn't re-triggered next frame

        # Punch combo cooldown — after punch_2 finishes, wait before resetting combo
        if self.punch_combo_step == 2 and not self.attacking:
            self.punch_cooldown_timer += dt
            if self.punch_cooldown_timer >= self.punch_cooldown_duration:
                self.punch_combo_step = 0
                self.punch_cooldown_timer = 0.0

        # Jump strike cooldown — tick down while not attacking in the air
        if self.jump_strike_cooldown_timer > 0.0:
            self.jump_strike_cooldown_timer = max(0.0, self.jump_strike_cooldown_timer - dt)

        # Taking damage timer — clears state after duration
        if self.is_taking_damage:
            self.taking_damage_timer += dt
            if self.taking_damage_timer >= self.taking_damage_duration:
                self.is_taking_damage = False
                self.taking_damage_timer = 0.0

        # Energy punch state machine: activating -> charging (overlay) -> striking -> done
        if self.energy_punch_phase == "activating" and not self.animation_manager.is_playing():
            # activate anim finished — overlay starts looping; player can move/attack freely
            self.energy_punch_phase = "charging"
            self.energy_charge_overlay = True
        elif self.energy_punch_phase == "striking" and not self.animation_manager.is_playing():
            # energy_punch anim finished — clear overlay and attack state
            self.energy_punch_phase = None
            self.energy_charge_overlay = False
            self.attacking = False
            self.attack_name = None

        # Teleport state machine — game.py handles portal placement and position warp
        if self.teleport_phase == "in" and not self.animation_manager.is_playing():
            self.teleport_phase = None

        # Clear attack state once any non-energy-punch animation finishes AND is no longer frozen on its last frame.
        # Clearing while still frozen lets same-priority attacks (e.g. punch_1) fire before the anim visually ends.
        if self.attacking and self.energy_punch_phase != "striking" and not self.animation_manager.is_playing() and not self.animation_manager.freeze:
            self.attacking = False
            self.attack_name = None

    def event_handler(self, events):
        self.acceleration = self.vector(0, 0)
        inp = self.__get_input_state(events)
        self.apply_actions(inp)
        self.apply_movement(inp)
        self.select_animation(inp)

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
            "main_ability": False,
            "side_ability": False,
        }

        for event in events:
            for action in ("jump", "punch", "main_ability", "side_ability"):
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
        self._attack_just_started = False  # Reset every frame; only True on the frame a new attack begins
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

        if inp["punch"] and not self.attacking and self.punch_combo_step != 2:
            self.attacking = True
            self._attack_just_started = True
            if inp["sprint"] and inp["down"] and self.on_ground and (inp["left"] or inp["right"]):
                # Slide attack — plays normally, overlay stays if charging
                self.attack_name = "slide_attack"
                self.punch_combo_step = 0
            elif self.on_ground:
                if self.energy_punch_phase == "charging":
                    # Ground punch while charged — consume charge and fire energy punch
                    self.attack_name = "energy_punch"
                    self.energy_punch_phase = "striking"
                    self.energy_charge_overlay = False
                    self.punch_combo_step = 0
                elif self.punch_combo_step == 0:
                    self.attack_name = "punch_1"
                    self.punch_combo_step = 1
                else:
                    self.attack_name = "punch_2"
                    self.punch_combo_step = 2
                    self.punch_cooldown_timer = 0.0
            elif self.jump_strike_cooldown_timer <= 0.0:
                # Jump strike — plays normally, overlay stays if charging
                self.attack_name = "jump_strike"
                self.punch_combo_step = 0
                self.jump_strike_cooldown_timer = self.jump_strike_cooldown_duration
            else:
                # Jump strike on cooldown — cancel the attack
                self.attacking = False
                self._attack_just_started = False
            self.attack_id += 1

        if inp["main_ability"] and self.energy_punch_phase is None:
            if self.energy >= self.main_energy_consumption:
                self.energy -= self.main_energy_consumption
                self.can_activate = True
                if self.main_ability == "energy_punch":
                    self.energy_punch_phase = "activating"
                # else: just plays activate anim with no follow-up ability effect
            else:
                self.can_activate = False

        elif inp["side_ability"] and self.energy_punch_phase is None and self.teleport_phase is None:
            if self.side_ability == "teleport":
                if not self.portal_open and self.energy >= self.side_energy_consumption:
                    # No portal exists yet — open one, costs energy
                    self.energy -= self.side_energy_consumption
                    self.teleport_requested = True
                elif self.portal_open:
                    # Portal already open — return to it, free of charge
                    self.teleport_return_requested = True
                    self.teleport_phase = "out"
                    self.teleport_just_started = True
            elif self.side_ability != "teleport" and self.energy >= self.side_energy_consumption:
                self.energy -= self.side_energy_consumption
                self.can_activate = True
            else:
                self.can_activate = False

        self.is_blocking = inp["block"] and self.blocks_remaining > 0


    def apply_movement(self, inp):
        # Guard broken — freeze horizontal movement and axis for 2 seconds
        if self.guard_broken:
            self.acceleration.x = 0.0
            self.is_moving = False
            return

        if inp["down"] and not self.on_ground:
            self.acceleration.y += self.down_force

        axis = (1 if inp["right"] else 0) - (1 if inp["left"] else 0)
        locked_axis = -1 if self.flip_x else 1

        # During slide attack — keep sliding in locked direction, prevent reversal
        if self.attacking and self.attack_name == "slide_attack" and self.animation_manager.is_playing():
            self.acceleration.x = locked_axis * (self.horizontal_acceleration + self.sprint_force + self.slide_force)
            self.is_moving = True
            return

        if axis == 0:
            self.acceleration.x = 0.0
            self.is_moving = False
            return
        self.is_moving = True
        self.flip_x = (axis < 0)
        sprint_force = self.sprint_force if inp["sprint"] else 0.0
        accel = self.horizontal_acceleration + sprint_force
        self.acceleration.x = axis * accel

        # Taking damage slows horizontal movement
        if self.is_taking_damage:
            self.acceleration.x *= self.taking_damage_speed_multiplier

    def select_animation(self, inp):
        current = self.animation_manager.get_name()
        requested = None
        loop = False
        restart = False

        # apply_actions() already decremented jumps_remaining each check is 1 less
        if self.jump_anim:
            requested = self.jump_anim
            restart = True

        elif self._attack_just_started:
            # Only start (and restart) the attack animation on the exact frame the attack was initiated.
            requested = self.attack_name
            restart = True

        elif inp["down"] and not inp["sprint"] and not self.attacking:
            requested = "crouch"

        elif self.is_taking_damage:
            requested = "taking_damage"
            restart = True

        elif self.is_blocking:
            requested = "block"

        elif self.teleport_phase == "out":
            if self.teleport_just_started:
                requested = "teleport_out"
                restart = True
            else:
                return  # let teleport_out play uninterrupted

        elif self.teleport_phase == "in":
            if self.teleport_just_started:
                requested = "teleport_in"
                restart = True
            else:
                return  # let teleport_in play uninterrupted

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

        # Block lower-priority interruptions whether the animation is actively playing
        # OR frozen on its last frame (freeze=True means it finished, not that it can be replaced freely)
        # Exception: hold-input animations (crouch, block) should not block transitions once their input is released
        hold_anim_released = (current == "crouch" and not inp["down"]) or \
                             (current == "block" and not inp["block"])
        anim_active = (self.animation_manager.is_playing() or self.animation_manager.freeze) and not hold_anim_released
        if anim_active:
            if self.__get_priority(requested) < self.__get_priority(current):
                return

        self.animation_manager.set_animation(requested, loop=loop, restart=restart)
        self.teleport_just_started = False  # consumed — clear so we don't restart next frame

    def __get_priority(self, name: str) -> int:
        """Look up animation priority, defaulting to 0 for unknown animations."""
        return self.animation_priority.get(name, 0)

    def teleport_to(self, position: tuple) -> None:
        """
            Warp the entity to a position and begin the teleport_in animation.

            Called by game.py once teleport_out finishes and the portal position
            is known. Owns all entity-side state changes so game.py only needs to
            call one method rather than writing six fields directly.

            Args:
                position: (x, y) midbottom target coordinates to warp to.
        """
        self.position.x = position[0]
        self.position.y = position[1]
        self.body.midbottom = position
        self.velocity = self.vector(0, 0)
        self.teleport_phase = "in"
        self.teleport_just_started = True  # tells select_animation to start teleport_in this frame only
        self.teleport_return_requested = False
        self.portal_open = False  # portal is closing - entity can open a new one after this

    def take_hit(self, damage: int):
        """Called by combat system when a hit lands. Applies damage and triggers taking_damage state."""
        self.health -= damage
        self.is_taking_damage = True
        self.taking_damage_timer = 0.0  # reset so each new hit gives full duration

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