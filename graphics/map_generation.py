"""Tile Map Generation"""

import pygame
from core.collider import Collider
from graphics.tile_map import TileMap

"""
0 = Sky
1 = Dirt
"""
class MapGeneration:
    def __init__(self, display):
        self.display = display
        #game_variables
        self.tile_size = 60
        self.game_map = TileMap.game_map1

        self.solid_tiles = []
        self.non_solid_tiles = []

    def create_map(self):
        for row in range(len(self.game_map)):
            for column in range(len(self.game_map[row])):
                tile_code = self.game_map[row][column]
                x = column * self.tile_size # do u need to multiply by a factor depending on resolution
                y = row * self.tile_size # len(game_map[0])
                if tile_code == 0: # Empty tile
                    continue
                elif tile_code == 1:
                    tile_rect = pygame.Rect(x, y, self.tile_size, self.tile_size)
                    self.solid_tiles.append(Collider(tile_rect, "ground")) # self.tile = x, y, dirt_tile_image

    def draw_grid(self):
        for tile in self.non_solid_tiles:
            self.display.blit(tile.image, tile)

        for tile in self.solid_tiles:
            self.display.blit(tile.image, tile)