from PySide2.QtWidgets import QMainWindow, QWidget, QPushButton, QVBoxLayout

from View.viewcanvas import ViewCanvas


class CentralWidget(QWidget):
    def __init__(self):
        QWidget.__init__(self)

        self.v_canvas = ViewCanvas()
        self.btn = QPushButton("+")
        self.btn.clicked.connect(self.new_tile)
        self.sig_add_tile = None

        layout = QVBoxLayout()
        layout.addWidget(self.v_canvas)
        layout.addWidget(self.btn)
        self.setLayout(layout)

    def new_tile(self):
        self.sig_add_tile.emit()


class ViewMainFrame(QMainWindow):

    def __init__(self,  sig_quit):
        QMainWindow.__init__(self)
        self.central_widget = CentralWidget()
        self.setCentralWidget(self.central_widget)
        self.sig_quit = sig_quit
    
    def do_quit(self):
        pass

    def closeEvent(self, event):
        self.do_quit()
        self.sig_quit.emit()
        event.accept()
