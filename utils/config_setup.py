from configparser import ConfigParser


#check if user settings are already created
class Configuration:
    def __init__(self):
        self.config = ConfigParser()
        self.config.optionxform = str #this line just makes it so any writing I do to an ini file is saved the way I type it
        self.path = r"assets\\game_settings\\config_user.ini"
        #check if file exists in directory if not then we create a user file
        if os.path.isfile(self.path):
            self.config.read("assets\\game_settings\\config_user.ini")
            #get resolution
            self.screen_width = config.getint("Graphics", "Screen_Width")
            self.screen_height = config.getint("Graphics", "Screen_Height")

        else:
            self.screen_width, self.screen_height = pygame.display.get_desktop_sizes()[0]
            # Save default resolution
            self.config["Graphics"] = {"Screen_Width": str(screen_width), "Screen_Height": str(screen_height)}

            with open("assets\\game_settings\\config_user.ini", "w") as self.save: # Makes sure file is saved even if errors occur
                self.config.write(self.save)

    def get_screen(self):
        return self.screen_width, self.screen_height