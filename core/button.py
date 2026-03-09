"""
    Interactive UI button sprite for game.

    This module provides the Button class, which handles all on-screen UI elements
    including static labels, clickable action buttons, and text input fields.
    Buttons render themselves onto their own Surface and are stored in pygame
    sprite groups so they can be updated and drawn in a single call each frame.
"""

import pygame


class Button(pygame.sprite.Sprite):
    """
        A self-rendering UI element that supports labels, click actions, and text input.

        Button covers three usage modes controlled by constructor arguments:

        - Static label: no action, no typing. Used for headers and display-only text.
        - Action button: action is set. Returns the action string on click, which
          Window.event_handler routes to handle_action.
        - Text input field: typing=True. Captures keyboard input, shows a blinking
          cursor, supports placeholder text, optional masking for passwords, and
          key-repeat for held backspace or character keys.

        Hover styling is applied automatically during update() when the mouse
        overlaps the button rect. All visual state changes re-render the surface
        in place so the sprite group always draws the current appearance.
    """

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
                 typing=False, # Enables text input mode
                 mask=False, # Masks typed characters - useful for passwords
                 max_length=32, # Maximum number of typeable characters
                 active_rect_colour=None, # Fill colour override while the field is focused
                 active_border_colour=None # Border colour override while the field is focused # TODO allow it to flicker
                 ):
        """
            Initialise the button and render its initial appearance.

            Args:
                position:            (x, y) center position in virtual coordinates.
                dimensions:          (width, height) of the button surface.
                text:                display text, or placeholder text when typing=True.
                font:                pygame.font.Font instance used to render text.
                text_colour:         default text colour as a hex string or RGB tuple.
                rect_colour:         default background fill colour.
                border:              border thickness in pixels - 0 disables the border.
                border_colour:       border colour - defaults to rect_colour if not set.
                fill:                whether to fill the background - set False for outline-only buttons.
                offset_x:            horizontal pixel offset applied to the rendered text position.
                offset_y:            vertical pixel offset applied to the rendered text position.
                action:              value returned by handle_event on click or Enter key.
                hover_rect_colour:   background colour while the mouse is hovering.
                hover_text_colour:   text colour while the mouse is hovering.
                hover_border_colour: border colour while the mouse is hovering.
                fill_on_hover:       if True, fills the background on hover even when fill=False.
                typing:              enables text input mode - text becomes a placeholder.
                mask:                replaces typed characters with asterisks.
                max_length:          maximum number of characters the field will accept.
                active_rect_colour:  background colour override while the field is focused.
                active_border_colour: border colour override while the field is focused.
        """
        super().__init__()
        self.image = pygame.Surface(dimensions, pygame.SRCALPHA)  # SRCALPHA so transparent backgrounds work correctly
        self.rect = self.image.get_rect(center=position)         # Positioned by center so layout coords are intuitive

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

        # Hover styling - fall back to the base colour if no hover override was given
        self.border_colour = border_colour if border_colour is not None else self.rect_colour
        self.hover_border_colour = hover_border_colour if hover_border_colour is not None else self.border_colour
        self.hover_rect_colour = hover_rect_colour if hover_rect_colour is not None else self.rect_colour
        self.hover_text_colour = hover_text_colour if hover_text_colour is not None else self.text_colour
        self.is_hovering = False  # Tracks current hover state so __render only runs when it changes

        # Typing mode state
        self.typing = typing
        self.mask = mask
        self.max_length = max_length
        self.active_border_colour = active_border_colour if active_border_colour is not None else self.border_colour
        self.active_rect_colour = active_rect_colour if active_rect_colour is not None else self.rect_colour

        if self.typing:
            self.placeholder = text # Original text arg becomes the greyed-out placeholder
            self.text = "" # Actual typed content starts empty
            self.active = False # True when the field has focus
            self.cursor_visible = False # Toggled by cursor_timer to produce the blinking effect
            self.cursor_timer = 0
            self.cursor_interval = 0.4 # Seconds between cursor blink state changes
        else:
            self.text = text

        # Key repeat state - tracks a held key so it fires repeatedly after an initial delay
        self._held_key = None # The key code currently being held, or None
        self._held_char = "" # The unicode character for the held key - empty string for backspace
        self._hold_timer = 0.0
        self._hold_delay = 0.4 # Seconds before key repeat begins after initial press
        self._hold_interval = 0.05 # Seconds between each repeated key fire once repeat is active

        self.__render()

    def __render(self):
        """
            Redraw the button surface to reflect the current visual state.

            Called on init and whenever state changes (hover, focus, text update,
            cursor blink). Clears the surface, fills the background, draws the
            border, then renders and blits the text or cursor.
        """
        self.image.fill((0, 0, 0, 0)) # Clear to fully transparent before redrawing - required for SRCALPHA surfaces

        # Select colours based on current state - typing fields use active/inactive, others use hover/default
        if self.typing:
            rect_colour = self.active_rect_colour if self.active else self.rect_colour
            border_colour = self.active_border_colour if self.active else self.border_colour
            text_colour = self.text_colour # Text colour doesn't change with focus state
        else:
            rect_colour = self.hover_rect_colour if self.is_hovering else self.rect_colour
            text_colour = self.hover_text_colour if self.is_hovering else self.text_colour
            border_colour = self.hover_border_colour if self.is_hovering else self.border_colour

        # Fill background - skipped for outline-only buttons unless hover fill is active
        if self.fill or (self.is_hovering and self.fill_on_hover):
            self.image.fill(rect_colour)

        if self.border:
            pygame.draw.rect(self.image, border_colour, self.image.get_rect(), width=self.border)

        if self.typing:
            if self.text:
                # Show masked asterisks for password fields, otherwise show the real text
                display = "*" * len(self.text) if self.mask else self.text
                text_surf = self.font.render(display, False, text_colour)
            else:
                # No text typed yet - render the placeholder at reduced opacity
                placeholder_surf = self.font.render(self.placeholder, False, text_colour)
                text_surf = pygame.Surface(placeholder_surf.get_size(), pygame.SRCALPHA)
                text_surf.blit(placeholder_surf, (0, 0))
                text_surf.set_alpha(100) # Dim the placeholder so it reads as hint text, not real input

            # Left-align typed text with a small margin from the left edge
            text_rect = text_surf.get_rect(midleft=(8 + self.offset_x, self.image.get_height() // 2 + self.offset_y))

            # Blinking cursor - only drawn when the field is active and cursor is in its visible phase
            if self.active and self.cursor_visible:
                # Place cursor after the last character, or at the start margin if the field is empty
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
            text_rect = text_surf.get_rect(center=self.image.get_rect().center) # Center text within the button surface
            text_rect.x += self.offset_x
            text_rect.y += self.offset_y

        self.image.blit(text_surf, text_rect)

    def update(self, mouse_pos=None, dt=0):
        """
            Advance per-frame state: cursor blink, key repeat, and hover detection.

            Called once per frame by the sprite group in Window.draw(). For active
            typing fields, this ticks the cursor blink timer and fires held-key
            repeats. For non-typing buttons it checks hover state and re-renders
            only if hover state has changed, avoiding unnecessary redraws.

            Args:
                mouse_pos: current mouse position in virtual coordinates, or None.
                dt:        delta time in seconds since the last frame.
        """
        if self.typing and self.active:
            # Advance cursor blink timer and toggle visibility when the interval elapses
            self.cursor_timer += dt
            if self.cursor_timer >= self.cursor_interval:
                self.cursor_visible = not self.cursor_visible
                self.cursor_timer = 0
                self.__render()

            # Fire key repeat if a key has been held past the initial delay
            if self._held_key is not None:
                self._hold_timer += dt
                if self._hold_timer >= self._hold_delay:
                    # Subtract interval instead of resetting to zero so repeat stays at a fixed cadence
                    self._hold_timer -= self._hold_interval
                    self.__apply_key(self._held_key, self._held_char)
        else:
            # Only re-render when hover state actually changes to avoid per-frame surface redraws
            is_hovering_now = self.rect.collidepoint(mouse_pos) if mouse_pos else False
            if is_hovering_now != self.is_hovering:
                self.is_hovering = is_hovering_now
                self.__render()

    def handle_event(self, event):
        """
            Process a single pygame event and return an action if one is triggered.

            For typing fields: left-click toggles focus, KEYDOWN feeds input or
            starts key repeat, KEYUP clears the held key. For action buttons: a
            left-click within the button rect returns the action value.

            Args:
                event: a single pygame event from the event list.

            Returns:
                The button's action value if triggered, or None otherwise.
        """
        if self.typing:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                was_active = self.active
                self.active = self.rect.collidepoint(event.pos) # Focus this field if click was inside it
                if self.active != was_active:
                    # Reset cursor to visible so the player gets immediate feedback on focus change
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
                    return self.action # Treat Enter as a form submit - return the field's action
                elif event.key == pygame.K_TAB:
                    pass # Tab is consumed without action - prevents focus jumping to OS elements
                elif len(self.text) < self.max_length:
                    self.__apply_key(event.key, event.unicode)
                    self._held_key = event.key
                    self._held_char = event.unicode
                    self._hold_timer = 0.0

            if event.type == pygame.KEYUP:
                if event.key == self._held_key:
                    self._held_key = None # Clear held key so repeat stops on release

        elif self.action is not None:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.rect.collidepoint(event.pos):
                    return self.action

        return None

    def update_text(self, text):
        """
            Update the displayed text and re-render.

            For typing fields this updates the placeholder, not the typed content.
            Used by game logic to refresh HUD labels and button labels dynamically.

            Args:
                text: the new text string to display.
        """
        if self.typing:
            self.placeholder = text # Typing fields show placeholder when input is empty
        else:
            self.text = text
        self.__render()

    def get_text(self):
        """
            Return the current typed text content.

            Returns:
                The typed string. Empty string if nothing has been typed yet.
        """
        return self.text

    def clear(self):
        """
            Clear all typed input and re-render.

            Only meaningful when typing=True. Called after a successful login or
            registration to reset the field for the next use.
        """
        if self.typing:
            self.text = ""
            self.__render()

    def toggle_mask(self):
        """
            Toggle password masking on or off and re-render.

            Only meaningful when typing=True. Flips the mask flag so typed
            characters are either shown as asterisks or revealed as plain text.
        """
        if self.typing:
            self.mask = not self.mask
            self.__render()

    def __apply_key(self, key, char):
        """
            Apply a single key action to the typed text and re-render.

            Handles backspace by removing the last character, or appends the
            given unicode character if the field is not at max length. Called
            both on the initial KEYDOWN and on each key-repeat tick in update().

            Args:
                key:  the pygame key code (e.g. pygame.K_BACKSPACE).
                char: the unicode character to append, or empty string for backspace.
        """
        if key == pygame.K_BACKSPACE:
            self.text = self.text[:-1] # Remove the last character - slice is safe on empty strings
        elif len(self.text) < self.max_length and char:
            self.text += char
        self.__render()