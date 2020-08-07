import sys
from PySide2.QtWidgets import QApplication
from src.Controllers.main_controller import MainController
from src.webserver import flask_app
import logging

if __name__ == "__main__":

    logging.basicConfig(filename='sdc.log', level=logging.DEBUG)
    logging.info('Starting the app')

    app = QApplication(sys.argv)

    flask = flask_app.FlaskThread()
    ctrl = MainController()
    flask.init_controller(ctrl)
    ctrl.gui.show()

    sys.exit(app.exec_())
