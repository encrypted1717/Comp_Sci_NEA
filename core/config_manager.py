"""
    Configuration file utilities for game.

    This module provides the ConfigManager class, which handles reading from
    and writing to .ini config files. It preserves the original casing of
    keys and supports batch updates across multiple sections in one call.
"""

from configparser import ConfigParser


class ConfigManager:
    """
        Read and write .ini configuration files for a single config path.

        ConfigManager wraps Python's ConfigParser to provide a simpler interface
        for loading, updating, and saving game settings. Only one file path is
        managed per instance. Callers can check self.file_read after construction
        to confirm the file was found and parsed successfully.
    """

    def __init__(self, path: str):
        """
            Initialise the manager and attempt to load the config file at the given path.

            Args:
                path: path to the .ini config file to read from and write to.
        """
        self.__path = path
        self.__config = ConfigParser()
        self.__config.optionxform = str  # Preserve key casing - without this ConfigParser lowercases all option names on write
        self.file_read = self.__load()   # True if the file exists and was parsed without error, False otherwise

    def __load(self) -> bool:
        """
            Clear any previously loaded config and read the file from disk.

            Returns:
                True if the file was found and read successfully, False if the
                file does not exist or could not be parsed.
        """
        self.__config.clear()
        return bool(self.__config.read(self.__path))  # read() returns a list of successfully read files - empty list is falsy

    def get_config(self) -> ConfigParser:
        """
            Return the underlying ConfigParser instance.

            Gives direct access to the parsed config for callers that need to
            use ConfigParser's full interface (e.g. config.get, config.sections).

            Returns:
                The internal ConfigParser object with the loaded config data.
        """
        return self.__config

    def set_values(self, update: dict) -> None:
        """
            Write one or more values across one or more sections, then save to disk.

            Accepts a nested dict of the form {section: {option: value}} so that
            multiple keys across multiple sections can be updated in a single call.
            Sections that do not yet exist in the file are created automatically.

            Args:
                update: nested dict mapping section names to dicts of option/value pairs.
                        Values are converted to strings before being written.

            Example:
                manager.set_values({"Graphics": {"Screen_Width": 1920, "Screen_Height": 1080}})
        """
        for section, option_value in update.items():
            if not self.__config.has_section(section):
                self.__config.add_section(section)  # Create the section if it doesn't already exist in the file
            for option, value in option_value.items():
                self.__config.set(section, option, str(value))  # ConfigParser requires all values to be strings
        self.__save()

    def __save(self) -> None:
        """
            Write the current in-memory config state back to disk.

            Called automatically at the end of set_values - should not need
            to be called directly.
        """
        with open(self.__path, "w") as save:
            self.__config.write(save)