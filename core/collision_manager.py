import pygame


class CollisionManager:
    def __init__(self, entities : pygame.sprite.Group ,colliders : pygame.sprite.Group) -> None:
        self.entities = entities
        self.colliders = colliders

    def resolve_entity(self):
        for entity in self.entities:
            entity.on_ground = False
            for collider in self.colliders:
                if collider.collider_type == "ground":
                    self.__resolve_ground(entity, collider)

    def __resolve_ground(self, entity, ground):
        # Only resolve if falling
        if entity.velocity.y >= 0 and pygame.sprite.collide_rect(entity, ground):
            entity.rect.bottom = ground.rect.top
            entity.position.y = entity.rect.bottom
            entity.velocity.y = 0
            entity.on_ground = True
            entity.jumps = 0
            entity.air_time = 0.0