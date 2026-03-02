"""
    Virtual rendering and coordinate mapping utilities.

    This module provides the VirtualRenderer class, which draws all game content
    onto a fixed-resolution virtual surface (the design resolution) and then scales
    and letterboxes that surface onto the real window. It also handles remapping
    mouse events from window pixel coordinates into virtual coordinates so that all
    game and UI logic can work exclusively in design-resolution space.
"""

import pygame


class VirtualRenderer:
    """
        Render game content at a fixed design resolution, scaled to fit any window size.

        All drawing is done onto a virtual surface at the design resolution (default 1920x1080).
        Each frame that surface is scaled to fill the window as large as possible while
        preserving aspect ratio, with black letterbox bars filling any leftover space.
        Mouse events are remapped from window pixels into virtual coordinates so the rest
        of the codebase never needs to account for the real window size.
    """

    def __init__(self, window_surface: pygame.Surface, design_size: tuple[int, int] = (1920, 1080)) -> None:
        """
            Initialise the virtual renderer.

            Args:
                window_surface: the real pygame display surface to render onto.
                design_size: the fixed virtual resolution all content is drawn at.
        """
        self.design_size = design_size
        self.black = (0, 0, 0)

        # No alpha channel needed — this is the main render target, not a composited layer
        self.virtual_surface = pygame.Surface(self.design_size).convert()
        self.virtual_surface.fill(self.black)

        self.window_surface = window_surface
        self.scale      = 1.0    # Scale factor mapping virtual pixels to window pixels
        self.offset     = (0, 0)  # Top-left position of the scaled image on the window (letterbox origin)
        self.final_size = (0, 0)  # Pixel dimensions of the scaled virtual surface on the window

        self.update_viewport()

    def set_window_surface(self, window_surface: pygame.Surface) -> None:
        """
            Replace the target window surface and recalculate the viewport.

            Called when the window is resized or the display mode changes.

            Args:
                window_surface: the new pygame display surface.
        """
        self.window_surface = window_surface
        self.update_viewport()

    def update_viewport(self) -> None:
        """
            Recalculate the scale factor, final render size, and letterbox offset.

            Should be called whenever the window size changes. Uses the smaller of
            the two axis scale factors so the virtual surface always fits within the
            window without cropping.
        """
        win_width,    win_height    = self.window_surface.get_size()
        design_width, design_height = self.design_size

        # Pick the axis that needs the most shrinking so the image always fits inside the window
        self.scale = min(win_width / design_width, win_height / design_height)

        final_width  = int(design_width  * self.scale)
        final_height = int(design_height * self.scale)
        self.final_size = (final_width, final_height)

        # Centre the scaled image — whichever axis is shorter gets equal black bars on both sides
        self.offset = (
            (win_width  - final_width)  // 2,
            (win_height - final_height) // 2
        )

    def clear_frame(self) -> pygame.Surface:
        """
            Clear the virtual surface to black, ready for the next frame to be drawn.

            Returns:
                The cleared virtual surface.
        """
        self.virtual_surface.fill(self.black)
        return self.virtual_surface

    def draw(self) -> None:
        """
            Scale the virtual surface onto the window with black letterbox bars on unused edges.

            Should be called once per frame after all game content has been drawn
            onto the virtual surface.
        """
        self.window_surface.fill(self.black)  # Paint bars black before blitting the scaled image
        scaled = pygame.transform.scale(self.virtual_surface, self.final_size)
        self.window_surface.blit(scaled, self.offset)

    def __window_to_virtual(self, position: tuple[int, int]) -> tuple[int, int] | None:
        """
            Convert a window pixel position into virtual coordinates.

            Args:
                position: an (x, y) position in real window pixels.

            Returns:
                The corresponding (x, y) in virtual coordinates, or None if the
                position falls within the letterbox bars outside the rendered image.
        """
        mouse_x, mouse_y = position
        offset_x, offset_y = self.offset

        final_x = mouse_x - offset_x  # Position relative to the top-left of the scaled game image
        final_y = mouse_y - offset_y

        if final_x < 0 or final_y < 0:  # Mouse is in the left or top letterbox bar
            return None
        if final_x >= self.final_size[0] or final_y >= self.final_size[1]:  # Mouse is in the right or bottom bar
            return None

        return int(final_x / self.scale), int(final_y / self.scale)

    def virtual_to_window(self, position: tuple[int, int]) -> tuple[int, int]:
        """
            Convert virtual coordinates into real window pixel coordinates.

            Useful when something needs to be drawn directly onto the window surface
            after the virtual surface has already been scaled and blitted.

            Args:
                position: an (x, y) position in virtual coordinates.

            Returns:
                The corresponding (x, y) in real window pixels.
        """
        virtual_x, virtual_y = position
        offset_x, offset_y   = self.offset
        return (
            int(virtual_x * self.scale) + offset_x,
            int(virtual_y * self.scale) + offset_y
        )

    def get_virtual_mouse_pos(self) -> tuple[int, int] | None:
        """
            Return the current mouse position in virtual coordinates.

            Returns:
                The (x, y) virtual position, or None if the mouse is over the letterbox bars.
        """
        return self.__window_to_virtual(pygame.mouse.get_pos())

    def map_event_to_virtual(self, event: pygame.event.Event) -> pygame.event.Event | None:
        """
            Rewrite mouse event positions from window pixels into virtual coordinates.

            Only processes MOUSEMOTION, MOUSEBUTTONDOWN, and MOUSEBUTTONUP. For these,
            the event's pos is converted to virtual space. If the position falls in the
            letterbox bars, None is returned so the event is discarded. For MOUSEMOTION,
            the relative movement (rel) is also scaled to match virtual space. All other
            event types are returned unchanged.

            Args:
                event: a raw pygame event from pygame.event.get().

            Returns:
                A new event with virtual coordinates, the original event unchanged, or
                None if the mouse event should be discarded.
        """
        if event.type not in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
            return event  # Non-mouse events need no coordinate conversion

        virtual_pos = self.__window_to_virtual(event.pos)
        if virtual_pos is None:
            return None  # Mouse is over a letterbox bar — discard the event

        data = event.dict.copy()  # Copy before mutating — event dicts are shared
        data["pos"] = virtual_pos

        if event.type == pygame.MOUSEMOTION and "rel" in data:
            # Scale relative movement to match virtual space —
            # e.g. at scale=0.5, a 10px window drag equals 20 virtual pixels
            rel_x, rel_y = data["rel"]
            data["rel"] = (int(rel_x / self.scale), int(rel_y / self.scale))

        return pygame.event.Event(event.type, data)