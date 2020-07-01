from PySide2.QtWidgets import QWidget, QPushButton, QVBoxLayout
from PySide2.QtGui import QPainter, QColor
from PySide2.QtCore import QPoint, QRect


class ViewTile:

    def __init__(self, x, y):
        """
        Description object, contains the information that needs to be displayed in the associated tile's position

        :param x: row coordinate
        :param y: column coordinate
        """
        self.name = "Toto"
        self.surname = "AZERTY"

        self.pos = (x, y)


class ViewCanvas(QWidget):

    def __init__(self):
        """
        Application's main canvas, in which is drawn desks and student's names.
        """
        QWidget.__init__(self)

        self.square_size = 70
        self.tiles = []

        self.setFixedSize(self.square_size * 5, self.square_size * 5)

        self.sig_canvas_click = None  # Signal triggered when a click is performed on a desk
        self.sig_canvas_drag = None  # Signal triggered when a drag operation is performed on the canvas

    def paintEvent(self, event):
        """
        Draws the desks and students' names given the self.tiles list
        """
        super().paintEvent(event)

        painter = QPainter(self)
        for t in self.tiles:
            x, y = t.pos
            painter.fillRect(self.convert_point_at(x, y), QColor("cyan"))
            painter.drawText(QPoint(self.square_size * x, self.square_size * y + 10), f"{t.name}")
            painter.drawText(QPoint(self.square_size * x, self.square_size * y + 20), f"{t.surname}")

    def mousePressEvent(self, event):
        """
        Intercepts the mousePressEvent in order to get where the user clicked and signal it to the controller,
        using self.sig_click.

        :param event:
        """
        x = event.x() // self.square_size
        y = event.y() // self.square_size

        self.sig_canvas_click.emit((x, y))

    def convert_point_at(self, x, y):
        """
        Gets the QRect associated with the given position. Used for drawing the desks
        :rtype: QRect
        """
        return QRect(QPoint(self.square_size * x, self.square_size * y),
                     QPoint(self.square_size * x + self.square_size, self.square_size * y + self.square_size))
