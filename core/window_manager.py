import pygame
from core.game import Game
from menus.main_menu import MainMenu
from menus.controls_menu import ControlsMenu
from menus.pause_menu import PauseMenu
from menus.settings_menu import SettingsMenu
from menus.exit_menu import ExitMenu


#WindowManager handles everything to do with the windows (i.e. switching/creating/deleting windows
class WindowManager:
    def __init__(self, display, renderer):
        self.display = display
        self.renderer = renderer
        self.state = "main_menu" # Defaults to this
        self.windows = {"main_menu" : MainMenu(self.display, self.renderer)} # Windows that are preloaded

        # Store last pause background frame here
        self.pause_background = None

    # Create/load anything that isn't already loaded into the windows
    # noinspection PyTypeChecker
    def __get_window(self):
        if self.state not in self.windows:
            if self.state == "main_menu":
                self.windows["main_menu"] = MainMenu(self.display, self.renderer)
            elif self.state == "start":
                self.windows["start"] = Game(self.display, self.renderer)
            elif self.state == "controls":
                self.windows["controls"] = ControlsMenu(self.display, self.renderer)
            elif self.state == "settings":
                self.windows["settings"] = SettingsMenu(self.display, self.renderer)
            elif self.state == "pause_menu":
                self.windows["pause_menu"] = PauseMenu(self.display, self.renderer, self.pause_background)
            else:
                self.windows["exit"] = ExitMenu(self.display, self.renderer)
        return self.windows[self.state]

    def update_window(self, events):
        new_state = self.__get_window().event_handler(events)
        if new_state: #if true then there is a new state
            if new_state == "apply_display":
                return "update_display"
            if type(new_state) is tuple and len(new_state) == 2 and new_state[0] == "pause_menu":
                self.pause_background = new_state[1]
                del self.windows[self.state]
                self.state = "pause_menu"
            else:
                del self.windows[self.state]
                self.state = new_state
        return None

    def update_display(self, new_display):
        self.display = new_display
        for window in self.windows.values():
            window.set_display(self.display)

    def draw(self, dt):
        self.__get_window().draw(dt)