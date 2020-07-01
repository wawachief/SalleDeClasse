from PySide2.QtWidgets import QWidget
from PySide2.QtGui import QPainter, QColor
from PySide2.QtCore import QPoint, QRect, Qt


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

        self.sig_click = None  # Signal triggered when a click is performed on a desk
        self.sig_drag = None  # Signal triggered when a drag operation is performed on the canvas

        # Tracking for drag/drop operation
        self.mouse_btn_left_click = False
        self.drag_start = ()
        self.drag_end = ()

    def paintEvent(self, event):
        """
        Draws the desks and students' names given the self.tiles list
        """
        super().paintEvent(event)

        painter = QPainter(self)
        for t in self.tiles:
            x, y = t.pos
            painter.fillRect(self.__get_rect_at(x, y), QColor("cyan"))
            painter.drawText(QPoint(self.square_size * x, self.square_size * y + 10), f"{t.name}")
            painter.drawText(QPoint(self.square_size * x, self.square_size * y + 20), f"{t.surname}")

    def mousePressEvent(self, event):
        """
        Intercepts the mousePressEvent in order to get where the user clicked and signal it to the controller,
        using self.sig_click.
        """
        if event.button() == Qt.LeftButton:
            self.mouse_btn_left_click = True  # For the mouse tracking in case of drag/drop operation

        # self.sig_click.emit(self.__convert_point(x, y)) TODO

    def mouseMoveEvent(self, event):
        """
        Intercepted to process the drag operation.
        This method will register the drag operation from the start click to the final release.
        """
        if not self.mouse_btn_left_click:  # We track only if we use mouse's left button
            return

        if not self.drag_start:  # Register the first point
            self.drag_start = self.__convert_point(event.x(), event.y())

        self.drag_end = self.__convert_point(event.x(), event.y())  # Updates the end points each time

    def mouseReleaseEvent(self, event):
        """
        Processes the drag operation, using the drag coordinates intercepted by the mouseMoveEvent.
        Triggers the self.sig_drag signal if the drag/drop is valid.

        We identify a drag drop operation if:
        - We have a start point and an end point
        - The mouse left button was the one used
        - The start point differs from the end point
        """
        if self.mouse_btn_left_click and self.drag_start and self.drag_end and self.drag_start != self.drag_end:
            # self.sig_drag.emit(self.drag_start, self.drag_end) TODO
            self.mouse_btn_left_click = False
            self.drag_start = ()

    def __convert_point(self, x, y):
        """
        Converts the mouse positions into row/column positions

        :param x: mouse x coordinate
        :param y: mouse y coordinate
        :return: (row, column) coordinates associated to the mouse position
        :rtype: tuple
        """
        return x // self.square_size, y // self.square_size

    def __get_rect_at(self, x, y):
        """
        Gets the QRect associated with the given position. Used for drawing the desks

        :param x: row
        :param y: column
        :rtype: QRect
        """
        return QRect(QPoint(self.square_size * x, self.square_size * y),
                     QPoint(self.square_size * x + self.square_size, self.square_size * y + self.square_size))
