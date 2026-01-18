import pygame


class Button(pygame.sprite.Sprite):
    # TODO consider adding a log as an image
    def __init__(self,
                 position,
                 dimensions,
                 text: str,
                 font,
                 text_colour,
                 rect_colour,
                 border = 0,
                 border_colour = None,
                 fill = True,
                 offset_x = 0,
                 offset_y = 0,
                 action = None,
                 hover_rect_colour = None,
                 hover_text_colour = None,
                 hover_border_colour = None,
                 fill_on_hover = False,
                 ):

        super().__init__()
        self.image = pygame.Surface(dimensions, pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=position)

        self.text = text
        self.font = font
        self.text_colour = text_colour
        self.rect_colour = rect_colour
        self.border = border
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.fill_on_hover = fill_on_hover
        self.action = action

        # hover styling
        self.border_colour = border_colour if border_colour is not None else self.rect_colour
        self.hover_border_colour = hover_border_colour if hover_border_colour is not None else self.border_colour
        self.hover_rect_colour = hover_rect_colour if hover_rect_colour is not None else self.rect_colour
        self.hover_text_colour = hover_text_colour if hover_text_colour is not None else self.text_colour

        self.fill = fill

        self.is_hovering = False  # internal state checking if already hovered

        self.__render()

    def __render(self):
        # choose colors based on hover state
        if self.is_hovering:
            rect_colour = self.hover_rect_colour
            text_colour = self.hover_text_colour
            border_colour = self.hover_border_colour
        else:
            rect_colour = self.rect_colour
            text_colour = self.text_colour
            border_colour = self.border_colour

        # clear + fill background
        self.image.fill((0, 0, 0, 0))  # clear to transparent (important if SRCALPHA)
        if self.fill or (self.is_hovering and self.fill_on_hover):
            self.image.fill(rect_colour)

        # optional border (if you want border effect)
        if self.border:
            pygame.draw.rect(self.image, border_colour, self.image.get_rect(), width = self.border)

        text_surf = self.font.render(self.text, False, text_colour)
        text_rect = text_surf.get_rect(center=self.image.get_rect().center)
        text_rect.x += self.offset_x
        text_rect.y += self.offset_y
        self.image.blit(text_surf, text_rect)

    def update(self, mouse_pos = None):
        if mouse_pos is not None:
            is_hovering_now = self.rect.collidepoint(mouse_pos)
            if is_hovering_now != self.is_hovering:
                self.is_hovering = is_hovering_now
                self.__render()

    def handle_event(self, event):
        if self.action is not None:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.rect.collidepoint(event.pos):
                    return self.action
        return None

    def update_text(self, text):
        self.text = text
        self.__render()