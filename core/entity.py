import pygame


class Entity(pygame.sprite.Sprite):
    def __init__(self, position, speed):
        pygame.sprite.Sprite.__init__(self)
        self.position = position
        self.speed = speed

    def get_entity(self):
        return self.position

    def update(self):
        pass

    def draw(self):
        pass

