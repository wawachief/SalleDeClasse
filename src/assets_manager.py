from PySide2.QtGui import QIcon

ASSETS_PATH = "assets/"
ICONS_PATH = "icons/"

ICONS_EXT = ".png"


def get_icon(name):
    """
    Retrives the icon associated to the given name, into a QIcon for a button.

    :param name: icon name (without extension and path)
    :type name: str
    :return: Icon to set as icon for a button
    :rtype: QIcon
    """
    return QIcon(f"{ASSETS_PATH}{ICONS_PATH}{name}{ICONS_EXT}")
