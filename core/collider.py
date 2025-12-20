import pygame


class Collider(pygame.sprite.Sprite):
    def __init__(self, rect: pygame.Rect, collider: str) -> None:
        super().__init__()
        self.image = pygame.Surface(rect.size)
        self.image.fill(pygame.Color('yellow'))
        self.rect = self.image.get_rect(bottom=rect.top)
        self.collider_type = collider