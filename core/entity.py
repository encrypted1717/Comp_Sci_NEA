"""
    Player entity class for game.

    This module provides the Entity class, which represents a single player-
    controlled character. It owns all physics state, combat state, animation
    state, and input binds for one player. Game logic (collision, combat, portal
    teleportation) lives in game.py and cooperates with Entity through public
    fields and methods rather than calling private internals.
"""

import logging
import pygame
from graphics import AnimationManager


# TODO add more animations
# TODO support different times of punches/combos using delays/elapsed time between clicks
# TODO fix bug: sprinting anim continues after releasing movement key before removing sprint key
# TODO Add functions for energy
class Entity(pygame.sprite.Sprite):
    """
        A player-controlled character with physics, combat, animation, and input.

        Entity owns three interlocked systems that run every frame:
        - Physics: velocity and acceleration updated in update(), positions resolved
          by CollisionManager after update() returns.
        - Combat: attack state tracked here; hit detection and damage application
          are driven by CombatSystem in game.py.
        - Animation: AnimationManager selects and advances frames based on the
          current movement and action state produced by event_handler().

        Input binds are stored as (device, code) pairs per action and are loaded
        from config by game.py via set_bind(). Teleport and portal state is
        managed cooperatively with game.py: Entity sets request flags, game.py
        creates/destroys portals, then calls teleport_to() to complete the warp.
    """

    def __init__(self, start_position: tuple, sprite_type: str, health=100):
        """
            Initialise all entity state and load animations.

            Args:
                start_position: (x, y) midbottom spawn coordinates in world space.
                sprite_type:    identifier string used to select animations and
                                distinguish players in collision resolution - e.g.
                                "player1" or "player2".
                health:         starting health value, default 100.
        """
        super().__init__()

        # Logging setup
        self.__log = logging.getLogger(__name__)
        self.__log.info("Creating an entity: sprite_type = %s pos = %s", sprite_type, start_position)

        # Main setup
        self.vector = pygame.math.Vector2 # Alias so vector literals don't need the full module path
        self.sprite = sprite_type
        self.dt = None # Stored each update() so helpers called within the same frame can access it
        self.flip_x = False # True when the entity is facing left - applied to the animation frame on draw

        # Sprite attributes
        self.entity_id = id(self) # Unique identifier used by portal system to map portals to their owner
        self.health = health
        self.energy = 0

        # Sprite creation - body is the physics collision rect, img_rect tracks the visible frame position
        self.sprite_scale = 1.2
        self.frame_size = (int(128 * self.sprite_scale), int(128 * self.sprite_scale))
        body_w, body_h = int(36 * self.sprite_scale), int(72 * self.sprite_scale)
        self.body = pygame.Rect(0, 0, body_w, body_h) # Collision box - narrower than the frame to avoid phantom hits
        self.position = self.vector(start_position)
        self.body.midbottom = (int(self.position.x), int(self.position.y)) # Position anchor is midbottom (feet)
        self.rect = self.body # pygame sprite group uses self.rect for culling
        self.image = pygame.Surface(self.frame_size, pygame.SRCALPHA)
        self.img_rect = self.image.get_rect(midbottom=self.body.midbottom)
        self.sprite_bounds = self.image.get_bounding_rect().move(self.img_rect.topleft) # Pixel-tight hitbox updated each frame

        # Physics state
        self.is_moving = False
        self.velocity = self.vector(0, 0)
        self.acceleration = self.vector(0, 0)
        self.horizontal_acceleration = 2250.0
        self.horizontal_friction = 11 # Applied as a drag multiplier against current x velocity
        self.sprint_force = 1450 # Extra horizontal acceleration added while sprinting
        self.slide_force = 650 # Extra force applied during a slide attack
        self.jump_force = 650 # Upward velocity applied on first jump
        self.double_jump_force = 450 # Upward velocity applied on second jump (weaker)
        self.down_force = 1500 # Downward acceleration applied when holding down mid-air
        self.gravity = 1250 # Constant downward acceleration applied every frame
        self.on_ground = False # Set True by CollisionManager on landing, reset to False every update()
        self.jumps_remaining = 2 # Decremented on each jump, restored to 2 on landing
        self.jump_anim = None # Set to "jump" or "double_jump" in apply_actions for select_animation to read
        self.air_time = 0.0 # Accumulated time since leaving the ground - used for double jump delay guard
        self.can_activate = False # Set True when an ability activation animation should play
        self.energy_timer = 0.0
        self.main_energy_consumption = 100
        self.side_energy_consumption = 20
        self.energy_delay = 2 # Seconds between each energy regeneration tick
        self.double_jump_delay = 0.01 # Minimum air_time before a double jump is allowed

        # Combat state
        self.punch_1_damage = 6
        self.punch_2_damage = 8
        self.jump_strike_damage = 10
        self.slide_attack_damage = 10
        self.energy_punch_damage = 25
        self.energy_punch_phase = None # None | "activating" | "charging" | "striking"
        self.energy_charge_overlay = False  # True while the energy charge overlay animation should render on top
        self.attacking = False
        self.attack_name = None
        self.attack_id = 0 # Incremented each attack so CombatSystem can track unique hits
        self.last_punch = 2 # Starts at 2 so the first punch is always punch_1
        self.combos = 0
        self.punch_combo_step = 0 # 0 = ready for punch_1, 1 = ready for punch_2, 2 = combo complete
        self.punch_cooldown_timer = 0.0
        self.punch_cooldown_duration = 1    # Seconds after punch_2 before the combo resets to step 0
        self.jump_strike_cooldown_timer = 0.0
        self.jump_strike_cooldown_duration = 0.4    # Seconds between air jump strikes
        self._attack_just_started = False  # True only on the exact frame an attack begins - used by select_animation
        self.is_taking_damage = False
        self.taking_damage_timer = 0.0
        self.taking_damage_duration = 0.45   # Seconds the taking_damage state persists after a hit
        self.taking_damage_speed_multiplier = 0.35  # Horizontal movement is scaled down while taking damage
        self.max_blocks = 2
        self.blocks_remaining = self.max_blocks
        self.is_blocking = False
        self.block_regen_timer = 0.0
        self.block_regen_delay = 10.0   # Seconds after the last blocked hit before blocks are restored
        self.guard_broken = False  # True during the guard break stun period
        self.guard_break_timer = 0.0
        self.guard_break_duration = 1.3    # Seconds of movement lock after guard breaks
        self.side_ability = "teleport"
        self.main_ability = "energy_punch"

        # Teleport state - managed cooperatively with game.py via request flags
        self.teleport_phase = None   # None | "out" | "in"
        self.teleport_requested = False  # game.py reads this to spawn a portal at the entity's current position
        self.portal_open = False  # Set True by game.py once a portal exists, False once it closes
        self.teleport_return_requested = False  # game.py reads this to execute the warp once teleport_out finishes
        self.teleport_just_started = False  # True only on the frame teleport_out or teleport_in begins

        # Input
        self.keys = None # Snapshot of pygame.key.get_pressed() updated each event_handler call
        self.binds = { # Maps action names to (device, code) pairs - loaded from config by game.py via set_bind()
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
        # TODO update system so the scale can be updated and doesn't need to be stated at every load of animation
        self.animation_manager = AnimationManager()
        self._load_animations()

        # Priority levels - a playing animation can only be interrupted by something strictly higher.
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
        """Load all animation sprite sheets from disk and register them with the animation manager."""
        load = self.animation_manager.load_animation
        path_fight = "assets\\characters\\default\\fighting\\animations\\"
        path_move = "assets\\characters\\default\\movement\\animations\\"
        path_other = "assets\\characters\\default\\other\\animations\\"

        load("default", path_fight + "punch_1.png", scale=self.sprite_scale, frame_indices=[0])  # Single idle frame reused from punch sheet
        load("taking_damage", path_other + "taking_damage.png", scale=self.sprite_scale)
        load("punch_1", path_fight + "punch_1.png", scale=self.sprite_scale, cooldown=0.075)
        load("punch_2", path_fight + "punch_2.png", scale=self.sprite_scale, cooldown=0.075)
        load("energy_charge", path_other + "energy_charge.png", scale=self.sprite_scale)
        load("energy_punch", path_other + "energy_punch.png", scale=self.sprite_scale)
        load("teleport_in", path_other + "teleport_in.png", scale=self.sprite_scale)
        load("teleport_out", path_other + "teleport_out.png", scale=self.sprite_scale)
        load("block", path_fight + "block.png", scale=self.sprite_scale, cooldown=0.15)
        load("activate", path_fight + "skill_charging.png", scale=self.sprite_scale, cooldown=0.12)
        load("jump", path_move + "upward_jump.png", scale=self.sprite_scale, frame_indices=[0,1,2,3,4,5,6,7,8,9,10,3,2,1,0], cooldown=0.04)
        load("double_jump", path_move  + "double_jump.png", scale=self.sprite_scale, cooldown=0.04)
        load("walk", path_move + "walking.png", scale=self.sprite_scale)
        load("sprint", path_move + "running.png", scale=self.sprite_scale, cooldown=0.08)
        load("stop_sprint", path_move + "stop_running.png", scale=self.sprite_scale)
        load("crouch", path_move + "crouch.png", scale=self.sprite_scale, cooldown=0.035)
        load("jump_strike", path_move + "jump_strike.png", scale=self.sprite_scale)
        load("slide_attack", path_fight + "slide_attack.png", scale=self.sprite_scale)
        load("death", path_other + "death.png", scale=self.sprite_scale)

    def update(self, dt):
        """
            Advance physics, animation, and all timer-based state for one frame.

            Death is checked first and short-circuits all other logic - the death
            animation still needs update() called so it can advance and finish.
            CollisionManager is expected to run after this method and correct any
            position overlap before the frame is drawn.

            Args:
                dt: delta time in seconds since the last frame.
        """
        self.dt = dt

        # Death takes priority over everything - lock into death anim and skip all other logic
        if self.health <= 0:
            self.animation_manager.set_animation("death", loop=False, restart=False)
            self.animation_manager.update(dt)  # Must still tick so death anim advances and is_playing() can reach False
            self.image = pygame.transform.flip(self.animation_manager.get_frame(), self.flip_x, False)
            self.sync_img_rect_to_body()
            return

        # Reset on_ground each frame so CollisionManager is the sole authority on grounded state.
        # Without this, walking off a ledge keeps on_ground=True for one extra frame.
        self.on_ground = False
        self.air_time = 0.0 if self.on_ground else self.air_time + dt

        # Physics integration - apply gravity, friction, acceleration, then integrate position
        self.velocity.y += self.gravity * dt
        self.acceleration.x -= self.velocity.x * self.horizontal_friction  # Friction opposes current horizontal velocity
        self.velocity += self.acceleration * dt
        self.position += self.velocity * dt + 0.5 * self.acceleration * (dt ** 2)  # Verlet integration for smoother movement

        # Sync the physics body rect to the integrated position
        self.body.midbottom = (int(self.position.x), int(self.position.y))
        self.rect = self.body  # Keep self.rect in sync so sprite group culling uses the correct position

        # Advance animation and flip the frame if facing left
        self.animation_manager.update(dt)
        self.image = pygame.transform.flip(self.animation_manager.get_frame(), self.flip_x, False)
        self.sync_img_rect_to_body()

        # Energy regeneration - ticks up by 10 every energy_delay seconds, capped at 100
        self.energy_timer += dt
        if self.energy_timer >= self.energy_delay:
            self.energy = min(self.energy + 10, 100)
            self.energy_timer = 0.0

        # Block regeneration - restore all blocks after not being hit for block_regen_delay seconds
        if self.blocks_remaining < self.max_blocks:
            self.block_regen_timer += dt
            if self.block_regen_timer >= self.block_regen_delay:
                self.blocks_remaining = self.max_blocks
                self.block_regen_timer = 0.0

        # Guard break - lock movement for guard_break_duration when blocks hit zero
        if self.blocks_remaining == 0 and not self.guard_broken:
            self.guard_broken = True
            self.guard_break_timer = 0.0
        if self.guard_broken:
            self.guard_break_timer += dt
            if self.guard_break_timer >= self.guard_break_duration:
                self.guard_broken = False
                self.blocks_remaining = self.max_blocks  # Restore blocks so guard_broken isn't re-triggered next frame

        # Punch combo cooldown - after punch_2 completes, wait before resetting step to 0
        if self.punch_combo_step == 2 and not self.attacking:
            self.punch_cooldown_timer += dt
            if self.punch_cooldown_timer >= self.punch_cooldown_duration:
                self.punch_combo_step = 0
                self.punch_cooldown_timer = 0.0

        # Jump strike cooldown - tick down each frame regardless of ground state
        if self.jump_strike_cooldown_timer > 0.0:
            self.jump_strike_cooldown_timer = max(0.0, self.jump_strike_cooldown_timer - dt)

        # Taking damage timer - clears the state after the stun duration elapses
        if self.is_taking_damage:
            self.taking_damage_timer += dt
            if self.taking_damage_timer >= self.taking_damage_duration:
                self.is_taking_damage = False
                self.taking_damage_timer = 0.0

        # Energy punch state machine: activating -> charging (overlay) -> striking -> done
        if self.energy_punch_phase == "activating" and not self.animation_manager.is_playing():
            # activate anim finished - overlay starts looping; player can move and attack freely
            self.energy_punch_phase = "charging"
            self.energy_charge_overlay = True
        elif self.energy_punch_phase == "striking" and not self.animation_manager.is_playing():
            # energy_punch anim finished - clear overlay and attack state
            self.energy_punch_phase = None
            self.energy_charge_overlay = False
            self.attacking = False
            self.attack_name = None

        # Teleport state machine - game.py handles portal placement and position warp
        if self.teleport_phase == "in" and not self.animation_manager.is_playing():
            self.teleport_phase = None  # teleport_in finished - entity is back in normal state

        # Clear attack state once any non-energy-punch animation finishes AND is no longer frozen on its last frame.
        # Clearing while still frozen lets same-priority attacks (e.g. punch_1) fire before the anim visually ends.
        if self.attacking and self.energy_punch_phase != "striking" and not self.animation_manager.is_playing() and not self.animation_manager.freeze:
            self.attacking = False
            self.attack_name = None

    def event_handler(self, events):
        """
            Process player input and drive actions, movement, and animation for this frame.

            Resets acceleration to zero first so each frame builds from scratch.
            Input state is sampled once and passed to all three sub-methods so
            they operate on the same snapshot.

            Args:
                events: list of mapped pygame events for this frame.
        """
        self.acceleration = self.vector(0, 0)  # Clear acceleration so held keys must re-apply force each frame
        inp = self.__get_input_state(events)
        self.apply_actions(inp)
        self.apply_movement(inp)
        self.select_animation(inp)

    def __get_input_state(self, events) -> dict:
        """
            Sample all input binds and return a unified input state dict for this frame.

            Held actions (movement, sprint, block) are read from the key/mouse state
            snapshot. One-shot actions (jump, punch, abilities) are read from KEYDOWN
            and MOUSEBUTTONDOWN events so they fire exactly once per press.

            Args:
                events: list of mapped pygame events for this frame.

            Returns:
                Dict mapping action names to bool - True if the action is active.
        """
        self.keys = pygame.key.get_pressed() # Snapshot held key state once per frame

        # Held actions are sampled directly from hardware state
        state = {
            "left":   self.__is_held("left"),
            "right":  self.__is_held("right"),
            "down":   self.__is_held("down"),
            "sprint": self.__is_held("sprint"),
            "block":  self.__is_held("block"),
            # One-shot actions start False and are set True by event scanning below
            "jump":         False,
            "punch":        False,
            "main_ability": False,
            "side_ability": False,
        }

        # One-shot actions are only True on the frame the key/button was first pressed
        for event in events:
            for action in ("jump", "punch", "main_ability", "side_ability"):
                dev, bind = self.binds[action]
                if dev == "key"   and event.type == pygame.KEYDOWN       and event.key    == bind:
                    state[action] = True
                elif dev == "mouse" and event.type == pygame.MOUSEBUTTONDOWN and event.button == bind:
                    state[action] = True

        return state

    def __is_held(self, action: str) -> bool:
        """
            Return whether a held-input action is currently active.

            Reads from the key snapshot or mouse button state depending on the
            device recorded in the bind. Returns False for unbound actions.

            Args:
                action: the action name to check.

            Returns:
                True if the bound key or mouse button is currently held.
        """
        device, code = self.binds[action]
        if device == "key":
            return bool(self.keys[code])
        if device == "mouse":
            buttons = pygame.mouse.get_pressed(5)
            idx = code - 1 # Mouse event buttons start at 1; get_pressed index starts at 0
            if not 0 <= idx < len(buttons):
                self.__log.warning("Bind uses mouse button %s, but only %s buttons are tracked", code, len(buttons))
                return False
            return buttons[idx]
        return False # Unbound action - device is "none"

    def apply_actions(self, inp):
        """
            Process one-shot actions: jump, attack, abilities, and block.

            Jump and double-jump are gated by jumps_remaining and air_time.
            Punch selects the correct attack type based on combo step, ground
            state, and energy charge. Abilities gate on energy and phase state.

            Args:
                inp: input state dict from __get_input_state.
        """
        self.jump_anim = None # Cleared each frame; set to "jump" or "double_jump" when a jump fires
        self._attack_just_started = False # Reset every frame; only True on the frame a new attack begins

        if inp["jump"]:
            if self.jumps_remaining == 2:
                self.velocity.y = -self.jump_force
                self.jumps_remaining  -= 1
                self.on_ground = False
                self.jump_anim = "jump"
            elif self.jumps_remaining == 1 and self.air_time >= self.double_jump_delay and not self.on_ground:
                self.velocity.y = -self.double_jump_force
                self.jumps_remaining  -= 1
                self.jump_anim = "double_jump"

        if inp["punch"] and not self.attacking and self.punch_combo_step != 2:
            self.attacking = True
            self._attack_just_started = True

            if inp["sprint"] and inp["down"] and self.on_ground and (inp["left"] or inp["right"]):
                # Slide attack - sprint + down + a direction while on ground
                self.attack_name = "slide_attack"
                self.punch_combo_step = 0
            elif self.on_ground:
                if self.energy_punch_phase == "charging":
                    # Ground punch while charged - consume the charge and fire energy punch
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
                    self.punch_cooldown_timer = 0.0 # Reset timer so cooldown starts from this frame
            elif self.jump_strike_cooldown_timer <= 0.0:
                # Air punch - jump strike
                self.attack_name = "jump_strike"
                self.punch_combo_step = 0
                self.jump_strike_cooldown_timer = self.jump_strike_cooldown_duration
            else:
                # Jump strike on cooldown - cancel the attack rather than entering a broken state
                self.attacking = False
                self._attack_just_started = False

            self.attack_id += 1  # Increment each attack so CombatSystem can detect new hits vs repeated frames

        if inp["main_ability"] and self.energy_punch_phase is None:
            if self.energy >= self.main_energy_consumption:
                self.energy               -= self.main_energy_consumption
                self.can_activate = True
                if self.main_ability == "energy_punch":
                    self.energy_punch_phase = "activating"
                # else: plays the activate anim with no follow-up ability effect
            else:
                self.can_activate = False

        elif inp["side_ability"] and self.energy_punch_phase is None and self.teleport_phase is None:
            if self.side_ability == "teleport":
                if not self.portal_open and self.energy >= self.side_energy_consumption:
                    # No portal exists yet - place one at current position, costs energy
                    self.energy                -= self.side_energy_consumption
                    self.teleport_requested = True
                elif self.portal_open:
                    # Portal already open - warp back to it, free of charge
                    self.teleport_return_requested = True
                    self.teleport_phase = "out"
                    self.teleport_just_started = True
            elif self.side_ability != "teleport" and self.energy >= self.side_energy_consumption:
                self.energy      -= self.side_energy_consumption
                self.can_activate = True
            else:
                self.can_activate = False

        # Block is active while the key is held and blocks are available
        self.is_blocking = inp["block"] and self.blocks_remaining > 0

    def apply_movement(self, inp):
        """
            Apply horizontal and vertical acceleration based on current input.

            Guard break and slide attack override normal movement. Otherwise,
            acceleration is computed from the directional axis and sprint state.
            Taking damage reduces horizontal acceleration as a stun effect.

            Args:
                inp: input state dict from __get_input_state.
        """
        # Guard broken - freeze horizontal movement for the full guard_break_duration
        if self.guard_broken:
            self.acceleration.x = 0.0
            self.is_moving = False
            return

        if inp["down"] and not self.on_ground:
            self.acceleration.y += self.down_force  # Fast-fall when holding down in the air

        axis = (1 if inp["right"] else 0) - (1 if inp["left"] else 0)  # -1 left, 0 neutral, 1 right
        locked_axis = -1 if self.flip_x else 1  # Direction the entity is currently facing

        # During slide attack - lock direction and apply combined sprint + slide force
        if self.attacking and self.attack_name == "slide_attack" and self.animation_manager.is_playing():
            self.acceleration.x = locked_axis * (self.horizontal_acceleration + self.sprint_force + self.slide_force)
            self.is_moving = True
            return

        if axis == 0:
            self.acceleration.x = 0.0
            self.is_moving = False
            return

        self.is_moving = True
        self.flip_x = (axis < 0)  # Face the direction of movement
        sprint_force = self.sprint_force if inp["sprint"] else 0.0
        accel = self.horizontal_acceleration + sprint_force
        self.acceleration.x = axis * accel

        if self.is_taking_damage:
            self.acceleration.x *= self.taking_damage_speed_multiplier  # Reduce mobility during hit stun

    def select_animation(self, inp):
        """
            Choose and set the animation that best matches the current state.

            Priority rules prevent low-priority animations from interrupting
            high-priority ones that are still playing. Hold-input animations
            (crouch, block) are exempt from the freeze check once their input
            is released so they transition out cleanly.

            Args:
                inp: input state dict from __get_input_state.
        """
        current = self.animation_manager.get_name()
        loop = False
        restart = False

        # Evaluate requested animation in priority order - first match wins
        if self.jump_anim:
            requested = self.jump_anim
            restart = True

        elif self._attack_just_started:
            # Only start (and restart) the attack animation on the exact frame the attack was initiated
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
                return # Let teleport_out play uninterrupted until it finishes

        elif self.teleport_phase == "in":
            if self.teleport_just_started:
                requested = "teleport_in"
                restart = True
            else:
                return # Let teleport_in play uninterrupted until it finishes

        elif self.can_activate:
            self.can_activate = False # Consume the flag so the animation only fires once
            requested = "activate"

        else:
            axis = (1 if inp["right"] else 0) - (1 if inp["left"] else 0)
            if axis != 0:
                if inp["sprint"]:
                    requested = "sprint"
                    loop = True
                elif current == "sprint":
                    requested = "stop_sprint" # Play the deceleration animation before transitioning to walk/idle
                else:
                    requested = "walk"
                    loop = True
            else:
                requested = "default"

        # Block lower-priority interruptions while an animation is actively playing or frozen on its last frame.
        # Exception: hold-input animations (crouch, block) should not block transitions once their input is released.
        hold_anim_released = (current == "crouch" and not inp["down"]) or \
                             (current == "block"  and not inp["block"])
        anim_active = (self.animation_manager.is_playing() or self.animation_manager.freeze) and not hold_anim_released
        if anim_active:
            if self.__get_priority(requested) < self.__get_priority(current):
                return # Requested animation has lower priority - let the current one finish

        self.animation_manager.set_animation(requested, loop=loop, restart=restart)
        self.teleport_just_started = False # Consumed - clear so we don't restart the teleport anim next frame

    def __get_priority(self, name: str) -> int:
        """
            Look up the animation priority for a given animation name.

            Args:
                name: the animation name to look up.

            Returns:
                The integer priority level, defaulting to 0 for unknown names.
        """
        return self.animation_priority.get(name, 0)

    def teleport_to(self, position: tuple) -> None:
        """
            Warp the entity to a new position and begin the teleport_in animation.

            Called by game.py once the teleport_out animation finishes and the portal
            position is known. All entity-side state changes are owned here so
            game.py only needs to call one method rather than writing multiple fields.

            Args:
                position: (x, y) midbottom target coordinates in world space.
        """
        self.position.x = position[0]
        self.position.y = position[1]
        self.body.midbottom = position
        self.velocity = self.vector(0, 0) # Kill all momentum so the entity doesn't carry speed through the warp
        self.teleport_phase = "in"
        self.teleport_just_started = True # Tells select_animation to start teleport_in on this frame only
        self.teleport_return_requested = False
        self.portal_open = False # Portal is closing - entity can open a new one after arriving

    def take_hit(self, damage: int):
        """
            Apply damage and trigger the taking_damage stun state.

            Called by CombatSystem when a hit lands. Resetting taking_damage_timer
            to zero gives the full stun duration on each new hit even if one was
            already in progress.

            Args:
                damage: the amount of health to subtract.
        """
        self.health -= damage
        self.is_taking_damage = True
        self.taking_damage_timer = 0.0 # Reset so each new hit gives the full stun duration

    def set_bind(self, action: str, device: str, code: int | None):
        """
            Set the input bind for a single action.

            Called by game.py after reading the player's config file. Replaces
            the default ("none", None) with the actual device and key/button code.

            Args:
                action: the action name to bind - e.g. "jump" or "punch".
                device: "key" or "mouse".
                code:   pygame key code or mouse button number.
        """
        self.binds[action] = (device, code)

    def set_body_size(self, w: int, h: int):
        """
            Resize the physics collision body while preserving its midbottom anchor.

            Args:
                w: new body width in pixels.
                h: new body height in pixels.
        """
        midbottom = self.body.midbottom # Save anchor before resize - Rect.size assignment moves the topleft
        self.body.size = (w, h)
        self.body.midbottom = midbottom # Restore anchor so the entity doesn't shift position on resize

    def sync_img_rect_to_body(self):
        """
            Align the visible image rect to the physics body anchor.

            The animation frame includes transparent padding around the character
            sprite. When the frame is flipped horizontally the padding shifts,
            causing the sprite to drift left or right relative to the body.
            This method corrects for that by anchoring the bounding pixels of the
            frame to the body's midbottom rather than the full frame rect.
        """
        bounds = self.image.get_bounding_rect() # Tight rect around non-transparent pixels in the current frame
        self.img_rect = self.image.get_rect()
        self.img_rect.topleft = (
            self.body.midbottom[0] - bounds.midbottom[0], # Shift so the visible pixel anchor lines up with the physics body
            self.body.midbottom[1] - bounds.midbottom[1],
        )
        self.sprite_bounds = bounds.move(self.img_rect.topleft) # World-space bounding rect used for combat hit detection