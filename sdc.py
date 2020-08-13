import sys

from PySide2 import QtCore
from PySide2.QtWidgets import QApplication
from src.Controllers.main_controller import MainController

from src.View.view_mainframe import EXIT_CODE_REBOOT
from src.assets_manager import AssetManager, COLOR_DICT
from src.webserver import flask_app
import logging
import sys
from os import path


class StreamToLogger(object):
    """
   Fake file-like stream object that redirects writes to a logger instance.
   """

    def __init__(self, logger, log_level=logging.DEBUG):
        self.logger = logger
        self.log_level = log_level
        self.linebuf = ''

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.log_level, line.rstrip())


def init_logger():
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s:%(levelname)s:%(name)s:%(message)s',
                        filename=path.expanduser("~/sdc.log"),
                        filemode='a'
                        )
    stdout_logger = logging.getLogger('STDOUT')
    sl = StreamToLogger(stdout_logger)
    # sys.stdout = sl
    stderr_logger = logging.getLogger('STDERR')
    sl = StreamToLogger(stderr_logger, logging.ERROR)
    # sys.stderr = sl


def start_app():

    while True:
        AssetManager.start_instance()
        try:
            app = QApplication(sys.argv)
        except RuntimeError:
            app = QtCore.QCoreApplication.instance()
        flask = flask_app.FlaskThread()
        ctrl = MainController()

        exit_code = None
        if ctrl.mod_bdd is not None:
            flask.init_controller(ctrl)
            ctrl.gui.show()
            exit_code = app.exec_()
        else:
            flask.stop_flask()
        if exit_code != EXIT_CODE_REBOOT:
            break
    return exit_code


if __name__ == "__main__":
    init_logger()
    sys.exit(start_app())

