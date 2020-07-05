from PySide2.QtGui import QIcon

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
