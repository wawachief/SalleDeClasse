import sys
from PySide2.QtWidgets import QApplication
from src.controller import Controller

from configparser import ConfigParser

CONFIG_PATH = 'config.ini'


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Application's config file
    config = ConfigParser()
    config.read(CONFIG_PATH)

    ctrl = Controller(config)
    ctrl.gui.show()

    sys.exit(app.exec_())
