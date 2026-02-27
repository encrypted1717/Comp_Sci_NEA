import pygame
import sqlite3
# import bcrypt
from core.window import Window
from core.button import Button
from core.config_manager import ConfigManager


class LoginMenu(Window):
    def __init__(self, display, renderer):
        super().__init__(display, renderer)

        # Setup Configs
        self.config_manager = ConfigManager("assets\\game_settings\\config_user.ini")
        self.config = self.config_manager.get_config()
        self.changed = False  # Whether any settings have been changed

        # Setup Database
        con = sqlite3.connect("assets\\login_credentials.db")
        cursor = con.cursor()

        # Setup Credentials
        username = "Arthur"
        password = "Kingart"

        # Hash here
        hashed_pass = password

        cursor.execute("""
                       CREATE TABLE IF NOT EXISTS login_credentials
                       (
                           userID INTEGER PRIMARY KEY AUTOINCREMENT,
                           username TEXT NOT NULL,
                           hashed_pass TEXT NOT NULL
                       )
                       """)

        credentials = [(username, hashed_pass)]
        cursor.executemany("""
                           INSERT INTO login_credentials
                               (
                                   username,
                                   hashed_pass
                               ) 
                           VALUES (?, ?)""", credentials)

        con.commit()

        # Setup Buttons
        font = pygame.font.Font(self.fonts["OldeTome"], 37)

        self.__username_label = Button(
            (960, 480),
            (400, 50),
            "Username",
            font,
            "#ffffff",
            "#000000",
            border=2,
            border_colour="#ffffff",
            fill=True,
            typing=True,
            active_border_colour="#aaaaff"
        )

        self.__password_btn =Button(
            (960, 560),
            (400, 50),
            "Password",
            font,
            "#ffffff",
            "#000000",
            border=2,
            border_colour="#ffffff",
            fill=True,
            typing=True,
            mask=True,
            action="login"
        )

        self.buttons.add(
            self.__username_label,
            self.__password_btn
        )

    def event_handler(self, events):
        for event in events:
            for btn in self.buttons:
                action = btn.handle_event(event)
                if action is not None:
                    return action
        return None

    def draw(self, dt):
        self.surface.fill((255, 255, 255)) # White background
        super().draw(dt)


    def check_credentials(self, path, logger):
        config_manager = ConfigManager(path)
        # check if user settings are already created
        if config_manager.file_read:
            config = config_manager.get_config()
            width = config.getint("Graphics", "Screen_Width")
            height = config.getint("Graphics", "Screen_Height")
            display_mode = config.get("Window", "Display_Mode")
            fps = config.get("Window", "FPS")
        # TODO get default values not python set values through the programming
        else:
            logger.warning("Could not open config file in path: %s", path)
            width, height = pygame.display.get_desktop_sizes()[0]
            display_mode = "Fullscreen"
            fps = "60"
            config_manager.set_values({
                "Graphics": {"Screen_Width": width, "Screen_Height": height},
                "Window": {"Display_Mode": display_mode, "FPS": fps}
            })
        framerate = 0 if fps.lower() == "unlimited" else int(fps)
        return width, height, display_mode, framerate