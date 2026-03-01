import pygame
import sqlite3
import bcrypt
import logging
from core.window import Window
from core.button import Button
from graphics.parallax_background import Background


class LoginMenu(Window):
    def __init__(self, display, renderer, player):
        super().__init__(display, renderer)

        # Setup Logging
        self.log = logging.getLogger(__name__)
        self.log.info("Initialising Login Menu module")

        # Setup Main
        self.player = player  # Tracks whether the next login is for player 1 or 2

        # Setup parallax background
        self.bg = Background()
        self.bg.resize((self.display_width, self.display_height))  # Resize to virtual resolution (1920 x 1080)

        # Setup Database
        self.con = sqlite3.connect("assets\\login_credentials.db")
        self.cursor = self.con.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS login_credentials (
                userID      INTEGER PRIMARY KEY AUTOINCREMENT,
                username    TEXT    NOT NULL,
                hashed_pass BLOB    NOT NULL
            )
        """)

        # Setup Buttons
        font = pygame.font.Font(self.fonts["GothicPixel"], 16)
        font1 = pygame.font.Font(self.fonts["GothicPixel"], 12)
        small_font = pygame.font.Font(self.fonts["GothicPixel"], 8)
        medium_font = pygame.font.Font(self.fonts["GothicPixel"], 20)
        big_font = pygame.font.Font(self.fonts["GothicPixel"], 28)

        self.__player_label = Button(
            (self.center_x, 295),
            (440, 115), #40
            f"Player {self.player}",
            big_font,
            "#000000",
            "#ffffff",
            border=7,
            border_colour="#000000",
            offset_y=4

        )
        self.__username_txt = Button(
            (self.center_x, 430), (440, 90),
            "Username", font,
            "#000000", "#ffffff", border=4, border_colour="#000000",
            typing=True, active_border_colour="#999999",
            offset_y=4
        )
        self.__password_txt = Button(
            (self.center_x, 530), (440, 90),
            "Password", font,
            "#000000", "#ffffff", border=4, border_colour="#000000",
            typing=True, mask=True, active_border_colour="#999999",
            offset_y=4
        )
        self.__peak_btn = Button(
            (1230, 530), (90, 90), "Peak", font,
            "#000000", "#ffffff", border=4, border_colour="#000000",
            hover_border_colour="#999999", action="toggle_pass",
            offset_y=4
        )
        self.__register_btn = Button(
            (850, 650), (210, 75), "Register", medium_font,
            "#000000", "#ffffff", border=6, border_colour="#000000",
            hover_border_colour="#999999", action="register",
            offset_y=4
        )
        self.__login_btn = Button(
            (1070, 650), (210, 75), "Login", medium_font,
            "#000000", "#ffffff", border=6, border_colour="#000000",
            hover_border_colour="#999999", action="login",
            offset_y=4
        )
        self.__reg_user_error_label = Button(
            (1500, 350), (400, 245),
            "USERNAME ERROR\nUsernames must be:\n- at least 3 characters long\n- maximum 26 characters long", font1,
            "#FF3131", "#ffffff", border=3, border_colour="#000000",
            offset_y=4
        )
        self.__reg_pass_error_label = Button(
            (1500, 605), (400, 245),
            "PASSWORD ERROR\nPasswords must have:\n- at least 6 characters\n- a capital and lowercase letter\n- a number\n- a special character\n- a maximum of 26 characters",
            font1,
            "#FF3131", "#ffffff", border=3, border_colour="#000000",
            offset_y=4
        )
        self.__login_error_label = Button(
            (1500, 605), (400, 245),
            "ERROR\nUser doesn't exist\nor password is incorrect", font1,
            "#FF3131", "#ffffff", border=3, border_colour="#000000",
            offset_y=4
        )
        self.buttons.add(
            self.__player_label, self.__login_btn, self.__register_btn,
            self.__username_txt, self.__password_txt, self.__peak_btn
        )

    def __get_credentials(self):
        username = self.__username_txt.get_text()
        password = self.__password_txt.get_text()
        return username, password

    def __clear_inputs(self):
        self.__username_txt.clear()
        self.__password_txt.clear()

    def event_handler(self, events):
        for event in events:
            for btn in self.buttons:
                action = btn.handle_event(event)

                if action == "toggle_pass":
                    self.__password_txt.toggle_mask()

                elif action == "register":
                    username, password = self.__get_credentials()
                    check = self.__check_credentials(username, password)
                    if check[0] and check[1]:
                        password = password.encode("utf-8")
                        hashed = bcrypt.hashpw(password, bcrypt.gensalt())
                        self.cursor.execute(
                            "INSERT INTO login_credentials(username, hashed_pass) VALUES (?, ?)",
                            (username, hashed)
                        )
                        self.con.commit()
                        # Fetch the new user's ID so player data is available immediately
                        user_id = self.cursor.lastrowid
                        self.log.info("Registered new user: %s (id=%s)", username, user_id)
                        self.__clear_inputs()
                        return "main", (user_id, username)
                    elif not check[0] and check[1]: # Username error
                        self.buttons.remove(self.__reg_pass_error_label, self.__login_error_label)
                        self.buttons.add(self.__reg_user_error_label)
                    elif check[0] and not check[1]:
                        self.buttons.remove(self.__reg_user_error_label, self.__login_error_label)
                        self.buttons.add(self.__reg_pass_error_label)
                    else:
                        self.buttons.remove(self.__login_error_label)
                        self.buttons.add(self.__reg_user_error_label, self.__reg_pass_error_label)

                elif action == "login":
                    username, password = self.__get_credentials()
                    password = password.encode("utf-8")
                    self.cursor.execute(
                        "SELECT userID, hashed_pass FROM login_credentials WHERE username = ?",
                        (username,)
                    )
                    row = self.cursor.fetchone()
                    if row and bcrypt.checkpw(password, row[1]):
                        self.log.info("User logged in: %s (id=%s)", username, row[0])
                        self.__clear_inputs()
                        return "main", (row[0], username)
                    else:
                        self.log.warning("Failed login attempt for username: %s", username)
                        self.buttons.remove(self.__reg_user_error_label, self.__reg_pass_error_label)
                        self.buttons.add(self.__login_error_label)

                    return None

                elif action:
                    return action

        return None

    def draw(self, dt):
        self.bg.update(dt)
        self.bg.draw(self.surface)
        super().draw(dt)

    def __check_credentials(self, username, password):
        check = [False, False] # Username, Pass
        has_upper = has_lower = has_special = has_num = False # All variables are false
        special = "!@#$%^&*()-_+= "
        min_user_length = 3
        min_pass_length = 6
        if username and password:
            print(type(username), type(password))
            if len(username) >= min_user_length:
                check[0] = True
            if len(password) >= min_pass_length:
                for char in password: #KingArt12!
                    if char.isupper():
                        has_upper = True
                    if char.islower():
                        has_lower = True
                    if char.isdigit():
                        has_num = True
                    if char in special:
                        has_special = True
                    if has_upper and has_lower and has_special and has_num:
                        check[1] = True
                        break # Efficient
        return check