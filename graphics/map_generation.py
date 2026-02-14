"""Tile Map Generation"""

import pygame
from core.collider import Collider
from utils.tile_map import TileMap


"""
0 = Sky
1 = Dirt
"""
class MapGeneration:
    def __init__(self):
        # Virtual/design map setup
        self.tile_size = 40
        self.game_map = TileMap.game_map1
        self.solid_tiles = []
        self.non_solid_tiles = []

    def create_map(self):
        # Empty/reset the lists
        self.solid_tiles = []
        self.non_solid_tiles = []

        for row in range(len(self.game_map)):
            for column in range(len(self.game_map[row])):
                tile_code = self.game_map[row][column]
                if tile_code == 0: # Empty tile
                    continue
                x = column * self.tile_size # do u need to multiply by a factor depending on resolution
                y = row * self.tile_size # len(game_map[0])
                if tile_code == 1:
                    tile_rect = pygame.Rect(x, y, self.tile_size, self.tile_size)
                    self.solid_tiles.append(Collider(tile_rect, "ground"))
                else:
                    # I add more tile types here
                    pass