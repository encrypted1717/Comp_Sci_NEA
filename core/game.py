import pygame
from core.entity import Entity
from core.config_manager import ConfigManager
from core.button import Button
from graphics.animation_manager import AnimationManager


class Game(Button):
    def __init__(self, window):
        super().__init__()
        # Main Setup
        self.pos_x = 0
        self.pos_y = 0
        self.elapsed_time = 0
        self.dt = 0
        self.events = None
        # Setup animations
        self.is_animating = False
        self.moving_left = False
        self.moving_right = False
        self.jumping = False
        self.left_click = False
        self.animation_cooldown = 0.1 # Seconds
        self.animation_manager = AnimationManager()
        self.default_stance = [self.animation_manager.get_animation("assets\\characters\\default\\fighting\\Animations\\punch_1.png", scale = 3)[0]]
        self.punch_1 = self.animation_manager.get_animation("assets\\characters\\default\\fighting\\Animations\\punch_1.png", scale = 3)
        self.jump = self.animation_manager.get_animation("assets\\characters\\default\\movement\\Animations\\upward_jump.png", scale = 3)
        self.current_animation = self.default_stance
        self.current_frame = 0
        # Player setup
        self.player = Entity((680, 540), 600)
        self.position = self.player.get_position()
        self.rect = self.current_animation[0].get_rect(bottomleft=self.position)
        # Setup Movement
        self.direction = 1 #1/-1 = right or left
        self.flip = False
        self.delta_y = 0
        self.delta_x = 0
        self.window = window
        # Setup configurations
        self.config_manager = ConfigManager()
        self.config = self.config_manager.get_config()
        self.config_manager.open_file("assets\\game_settings\\config_user.ini")

    def event_handler(self, events):
        self.events = events
        for event in self.events:
            #kb press down
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_d:
                    self.moving_right = True
                if event.key == pygame.K_a:
                    self.moving_left = True
                if event.key == pygame.K_w:
                    self.jumping = True
                if event.key == pygame.K_ESCAPE:
                    return "main_menu"

            #kb up
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_d:
                    self.moving_right = False
                if event.key == pygame.K_a:
                    self.moving_left = False
                if event.key == pygame.K_w:
                    self.jumping = False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.left_click = True
        return None

    def update_animation(self):
        self.elapsed_time += self.dt
        if not self.is_animating:
            if self.left_click and self.current_animation != self.punch_1:
                self.current_animation = self.punch_1
                self.current_frame = 0
                self.is_animating = True
                self.left_click = False

            if self.jumping and self.current_animation != self.jump:
                self.current_animation = self.jump
                self.current_frame = 0
                self.is_animating = True
                self.jumping = False

        if self.elapsed_time > self.animation_cooldown: # If the elapsed time is larger than my cooldown
            self.current_frame += 1
            self.elapsed_time = 0
            if self.current_frame >= len(self.current_animation): # Len of current_animation returns total amount of frames
                self.current_frame = 0
                self.current_animation = self.default_stance
                self.is_animating = False

    def draw(self, dt):
        self.dt = dt
        self.update_animation()
        self.delta_x = 0 # Delta means diff between two points
        self.delta_y = 0
        if self.moving_right:
            self.delta_x = self.player.speed * self.dt
            self.flip = False
            self.direction = 1
        if self.moving_left:
            self.delta_x = -self.player.speed * self.dt
            self.flip = True
            self.direction = -1
        self.pos_x = self.delta_x # Needed to avoid truncation error
        self.pos_y = self.delta_y
        self.rect.x += int(self.pos_x)
        self.rect.y += int(self.pos_y)
        self.window.blit(pygame.transform.flip(self.current_animation[self.current_frame], self.flip, False), self.rect) #flip when character goes left
