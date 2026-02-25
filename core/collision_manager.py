import pygame


class CollisionManager:
    def __init__(self, entities : pygame.sprite.Group ,colliders : pygame.sprite.Group) -> None:
        self.dt = 1
        self.entities = entities
        self.colliders = colliders

    def resolve_entity(self, dt : float):
        self.dt = dt
        for entity in self.entities:
            # Resolve platform
            for collider in self.colliders:
                if collider.collider_type == "platform":
                    self.__resolve_platform(entity, collider)
            if entity.sprite == "player1":
                collided_entities = pygame.sprite.spritecollide(entity, self.entities, False)
                for collided_entity in collided_entities:
                    if collided_entity is entity:
                        continue
                    self.__resolve_player(entity, collided_entity)

    def __resolve_platform(self, entity, collider):
        platform_rect = collider.rect
        body = entity.body

        if not body.colliderect(platform_rect):
            return

        overlap = body.clip(platform_rect)

        # Previous feet position (midbottom.y before this frame moved)
        prev_feet_y = entity.position.y - (entity.velocity.y * self.dt)

        # Platform classification
        platform_is_tall = platform_rect.height > body.height

        # --- One-way landing from above ---
        # If feet were above the platform last frame and the player is falling,
        # allow landing on the top surface.
        landing_tolerance = max(4, int(abs(entity.velocity.y * self.dt)) + 1) # Explain
        coming_from_above = prev_feet_y <= platform_rect.top + landing_tolerance
        falling = entity.velocity.y >= 0
        step_height = 40 * entity.sprite_scale
        step = platform_rect.top >= entity.body.bottom - step_height
        if falling and (coming_from_above or step):
            # Snap feet to platform top
            entity.position.y = platform_rect.top
            entity.velocity.y = 0
            entity.on_ground = True
            entity.jumps_remaining = 2
            entity.air_time = 0.0

            entity.body.midbottom = (int(entity.position.x), int(entity.position.y))
            entity.rect = entity.body
            entity.sync_img_rect_to_body()
            return

        # --- From below / inside short platform ---
        # Short platforms are pass-through from below and from the sides.
        if not platform_is_tall:
            return

        # --- Tall platforms act like walls/barriers ---
        # Only resolve horizontally here (top landing was already handled above).
        if body.centerx < platform_rect.centerx:
            entity.position.x -= overlap.width
        else:
            entity.position.x += overlap.width

        entity.velocity.x = 0
        entity.body.midbottom = (int(entity.position.x), int(entity.position.y))
        entity.rect = entity.body
        entity.sync_img_rect_to_body()

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

        player1.body.midbottom = player1.position
        player2.body.midbottom = player2.position
        player1.rect = player1.body
        player2.rect = player2.body
        player1.sync_img_rect_to_body()
        player2.sync_img_rect_to_body()

    def __resolve_vertical_players(self, top_player, bottom_player, overlap):
        if top_player.rect.centery < bottom_player.rect.centery:
            # top lands on bottom
            top_player.position.y -= overlap
            top_player.velocity.y = 0
            top_player.on_ground = True
            top_player.jumps_remaining = 2
            top_player.air_time = 0.0
            # Move with bottom
            top_player.velocity.y = bottom_player.velocity.y

        else:
            # bottom hits top from below
            bottom_player.position.y += overlap
            bottom_player.velocity.y = 0

        top_player.body.midbottom = top_player.position
        bottom_player.body.midbottom = bottom_player.position
        top_player.rect = top_player.body
        bottom_player.rect = bottom_player.body
        top_player.sync_img_rect_to_body()
        bottom_player.sync_img_rect_to_body()