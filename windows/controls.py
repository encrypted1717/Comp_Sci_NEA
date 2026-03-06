import pygame
import configparser
from core.window import Window
from core.button import Button
from core.config_manager import ConfigManager


class Controls(Window):
    def __init__(self, display, renderer, player1, player2):
        super().__init__(display, renderer)

        # Main setup
        self.player1 = player1  # (user_id, username)
        self.player2 = player2  # (user_id, username) or None

        # Setup defaults
        default_config_manager = ConfigManager("assets\\game_settings\\config_default.ini")
        default_config = default_config_manager.get_config()

        self.actions = list(default_config.options("Player1 Controls"))
        self._default_p1_controls = dict(default_config.items("Player1 Controls"))
        self._default_p2_controls = dict(default_config.items("Player2 Controls"))

        # Setup user
        self._p1_path = f"assets\\game_settings\\users\\config_{player1[0]}.ini"
        self._p2_path = f"assets\\game_settings\\users\\config_{player2[0]}.ini" if player2 else None

        self._p1_controls = self._load_section("Player1 Controls", self._p1_path, self._default_p1_controls)

        if player2:
            self._p2_controls = self._load_section("Player2 Controls", self._p2_path, self._default_p2_controls)
        else:
            self._p2_controls = self._load_section("Player2 Controls", self._p1_path, self._default_p2_controls)

        self.changed = False
        self._rebinding = None   # (player_num: int, action: str) while listening for keypress
        self._rebind_btns = {}   # action -> (p1_btn, p2_btn)

        self.__create_buttons()

    def event_handler(self, events):
        # Sync apply button and rebind overlay in/out of the sprite group
        if self.changed and not self.buttons.has(self._apply_btn):
            self.buttons.add(self._apply_btn)
        elif not self.changed and self.buttons.has(self._apply_btn):
            self.buttons.remove(self._apply_btn)

        if self._rebinding and not self.buttons.has(self._rebind_overlay):
            self.buttons.add(self._rebind_overlay)
        elif not self._rebinding and self.buttons.has(self._rebind_overlay):
            self.buttons.remove(self._rebind_overlay)

        # While waiting for a keypress, intercept all events before normal handling
        if self._rebinding:
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self._rebinding = None
                        return None
                    self._apply_rebind("key", pygame.key.name(event.key))
                    return None
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self._apply_rebind("mouse", str(event.button))
                    return None
            return None  # eat all events until input received

        return super().event_handler(events)

    def draw(self, dt):
        self.surface.fill((255, 255, 255))
        super().draw(dt)

    def handle_action(self, action: str) -> str | None:
        """Route button actions - rebind triggers and apply are handled here; everything else passes through."""
        if action == "apply":
            self._save_controls()
            self.changed = False
            self.log.info("Controls saved")
            return "reload_controls"

        if action.startswith("rebind_p1_"):
            self._rebinding = (1, action[len("rebind_p1_"):])
            return None

        if action.startswith("rebind_p2_"):
            self._rebinding = (2, action[len("rebind_p2_"):])
            return None

        return action  # passes "back" through to Window, which returns it to WindowManager

    def _apply_rebind(self, device: str, raw_name: str) -> None:
        """Commit a newly captured key/mouse bind for the player currently in self._rebinding."""
        player_num, action = self._rebinding
        ini_value = self._build_value(device, raw_name)
        display    = self._get_key_name(ini_value)
        controls   = self._p1_controls if player_num == 1 else self._p2_controls

        # Clear any action already using this bind for the same player
        for existing_action, existing_value in controls.items():
            if existing_value == ini_value and existing_action != action:
                controls[existing_action] = "none"
                ex_p1_btn, ex_p2_btn = self._rebind_btns[existing_action]
                ex_btn = ex_p1_btn if player_num == 1 else ex_p2_btn
                ex_btn.update_text("Unbound")
                self.log.debug("P%s %s unbound due to conflict", player_num, existing_action)
                break

        p1_btn, p2_btn = self._rebind_btns[action]
        if player_num == 1:
            self._p1_controls[action] = ini_value
            p1_btn.update_text(display)
        else:
            self._p2_controls[action] = ini_value
            p2_btn.update_text(display)

        self._rebinding = None
        self.changed = True
        self.log.debug("Rebound P%s %s -> %s", player_num, action, ini_value)

    def _load_section(self, section: str, path: str, defaults: dict) -> dict:
        """Load all CONTROL_ACTIONS from the given section, falling back to defaults."""
        config_manager = ConfigManager(path)
        config = config_manager.get_config()
        result = {}
        for action in self.actions:
            try:
                result[action] = config.get(section, action)
            except configparser.Error:
                result[action] = defaults[action]
        return result

    def __create_buttons(self):
        title_font = pygame.font.Font(self.fonts["OldeTome"],56)
        action_font = pygame.font.Font(self.fonts["OldeTome"],36)
        general_font = pygame.font.Font(self.fonts["GothicPixel"],16)

        self._title = Button(
            (self.center_x, 70),
            (350, 70),
            "Controls",
            title_font,
            "#ffffff",
            "#000000",
            offset_y=4
        )

        player1_offset = 22 * (len(self.player1[1]) - 11) if len(self.player1[1]) > 11 else 0
        p2_label = f"P2 - {self.player2[1]}" if self.player2 else "P2 - Guest"
        if self.player2:
            if len(self.player1[1]) > 11:
                player2_offset = 22 * (len(self.player2[1]) - 11)
            else:
                player2_offset = 0
        else:
            player2_offset = 0

        self._p1_header = Button(
            (600 + (player1_offset//2), 150),
            (340 + player1_offset, 60),
            f"P1 - {self.player1[1]}",
            general_font,
            "#ffffff",
            "#000000",
            offset_y=4
        )
        self._p2_header = Button(
            (1320, 150),
            (340 + player2_offset, 60),
            p2_label,
            general_font,
            "#ffffff",
            "#000000",
            offset_y=4
        )
        y_step  = 90
        self._action_labels = []
        for index, action in enumerate(self.actions): # return index and the action
            y = 250 + index * y_step

            label = Button(
                (self.center_x, y),
                (300, 60),
                action.capitalize(),
                action_font,
                "#ffffff",
                "#000000",
                offset_y=4
            )
            self._action_labels.append(label)

            p1_btn = Button(
                (600 + (player1_offset//2), y),
                (280, 60),
                self._get_key_name(self._p1_controls[action]),
                general_font,
                "#000000",
                "#ffffff",
                5,
                border_colour="#000000",
                offset_y=4,
                action=f"rebind_p1_{action}",
                hover_text_colour="#ffffff",
                hover_rect_colour="#000000",
                hover_border_colour="#ffffff",
                fill_on_hover=True
            )
            p2_btn = Button(
                (1320, y), (280, 60),
                self._get_key_name(self._p2_controls[action]),
                general_font,
                "#000000",
                "#ffffff",
                5,
                border_colour="#000000",
                offset_y=4,
                action=f"rebind_p2_{action}",
                hover_text_colour="#ffffff",
                hover_rect_colour="#000000",
                hover_border_colour="#ffffff",
                fill_on_hover=True
            )
            self._rebind_btns[action] = (p1_btn, p2_btn)
        self._apply_btn = Button(
            (1770, 960), (160, 60), "Apply",
            general_font, "#000000", "#ffffff", 5,
            border_colour="#000000", offset_y=4,
            action="apply",
            hover_text_colour="#ffffff", hover_rect_colour="#000000",
            hover_border_colour="#ffffff", fill_on_hover=True,
        )
        self._rebind_overlay = Button(
            (self.center_x, self.center_y + 100), (700, 100),
            "Press any key  –  Esc to cancel",
            pygame.font.Font(self.fonts["OldeTome"], 37),
            "#ffffff", "#000000", 5,
            border_colour="#ffffff", offset_y=4,
        )

        self.buttons.add(
            self._back_btn,
            self._title,
            self._p1_header,
            self._p2_header,
            *self._action_labels, # * Unpacks every item within list
            *(btn for pair in self._rebind_btns.values() for btn in pair), # Same here
        )

    def _save_controls(self):
        """Write both players' controls back to the correct config files/sections."""
        p1_config_manager = ConfigManager(self._p1_path)
        p1_config_manager.set_values({"Player1 Controls": dict(self._p1_controls)})

        if self.player2:
            # P2 is logged in — save under their own personal config
            p2_config_manager = ConfigManager(self._p2_path)
            p2_config_manager.set_values({"Player2 Controls": dict(self._p2_controls)})
        else:
            # Guest P2 — save into player1's [Player2 Controls] fallback section
            p1_config_manager.set_values({"Player2 Controls": dict(self._p2_controls)})

    def _get_key_name(self, raw: str) -> str:
        """
        Turn a stored value into a display string for the button.
        'key, left shift' -> 'LEFT SHIFT'
        'mouse, 1'        -> 'Left Click'
        'none'            -> 'Unbound'
        """
        mouse_names = {
            "1": "LEFT CLICK",
            "2": "MIDDLE CLICK",
            "3": "RIGHT CLICK",
            "4": "SCROLL UP",
            "5": "SCROLL DOWN",
        }

        numpad_names = {
            "[0]": "Numpad 0",
            "[1]": "Numpad 1",
            "[2]": "Numpad 2",
            "[3]": "Numpad 3",
            "[4]": "Numpad 4",
            "[5]": "Numpad 5",
            "[6]": "Numpad 6",
            "[7]": "Numpad 7",
            "[8]": "Numpad 8",
            "[9]": "Numpad 9",
            "[.]": "Numpad .",
            "[/]": "Numpad /",
            "[*]": "Numpad *",
            "[-]": "Numpad -",
            "[+]": "Numpad +",
            "[enter]": "Numpad Enter",
            "[=]": "Numpad =",
        }
        if raw.lower() == "none":
            return "Unbound"
        parts = raw.split(", ", 1)
        if len(parts) == 2:
            device, value = parts[0].strip().lower(), parts[1].strip()
            if device == "mouse":
                return mouse_names.get(value, f"M{value}")
            return numpad_names.get(value, value.upper())
        self.log.warning("Unexpected control value in config: %s", raw)
        return "???"

    def _build_value(self, device: str, raw_name: str) -> str:
        """Build the ini storage format from a device and raw name.
        e.g. ("key", "left shift") -> "key, LEFT SHIFT"
             ("mouse", "1")        -> "mouse, 1"
        """
        return f"{device}, {raw_name.upper()}"