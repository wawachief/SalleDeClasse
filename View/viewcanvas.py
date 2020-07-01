from PySide2.QtWidgets import QWidget, QPushButton, QVBoxLayout
from PySide2.QtGui import QPainter, QColor
from PySide2.QtCore import QPoint, QRect


class ViewCanvas(QWidget):

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

    def convert_point_at(self, x, y):
        """
        Gets the QRect associated with the given position
        :rtype: QRect
        """
        return QRect(QPoint(self.square_size * x, self.square_size * y),
                     QPoint(self.square_size * x + self.square_size, self.square_size * y + self.square_size))
