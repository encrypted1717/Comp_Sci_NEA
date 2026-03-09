"""
    Tile map generation utilities for game.

    This module provides the MapGeneration class, which converts a 2D tile grid
    into a flat list of merged Collider rectangles. Adjacent solid tiles are
    merged into the largest possible rectangles to minimise the number
    of colliders the physics system has to check each frame.

    Tile key
    --------
    0 - Sky (empty, non-solid)
    1 - Dirt (solid)
"""

import pygame
import logging
from random import choice
from core import Collider
from utils import maps


class MapGeneration:
    """
        Convert a 2D tile grid into a list of merged platform Colliders.

        On construction a random map layout is selected from TileMap.maps.
        Calling create_map() then runs a rectangle merge pass over the
        grid and adds to self.solid_tiles with one Collider per merged block.
    """

    def __init__(self):
        """Initialise the module and pick a random map layout."""
        # Logging setup
        self.log = logging.getLogger(__name__)
        self.log.info("Initialising MapGeneration module")
        # Virtual/design map setup
        self.tile_size = 40
        self.game_map = choice(maps)  # Pick a random layout from the available maps
        self.solid_tiles = []
        self.non_solid_tiles = []

    def create_map(self) -> None:
        """
            Parse the current tile grid and build a merged list of platform Colliders.

            Uses a rectangle merging algorithm: for each unvisited solid tile,
            the largest possible rectangle is grown rightward then downward.
            A rectangle can only start at a tile that is:
                - Not already part of a previous rectangle (not yet visited)
                - Solid (tile value > 0)

            Clears and adds to self.solid_tiles on every call, so it is safe
            to call again if the map changes.
        """
        self.log.info("Generating map")

        # Reset lists so stale colliders from a previous call don't persist
        self.solid_tiles = []
        self.non_solid_tiles = []

        tile_grid = self.game_map
        rows = len(tile_grid)
        columns = len(tile_grid[0])
        tile_size = self.tile_size

        # Track which tiles have already been absorbed into a rectangle so they are skipped
        visited = [[False] * columns for _ in range(rows)]

        for row_index in range(rows):
            for column_index in range(columns):
                if visited[row_index][column_index]:
                    continue
                if not self.is_solid_tile(tile_grid, row_index, column_index):
                    continue

                # Grow width to the right until hitting an edge, a visited tile, or a non-solid tile
                rectangle_width = 1  # In tiles
                while True:
                    next_column = column_index + rectangle_width
                    if next_column >= columns:
                        break
                    if visited[row_index][next_column]:
                        break
                    if not self.is_solid_tile(tile_grid, row_index, next_column):
                        break
                    rectangle_width += 1

                # Grow height downward - every tile in the full width of the current row must be solid and unvisited to expand down
                rectangle_height = 1
                while True:
                    next_row = row_index + rectangle_height
                    if next_row >= rows:
                        break

                    # Check every column in the candidate row before committing
                    can_grow_down = all(
                        not visited[next_row][col] and self.is_solid_tile(tile_grid, next_row, col)
                        for col in range(column_index, column_index + rectangle_width)
                    )
                    if not can_grow_down:
                        break

                    rectangle_height += 1

                # Mark every tile inside the merged rectangle as visited
                for row in range(row_index, row_index + rectangle_height):
                    for column in range(column_index, column_index + rectangle_width):
                        visited[row][column] = True

                # Convert tile coordinates to pixel coordinates and create the Collider
                merged_rect = pygame.Rect(
                    column_index * tile_size,
                    row_index * tile_size,
                    rectangle_width * tile_size,
                    rectangle_height * tile_size,
                )
                self.solid_tiles.append(Collider(merged_rect, "platform"))

    def is_solid_tile(self, grid: list, row: int, column: int) -> bool:
        """
            Return True if the tile at (row, column) is solid.

            Any value greater than 0 is treated as solid. 0 represents empty sky.

            Args:
                grid: the 2D tile grid to query.
                row: row index into the grid.
                column: column index into the grid.

            Returns:
                True if the tile is solid, False if it is empty.
        """
        return grid[row][column] > 0