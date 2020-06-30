import sys
from PySide2.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout
from PySide2.QtGui import QPainter, QColor
from PySide2.QtCore import QPoint, QRect

from random import randint


class Tile:

    def __init__(self, x, y):
        self.name = "Toto"
        self.surname = "AZERTY"

        self.pos = (x, y)


class Canvas(QWidget):

    def __init__(self):
        QWidget.__init__(self)

        self.square_size = 70
        self.tiles = []

        self.setFixedSize(self.square_size * 5, self.square_size * 5)

    def paintEvent(self, event):
        super().paintEvent(event)

        painter = QPainter(self)
        for t in self.tiles:
            x, y = t.pos
            painter.fillRect(self.convert_point_at(x, y), QColor("cyan"))
            painter.drawText(QPoint(self.square_size * x, self.square_size * y + 10), f"{t.name}")
            painter.drawText(QPoint(self.square_size * x, self.square_size * y + 20), f"{t.surname}")

    def generate(self):
        self.tiles.clear()

        generated = []

        while len(generated) < 5:
            x = randint(0, 4)
            y = randint(0, 4)

            if (x, y) not in generated:
                generated.append((x, y))

        for x, y in generated:
            self.tiles.append(Tile(x, y))

        self.repaint()

    def convert_point_at(self, x, y):
        """
        Gets the QRect associated with the given position
        :rtype: QRect
        """
        return QRect(QPoint(self.square_size * x, self.square_size * y),
                     QPoint(self.square_size * x + self.square_size, self.square_size * y + self.square_size))


class MainFrame(QWidget):

    def __init__(self):
        QWidget.__init__(self)

        self.canvas = Canvas()
        self.btn = QPushButton("+")
        self.btn.clicked.connect(self.canvas.generate)

        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        layout.addWidget(self.btn)
        self.setLayout(layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = MainFrame()
    gui.show()

    sys.exit(app.exec_())
