import pygame


# Loading background layers and making sure addresses are portable as they refer to the files within the actual game folder.
class Background:
    def __init__(self):
        self.__width, self.__height = (0, 0)
        self.__design_width = 1920

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

        # Each layer stores scaled and original image
        self.__background = [
            {"img_original": self.__img_bg, "img": self.__img_bg, "speed": 2, "x": -1150},  #could have a less complex data structure but this wouldn't allow me to have different speeds or wtv
            {"img_original": self.__img_far_mountains, "img": self.__img_far_mountains, "speed": 9, "x": 0},
            {"img_original": self.__img_mountains, "img": self.__img_mountains, "speed": 15, "x": 0},
            {"img_original": self.__img_trees, "img": self.__img_trees, "speed": 24, "x": 0},
            {"img_original": self.__img_fg, "img": self.__img_fg, "speed": 75, "x": 0} #have to include factor of y to minus when scaling
        ]

    def get_background(self):
        return self.__background

    # Call at startup and if window gets resized due to settings
    def resize(self, display_size: tuple):
        self.__width, self.__height = display_size

        for layer in self.__background:
            original = layer["img_original"]
            image_width, image_height = original.get_size()

            # scale to fill screen (no gaps)
            scale = max(self.__width / image_width, self.__height / image_height) * 1.01 # Tiny extra because rounding can cause small seams to appear on the edge of screen

            new_size = (int(image_width * scale), int(image_height * scale)) # Using int() causes rounding so that's why I multiply by 1.01
            layer["img"] = pygame.transform.scale(original, new_size)
            layer["x"] %= layer["img"].get_width() # TODO explain this line better

    def update(self, dt):
        if self.__width != 0:
            for layer in self.__background:
                img = layer["img"]
                layer_width = img.get_width()
                layer["x"] = (layer["x"] - layer["speed"] * dt) % layer_width # Speed in pixels

    def draw(self, surface):
        for layer in self.__background:
            img = layer["img"]
            width = img.get_width()
            x = layer["x"]

            # draw two copies to cover the screen
            surface.blit(img, (x - width, 0))
            surface.blit(img, (x, 0))