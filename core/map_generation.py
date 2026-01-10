"""Tile Map Generation"""

import pygame
from collider import Collider
import tile_map
from core.tile_map import game_map1

"""
0 = Sky
1 = Dirt
"""
class MapGeneration:
    def __init__(self, display):
        self.map_code = None
        self.display = display
        screen = pygame.display.list_modes()
        self.screen_width, self.screen_height = screen[0][0], screen[0][1]
        #game_variables
        self.tiles = None
        self.tile_size = 120
        self.row_count = 9
        self.column_count = 16
        self.game_width = self.tile_size * self.row_count
        self.game_height = self.tile_size * self.column_count
        self.game_map = tile_map.game_map1
        self.dirt = Collider(pygame.Rect(0, 1080, 1920, 100), "ground")
        self.x = None
        self.y = None
        self.background_tiles = []

    def draw_grid(self):
        for tile in self.background_tiles:
            self.display.blit(tile.image, tile)

        for tile in self.tiles:
            self.display.blit(tile.image, tile)

    def create_map(self):
        for row in range(len(self.game_map)):
            for column in range(len(self.game_map[row])):
                self.map_code = self.game_map[row][column]
                self.x = column * self.tile_size
                self.y = row * self.tile_size
                if self.map_code == 0: # Empty tile
                    continue
                elif self.map_code == 1:
                    self.tiles.append(self.tile)