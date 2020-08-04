import sys
from PySide2.QtWidgets import QApplication
from src.Controllers.main_controller import MainController
from src.webserver import flask_app

if __name__ == "__main__":
    app = QApplication(sys.argv)

    flask = flask_app.FlaskThread()
    ctrl = MainController()
    flask.init_controller(ctrl)
    ctrl.gui.show()

    sys.exit(app.exec_())
