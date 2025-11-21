import pygame
#loading background layers and making sure addresses are portable as they refer to the files within the actual game folder.
img_bg = pygame.image.load(
    "assets\\images\\background\\parallax_mountain_pack\\layers\\parallax-mountain-bg.png"
    ).convert()

img_fg = pygame.image.load(
    "assets\\images\\background\\parallax_mountain_pack\\layers\\parallax-mountain-foreground-trees.png"
    ).convert_alpha()

img_far_mountains = pygame.image.load(
    "assets\\images\\background\\parallax_mountain_pack\\layers\\parallax-mountain-montain-far.png"
    ).convert_alpha()

img_mountains = pygame.image.load("assets\\images\\background\\parallax_mountain_pack/layers/parallax-mountain-mountains.png"
    ).convert_alpha()

img_trees = pygame.image.load(
    "assets\\images\\background\\parallax_mountain_pack\\layers\\parallax-mountain-trees.png"
    ).convert_alpha()

background = [
    {"img": img_bg, "speed": 0.05, "x": -1150},  #could have a less complex data structure but this wouldn't allow me to have different speeds or wtv
    {"img": img_far_mountains, "speed": 0.3, "x": 0},
    {"img": img_mountains, "speed": 0.5, "x": 0},
    {"img": img_trees, "speed": 0.8, "x": 0}, {"img": img_fg, "speed": 3, "x": 0} #have to include factor of y to minus when scaling
    ]