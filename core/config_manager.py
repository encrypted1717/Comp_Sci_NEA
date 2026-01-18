from configparser import ConfigParser


class ConfigManager:
    def __init__(self, path: str):
        self.__path = path
        self.__config = ConfigParser()
        self.__config.optionxform = str  # this line just makes it so any writing I do to an ini file is saved the way I type it
        self.file_read = self.__load()

    def __load(self) -> bool:
        self.__config.clear()
        # Returns if file exists or isn't corrupt
        return bool(self.__config.read(self.__path))

    def get_config(self):
        return self.__config

    # Allows you set many values instead of just one
    def set_values(self, update: dict) -> None:
        for section, option_value in update.items():
            if not self.__config.has_section(section):
                self.__config.add_section(section)
            for option, value in option_value.items():
                self.__config.set(section, option, str(value))
        self.__save()

    def __save(self):
        with open(self.__path, "w") as save:
            self.__config.write(save)