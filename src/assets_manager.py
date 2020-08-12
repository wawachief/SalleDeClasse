from PySide2.QtGui import QIcon
from importlib import import_module
from configparser import ConfigParser
from os import path
import shutil

CONFIG_PATH = 'config.ini'

ASSETS_PATH = "assets/"
ICONS_PATH = "icons/"
STYLE_PATH = "styles/"

ICONS_EXT = ".png"
STYLE_EXT = ".qss"


def get_icon(name):
    """
    Retrives the icon associated to the given name, into a QIcon for a button.

    :param name: icon name (without extension and path)
    :type name: str
    :return: Icon to set as icon for a button
    :rtype: QIcon
    """
    return QIcon(f"{ASSETS_PATH}{ICONS_PATH}{name}{ICONS_EXT}")


def get_stylesheet(file):
    """
    Gets the qss content into a string

    :param file: file name (without extension)
    :return: stylesheet content
    """
    with open(ASSETS_PATH + STYLE_PATH + file + STYLE_EXT, "r") as f:
        return f.read()


def tr(message):
    return AssetManager.getInstance().get_text(message)


class AssetManager:
    __instance = None

    def __init__(self):
        if AssetManager.__instance is None:
            AssetManager.__instance = self
        else:
            raise Exception("Use getInstance() to access the unique AssetManager instance")

        # Application's config file
        # Copy config file into home directory
        self.config_path = path.expanduser("~/.SdCrc")
        if not path.exists(self.config_path):
            shutil.copyfile(CONFIG_PATH, self.config_path)

        # Compare local version with app version
        config_ori = ConfigParser()
        config_ori.read(CONFIG_PATH)
        self.__config = ConfigParser()
        self.__config.read(self.config_path)
        if config_ori.get('main', 'version') != self.__config.get('main', 'version'):
            # backup old settings in a dictionary
            old_settings = self.config_to_dico(self.__config)

            # .SdCrc is obsolete, We overwrite the config file
            shutil.copyfile(CONFIG_PATH, self.config_path)
            self.__config = ConfigParser()
            self.__config.read(self.config_path)

            # we integrate old settings except version back in .SdCrc
            for s in old_settings:
                if s in config_ori.sections():                           # check section still exists
                    optn_ori = config_ori.options(s)
                    for o in old_settings[s]:
                        if o in optn_ori and o != "version":             # check option still exists and exclude version
                            self.__config.set(s, o, old_settings[s][o])  # reintegrate old value in current config

            self.save_config(self.__config)

        language = import_module("assets.languages." + self.__config.get("main", "language"))
        self.__language_dico = language.dico

    def save_config(self, config: ConfigParser) -> None:
        """
        Save the given configuration parser
        """
        with open(self.config_path, 'w') as configfile:  # write the config file
            config.write(configfile)  # in ~/.SdCrc

    def config_to_dico(self, config: ConfigParser) -> dict:
        """
        Converts a configuration parser object into a Python dictionary
        """
        settings = dict()
        for s in config.sections():
            settings[s] = dict()
            for o in config.options(s):
                settings[s][o] = config.get(s, o)

        return settings

    def get_config_parser(self) -> ConfigParser:
        """
        Gets the current config parser
        """
        return self.__config

    def restore_default_settings(self) -> None:
        """
        Restores back the default config.ini file
        """
        config_ori = ConfigParser()
        config_ori.read(CONFIG_PATH)

        self.save_config(config_ori)

    @staticmethod
    def getInstance():
        """
        :rtype: AssetManager
        """
        if AssetManager.__instance == None:
            AssetManager()
        return AssetManager.__instance

    def config(self, section: str, key: str) -> str:
        """
        Gets the value of the specified section, key in the configuration file.

        :param section: Config's section
        :param key: Section's key
        :return: value
        """
        return self.__config.get(section, key)

    def bdd_path(self):
        """return the BDD path or None if no bdd is found"""
        bp = path.expanduser(self.__config.get("main", "bdd_path"))
        return bp, path.isfile(bp)

    def get_text(self, key: str) -> str:
        if key in self.__language_dico:
            return self.__language_dico[key]
        return "-_-"


