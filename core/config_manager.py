from configparser import ConfigParser


class ConfigManager:
    def __init__(self):
        self.config = ConfigParser()
        self.config.optionxform = str  # this line just makes it so any writing I do to an ini file is saved the way I type it
        self.path = None

    def open_file(self, path: str) -> bool:
        self.config.clear()
        self.path = path
        # Returns if file exists or isn't corrupt
        return bool(self.config.read(path))

    def get_config(self):
        return self.config

    # Allows you set many values instead of just one
    def set_value(self, update: dict) -> None:
        for section, option_value in update.items():
            if not self.config.has_section(section):
                self.config.add_section(section)
            for option, value in option_value.items():
                self.config.set(section, option, str(value))
        with open(self.path, "w") as save:
            self.config.write(save)