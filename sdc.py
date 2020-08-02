import sys
from PySide2.QtWidgets import QApplication
from src.controller import Controller
from src.webserver import flask_app

if __name__ == "__main__":
    app = QApplication(sys.argv)
    flask = flask_app.FlaskThread()

    ctrl = Controller()
    ctrl.gui.show()


    sys.exit(app.exec_())
