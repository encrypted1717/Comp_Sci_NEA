from core.window import Window
from windows.game import Game
from windows.main_menu import MainMenu
from windows.controls_menu import ControlsMenu
from windows.pause_menu import PauseMenu
from windows.settings_menu import SettingsMenu
from windows.exit_menu import ExitMenu


# WindowManager handles everything to do with the windows (i.e. switching/creating/deleting windows
class WindowManager:
    def __init__(self, display, renderer):
        self.display = display
        self.renderer = renderer
        # Top of stack is the active window
        self.stack = ["main_menu"] # Defaults to this
        # Windows that are preloaded
        self.windows: dict[str, Window] = {"main_menu" : MainMenu(self.display, self.renderer)} # the type hint here is to fix a slight warning. The type hint now states that each dict contains a key of str and a value of a Window
        # Store last pause background frame
        self.pause_background = None

    def get_state(self) -> str:
        return self.stack[-1]

    def __ensure_window(self, state: str): # Ensures any needed windows are already created
        """Create/load anything that isn't already loaded into self.windows."""
        if state not in self.windows:
            if state == "main":
                self.windows[state] = MainMenu(self.display, self.renderer)
            elif state == "game":
                self.windows[state] = Game(self.display, self.renderer)
            elif state == "controls":
                self.windows[state] = ControlsMenu(self.display, self.renderer)
            elif state == "settings":
                self.windows[state] = SettingsMenu(self.display, self.renderer)
            elif state == "pause":
                self.windows[state] = PauseMenu(self.display, self.renderer, self.pause_background)
            else:
                self.windows[state] = ExitMenu(self.display, self.renderer) # TODO check if this line can be improved as state is assumed to be exit

    def __get_window(self) -> Window:
        state = self.get_state()
        self.__ensure_window(state)
        return self.windows[state]

    def __push(self, state: str):
        self.__ensure_window(state)
        self.stack.append(state)

    def __pop(self):
        """Go back to previous window (and optionally discard overlay windows)."""
        if len(self.stack) > 1:
            top = self.stack.pop()
            if top in ("pause", "settings", "controls", "exit"): # Windows that will be deleted and not cached
                self.windows.pop(top, None) # TODO explain this

    def __reset_to(self, state: str):
        """
        Hard navigation: clear stack to base and go to state. empties the "history"
        Useful for returning to main menu and discarding game instance.
        """
        self.stack = [state]
        self.windows = {}
        self.pause_background = None
        self.__ensure_window(state)


    def update_window(self, events):
        action = self.__get_window().event_handler(events)
        if action:
            if action == "apply_display":
                return "update_display"

            if type(action) is tuple and len(action) == 2 and action[0] == "pause":
                self.pause_background = action[1]
                self.windows.pop("pause", None)
                self.__push("pause")
                return None

            if action == "back":
                self.__pop()
                return None

            if action in ("game", "settings", "controls", "exit"):
                self.__push(action)
                return None

            if action == "main":
                self.__reset_to(action)
                return None
        return None

    def update_display(self, new_display):
        self.display = new_display
        for window in self.windows.values():
            window.set_display(self.display)

    def draw(self, dt):
        self.__get_window().draw(dt)