import pygame
from core.game import Game
from menus.main_menu import MainMenu
from menus.controls_menu import ControlsMenu
from menus.settings_menu import SettingsMenu
from menus.exit_menu import ExitMenu


#WindowManager handles everything to do with the windows (i.e. switching/creating/deleting windows
class WindowManager:
    def __init__(self, window):
        self.events = None
        self.window = window
        self.state = "main_menu" #defaults to this
        self.win_res = pygame.display.list_modes()
        self.windows = {"main_menu" : MainMenu(self.window, self.win_res)} #windows that are preloaded
        self.new_state = None

    def get_window(self): #or create/load anything that isn't already loaded into the windows
        if self.state not in self.windows:
            if self.state == "main_menu":
                self.windows["main_menu"] = MainMenu(self.window, self.win_res)
            elif self.state == "start":
                self.windows["start"] = Game(self.window)
            elif self.state == "controls":
                self.windows["controls"] = ControlsMenu(self.window)
            elif self.state == "settings":
                self.windows["settings"] = SettingsMenu(self.window)
            else:
                self.windows["exit"] = ExitMenu(self.window)
        return self.windows[self.state]

    def set_window(self, events):
        self.events = events
        self.new_state = self.get_window().event_handler(self.events)
        if self.new_state: #if true then there is a new state
            del self.windows[self.state]
            self.state = self.new_state

    def draw(self):
        self.get_window().draw()