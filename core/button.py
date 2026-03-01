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
                 border=0,
                 border_colour=None,
                 fill=True,
                 offset_x=0,
                 offset_y=0,
                 action=None,
                 hover_rect_colour=None,
                 hover_text_colour=None,
                 hover_border_colour=None,
                 fill_on_hover=False,
                 typing=False,  # Enables text input mode
                 mask=False,  # Masks text, useful for passwords
                 max_length=32,  # Max number of typeable characters
                 active_rect_colour=None,  # Fill colour when typing
                 active_border_colour=None  # Border colour when typing # TODO allow it to flicker
                 ):

        super().__init__()
        self.image = pygame.Surface(dimensions, pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=position)

        self.font = font
        self.text = text
        self.text_colour = text_colour
        self.rect_colour = rect_colour
        self.border = border
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.fill_on_hover = fill_on_hover
        self.action = action
        self.fill = fill

        # Hover styling
        self.border_colour = border_colour if border_colour is not None else self.rect_colour
        self.hover_border_colour = hover_border_colour if hover_border_colour is not None else self.border_colour
        self.hover_rect_colour = hover_rect_colour if hover_rect_colour is not None else self.rect_colour
        self.hover_text_colour = hover_text_colour if hover_text_colour is not None else self.text_colour
        self.is_hovering = False  # internal state checking if already hovered

        # Typing mode
        self.typing = typing
        self.mask = mask
        self.max_length = max_length
        self.active_border_colour = active_border_colour if active_border_colour is not None else self.border_colour
        self.active_rect_colour = active_rect_colour if active_rect_colour is not None else self.rect_colour

        if self.typing:
            self.placeholder = text  # 'text' acts as placeholder when typing is enabled
            self.text = ""
            self.active = False
            self.cursor_visible = False
            self.cursor_timer = 0
            self.cursor_interval = 0.4  # ms between blinks
        else:
            self.text = text

        # Key repeat state
        self._held_key = None  # which key is currently held
        self._held_char = ""  # the character for that key (empty for backspace)
        self._hold_timer = 0.0
        self._hold_delay = 0.4  # seconds before repeat starts
        self._hold_interval = 0.05  # seconds between each repeat

        self.__render()

    def __render(self):
        self.image.fill((0, 0, 0, 0))  # clear to transparent (important if SRCALPHA)

        if self.typing:
            rect_colour = self.active_rect_colour if self.active else self.rect_colour
            border_colour = self.active_border_colour if self.active else self.border_colour
            text_colour = self.text_colour if self.active else self.text_colour
        else:
            rect_colour = self.hover_rect_colour if self.is_hovering else self.rect_colour
            text_colour = self.hover_text_colour if self.is_hovering else self.text_colour
            border_colour = self.hover_border_colour if self.is_hovering else self.border_colour

        if self.fill or (self.is_hovering and self.fill_on_hover):
            self.image.fill(rect_colour)

        if self.border:
            pygame.draw.rect(self.image, border_colour, self.image.get_rect(), width=self.border)

        if self.typing:
            if self.text:
                display = "*" * len(self.text) if self.mask else self.text
                text_surf = self.font.render(display, False, text_colour)
            else:
                placeholder_surf = self.font.render(self.placeholder, False, text_colour)
                text_surf = pygame.Surface(placeholder_surf.get_size(), pygame.SRCALPHA)
                text_surf.blit(placeholder_surf, (0, 0))
                text_surf.set_alpha(100)  # Reduce opacity

            text_rect = text_surf.get_rect(midleft=(8 + self.offset_x, self.image.get_height() // 2 + self.offset_y))

            # Blinking cursor
            if self.active and self.cursor_visible:
                cursor_x = text_rect.right + 2 if self.text else 8 + self.offset_x
                mid_y = self.image.get_height() // 2
                half_height = text_surf.get_height() // 2
                pygame.draw.line(
                    self.image, text_colour,
                    (cursor_x, mid_y - half_height),
                    (cursor_x, mid_y + half_height),
                    2
                )
        else:
            text_surf = self.font.render(self.text, False, text_colour)
            text_rect = text_surf.get_rect(center=self.image.get_rect().center)
            text_rect.x += self.offset_x
            text_rect.y += self.offset_y

        self.image.blit(text_surf, text_rect)

    def update(self, mouse_pos=None, dt=0):
        if self.typing and self.active:
            # Cursor blink
            self.cursor_timer += dt
            if self.cursor_timer >= self.cursor_interval:
                self.cursor_visible = not self.cursor_visible
                self.cursor_timer = 0
                self.__render()

            # Key repeat
            if self._held_key is not None:
                self._hold_timer += dt
                if self._hold_timer >= self._hold_delay:
                    # Subtract delay so repeat fires at interval cadence, not delay cadence
                    self._hold_timer -= self._hold_interval
                    self.__apply_key(self._held_key, self._held_char)
        else:
            is_hovering_now = self.rect.collidepoint(mouse_pos) if mouse_pos else False
            if is_hovering_now != self.is_hovering:
                self.is_hovering = is_hovering_now
                self.__render()

    def handle_event(self, event):
        if self.typing:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # if click in
                was_active = self.active
                self.active = self.rect.collidepoint(event.pos)
                if self.active != was_active:
                    self.cursor_visible = True
                    self.cursor_timer = 0
                    self.__render()

            if self.active and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    self.__apply_key(event.key, "")
                    self._held_key = event.key
                    self._held_char = ""
                    self._hold_timer = 0.0
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    return self.action
                elif event.key == pygame.K_TAB:
                    pass
                elif len(self.text) < self.max_length:
                    self.__apply_key(event.key, event.unicode)
                    self._held_key = event.key
                    self._held_char = event.unicode
                    self._hold_timer = 0.0

            if event.type == pygame.KEYUP:
                if event.key == self._held_key:
                    self._held_key = None  # Stop repeating when key is released

        elif self.action is not None:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.rect.collidepoint(event.pos):
                    return self.action
        return None

    def update_text(self, text):
        """Updates displayed text. For typing=True this updates the placeholder."""
        if self.typing:
            self.placeholder = text
        else:
            self.text = text
        self.__render()

    def get_text(self):
        return self.text

    def clear(self):
        """Clears typed input. Only meaningful when typing=True."""
        if self.typing:
            self.text = ""
            self.__render()

    def toggle_mask(self):
        if self.typing:
            self.mask = not self.mask
            self.__render()

    def __apply_key(self, key, char):
        if key == pygame.K_BACKSPACE:
            self.text = self.text[:-1]
        elif len(self.text) < self.max_length and char:
            self.text += char
        self.__render()