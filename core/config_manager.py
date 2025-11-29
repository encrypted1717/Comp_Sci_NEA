from configparser import ConfigParser


class ConfigManager:
    def __init__(self):
        self.__config = ConfigParser()
        self.__config.optionxform = str  # this line just makes it so any writing I do to an ini file is saved the way I type it
        self.__path = None

    def open_file(self, path: str) -> bool:
        self.__config.clear()
        self.__path = path
        # Returns if file exists or isn't corrupt
        return bool(self.__config.read(self.__path))

    def get_config(self):
        return self.__config

    # Allows you set many values instead of just one
    def set_value(self, update: dict) -> None:
        for section, option_value in update.items():
            if not self.__config.has_section(section):
                self.__config.add_section(section)
            for option, value in option_value.items():
                self.__config.set(section, option, str(value))
        with open(self.__path, "w") as save:
            self.__config.write(save)