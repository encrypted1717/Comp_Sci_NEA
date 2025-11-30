import pygame
from core.entity import Entity
from core.config_manager import ConfigManager
from core.button import Button
from graphics.animations import Animations


class Game(Button):
    def __init__(self, window):
        super().__init__()
        self.frames = None
        self.last_index = None
        self.now = None
        self.left_click = None
        self.animation_cooldown = 60
        self.animation = Animations()
        self.animations = self.animation.get_animations()
        self.current_animation = self.animations["idle"]
        self.dt = None
        self.current_index = 0
        self.events = None
        self.direction = 1 #1/-1 = right or left
        self.update_time = pygame.time.get_ticks() #time in seconds since init ran
        self.flip = False
        self.moving_left = False
        self.moving_right = False
        self.delta_y = 0
        self.delta_x = 0
        self.window = window
        self.config_manager = ConfigManager()
        self.config = self.config_manager.get_config()
        self.config_manager.open_file("assets\\game_settings\\config_user.ini")
        self.player = Entity((680,540), 200)
        #self.image, self.rect = self.player.get_entity()
        self.position = self.player.get_entity()
        self.image = self.current_animation[0][0]
        self.rect = self.image.get_rect(bottomleft = self.position)

    def event_handler(self, events):
        self.events = events
        for event in self.events:
            #kb press down
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_d:
                    self.moving_right = True
                if event.key == pygame.K_a:
                    self.moving_left = True
                if event.key == pygame.K_ESCAPE:
                    return "main_menu"

            #kb up
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_d:
                    self.moving_right = False
                if event.key == pygame.K_a:
                    self.moving_left = False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.left_click = True
        return None

    def update_animation(self):
        self.now = pygame.time.get_ticks()

        if self.left_click and self.current_animation != self.animations["punch"]:
            self.current_animation = self.animations["punch"]
            self.current_index = 0
            self.update_time = self.now
            self.left_click = False

        if self.now - self.update_time > self.animation_cooldown: #if the elapsed time is larger than my cooldown
            self.frames, self.last_index = self.current_animation
            if self.current_index >= self.last_index:
                self.current_index = 0
                if self.current_animation == self.animations["punch"]:
                    self.current_animation = self.animations["idle"]

            self.image = self.frames[self.current_index]
            self.update_time = self.now #could change name to elapsed time
            self.current_index += 1

    def draw(self, dt):
        self.update_animation()
        self.dt = dt
        self.delta_x = 0
        self.delta_y = 0
        if self.moving_right:
            self.delta_x += self.player.speed * self.dt
            self.flip = False
            self.direction = 1
        if self.moving_left:
            self.delta_x -= self.player.speed * self.dt
            self.flip = True
            self.direction = -1
        self.rect.x += self.delta_x
        self.rect.y += self.delta_y
        self.window.blit(pygame.transform.flip(self.image, self.flip, False), self.rect) #flip when character goes left
