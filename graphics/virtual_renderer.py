import pygame


class VirtualRenderer:
    """
    Renders everything to a fixed 'virtual' surface (design resolution),
    then scales + letterboxes onto the real window surface.
    """

    def __init__(self, window_surface: pygame.Surface, design_size = (1920, 1080)):
        self.design_size = design_size
        self.black = (0, 0, 0) # Black

        self.virtual_surface = pygame.Surface(self.design_size).convert_alpha()
        self.virtual_surface.fill(self.black) # black background for black bars

        self.window_surface = window_surface
        self.scale = 1.0 # scale from virtual to window
        self.offset = (0, 0) # Top left of the letterboxed/black bars area on window
        self.final_size = (0, 0) # Scaled size on window

        self.update_viewport()

    # Called when recreating surface due to setting change for example
    def set_window_surface(self, window_surface: pygame.Surface):
        self.window_surface = window_surface
        self.update_viewport()

    def update_viewport(self):
        win_width, win_height = self.window_surface.get_size()
        design_width, design_height = self.design_size

        scaled_x = win_width / design_width
        scaled_y = win_height / design_height
        self.scale = min(scaled_x, scaled_y)

        final_width = int(design_width * self.scale)
        final_height = int(design_height * self.scale)
        self.final_size = (final_width, final_height)

        # Compute the center offset so that
        offset_x = (win_width - final_width) // 2
        offset_y = (win_height - final_height) // 2
        self.offset = (offset_x, offset_y)

    def clear_frame(self) -> pygame.Surface:
        self.virtual_surface.fill(self.black)
        return self.virtual_surface

    def draw(self):
        # Fill with black bars
        self.window_surface.fill(self.black)

        # Scale virtual to final size and blit at offset
        scaled = pygame.transform.smoothscale(self.virtual_surface, self.final_size)
        self.window_surface.blit(scaled, self.offset)

    def __window_to_virtual(self, position: tuple) -> tuple | None:
        """
        Convert a window pixel position to virtual coordinates.
        Returns None if the position is in the letterbox bars.
        """
        mouse_x, mouse_y = position
        offset_x, offset_y = self.offset
        final_x, final_y = mouse_x - offset_x, mouse_y - offset_y# Mouse position relative to scaled game
        if final_x < 0 or final_y < 0: # means mouse is left of the image (in left bar) is above the image (in top bar)
            return None
        if final_x >= self.final_size[0] or final_y >= self.final_size[1]: # means mouse is right of the image (right bar) or below the image (bottom bar)
            return None

        virtual_x = int(final_x / self.scale)
        virtual_y = int(final_y / self.scale)
        return virtual_x, virtual_y

    # convert mouse events from window pixels to virtual coordinates. Only needed in specific scenarios where you draw something directly to the real window surface after already having drawn the surface
    def virtual_to_window(self, position: tuple) -> tuple:
        virtual_x, virtual_y = position
        offset_x, offset_y = self.offset
        window_x = int(virtual_x * self.scale) + offset_x
        window_y = int(virtual_y * self.scale) + offset_y
        return window_x, window_y

    def get_virtual_mouse_pos(self) -> tuple | None:
        return self.__window_to_virtual(pygame.mouse.get_pos())

    def map_event_to_virtual(self, event: pygame.event.Event) -> pygame.event.Event | None:
        """
        For mouse events, rewrite event.pos into virtual coordinates.
        If the mouse is in letterbox bars, return None (ignore the event).

        Purpose: convert mouse events (and only mouse events) so they are correct in virtual space.
        It checks:
            MOUSEMOTION
            MOUSEBUTTONDOWN
            MOUSEBUTTONUP
        For these:
            Convert event.pos window→virtual using window_to_virtual.
            If it returns None (mouse in bars), return None so the game ignores the event.
        Otherwise, create a new event:
            same event type
            same data as original
            but pos replaced with the virtual (x,y)
            for motion, also scale rel (relative movement) so drag distances match virtual scale
        For non-mouse events (keyboard, quit, etc.):
            return them unchanged.
        """

        if event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP): # Only process mouse events
            # Convert window pixel coordinates → virtual coordinates
            virtual_pos = self.__window_to_virtual(event.pos)
            if virtual_pos is None:
                return None # the mouse is in the black bars (letterbox area), not over the rendered game image so ignore this mouse event entirely

            data = event.dict.copy() # safely change information have to copy events
            data["pos"] = virtual_pos # change position stored

            # Also map "rel" for MOUSEMOTION
            """
            You use rel when you want to move something based on mouse movement rather than absolute position, e.g.:
            camera panning (drag mouse to move camera)
            rotating a character/aim based on mouse delta
            dragging UI panels by movement amount
            “look around” controls
            If you only need clicking and hovering, you can ignore rel completely.
            Why we scale rel in the virtual renderer
            With virtual rendering, your game coordinates are 1920×1080, but your real window might be larger or smaller.
            If the real window is scaled by scale = 0.5 (meaning the virtual world is being drawn at half size), then:
            a movement of 10 pixels in the real window corresponds to 20 virtual pixels (because each window pixel covers more virtual space after scaling back).
            So you convert:
            rel_virtual = rel_window / scale
            """
            if event.type == pygame.MOUSEMOTION and "rel" in data:
                relative_x, relative_y = data["rel"]
                data["rel"] = (int(relative_x / self.scale), int(relative_y / self.scale))

            return pygame.event.Event(event.type, data)

        return event