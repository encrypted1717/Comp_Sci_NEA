"""Tile Map Generation"""
import random

import pygame
import logging
from random import choice
from core.collider import Collider
from utils.tile_map import TileMap


"""
0 = Sky
1 = Dirt
"""
class MapGeneration:
    def __init__(self):
        # Logging setup
        self.log = logging.getLogger(__name__)
        self.log.info("Initialising MapGeneration module")
        # Virtual/design map setup
        self.tile_size = 40
        self.game_map = choice(TileMap.maps)
        self.solid_tiles = []
        self.non_solid_tiles = []

    # TODO Make function be able to work with any map that is passed as a param
    def create_map(self):
        # Empty/reset the lists so it clears previous colliders
        self.solid_tiles = []
        self.non_solid_tiles = []

        tile_grid = self.game_map
        rows = len(tile_grid)
        columns = len(tile_grid[0])
        tile_size = self.tile_size

        # Create a list of same dimensions as tile grid and fill with False
        visited = []
        for row_index in range(rows):
            visited_row = []
            for column_index in range(columns):
                visited_row.append(False)
            visited.append(visited_row)

        """
        A rectangle can only start at a tile that is:
            
            - Not already part of a previous rectangle (hasn't been visited yet)
            - Solid (is a solid tile)
            
        """
        for row_index in range(rows):
            for column_index in range(columns):
                if visited[row_index][column_index]:
                    continue
                if not self.is_solid_tile(tile_grid, row_index, column_index):
                    continue

                # Grow width to the right
                rectangle_width = 1 # In tiles
                while True:
                    next_column = column_index + rectangle_width
                    if next_column >= columns:
                        break
                    if visited[row_index][next_column]:
                        break
                    if not self.is_solid_tile(tile_grid, row_index, next_column):
                        break
                    rectangle_width += 1

                # Grow height downward, the full width needs to be solid + unvisited
                rectangle_height = 1
                while True:
                    next_row = row_index + rectangle_height
                    if next_row >= rows:
                        break

                    can_grow_down = True
                    for column in range(column_index, column_index + rectangle_width):
                        if visited[next_row][column] or not self.is_solid_tile(tile_grid, next_row, column):
                            can_grow_down = False
                            break

                    if not can_grow_down:
                        break

                    rectangle_height += 1

                # Mark the rectangle area as visited
                for row in range(row_index, row_index + rectangle_height):
                    for column in range(column_index, column_index + rectangle_width):
                        visited[row][column] = True

                # Create Collider
                rect_x = column_index * tile_size
                rect_y = row_index * tile_size
                rect_width = rectangle_width * tile_size
                rect_height = rectangle_height * tile_size

                merged_rect = pygame.Rect(
                    rect_x,
                    rect_y,
                    rect_width,
                    rect_height,
                )
                self.solid_tiles.append(Collider(merged_rect, "platform"))
        self.log.info("Generating Map")

    def is_solid_tile(self, grid: list, row: int, column: int) -> bool:
        return grid[row][column] > 0