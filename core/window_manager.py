from core.window import Window
from windows.game import Game
from windows.game_setup import GameSetup
from windows.login import LoginMenu
from windows.main_menu import MainMenu
from windows.controls_menu import ControlsMenu
from windows.pause_menu import PauseMenu
from windows.settings_menu import SettingsMenu
from windows.exit_menu import ExitMenu


# WindowManager handles everything to do with the windows (i.e. switching/creating/deleting windows)
class WindowManager:
    def __init__(self, display, renderer):
        self.display = display
        self.renderer = renderer
        # Store users logged in — player data is (user_id, username), set after login
        self.player1 = None
        self.player2 = None
        self.login_player = 1
        # Top of stack is the active window
        self.stack = ["login"]  # Defaults to this
        # the type hint here is to fix a slight warning. The type hint now states that each dict contains a key of str and a value of a Window
        self.windows: dict[str, Window] = {"login": LoginMenu(self.display, self.renderer, self.login_player)}
        # Store last pause background frame
        self.pause_background = None

    def get_state(self) -> str:
        return self.stack[-1]

    def __ensure_window(self, state: str):  # Ensures any needed windows are already created
        """Create a window instance if it isn't already cached."""
        if state not in self.windows:
            if state == "main":
                self.windows[state] = MainMenu(self.display, self.renderer, self.player1, self.player2)
            elif state == "game":
                self.windows[state] = Game(self.display, self.renderer, self.player1, self.player2)
            elif state == "setup":
                self.windows[state] = GameSetup(self.display, self.renderer, self.player1, self.player2)
            elif state == "controls":
                self.windows[state] = ControlsMenu(self.display, self.renderer, self.player1, self.player2)
            elif state == "settings":
                self.windows[state] = SettingsMenu(self.display, self.renderer, self.player1)
            elif state == "pause":
                self.windows[state] = PauseMenu(self.display, self.renderer, self.pause_background)
            elif state == "login":
                self.windows[state] = LoginMenu(self.display, self.renderer, self.login_player)
            else:
                self.windows[state] = ExitMenu(self.display, self.renderer)  # TODO check if this line can be improved as state is assumed to be exit

    def __get_window(self) -> Window:
        state = self.get_state()
        self.__ensure_window(state)
        return self.windows[state]

    def __push(self, state: str):
        self.__ensure_window(state)
        self.stack.append(state)

    def __pop(self):
        """Return to the previous window, discarding overlay windows so they reset next time."""
        if len(self.stack) > 1:
            top = self.stack.pop()
            if top in ("pause", "settings", "controls", "exit"):  # Windows that will be deleted and not cached
                self.windows.pop(top, None)  # dict.pop(key, default) — removes the key if it exists, does nothing if it doesn't (avoids a KeyError)

    def __reset_to(self, state: str):
        """
        Hard navigation: clear stack to base and go to state. Empties the "history".
        Useful for returning to main menu and discarding the game instance.
        """
        self.stack = [state]
        self.windows = {}
        self.pause_background = None
        self.__ensure_window(state)

    def update_window(self, events):
        action = self.__get_window().event_handler(events)
        if not action:
            return None

        if isinstance(action, tuple): # isinstance is the same as type(x) == x
            if action[0] == "main":
                player_data = action[1]  # (user_id, username)
                self.windows.pop("main", None)
                if not self.player1:  # If player 1 not logged in already then...
                    self.player1 = player_data
                    # Only player 1's display settings are applied (they're on this machine)
                    self.__push("main")
                    return "update_display", self.player1[0]  # pass user_id to main.py
                else:
                    self.player2 = player_data
                    self.__push("main")
                    return None

            if action[0] == "pause":
                self.pause_background = action[1]
                self.windows.pop("pause", None)
                self.__push("pause")
                return None

            if action[0] == "login":
                self.login_player = action[1]
                self.windows.pop("login", None)
                self.__push("login")
                return None

        if action == "back":
            self.__pop()
            return None

        if action in ("setup", "game", "settings", "controls", "exit"):
            self.__push(action)
            return None

        if action == "main":
            self.__reset_to(action)
            return None

        if action == "logout":
            # Clear all player state and return to a fresh login screen
            self.player1 = None
            self.player2 = None
            self.login_player = 1
            self.__reset_to("login")
            return None

        if action == "reload_controls":
            if "game" in self.windows:
                self.windows["game"].reload_controls()
            return None

        if action == "update_display":
            return action

        return None

    def update_display(self, new_display):
        self.display = new_display
        for window in self.windows.values():
            window.set_display(self.display)

    def draw(self, dt):
        self.__get_window().draw(dt)