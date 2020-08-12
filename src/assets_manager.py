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
COLOR_DICT = {'#f0f8ff': 'aliceblue', '#faebd7': 'antiquewhite', '#00ffff': 'cyan', '#7fffd4': 'aquamarine',
              '#f0ffff': 'azure', '#f5f5dc': 'beige', '#ffe4c4': 'bisque', '#000000': 'black',
              '#ffebcd': 'blanchedalmond', '#0000ff': 'blue', '#8a2be2': 'blueviolet', '#a52a2a': 'brown',
              '#deb887': 'burlywood', '#5f9ea0': 'cadetblue', '#7fff00': 'chartreuse', '#d2691e': 'chocolate',
              '#ff7f50': 'coral', '#6495ed': 'cornflowerblue', '#fff8dc': 'cornsilk', '#dc143c': 'crimson',
              '#00008b': 'darkblue', '#008b8b': 'darkcyan', '#b8860b': 'darkgoldenrod', '#a9a9a9': 'darkgray',
              '#006400': 'darkgreen', '#bdb76b': 'darkkhaki', '#8b008b': 'darkmagenta', '#556b2f': 'darkolivegreen',
              '#ff8c00': 'darkorange', '#9932cc': 'darkorchid', '#8b0000': 'darkred', '#e9967a': 'darksalmon',
              '#8fbc8f': 'darkseagreen', '#483d8b': 'darkslateblue', '#2f4f4f': 'darkslategray',
              '#00ced1': 'darkturquoise', '#9400d3': 'darkviolet', '#ff1493': 'deeppink', '#00bfff': 'deepskyblue',
              '#696969': 'dimgray', '#1e90ff': 'dodgerblue', '#b22222': 'firebrick', '#fffaf0': 'floralwhite',
              '#228b22': 'forestgreen', '#ff00ff': 'magenta', '#dcdcdc': 'gainsboro', '#f8f8ff': 'ghostwhite',
              '#ffd700': 'gold', '#daa520': 'goldenrod', '#808080': 'gray', '#008000': 'green',
              '#adff2f': 'greenyellow', '#f0fff0': 'honeydew', '#ff69b4': 'hotpink', '#cd5c5c': 'indianred',
              '#4b0082': 'indigo', '#fffff0': 'ivory', '#f0e68c': 'khaki', '#e6e6fa': 'lavender',
              '#fff0f5': 'lavenderblush', '#7cfc00': 'lawngreen', '#fffacd': 'lemonchiffon', '#add8e6': 'lightblue',
              '#f08080': 'lightcoral', '#e0ffff': 'lightcyan', '#fafad2': 'lightgoldenrodyellow',
              '#d3d3d3': 'lightgray', '#90ee90': 'lightgreen', '#ffb6c1': 'lightpink', '#ffa07a': 'lightsalmon',
              '#20b2aa': 'lightseagreen', '#87cefa': 'lightskyblue', '#778899': 'lightslategray',
              '#b0c4de': 'lightsteelblue', '#ffffe0': 'lightyellow', '#00ff00': 'lime', '#32cd32': 'limegreen',
              '#faf0e6': 'linen', '#800000': 'maroon', '#66cdaa': 'mediumaquamarine', '#0000cd': 'mediumblue',
              '#ba55d3': 'mediumorchid', '#9370db': 'mediumpurple', '#3cb371': 'mediumseagreen',
              '#7b68ee': 'mediumslateblue', '#00fa9a': 'mediumspringgreen', '#48d1cc': 'mediumturquoise',
              '#c71585': 'mediumvioletred', '#191970': 'midnightblue', '#f5fffa': 'mintcream', '#ffe4e1': 'mistyrose',
              '#ffe4b5': 'moccasin', '#ffdead': 'navajowhite', '#000080': 'navy', '#fdf5e6': 'oldlace',
              '#808000': 'olive', '#6b8e23': 'olivedrab', '#ffa500': 'orange', '#ff4500': 'orangered',
              '#da70d6': 'orchid', '#eee8aa': 'palegoldenrod', '#98fb98': 'palegreen', '#afeeee': 'paleturquoise',
              '#db7093': 'palevioletred', '#ffefd5': 'papayawhip', '#ffdab9': 'peachpuff', '#cd853f': 'peru',
              '#ffc0cb': 'pink', '#dda0dd': 'plum', '#b0e0e6': 'powderblue', '#800080': 'purple', '#ff0000': 'red',
              '#bc8f8f': 'rosybrown', '#4169e1': 'royalblue', '#8b4513': 'saddlebrown', '#fa8072': 'salmon',
              '#f4a460': 'sandybrown', '#2e8b57': 'seagreen', '#fff5ee': 'seashell', '#a0522d': 'sienna',
              '#c0c0c0': 'silver', '#87ceeb': 'skyblue', '#6a5acd': 'slateblue', '#708090': 'slategray',
              '#fffafa': 'snow', '#00ff7f': 'springgreen', '#4682b4': 'steelblue', '#d2b48c': 'tan', '#008080': 'teal',
              '#d8bfd8': 'thistle', '#ff6347': 'tomato', '#40e0d0': 'turquoise', '#ee82ee': 'violet',
              '#f5deb3': 'wheat', '#ffffff': 'white', '#f5f5f5': 'whitesmoke', '#ffff00': 'yellow',
              '#9acd32': 'yellowgreen'}


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
                if s in config_ori.sections():  # check section still exists
                    optn_ori = config_ori.options(s)
                    for o in old_settings[s]:
                        if o in optn_ori and o != "version":  # check option still exists and exclude version
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
        config = ConfigParser()
        config.read(self.config_path)
        return config

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

    @staticmethod
    def start_instance():
        """
        :rtype: AssetManager
        """
        AssetManager.__instance = None
        AssetManager()
        return AssetManager.__instance

    def config(self, section: str, key: str) -> str:
        """
        Gets the value of the specified section, key in the configuration file.

        :param section: Config's section
        :param key: Section's key
        :return: value
        """
        return self.get_config_parser().get(section, key)

    def bdd_path(self):
        """return the BDD path or None if no bdd is found"""
        bp = path.expanduser(self.get_config_parser().get("main", "bdd_path"))
        return bp, path.isfile(bp)

    def get_text(self, key: str) -> str:
        if key in self.__language_dico:
            return self.__language_dico[key]
        return "-_-"
