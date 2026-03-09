"""
    Collision resolution utilities for game.

    This module provides the CollisionManager class, which resolves physics
    collisions between entities and colliders each frame. It handles one-way
    platform landings, ceiling hits, wall pushes for tall platforms, and
    player-versus-player separation. Resolution is intentional and positional -
    entities are moved out of overlaps rather than using impulse-based responses.
"""

import pygame
import logging


class CollisionManager:
    """
        Resolve physics collisions between entities and the world each frame.

        CollisionManager owns two sprite groups - entities and colliders - and
        exposes a single public method, resolve_entity, which should be called
        once per frame after entity physics have been updated. All resolution
        is positional: overlapping bodies are separated by the minimum distance
        needed to remove the overlap, and velocities are zeroed or redistributed
        accordingly.

        Platform types:
            "platform" - short, one-way tiles. Entities land on top but pass
                         through from below and from the sides.
            tall (height > body height) - fully solid. Blocks ceiling and walls
                         in addition to the top surface.
    """

    def __init__(self, entities: pygame.sprite.Group, colliders: pygame.sprite.Group) -> None:
        """
            Initialise the collision manager with the entity and collider groups.

            Args:
                entities:  sprite group containing all active Entity instances.
                colliders: sprite group containing all active Collider instances.
        """
        # Logging setup
        self.log = logging.getLogger(__name__)
        self.log.info("Initialising Collision Manager module")

        # Setup
        self.dt = 1 # Delta time stored per-frame so resolution helpers can access it
        self.entities = entities # All living entities - iterated each frame for collision checks
        self.colliders = colliders # All world tiles - checked against every entity

    def resolve_entity(self, dt: float):
        """
            Resolve all entity-platform and player-player collisions for this frame.

            Platform collisions are checked for every entity. Player-player
            separation is only run from player1's perspective to avoid double
            resolution - player1 pushes both bodies, which is sufficient.

            Args:
                dt: delta time in seconds since the last frame - stored and used
                    by __resolve_platform to calculate landing tolerance.
        """
        self.dt = dt
        for entity in self.entities:
            # Resolve each platform collider against this entity in turn
            for collider in self.colliders:
                if collider.collider_type == "platform":
                    self.__resolve_platform(entity, collider)

            # Player-player separation is driven by player1 only to avoid resolving the same pair twice
            if entity.sprite == "player1":
                collided_entities = pygame.sprite.spritecollide(entity, self.entities, False)
                for collided_entity in collided_entities:
                    if collided_entity is entity:
                        continue  # Skip self - spritecollide includes the queried sprite in its results
                    self.__resolve_player(entity, collided_entity)

    def __resolve_platform(self, entity, collider):
        """
            Resolve a single entity-platform overlap.

            Handles three cases in priority order:
            1. Landing from above - snaps feet to platform top and restores jumps.
            2. Pass-through for short platforms hit from below or the sides.
            3. Ceiling and wall resolution for tall platforms.

            Args:
                entity:   the Entity to resolve.
                collider: the Collider tile to test against.
        """
        platform_rect = collider.rect
        body = entity.body

        if not body.colliderect(platform_rect):
            return # No overlap - nothing to resolve

        overlap = body.clip(platform_rect) # Rect representing the overlapping region between body and platform

        # Reconstruct feet position from last frame so we can tell which side the entity approached from
        prev_feet_y = entity.position.y - (entity.velocity.y * self.dt)

        platform_is_tall = platform_rect.height > body.height # Tall platforms block all sides; short ones are one-way

        # Landing from above - allow the entity to land if their feet were at or above the platform top last frame.
        # landing_tolerance grows with velocity so fast-moving entities don't tunnel through at high frame times.
        landing_tolerance = max(4, int(abs(entity.velocity.y * self.dt)) + 1)
        coming_from_above = prev_feet_y <= platform_rect.top + landing_tolerance
        falling = entity.velocity.y >= 0  # Positive y velocity means moving downward
        step_height = 40 * entity.sprite_scale
        # Step detection lets the entity auto-climb short lips without requiring a jump
        step = not platform_is_tall and platform_rect.top >= entity.body.bottom - step_height
        if falling and (coming_from_above or step):
            # Snap feet to the platform surface and kill downward momentum
            entity.position.y = platform_rect.top
            entity.velocity.y = 0
            if not entity.on_ground: # Only refill jumps on the frame of landing, not every frame while standing
                entity.jumps_remaining = 2
                entity.air_time = 0.0
            entity.on_ground = True

            entity.body.midbottom = (int(entity.position.x), int(entity.position.y))
            entity.rect = entity.body
            entity.sync_img_rect_to_body()
            return

        # Short platforms are pass-through from below and the sides - only their top surface is solid
        if not platform_is_tall:
            return

        # Ceiling resolution - entity moving upward has clipped into the underside of a tall platform
        hitting_ceiling = entity.velocity.y < 0 and body.top < platform_rect.bottom and body.top >= platform_rect.top
        if hitting_ceiling:
            entity.position.y = platform_rect.bottom + body.height  # Push entity down so head clears the ceiling
            entity.velocity.y = 0 # Kill upward momentum so they don't keep pressing into it
            entity.body.midbottom = (int(entity.position.x), int(entity.position.y))
            entity.rect = entity.body
            entity.sync_img_rect_to_body()
            return

        # Horizontal wall resolution - push the entity out sideways based on which side their center is on
        if body.centerx < platform_rect.centerx:
            entity.position.x -= overlap.width # Entity is to the left - push further left
        else:
            entity.position.x += overlap.width # Entity is to the right - push further right

        entity.velocity.x = 0 # Kill horizontal velocity so the entity doesn't keep accelerating into the wall
        entity.body.midbottom = (int(entity.position.x), int(entity.position.y))
        entity.rect = entity.body
        entity.sync_img_rect_to_body()

    def __resolve_player(self, player1, player2):
        """
            Separate two overlapping players by resolving along the shortest axis.

            Chooses horizontal or vertical resolution based on which axis has the
            smaller overlap, then delegates to the appropriate helper.

            Args:
                player1: the first Entity (always the one with sprite == "player1").
                player2: the second Entity.
        """
        overlap = player1.rect.clip(player2.rect) # Overlapping region between the two player bodies

        # Resolve along the axis with the smaller overlap to minimise visible displacement
        if overlap.width < overlap.height:
            self.__resolve_horizontal_players(player1, player2, overlap.width)
        else:
            self.__resolve_vertical_players(player1, player2, overlap.height)

    # TODO fix bug around jumping over player?
    def __resolve_horizontal_players(self, player1, player2, overlap):
        """
            Push two players apart horizontally and redistribute their velocities.

            Each player is moved by half the overlap so the separation is symmetric.
            Velocity is redistributed based on which player is moving - if both are
            moving they stop each other, otherwise the stationary one is pushed.

            Args:
                player1: the first Entity.
                player2: the second Entity.
                overlap: the horizontal overlap distance in pixels.
        """
        player1_left = player1.rect.centerx < player2.rect.centerx # True if player1 is to the left
        push = overlap / 2 # Each player absorbs half the separation so neither moves more than necessary

        # Move each player outward by their half of the overlap
        if player1_left:
            player1.position.x -= push
            player2.position.x += push
        else:
            player1.position.x += push
            player2.position.x -= push

        # Redistribute velocity based on which player was moving
        if player1.velocity.x != 0 and player2.velocity.x != 0:
            # Both moving toward each other - stop both to simulate a collision
            player1.velocity.x = 0
            player2.velocity.x = 0
        else:
            # One player is stationary - the moving player transfers a fraction of velocity to the stationary one
            if abs(player1.velocity.x) > abs(player2.velocity.x):
                player2.velocity.x = player1.velocity.x * 0.6 # Stationary player gets 60% of the moving player's speed
                player1.velocity.x *= 0.4 # Moving player retains 40% to simulate partial transfer
            else:
                player1.velocity.x = player2.velocity.x * 0.6
                player2.velocity.x *= 0.4

        # Sync physics body, rect, and image rect to the updated positions
        player1.body.midbottom = player1.position
        player2.body.midbottom = player2.position
        player1.rect = player1.body
        player2.rect = player2.body
        player1.sync_img_rect_to_body()
        player2.sync_img_rect_to_body()

    def __resolve_vertical_players(self, top_player, bottom_player, overlap):
        """
            Resolve a vertical overlap between two players - one standing on the other.

            The player whose center is higher is treated as the one on top. They are
            snapped upward by the full overlap and their jumps are refilled as if
            they had landed on a platform. The lower player is pushed down if hit
            from below.

            Args:
                top_player:    the Entity whose center is higher (the one on top).
                bottom_player: the Entity whose center is lower (the one below).
                overlap:       the vertical overlap distance in pixels.
        """
        if top_player.rect.centery < bottom_player.rect.centery:
            # Top player has landed on bottom player - treat it like a platform landing
            top_player.position.y -= overlap
            top_player.velocity.y = 0
            if not top_player.on_ground: # Only refill jumps on the frame of landing
                top_player.jumps_remaining = 2
                top_player.air_time = 0.0
            top_player.on_ground = True
            top_player.velocity.y = bottom_player.velocity.y # Inherit bottom player's vertical velocity so they move together
        else:
            # Bottom player has jumped into the top player from below - push them down
            bottom_player.position.y += overlap
            bottom_player.velocity.y = 0

        # Sync physics body, rect, and image rect to the updated positions
        top_player.body.midbottom = top_player.position
        bottom_player.body.midbottom = bottom_player.position
        top_player.rect = top_player.body
        bottom_player.rect = bottom_player.body
        top_player.sync_img_rect_to_body()
        bottom_player.sync_img_rect_to_body()