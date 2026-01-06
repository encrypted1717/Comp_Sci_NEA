import pygame


class CollisionManager:
    def __init__(self, entities : pygame.sprite.Group ,colliders : pygame.sprite.Group) -> None:
        self.dt = 1
        self.entities = entities
        self.colliders = colliders

    def resolve_entity(self, dt : float):
        self.dt = dt
        for entity in self.entities:
            entity.on_ground = False
            for collider in self.colliders:
                if collider.collider_type == "ground":
                    self.__resolve_ground(entity, collider)
            if entity.sprite == "player1":
                collided_entities = pygame.sprite.spritecollide(entity, self.entities, False)
                for collided_entity in collided_entities:
                    if collided_entity is entity:
                        continue
                    self.__resolve_enemy(entity, collided_entity)


    def __resolve_ground(self, entity, ground):
        # Only resolve if falling
        if entity.velocity.y >= 0 and pygame.sprite.collide_rect(entity, ground):
            entity.rect.bottom = ground.rect.top
            entity.position.y = entity.rect.bottom
            entity.img_rect.bottom = entity.position.y
            entity.velocity.y = 0
            entity.on_ground = True
            entity.jumps = 0
            entity.air_time = 0.0

    def __resolve_enemy(self, entity, enemy):
        if pygame.sprite.collide_rect(entity, enemy):
            if entity.flip_x:
                enemy.velocity.x -= 1300 * self.dt
                enemy.img_rect.bottom = entity.position.x
            else:
                enemy.velocity.x += 1300 * self.dt
                enemy.img_rect.bottom = entity.position.x