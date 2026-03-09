"""
    Login and registration menu window.

    This module provides the LoginMenu class, which handles player authentication.
    It supports both logging in with an existing account and registering a new one,
    with inline validation feedback for usernames and passwords. It is used for both
    player 1 and player 2 login flows, and prevents the same account being logged
    in twice simultaneously.
"""

import pygame
import sqlite3
import bcrypt
from core import Window, Button
from graphics import Background


class Login(Window):
    """
        Authentication screen for player login and registration.

        Presents username and password input fields alongside Login and Register
        buttons. Validation errors are shown as overlay labels that appear and
        disappear based on the current input state. The parallax background scrolls
        behind the UI. ESC and the auto back button are both disabled on this screen
        as there is nowhere to go back to.
    """

    def __init__(self,
                 display: pygame.Surface,
                 renderer,
                 player: int,
                 logged_in_player: tuple[int, str] | None = None
                 ) -> None:
        """
            Initialise the login menu.

            Args:
                display: the pygame display surface.
                renderer: the renderer managing the virtual surface and scaling.
                player: which player is logging in - 1 or 2 - shown in the header label.
                logged_in_player: (user_id, username) of the already logged-in player, used
                                  to block the same account from logging in twice. None if
                                  no player is yet logged in.
        """
        self.player = player  # Determines the "Player 1" / "Player 2" header labe
        super().__init__(display, renderer)
        self.logged_in_player = logged_in_player  # Used to detect duplicate login attempts

        # Parallax background scrolls behind the login UI
        self.bg = Background()
        self.bg.resize((self.design_width, self.design_height))

        # Connect to the credentials database, creating the table if this is the first run
        self.con = sqlite3.connect("assets\\data\\login_credentials.db")
        self.cursor = self.con.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS login_credentials (
                userID      INTEGER PRIMARY KEY AUTOINCREMENT,
                username    TEXT    NOT NULL,
                hashed_pass BLOB    NOT NULL
            )
        """)

        self._create_buttons()
        self.buttons.add(
            self.__player_label, self.__login_btn, self.__register_btn,
            self.__username_txt, self.__password_txt, self.__peak_btn
        )

    def on_escape(self) -> None | str:
        """Disable ESC — there is no previous screen to return to from login."""
        return "back" if self.player == 2 else None

    def show_back_button(self) -> bool:
        """Suppress the auto back button — login is the root screen."""
        return True if self.player == 2 else False

    def handle_action(self, action: str) -> tuple | str | None:
        """
            Handle button actions for login, registration, and password peeking.

            Args:
                action: the action string returned by a button.

            Returns:
                ("main", (user_id, username)) on successful login or registration,
                None for all other cases, or delegates to super() for unrecognised actions.
        """
        if action == "toggle_pass":
            self.__password_txt.toggle_mask()  # Show/hide password characters
            return None

        if action == "register":
            return self.__handle_register()

        if action == "login":
            return self.__handle_login()

        return super().handle_action(action)  # Fallback for any unrecognised action

    def draw(self, dt: float) -> None:
        """
            Draw the scrolling background then the login UI buttons.

            Args:
                dt: delta time in seconds since the last frame.
        """
        self.bg.update(dt)
        self.bg.draw(self.surface)
        super().draw(dt)

    def _create_buttons(self) -> None:
        """Create and store all input fields, buttons, and error labels for the login screen."""
        player_font = pygame.font.Font(self.fonts["GothicPixel"], 28)
        text_font   = pygame.font.Font(self.fonts["GothicPixel"], 16)
        btn_font    = pygame.font.Font(self.fonts["GothicPixel"], 20)
        error_font  = pygame.font.Font(self.fonts["GothicPixel"], 12)

        # Shared styling for error overlay labels — red text, white fill, thin border
        error_kwargs = {
            "font": error_font,
            "text_colour": "#FF3131",
            "rect_colour": "#ffffff",
            "border": 3,
            "border_colour": "#000000",
            "offset_y": 4
        }

        # Shared styling for text input fields
        text_kwargs = {
            "font": text_font,
            "text_colour": "#000000",
            "rect_colour": "#ffffff",
            "border": 4,
            "border_colour": "#000000",
            "offset_y": 4
        }

        # Shared styling for action buttons (Login / Register)
        btn_kwargs = {
            "font": btn_font,
            "text_colour": "#000000",
            "rect_colour": "#ffffff",
            "border": 6,
            "border_colour": "#000000",
            "hover_border_colour": "#999999",
            "offset_y": 4
        }

        self.__player_label = Button(
            (self.center_x, 295),
            (440, 115),
            f"Player {self.player}",
            player_font,
            "#000000", "#ffffff",
            border=7,
            border_colour="#000000",
            offset_y=4
        )

        self.__username_txt = Button(
            (self.center_x, 430), (440, 90),
            "Username",
            typing=True,
            active_border_colour="#999999",  # Border highlights when the field is focused
            **text_kwargs
        )

        self.__password_txt = Button(
            (self.center_x, 530), (440, 90),
            "Password",
            typing=True,
            mask=True,  # Characters are hidden by default — toggled by the peek button
            active_border_colour="#999999",
            **text_kwargs
        )

        self.__peak_btn = Button(
            (1230, 530), (90, 90),
            "Peak",
            hover_border_colour="#999999",
            action="toggle_pass",  # Toggles the password mask on/off
            **text_kwargs
        )

        self.__register_btn = Button(
            (850, 650), (210, 75),
            "Register",
            action="register",
            **btn_kwargs
        )

        self.__login_btn = Button(
            (1070, 650), (210, 75),
            "Login",
            action="login",
            **btn_kwargs
        )

        # Error labels are created here but only added to self.buttons when relevant,
        # so they only appear on screen when an error condition is active
        self.__reg_user_error_label = Button(
            (1500, 350), (400, 245),
            "USERNAME ERROR\nUsernames must be:\n- at least 3 characters long\n- maximum 26 characters long",
            **error_kwargs
        )

        self.__reg_pass_error_label = Button(
            (1500, 605), (400, 245),
            "PASSWORD ERROR\nPasswords must have:\n- at least 6 characters\n- a capital and lowercase letter\n- a number\n- a special character\n- a maximum of 26 characters",
            **error_kwargs
        )

        self.__login_error_label = Button(
            (1500, 605), (400, 245),
            "ERROR\nUser doesn't exist\nor password is incorrect",
            **error_kwargs
        )

        self.__duplicate_error_label = Button(
            (1500, 605), (400, 245),
            "ERROR\nThis account is already\nlogged in as Player 1",
            **error_kwargs
        )

        self.__username_taken_error_label = Button(
            (1500, 350), (400, 245),
            "USERNAME ERROR\nThis username is already\ntaken",
            **error_kwargs
        )

    def __handle_register(self) -> tuple | None:
        """
            Validate inputs and register a new account if they pass.

            Clears all existing error labels first, then re-adds only those
            relevant to the current validation failure. If both username and
            password are valid and the username is not taken, the account is
            created and the player is logged in immediately.

            Returns:
                ("main", (user_id, username)) on success, None otherwise.
        """
        username, password = self.__get_credentials()
        username_valid, password_valid = self.__check_credentials(username, password)

        # Clear all errors before re-evaluating so stale messages don't linger
        self.buttons.remove(
            self.__reg_user_error_label, self.__reg_pass_error_label,
            self.__login_error_label, self.__duplicate_error_label,
            self.__username_taken_error_label
        )

        if not username_valid:
            self.buttons.add(self.__reg_user_error_label)
        if not password_valid:
            self.buttons.add(self.__reg_pass_error_label)

        if username_valid:
            # Only check for duplicates once the format itself is valid
            self.cursor.execute(
                "SELECT userID FROM login_credentials WHERE username = ?", (username,)
            )
            if self.cursor.fetchone():
                self.log.warning("Registration failed: username already taken: %s", username)
                self.buttons.add(self.__username_taken_error_label)
                return None

        if username_valid and password_valid:
            hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
            self.cursor.execute(
                "INSERT INTO login_credentials(username, hashed_pass) VALUES (?, ?)",
                (username, hashed)
            )
            self.con.commit()
            user_id = self.cursor.lastrowid

            # Block if the newly registered account is already logged in as the other player
            if self.logged_in_player and self.logged_in_player[0] == user_id:
                self.buttons.add(self.__duplicate_error_label)
                return None

            self.log.info("Registered new user: %s (id=%s)", username, user_id)
            self.__clear_inputs()
            return "main", (user_id, username)

        return None

    def __handle_login(self) -> tuple | None:
        """
            Validate credentials against the database and log the player in if correct.

            Returns:
                ("main", (user_id, username)) on success, None otherwise.
        """
        username, password = self.__get_credentials()
        self.cursor.execute(
            "SELECT userID, hashed_pass FROM login_credentials WHERE username = ?", (username,)
        )
        row = self.cursor.fetchone()

        if row and bcrypt.checkpw(password.encode("utf-8"), row[1]):
            # Block if this account is already active as the other player
            if self.logged_in_player and self.logged_in_player[0] == row[0]:
                self.log.warning("Duplicate login attempt: %s already logged in", username)
                self.buttons.remove(
                    self.__reg_user_error_label, self.__reg_pass_error_label, self.__login_error_label
                )
                self.buttons.add(self.__duplicate_error_label)
                return None

            self.log.info("User logged in: %s (id=%s)", username, row[0])
            self.__clear_inputs()
            return "main", (row[0], username)

        # Credentials didn't match — show the generic login error
        self.log.warning("Failed login attempt for username: %s", username)
        self.buttons.remove(self.__reg_user_error_label, self.__reg_pass_error_label)
        self.buttons.add(self.__login_error_label)
        return None

    def __get_credentials(self) -> tuple[str, str]:
        """Read and return the current username and password from the input fields."""
        return self.__username_txt.get_text(), self.__password_txt.get_text()

    def __clear_inputs(self) -> None:
        """Clear both input fields after a successful login or registration."""
        self.__username_txt.clear()
        self.__password_txt.clear()

    def __check_credentials(self, username: str, password: str) -> tuple[bool, bool]:
        """
            Validate the format of a username and password.

            Username rules: 3–26 characters.
            Password rules: 6 characters, must contain at least one uppercase letter,
            one lowercase letter, one digit, and one special character.

            Args:
                username: the raw username string from the input field.
                password: the raw password string from the input field.

            Returns:
                A tuple of (username_valid, password_valid).
        """
        username_valid = bool(username) and 3 <= len(username) <= 26

        password_valid = False
        if password and len(password) >= 6:
            has_upper = has_lower = has_special = has_num = False
            special = "!@#$%^&*()-_+= "
            for char in password:
                if char.isupper():   has_upper = True
                if char.islower():   has_lower = True
                if char.isdigit():   has_num   = True
                if char in special:  has_special = True
                if has_upper and has_lower and has_num and has_special:
                    password_valid = True
                    break  # All conditions met - no need to check remaining characters

        return username_valid, password_valid