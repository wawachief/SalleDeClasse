from PySide2.QtWidgets import QWidget
from PySide2.QtGui import QPainter, QColor, QPen, QPalette
from PySide2.QtCore import QPoint, QRect, Qt

OFFSET = 1


class ViewTile:

    def __init__(self, x, y):
        """
        Description object, contains the information that needs to be displayed in the associated tile's position

        :param x: row coordinate
        :param y: column coordinate
        """
        self.firstname = "Toto"
        self.lastname = "AZERTY"

        self.pos = (x, y)


class ViewCanvas(QWidget):

    def __init__(self, config):
        """
        Application's main canvas, in which is drawn desks and student's names.

        :param config: application's parsed configuration
        """
        QWidget.__init__(self)

        self.config = config

        self.square_size = int(config.get('size', 'desk'))
        self.setAutoFillBackground(True)
        self.tiles = []

        self.setFixedSize(self.square_size * 5, self.square_size * 5)

        self.sig_canvas_click = None  # Signal triggered when a click is performed on a desk
        self.sig_canvas_drag = None  # Signal triggered when a drag operation is performed on the canvas

        # Tracking for drag/drop operation
        self.click_pos = ()
        self.mouse_pos = ()

        self.__init_style()

    def __init_style(self):
        pal = QPalette()
        pal.setColor(QPalette.Background, self.config.get('colors', 'room_bg'))
        self.setPalette(pal)

    def paintEvent(self, event):
        """
        Draws the desks and students' names given the self.tiles list
        """
        super().paintEvent(event)

        tile_hover_pos = self.__convert_point(self.mouse_pos[0], self.mouse_pos[1]) if self.mouse_pos else None
        tile_hover = None

        painter = QPainter(self)
        pen = QPen()
        pen.setColor(QColor(self.config.get('colors', 'tile_text')))
        painter.setPen(pen)

        for t in self.tiles:
            x, y = t.pos
            if t.pos == self.click_pos:  # If the tile is selected
                tile_hover = t
                color = QColor(self.config.get('colors', 'selected_tile'))
            elif t.pos == tile_hover_pos:  # If the mouse is hover
                color = QColor(self.config.get('colors', 'hovered_tile'))
            else:  # Regular tile
                color = QColor(self.config.get('colors', 'tile'))
            rect = self.__get_rect_at(x, y)
            painter.fillRect(rect, color)
            painter.drawText(rect, Qt.AlignCenter | Qt.TextWordWrap, f"{t.firstname}\n{t.lastname}")

        if self.click_pos != tile_hover_pos and tile_hover and self.mouse_pos:
            # If the mouse is no longer hover the clicked tile we draw the dragged tile
            self.__draw_dragged_tile(painter, tile_hover, self.mouse_pos[0], self.mouse_pos[1])

    def __draw_dragged_tile(self, painter, tile, x, y):
        """
        Draws the given tile under the mouse position

        :param painter: painter object
        :param tile: tile data object
        :param x: real mouse position x
        :param y: real mouse position y
        """
        rect = QRect(QPoint(OFFSET + x, OFFSET + y),
                     QPoint(x + self.square_size - OFFSET, y + self.square_size - OFFSET))
        painter.fillRect(rect, QColor(self.config.get('colors', 'dragged_tile')))
        painter.drawText(rect, Qt.AlignCenter | Qt.TextWordWrap, f"{tile.firstname}\n{tile.lastname}")

    def mousePressEvent(self, event):
        """
        Intercepts the mousePressEvent in order to get where the user clicked. We will compare this in the
        mouseReleaseEvent to process the event.
        """
        if event.button() == Qt.LeftButton:
            self.click_pos = self.__convert_point(event.x(), event.y())  # Register the click point

    def mouseMoveEvent(self, event):
        if not self.click_pos:  # The drag operation is performed only with a left click
            return

        self.mouse_pos = (event.x(), event.y())
        self.repaint()

    def mouseReleaseEvent(self, event):
        """
        Processes the click operation.
        If the user clicked and released inside the same tile, we consider it a simple click.

        If the user clicked and released in two different tiles, we consider it as a drag/drop operation.
        """

        click_end_pos = self.__convert_point(event.x(), event.y())

        if click_end_pos == self.click_pos:
            self.sig_canvas_click.emit(self.__convert_point(event.x(), event.y()))
        else:
            print(self.click_pos, click_end_pos)
            # self.sig_canvas_drag.emit(self.click_pos, click_end_pos)

        self.click_pos = ()
        self.mouse_pos = ()
        self.repaint()

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
        return QRect(QPoint(OFFSET + self.square_size * x, OFFSET + self.square_size * y),
                     QPoint(self.square_size * x + self.square_size - OFFSET,
                            self.square_size * y + self.square_size - OFFSET))
