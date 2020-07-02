from PySide2.QtWidgets import QMainWindow, QWidget, QPushButton, QVBoxLayout

from src.View.view_canvas import ViewCanvas


class CentralWidget(QWidget):
    def __init__(self, config):
        """
        Application's central widget, contains all the app's widgets.

        :param config: application's parsed configuration
        """
        QWidget.__init__(self)

        self.config = config

        self.v_canvas = ViewCanvas(config)  # Central canvas
        self.btn = QPushButton("+")
        self.btn.clicked.connect(self.new_tile)
        self.sig_add_tile = None

        self.__set_layout()

    def __set_layout(self):
        """
        Initializes the layout of this widget
        """
        layout = QVBoxLayout()
        layout.addWidget(self.v_canvas)
        layout.addWidget(self.btn)
        self.setLayout(layout)

    def new_tile(self):
        self.sig_add_tile.emit()


class ViewMainFrame(QMainWindow):

    def __init__(self, sig_quit, config):
        """
        Main application's frame

        :param sig_quit: signal to trigger when the application closes
        :param config: application's parsed configuration
        """
        QMainWindow.__init__(self)
        self.central_widget = CentralWidget(config)
        self.setCentralWidget(self.central_widget)

        self.sig_quit = sig_quit

        self.setStyleSheet("QMainWindow {" + f"background-color: {config.get('colors', 'main_bg')};" + "}")

    def closeEvent(self, event):
        """
        Triggered on a close operation. Signals to the controller the event
        """
        self.sig_quit.emit()
        event.accept()
