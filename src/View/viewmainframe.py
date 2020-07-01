from PySide2.QtWidgets import QMainWindow, QWidget, QPushButton, QVBoxLayout

from src.View.viewcanvas import ViewCanvas


class CentralWidget(QWidget):
    def __init__(self):
        """
        Application's central widget, contains all the app's widgets.
        """
        QWidget.__init__(self)

        self.v_canvas = ViewCanvas()  # Central canvas
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

    def __init__(self,  sig_quit):
        """
        Main application's frame

        :param sig_quit: signal to trigger when the application closes
        """
        QMainWindow.__init__(self)
        self.central_widget = CentralWidget()
        self.setCentralWidget(self.central_widget)
        self.sig_quit = sig_quit

    def closeEvent(self, event):
        """
        Triggered on a close operation. Signals to the controller the event
        """
        self.sig_quit.emit()
        event.accept()
