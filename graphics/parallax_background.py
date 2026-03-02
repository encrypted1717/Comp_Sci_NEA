"""
    Parallax scrolling background for menus and game screens.

    This module provides the Background class, which loads and scrolls a set of
    layered mountain images at different speeds to create a parallax depth effect.
    Each layer is scaled to fill the virtual surface and wraps seamlessly.
"""

import pygame


class Background:
    """
        Multi-layer parallax scrolling background.

        Loads a fixed set of mountain landscape layers from a png stored in assets, each scrolling at a
        different speed to simulate depth. The layers are scaled to fill any
        given surface size and wrap horizontally so they scroll indefinitely.
        resize() must be called before the first draw() to scale the images.
    """

    def __init__(self) -> None:
        """Load all background layer images and set up layer state."""
        self.__width  = 0
        self.__height = 0

        # Each layer holds the original image, its current scaled copy, scroll speed, and x position.
        # Speeds are in virtual pixels per second — higher values scroll faster, giving the impression
        # of being closer to the viewer. The dict structure allows each layer to have independent speed.
        layer_path = "assets\\images\\background\\parallax_mountain_pack\\layers\\"
        self.__background = [
            {"img_original": pygame.image.load(layer_path + "parallax-mountain-bg.png").convert(), "img": None, "speed": 2,  "x": -1150, "width": 0},
            {"img_original": pygame.image.load(layer_path + "parallax-mountain-montain-far.png").convert_alpha(), "img": None, "speed": 9,  "x": 0, "width": 0},
            {"img_original": pygame.image.load(layer_path + "parallax-mountain-mountains.png").convert_alpha(), "img": None, "speed": 15, "x": 0, "width": 0},
            {"img_original": pygame.image.load(layer_path + "parallax-mountain-trees.png").convert_alpha(), "img": None, "speed": 24, "x": 0, "width": 0},
            {"img_original": pygame.image.load(layer_path + "parallax-mountain-foreground-trees.png").convert_alpha(), "img": None, "speed": 75, "x": 0, "width": 0},
        ]

    def get_background(self) -> list[dict]:
        """Return the list of layer dicts."""
        return self.__background

    def resize(self, display_size: tuple[int, int]) -> None:
        """
            Scale all layers to fill the given display size.

            Must be called once at startup and again any time the window size changes.
            After scaling, each layer's width is cached in the layer dict so update()
            and draw() never need to call get_width() per frame.

            Args:
                display_size: the (width, height) of the virtual surface to fill.
        """
        self.__width, self.__height = display_size

        for layer in self.__background:
            original = layer["img_original"]
            img_w, img_h = original.get_size()

            # Scale up so the image fills the screen on both axes with no gaps.
            # The 1.01 factor guards against one-pixel seams caused by integer rounding.
            scale    = max(self.__width / img_w, self.__height / img_h) * 1.01
            new_size = (int(img_w * scale), int(img_h * scale))

            layer["img"]   = pygame.transform.scale(original, new_size)
            layer["width"] = layer["img"].get_width()  # Cache once — reused every frame in update/draw

            # Wrap x into [0, layer_width) so it stays valid after a resize mid-scroll
            layer["x"] %= layer["width"]

    def update(self, dt: float) -> None:
        """
            Advance each layer's scroll position by its speed.

            Args:
                dt: delta time in seconds since the last frame.
        """
        if self.__width == 0:  # resize() hasn't been called yet — nothing to scroll
            return
        for layer in self.__background:
            # Modulo wraps x back to 0 once it reaches the image width, giving seamless looping
            layer["x"] = (layer["x"] - layer["speed"] * dt) % layer["width"]

    def draw(self, surface: pygame.Surface) -> None:
        """
            Draw all layers onto the given surface in order from back to front.

            Each layer is drawn twice — once at x and once at x - width — so
            the seam where the image wraps is always off-screen.

            Args:
                surface: the pygame surface to draw onto.
        """
        for layer in self.__background:
            img = layer["img"]
            width = layer["width"]  # Already cached in resize() — no get_width() call needed
            x = layer["x"]

            surface.blit(img, (x - width, 0))  # Left copy — covers the seam as the right copy scrolls in
            surface.blit(img, (x, 0))           # Right copy — the primary visible tile