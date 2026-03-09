"""
    Static collider sprite for game.

    This module provides the Collider class, which represents a single solid
    tile or platform placed in the game world. Colliders are created by
    MapGeneration and registered with CollisionManager to participate in
    entity physics resolution.
"""

import pygame


class Collider(pygame.sprite.Sprite):
    """
        A static rectangular obstacle used for physics collision resolution.

        Collider wraps a pygame.Rect in a Sprite so it can be stored in sprite
        groups and drawn for debugging. The collider_type field tells
        CollisionManager how to treat this tile - platforms are one-way
        (entities can land on top and pass through from below), while tall
        platforms block from all sides.
    """

    def __init__(self, rect: pygame.Rect, collider: str) -> None:
        """
            Initialise the collider from a rect and a type string.

            Args:
                rect:     the position and size of this collider in world space.
                collider: the collision behaviour type - e.g. "platform" for
                          one-way tiles or "wall" for fully solid tiles.
        """
        super().__init__()
        self.image = pygame.Surface(rect.size) # Surface sized to match the rect so it draws correctly
        self.image.fill(pygame.Color('brown')) # Brown fill makes colliders visible when debug drawing is on
        self.rect = rect.copy() # Copy so external rect mutations don't affect this collider
        self.collider_type = collider # Read by CollisionManager to select the correct resolution path