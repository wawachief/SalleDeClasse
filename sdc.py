import sys
from PySide2.QtWidgets import QApplication
from src.Controllers.main_controller import MainController
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


if __name__ == "__main__":

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

    AssetManager.getInstance()

    app = QApplication(sys.argv)

    flask = flask_app.FlaskThread()
    ctrl = MainController()
    if ctrl.mod_bdd is not None:
        flask.init_controller(ctrl)
        ctrl.gui.show()
        sys.exit(app.exec_())
    else:
        flask.stop_flask()
