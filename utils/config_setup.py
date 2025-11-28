import pygame
from configparser import ConfigParser


#check if user settings are already created
class Configuration:
    def __init__(self):

        self.index_o = None
        self.index_s = None
        self.config = ConfigParser()
        self.config.optionxform = str  # this line just makes it so any writing I do to an ini file is saved the way I type it
        # check if file exists in directory if not then we create a user file
        self.path = None
        self.value = None

    def open_file(self, path):
        self.config.clear()
        self.path = path  # "assets\\game_settings\\config_user.ini"
        try:
            with open(self.path, "r") as default:
                self.config.read_file(default)
                # get resolution
                # self.screen_width = self.config.getint("Graphics", "Screen_Width")
                # self.screen_height = self.config.getint("Graphics", "Screen_Height")

        except FileNotFoundError:  # error for file not existing...section or option in config file
            print(f"Error file in directory {self.path} does not exist or is corrupted")
            return False
            #self.screen_width, self.screen_height = pygame.display.get_desktop_sizes()[0]
            # Save default resolution
            #self.config["Graphics"] = {"Screen_Width": str(self.screen_width), "Screen_Height": str(self.screen_height)}

    # TODO implement exception handling
    def get_value(self, section: str, option: str, data_type: str = None):
        # In main code you can choose to get as integer or other data types instead of always concatenating it as ini files always store integers
        if data_type.lower() == "int":
            self.value = self.config.intget(section, option)
        elif data_type.lower() == "bool":
            self.value = self.config.getboolean(section, option)
        elif data_type.lower() == "float":
            self.value = self.config.getfloat(section, option)
        else:
            self.value = self.config.get(section, option)
        return self.value

    # config.set_value([Graphics, Window], (([Screen_Width], [Screen_Height]), [Fps]), (([1920], [1080]), ([75]))
    def set_value(self, update: dict) -> None:
        # {"Graphics": {"Screen_Width": 1920, "Screen_Height": 1080}, "Window": {"Fps": 75}}
        for section, key_value in update.items():
            print(key_value)
            self.config[section] = key_value

        with open(self.path, "w") as save:
            self.config.write(save)