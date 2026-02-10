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
                    self.__resolve_player(entity, collided_entity)


    def __resolve_ground(self, entity, ground):
        # Only resolve if falling
        if entity.velocity.y >= 0 and pygame.sprite.collide_rect(entity, ground):
            entity.rect.bottom = ground.rect.top
            entity.position.y = entity.rect.bottom
            entity.img_rect.bottom = entity.position.y
            entity.velocity.y = 0
            entity.on_ground = True
            entity.jumps_remaining = 2
            entity.air_time = 0.0

    def __resolve_player(self, player1, player2):
        overlap = player1.rect.clip(player2.rect)
        # Decide axis
        if overlap.width < overlap.height:
            self.__resolve_horizontal_players(player1, player2, overlap.width)
        else:
            self.__resolve_vertical_players(player1, player2, overlap.height)

    def __resolve_horizontal_players(self, player1, player2, overlap):
        player1_left = player1.rect.centerx < player2.rect.centerx
        push = overlap / 2

        # Separate
        if player1_left:
            player1.position.x -= push
            player2.position.x += push
        else:
            player1.position.x += push
            player2.position.x -= push

        player1.img_rect.midbottom = player1.position
        player2.img_rect.midbottom = player2.position
        player1.rect = player1.image.get_bounding_rect().move(player1.img_rect.topleft)
        player2.rect = player2.image.get_bounding_rect().move(player2.img_rect.topleft)

        # Velocity logic
        if player1.velocity.x != 0 and player2.velocity.x != 0:
            # Both moving → stop both
            player1.velocity.x = 0
            player2.velocity.x = 0
        else:
            # One moving → push the other
            if abs(player1.velocity.x) > abs(player2.velocity.x):
                player2.velocity.x = player1.velocity.x * 0.6
                player1.velocity.x *= 0.4
            else:
                player1.velocity.x = player2.velocity.x * 0.6
                player2.velocity.x *= 0.4

    def __resolve_vertical_players(self, top_player, bottom_player, overlap):
        if top_player.rect.centery < bottom_player.rect.centery:
            # top lands on bottom
            top_player.position.y -= overlap
            top_player.velocity.y = 0
            top_player.on_ground = True
            top_player.jumps = 0
            top_player.air_time = 0.0

            # Move with bottom
            top_player.velocity.y = bottom_player.velocity.y

        else:
            # bottom hits top from below
            bottom_player.position.y += overlap
            bottom_player.velocity.y = 0

        top_player.img_rect.midbottom = top_player.position
        bottom_player.img_rect.midbottom = bottom_player.position
        top_player.rect = top_player.image.get_bounding_rect().move(top_player.img_rect.topleft)
        bottom_player.rect = bottom_player.image.get_bounding_rect().move(bottom_player.img_rect.topleft)