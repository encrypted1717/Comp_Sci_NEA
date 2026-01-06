import pygame
from graphics.animation_manager import AnimationManager

class Entity(pygame.sprite.Sprite):
    def __init__(self, start_position: tuple, sprite_type: str):
        super().__init__()
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
        self.double_jump_force = 100
        self.gravity = 1250
        # Setup sprite
        self.sprite = sprite_type
        self.rect = pygame.rect.Rect(start_position, (128, 128))  # size of player
        self.image = pygame.Surface(self.rect.size)
        self.img_rect = None
        # Movement
        self.position = self.vector(self.rect.midbottom)
        self.on_ground = False
        self.jumps = 2
        self.air_time = 0.0
        self.double_jump_delay = 0.01  # seconds

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

    def event_handler(self, events):
        self.acceleration = self.vector(0, 0)
        self.keys = pygame.key.get_pressed()

        moving_left = pygame.K_a
        moving_right = pygame.K_d
        moving_up = pygame.K_w
        moving_down = pygame.K_s

        if self.sprite == "player2":
            moving_left = pygame.K_LEFT
            moving_right = pygame.K_RIGHT
            moving_up = pygame.K_UP
            moving_down = pygame.K_DOWN

        if self.keys[moving_left]:
            self.acceleration.x = -self.horizontal_acceleration
            self.flip_x = True
        elif self.keys[moving_right]:
            self.acceleration.x = self.horizontal_acceleration
            self.flip_x = False
        self.events = events
        for event in self.events:
                # Jump / Double Jump
                if event.type == pygame.KEYDOWN and event.key == moving_up:
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

                # Punch
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.animation_manager.set_animation("punch_1", restart = True)

        if not self.animation_manager.is_playing() or self.animation_manager.get_name() == "default":
            self.animation_manager.set_animation("default", restart = True)