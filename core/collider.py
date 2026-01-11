import pygame


class Collider(pygame.sprite.Sprite):
    def __init__(self, rect: pygame.Rect, collider: str) -> None:
        super().__init__()
        self.image = pygame.Surface(rect.size)
        self.image.fill(pygame.Color('brown'))
        self.rect = rect.copy()
        self.collider_type = collider