import pygame


class Animations:
    def __init__(self):
        self.default_img = pygame.image.load("assets\\characters\\default\\fighting\\Animations\\Punch_1.png").convert_alpha()
        self.default_animation = [pygame.transform.scale_by(self.default_img.subsurface(pygame.Rect(0, 0, 128, 128)), 3)]

        self.punch_img = pygame.image.load("assets\\characters\\default\\fighting\\Animations\\Punch_1.png").convert_alpha()
        self.punch_animation = []
        for phase in range(5):
            self.punch_img = pygame.transform.scale_by(self.default_img.subsurface(pygame.Rect(128 * phase, 0, 128, 128)),3)
            self.punch_animation.append(self.punch_img)

        self.animations = {
            "idle": [self.default_animation, len(self.default_animation) - 1],
            "punch": [self.punch_animation, len(self.punch_animation) - 1]
            }

    def get_animations(self):
        return self.animations
