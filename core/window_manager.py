import pygame
from core.game import Game
from menus.main_menu import MainMenu
from menus.controls_menu import ControlsMenu
from menus.settings_menu import SettingsMenu
from menus.exit_menu import ExitMenu


#WindowManager handles everything to do with the windows (i.e. switching/creating/deleting windows
class WindowManager:
    def __init__(self, display):
        self.display = display
        self.state = "main_menu" # Defaults to this
        self.windows = {"main_menu" : MainMenu(self.display)} # Windows that are preloaded

    # Create/load anything that isn't already loaded into the windows
    # noinspection PyTypeChecker
    def __get_window(self):
        if self.state not in self.windows:
            if self.state == "main_menu":
                self.windows["main_menu"] = MainMenu(self.display)
            elif self.state == "start":
                self.windows["start"] = Game(self.display)
            elif self.state == "controls":
                self.windows["controls"] = ControlsMenu(self.display)
            elif self.state == "settings":
                self.windows["settings"] = SettingsMenu(self.display)
            else:
                self.windows["exit"] = ExitMenu(self.display)
        return self.windows[self.state]

    def update_window(self, events):
        new_state = self.__get_window().event_handler(events)
        if new_state: #if true then there is a new state
            if new_state == "apply_display":
                return "update_display"
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