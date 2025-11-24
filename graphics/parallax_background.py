import pygame


#loading background layers and making sure addresses are portable as they refer to the files within the actual game folder.
class Background:
    def __init__(self):
        self.__count = 0
        self.__img_bg = pygame.image.load(
            "assets\\images\\background\\parallax_mountain_pack\\layers\\parallax-mountain-bg.png"
            ).convert()

        self.__img_fg = pygame.image.load(
            "assets\\images\\background\\parallax_mountain_pack\\layers\\parallax-mountain-foreground-trees.png"
            ).convert_alpha()

        self.__img_far_mountains = pygame.image.load(
            "assets\\images\\background\\parallax_mountain_pack\\layers\\parallax-mountain-montain-far.png"
            ).convert_alpha()

        self.__img_mountains = pygame.image.load("assets\\images\\background\\parallax_mountain_pack/layers/parallax-mountain-mountains.png"
            ).convert_alpha()

        self.__img_trees = pygame.image.load(
            "assets\\images\\background\\parallax_mountain_pack\\layers\\parallax-mountain-trees.png"
            ).convert_alpha()

        self.__background = [
            {"img": self.__img_bg, "speed": 0.05, "x": -1150},  #could have a less complex data structure but this wouldn't allow me to have different speeds or wtv
            {"img": self.__img_far_mountains, "speed": 0.3, "x": 0},
            {"img": self.__img_mountains, "speed": 0.5, "x": 0},
            {"img": self.__img_trees, "speed": 0.8, "x": 0},
            {"img": self.__img_fg, "speed": 3, "x": 0} #have to include factor of y to minus when scaling
            ]

    def convert_background(self):
        #converts all images except the first to be transparent
        for image in self.background:
            self.__count += 1
            if self.__count == 1:
                image["img"].convert()
            else:
                image["img"].convert_alpha()

    def get_background(self):
        return self.__background