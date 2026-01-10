import logging
import pygame
from graphics.animation_manager import AnimationManager

class Entity(pygame.sprite.Sprite):
    def __init__(self, start_position: tuple, sprite_type: str, health = 100):
        super().__init__()
        # Logging setup
        self.__log = logging.getLogger(__name__)
        self.__log.info("Creating an entity sprite_type = %s pos = %s", sprite_type, start_position)
        # Main setup
        self.vector = pygame.math.Vector2
        self.flip_x = False # facing left or right (right is false)
        self.dt = None
        self.keys = None
        self.events = None
        # Setup animations
        self.animation_manager = AnimationManager()
        self.animation_manager.load_animation("default", "assets\\characters\\default\\fighting\\Animations\\punch_1.png", scale = 2.0, frame_indices = [0])
        self.animation_manager.load_animation("punch_1", "assets\\characters\\default\\fighting\\Animations\\punch_1.png", scale = 2.0)
        self.animation_manager.load_animation("jump", "assets\\characters\\default\\movement\\Animations\\upward_jump.png", scale = 2.0, frame_indices = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 3, 2, 1, 0])
        self.animation_manager.load_animation("double_jump", "assets/characters/default/movement/Animations/double_jump.png", scale = 2.0)
        self.animation_manager.set_animation("default", restart = True)
        # Kinematic vectors / equations
        self.velocity = self.vector(0, 0) # No moving at the start
        self.acceleration = self.vector(0, 0) # No accel at the start
        # Kinematic constants
        self.horizontal_acceleration = 2000.0
        self.horizontal_friction = 11 # Depending on the situation this is also air resistance
        self.jump_force = 600
        self.double_jump_force = 700
        self.gravity = 1250
        # Setup sprite
        self.sprite = sprite_type
        self.rect = pygame.rect.Rect(start_position, (128, 128))  # size of player
        self.image = pygame.Surface(self.rect.size)
        self.img_rect = None
        # Sprite attributes
        self.health = health
        self.punch_1_damage = 6
        # Keybinds
        if self.sprite == "player1":
            self.binds = {
                "left": ("key", pygame.K_a),
                "right": ("key", pygame.K_d),
                "jump":("key", pygame.K_w),
                "down": ("key", pygame.K_s),
                "punch": ("mouse", 1) #left click
            }
        elif self.sprite == "player2":
            self.binds = {
                "left": ("key", pygame.K_LEFT),
                "right": ("key", pygame.K_RIGHT),
                "jump": ("key", pygame.K_UP),
                "down": ("key", pygame.K_DOWN),
                "punch": ("key", pygame.K_RSHIFT),
            }
        # Movement
        self.position = self.vector(self.rect.midbottom)
        self.on_ground = False
        self.jumps = 2
        self.air_time = 0.0
        self.double_jump_delay = 0.01  # seconds
        # Unique ID
        self.entity_id = id(self)
        # Combat
        self.attacking = False
        self.attack_name = None
        self.attack_id = 0 # Increments each time an attack starts
        self.combos = 0
        self.__log.info("Entity created id = %s sprite_type = %s", id(self), sprite_type)

    # noinspection PyTypeChecker
    def update(self, dt):
        self.dt = dt
        if not self.on_ground:
            self.air_time += self.dt
        else:
            self.air_time = 0.0
        # Calc Jumping
        self.velocity.y += self.gravity * self.dt
        # Calc new kinematics
        self.acceleration.x -= self.velocity.x * self.horizontal_friction  # Faster you move friction is experienced
        self.velocity += self.acceleration * self.dt  # Add vectors together
        self.position += self.velocity * self.dt + 0.5 * self.acceleration * (self.dt ** 2)
        # Update Sprite
        self.animation_manager.update(self.dt, 0.05)
        self.image = pygame.transform.flip(self.animation_manager.get_frame(), self.flip_x, False)
        self.img_rect = self.image.get_rect(midbottom = self.position)
        self.rect = self.image.get_bounding_rect().move(self.img_rect.topleft) # used for collisions
        self.update_attack_state()

    def event_handler(self, events):
        self.acceleration = self.vector(0, 0)
        self.keys = pygame.key.get_pressed()
        # Held Down
        if self.__is_held("left"):
            self.acceleration.x = -self.horizontal_acceleration
            self.flip_x = True
        elif self.__is_held("right"):
            self.acceleration.x = self.horizontal_acceleration
            self.flip_x = False

        # Event-based actions (single press)
        for event in events:
                # Jump / Double Jump
                jump_dev, jump_bind = self.binds["jump"] # Dev is short for the device i.e. keyboard or mouse
                if jump_dev == "key" and event.type == pygame.KEYDOWN and event.key == jump_bind: # Is a key being pressed down and is it the jump bind
                    self.__jump()
                elif jump_dev == "mouse" and event.type == pygame.MOUSEBUTTONDOWN and event.button == jump_bind:
                    self.__jump()

                # Punch 
                punch_dev, punch_bind = self.binds["punch"]
                if punch_dev == "key" and event.type == pygame.KEYDOWN and event.key == punch_bind:
                    self.start_attack("punch_1")
                elif punch_dev == "mouse" and event.type == pygame.MOUSEBUTTONDOWN and event.button == punch_bind:
                    self.start_attack("punch_1")

        if not self.animation_manager.is_playing() or self.animation_manager.get_name() == "default":
            self.animation_manager.set_animation("default", restart = True)

    def __is_held(self, action: str):
        device, code = self.binds[action]
        if device == "key":
            return self.keys[code]
        elif device == "mouse":
            mouse_buttons = pygame.mouse.get_pressed(5) # Five allows people to bind their back and forward side buttons on a mouse
            idx = code - 1 # Unlike event.type mouse indexes start from 0 rather than 1
            if not 0 <= idx < len(mouse_buttons):
                self.__log.warning("Bind uses mouse button %s, but only %s buttons are tracked", code, len(mouse_buttons))
                return False
            else:
                return mouse_buttons[idx]
        else:
            return False

    def __jump(self):
        if self.jumps == 0:
            self.velocity.y = -self.jump_force
            self.animation_manager.set_animation("jump")
            self.jumps += 1
        elif self.jumps == 1 and self.air_time >= self.double_jump_delay:
            self.velocity.y = -self.double_jump_force
            self.animation_manager.set_animation("double_jump")
            self.jumps += 1
        else:
            self.acceleration.y = 0


    def start_attack(self, name: str):
        self.attacking = True
        self.attack_name = name
        self.attack_id += 1
        self.animation_manager.set_animation(name, restart=True)

    def update_attack_state(self):
        # If we started an attack and the animation finished, stop the attack
        if self.attacking and not self.animation_manager.is_playing():
            self.attacking = False
            self.attack_name = None

    def set_bind(self, action: str, device: str, code: int):
        self.binds[action] = (device, code)