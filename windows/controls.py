"""
    Controls configuration window for game.

    This module provides the Controls class, which lets both players remap their
    keybinds from inside the game. It reads current binds from the appropriate
    config files, displays them in a two-column table, captures any key or mouse
    button pressed while a rebind is active, and writes the updated binds back
    to the correct config files when Apply is pressed.
"""

import pygame
import configparser
from core import Window, Button, ConfigManager


class Controls(Window):
    """
        In-game controls remapping screen for both players.

        Inherits from Window for display surface, renderer, button group, font
        registry, and the auto back button. Displays each bindable action as a
        row with two clickable buttons - one per player - showing the current
        bind. Clicking a bind button enters rebind mode: all events are intercepted
        until a key or mouse button is received or ESC cancels. Conflicts within
        the same player's binds are automatically cleared. Changes are held in
        memory until Apply is pressed, which saves to config and triggers a live
        reload of the running game.
    """

    def __init__(self, display, renderer, player1, player2):
        """
            Initialise the controls screen and load current binds for both players.

            Args:
                display:  the pygame display surface.
                renderer: the renderer managing the virtual surface and scaling.
                player1:  (user_id, username) tuple for the logged-in player 1.
                player2:  (user_id, username) tuple for player 2, or None if guest.
        """
        super().__init__(display, renderer)

        # Main setup
        self.player1 = player1 # (user_id, username)
        self.player2 = player2 # (user_id, username) or None

        # Load the default config to get the canonical action list and fallback values
        default_config_manager = ConfigManager("assets\\game_settings\\config_default.ini")
        default_config = default_config_manager.get_config()

        self.actions = list(default_config.options("Player1 Controls")) # Ordered list of all bindable action names
        self._default_p1_controls = dict(default_config.items("Player1 Controls")) # Fallback values if a user config is missing an action
        self._default_p2_controls = dict(default_config.items("Player2 Controls"))

        # Resolve config file paths for both players
        self._p1_path = f"assets\\game_settings\\users\\config_{player1[0]}.ini"
        self._p2_path = f"assets\\game_settings\\users\\config_{player2[0]}.ini" if player2 else None

        # Load current binds - player 2 falls back to player 1's file if no account is logged in
        self._p1_controls = self._load_section("Player1 Controls", self._p1_path, self._default_p1_controls)
        if player2:
            self._p2_controls = self._load_section("Player2 Controls", self._p2_path, self._default_p2_controls)
        else:
            self._p2_controls = self._load_section("Player2 Controls", self._p1_path, self._default_p2_controls)

        self.changed = False # True once any bind has been changed - used to show/hide the Apply button
        self._rebinding = None # (player_num: int, action: str) while waiting for a keypress, None otherwise
        self._rebind_btns = {} # Maps action name -> (p1_btn, p2_btn) so __apply_rebind can update the right button

        self.__create_buttons()

    def event_handler(self, events):
        """
            Handle events, intercept all input during rebind mode, and sync button visibility.

            The Apply button and rebind overlay are added to or removed from the
            sprite group dynamically based on state, rather than being always present.
            During a rebind the method short-circuits after the first key or mouse
            event so nothing else processes while waiting for input.

            Args:
                events: list of mapped pygame events from the current frame.

            Returns:
                A navigation action string or None.
        """
        # Sync Apply button visibility - shown as soon as any change is made, hidden after applying
        if self.changed and not self.buttons.has(self._apply_btn):
            self.buttons.add(self._apply_btn)
        elif not self.changed and self.buttons.has(self._apply_btn):
            self.buttons.remove(self._apply_btn)

        # Sync rebind overlay visibility - shown while waiting for a key, hidden otherwise
        if self._rebinding and not self.buttons.has(self._rebind_overlay):
            self.buttons.add(self._rebind_overlay)
        elif not self._rebinding and self.buttons.has(self._rebind_overlay):
            self.buttons.remove(self._rebind_overlay)

        # While waiting for a rebind, consume all events and act only on the first key or mouse input
        if self._rebinding:
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self._rebinding = None # Cancel the rebind - leave the existing bind unchanged
                        return None
                    self._apply_rebind("key", pygame.key.name(event.key))
                    return None
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self._apply_rebind("mouse", str(event.button))
                    return None
            return None # Eat all events until a key or mouse input is received

        return super().event_handler(events)

    def draw(self, dt):
        """
            Draw the controls screen.

            Args:
                dt: delta time in seconds since the last frame.
        """
        self.surface.fill((255, 255, 255))
        super().draw(dt)

    def handle_action(self, action: str) -> str | None:
        """
            Route button actions - rebind triggers and apply are handled here; everything else passes through.

            Args:
                action: the action string returned by a button.

            Returns:
                "reload_controls" after saving, None while rebinding or for unknown
                actions, or the action unchanged so "back" reaches WindowManager.
        """
        if action == "apply":
            self._save_controls()
            self.changed = False
            self.log.info("Controls saved")
            return "reload_controls" # Tells WindowManager to call game.reload_controls() so changes take effect immediately

        if action.startswith("rebind_p1_"):
            self._rebinding = (1, action[len("rebind_p1_"):]) # Extract action name from the suffix and enter rebind mode
            return None

        if action.startswith("rebind_p2_"):
            self._rebinding = (2, action[len("rebind_p2_"):])
            return None

        return action # Pass "back" through to Window, which returns it to WindowManager

    def _apply_rebind(self, device: str, raw_name: str) -> None:
        """
            Commit a newly captured key or mouse bind for the player currently in self._rebinding.

            Clears any other action that was already using the same bind for the
            same player so no two actions share the same input. Updates the
            in-memory controls dict and the corresponding button label.

            Args:
                device:   "key" or "mouse".
                raw_name: raw name string from pygame - e.g. "left shift" or "1".
        """
        player_num, action = self._rebinding
        ini_value = self._build_value(device, raw_name) # Convert to the "device, VALUE" format stored in .ini
        display = self._get_key_name(ini_value) # Human-readable label shown on the button
        controls = self._p1_controls if player_num == 1 else self._p2_controls

        # Detect and clear any existing action already using this bind for the same player
        for existing_action, existing_value in controls.items():
            if existing_value == ini_value and existing_action != action:
                controls[existing_action] = "none"
                ex_p1_btn, ex_p2_btn = self._rebind_btns[existing_action]
                ex_btn = ex_p1_btn if player_num == 1 else ex_p2_btn
                ex_btn.update_text("Unbound")
                self.log.debug("P%s %s unbound due to conflict", player_num, existing_action)
                break

        # Update the in-memory bind and the button label for the action just rebound
        p1_btn, p2_btn = self._rebind_btns[action]
        if player_num == 1:
            self._p1_controls[action] = ini_value
            p1_btn.update_text(display)
        else:
            self._p2_controls[action] = ini_value
            p2_btn.update_text(display)

        self._rebinding = None # Exit rebind mode
        self.changed = True
        self.log.debug("Rebound P%s %s -> %s", player_num, action, ini_value)

    def _load_section(self, section: str, path: str, defaults: dict) -> dict:
        """
            Load all actions from a config section, falling back to defaults for missing keys.

            Args:
                section:  the config section name to read from - e.g. "Player1 Controls".
                path:     path to the .ini file.
                defaults: fallback dict used when the file or key is missing.

            Returns:
                A dict mapping action name to its stored bind value string.
        """
        config_manager = ConfigManager(path)
        config = config_manager.get_config()
        result = {}
        for action in self.actions:
            try:
                result[action] = config.get(section, action)
            except configparser.Error:
                result[action] = defaults[action] # Fall back to default if the key is absent or the file is missing
        return result

    def __create_buttons(self):
        """Create and register all labels, bind buttons, the Apply button, and the rebind overlay."""
        title_font = pygame.font.Font(self.fonts["OldeTome"],   56)
        action_font = pygame.font.Font(self.fonts["OldeTome"],   36)
        general_font = pygame.font.Font(self.fonts["GothicPixel"], 16)

        self._title = Button(
            (self.center_x, 70),
            (350, 70),
            "Controls",
            title_font,
            "#ffffff",
            "#000000",
            offset_y=4
        )

        # Widen the column header if the username is long - each extra character past 11 adds 22px
        player1_offset = 22 * (len(self.player1[1]) - 11) if len(self.player1[1]) > 11 else 0
        p2_label = f"P2 - {self.player2[1]}" if self.player2 else "P2 - Guest"
        if self.player2:
            player2_offset = 22 * (len(self.player2[1]) - 11) if len(self.player1[1]) > 11 else 0
        else:
            player2_offset = 0

        self._p1_header = Button(
            (600 + (player1_offset // 2), 150),
            (340 + player1_offset, 60),
            f"P1 - {self.player1[1]}",
            general_font,
            "#ffffff", "#000000",
            offset_y=4
        )
        self._p2_header = Button(
            (1320, 150),
            (340 + player2_offset, 60),
            p2_label,
            general_font,
            "#ffffff", "#000000",
            offset_y=4
        )

        y_step = 90 # Vertical spacing between each action row
        self._action_labels = []

        for index, action in enumerate(self.actions): # enumerate provides both position index and action name
            y = 250 + index * y_step

            # Centre column label showing the action name
            label = Button(
                (self.center_x, y),
                (300, 60),
                action.capitalize(),
                action_font,
                "#ffffff", "#000000",
                offset_y=4
            )
            self._action_labels.append(label)

            # Player 1 bind button - clicking triggers rebind mode for this action
            p1_btn = Button(
                (600 + (player1_offset // 2), y),
                (280, 60),
                self._get_key_name(self._p1_controls[action]),
                general_font,
                "#000000", "#ffffff", 5,
                border_colour="#000000",
                offset_y=4,
                action=f"rebind_p1_{action}", # Action string encodes both player and action name for handle_action to parse
                hover_text_colour="#ffffff",
                hover_rect_colour="#000000",
                hover_border_colour="#ffffff",
                fill_on_hover=True
            )

            # Player 2 bind button
            p2_btn = Button(
                (1320, y), (280, 60),
                self._get_key_name(self._p2_controls[action]),
                general_font,
                "#000000", "#ffffff", 5,
                border_colour="#000000",
                offset_y=4,
                action=f"rebind_p2_{action}",
                hover_text_colour="#ffffff",
                hover_rect_colour="#000000",
                hover_border_colour="#ffffff",
                fill_on_hover=True
            )

            self._rebind_btns[action] = (p1_btn, p2_btn) # Store pair so _apply_rebind can update the correct button

        # Apply button - not added to the group here; event_handler adds it dynamically once changed=True
        self._apply_btn = Button(
            (1770, 960), (160, 60), "Apply",
            general_font, "#000000", "#ffffff", 5,
            border_colour="#000000", offset_y=4,
            action="apply",
            hover_text_colour="#ffffff", hover_rect_colour="#000000",
            hover_border_colour="#ffffff", fill_on_hover=True,
        )

        # Rebind overlay - shown centered on screen while waiting for input; not added until rebind mode starts
        self._rebind_overlay = Button(
            (self.center_x, self.center_y + 100), (700, 100),
            "Press any key  -  Esc to cancel",
            pygame.font.Font(self.fonts["OldeTome"], 37),
            "#ffffff", "#000000", 5,
            border_colour="#ffffff", offset_y=4,
        )

        self.buttons.add(
            self._back_btn,
            self._title,
            self._p1_header,
            self._p2_header,
            *self._action_labels, # * unpacks the list into individual sprite arguments
            *(btn for pair in self._rebind_btns.values() for btn in pair), # Flatten the (p1, p2) pairs into a single sequence
        )

    def _save_controls(self):
        """
            Write both players' in-memory controls back to the correct config files and sections.

            Player 1 always saves to their own [Player1 Controls] section.
            Player 2 saves to their own file if logged in, otherwise into player 1's
            [Player2 Controls] section as a guest fallback.
        """
        p1_config_manager = ConfigManager(self._p1_path)
        p1_config_manager.set_values({"Player1 Controls": dict(self._p1_controls)})

        if self.player2:
            # Logged-in player 2 - save under their own personal config file
            p2_config_manager = ConfigManager(self._p2_path)
            p2_config_manager.set_values({"Player2 Controls": dict(self._p2_controls)})
        else:
            # Guest player 2 - save into player 1's config as a shared fallback section
            p1_config_manager.set_values({"Player2 Controls": dict(self._p2_controls)})

    def _get_key_name(self, raw: str) -> str:
        """
            Convert a stored .ini bind value into a human-readable display string.

            Handles keyboard keys, mouse buttons, and numpad keys. Unrecognised
            formats fall through to a warning and return "???".

            Examples:
                "key, left shift" -> "LEFT SHIFT"
                "mouse, 1"        -> "LEFT CLICK"
                "key, [0]"        -> "Numpad 0"
                "none"            -> "Unbound"

            Args:
                raw: the raw bind string as stored in the .ini file.

            Returns:
                A display string suitable for showing on a bind button.
        """
        mouse_names = {
            "1": "LEFT CLICK",
            "2": "MIDDLE CLICK",
            "3": "RIGHT CLICK",
            "4": "SCROLL UP",
            "5": "SCROLL DOWN",
        }

        numpad_names = {
            "[0]": "Numpad 0", "[1]": "Numpad 1", "[2]": "Numpad 2",
            "[3]": "Numpad 3", "[4]": "Numpad 4", "[5]": "Numpad 5",
            "[6]": "Numpad 6", "[7]": "Numpad 7", "[8]": "Numpad 8",
            "[9]": "Numpad 9", "[.]": "Numpad .",  "[/]": "Numpad /",
            "[*]": "Numpad *", "[-]": "Numpad -",  "[+]": "Numpad +",
            "[enter]": "Numpad Enter", "[=]": "Numpad =",
        }

        if raw.lower() == "none":
            return "Unbound"

        parts = raw.split(", ", 1) # Split on the first ", " only so values containing commas are preserved
        if len(parts) == 2:
            device, value = parts[0].strip().lower(), parts[1].strip()
            if device == "mouse":
                return mouse_names.get(value, f"M{value}") # Fall back to "M<n>" for unrecognised mouse buttons
            return numpad_names.get(value, value.upper()) # Fall back to uppercased key name for regular keys

        self.log.warning("Unexpected control value in config: %s", raw)
        return "???"

    def _build_value(self, device: str, raw_name: str) -> str:
        """
            Build the .ini storage string from a device identifier and raw input name.

            Args:
                device:   "key" or "mouse".
                raw_name: the raw name from pygame - e.g. "left shift" or "1".

            Returns:
                A string in the format "device, VALUE" - e.g. "key, LEFT SHIFT".

            Examples:
                ("key",   "left shift") -> "key, LEFT SHIFT"
                ("mouse", "1")          -> "mouse, 1"
        """
        return f"{device}, {raw_name.upper()}"