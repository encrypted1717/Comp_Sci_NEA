import pygame


class Entity(pygame.sprite.Sprite):
    def __init__(self, position, speed):
        pygame.sprite.Sprite.__init__(self)
        self.position = position
        self.speed = speed

    def get_position(self):
        return self.position

    def set_position(self, position):
        self.position = position


    def update(self):
        pass

    def draw(self):
        pass

