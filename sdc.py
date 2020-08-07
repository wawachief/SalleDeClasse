import sys
from PySide2.QtWidgets import QApplication
from src.Controllers.main_controller import MainController
from src.webserver import flask_app
import logging
import sys

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

    #logging.basicConfig(filename='sdc.log', level=logging.INFO)
    #logging.info('Starting the app')
    logging.basicConfig(level=logging.DEBUG,
        format='%(asctime)s:%(levelname)s:%(name)s:%(message)s',
        filename="sdc1.log",
        filemode='a'
    )
    stdout_logger = logging.getLogger('STDOUT')
    sl = StreamToLogger(stdout_logger)
    sys.stdout = sl
    stderr_logger = logging.getLogger('STDERR')
    sl = StreamToLogger(stderr_logger, logging.ERROR)
    sys.stderr = sl

    app = QApplication(sys.argv)

    flask = flask_app.FlaskThread()
    ctrl = MainController()
    flask.init_controller(ctrl)
    ctrl.gui.show()

    sys.exit(app.exec_())
