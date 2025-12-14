import pygame
from graphics.animation_manager import AnimationManager

class Entity(pygame.sprite.Sprite):
    def __init__(self, start_position: tuple):
        pygame.sprite.Sprite.__init__(self)
        self.vector = pygame.math.Vector2
        self.flip = False
        self.dt = None
        self.keys = None
        self.events = None
        # Setup animations
        self.animation_manager = AnimationManager(0.2)
        self.animation_manager.load_animation("default", "assets\\characters\\default\\fighting\\Animations\\punch_1.png", scale = 3.0, frame_indices = [0])
        self.animation_manager.load_animation("punch_1", "assets\\characters\\default\\fighting\\Animations\\punch_1.png", scale = 3.0)
        self.animation_manager.load_animation("jump", "assets\\characters\\default\\movement\\Animations\\upward_jump.png", scale = 3.0)
        self.animation_manager.set_animation("default", loop = True, reset = False)
        # Kinematic vectors / equations
        self.position = self.vector(start_position)
        self.velocity = self.vector(0, 0) # No moving at the start
        self.acceleration = self.vector(0, 0) # No accel at the start
        # Kinematic constants
        self.horizontal_acceleration = 500.0
        self.horizontal_friction = 50 # Depending on the situation this is also air resistance

    def event_handler(self, events):
        self.acceleration = self.vector(0, 0)
        self.keys = pygame.key.get_pressed()
        if self.keys[pygame.K_a]:
            self.acceleration.x = -self.horizontal_acceleration
            self.flip = True
        elif self.keys[pygame.K_d]:
            self.acceleration.x = self.horizontal_acceleration
            self.flip = False
        else:
            self.acceleration.x = 0 # Check if this line even has an effect

        # Handle discrete actions (jump, attack, etc.)
        self.events = events
        if not self.animation_manager.is_playing():
            for event in self.events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_w:  # Jump
                        self.animation_manager.set_animation("jump")

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.animation_manager.set_animation("punch_1")

                else:
                    self.animation_manager.set_animation("default")

    def update(self, dt):
        self.dt = dt
        # Calc new kinematics
        self.acceleration.x -= self.velocity.x * self.horizontal_friction  # Faster you move friction is experienced
        self.velocity += self.acceleration * self.dt  # Add vectors together
        self.position += self.velocity * self.dt + 0.5 * self.acceleration * (self.dt ** 2)
        self.animation_manager.update(self.dt)
        self.frame = self.animation_manager.get_frame()
        self.rect = self.frame.get_rect(bottomleft=self.position)

    def draw(self, window):
        window.blit(pygame.transform.flip(self.frame, self.flip, False), self.rect)