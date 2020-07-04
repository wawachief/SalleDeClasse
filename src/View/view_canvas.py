from PySide2.QtWidgets import QWidget
from PySide2.QtGui import QPainter, QColor, QPen, QPalette
from PySide2.QtCore import QPoint, QRect, Qt, Signal, Slot, QTimer, QThread, QObject

from time import sleep

PADDING = 1  # Padding of each tile
ANIMATE_REFRESH_RATE = 10  # In milliseconds
ANIMATION_DURATION = .7  # In seconds


class MoveAnimationThread(QThread):

    def __init__(self, departure, arrival, sig_update):
        """
        Handles the move animation of a tile

        :param departure: Tile departure coordinates (y, x)
        :type departure: tuple
        :param arrival: Tile arrival coordinates (y, x)
        :type arrival: tuple
        :param sig_update: Signal to emit when the coordinates changes
        :type sig_update: Signal
        """
        QThread.__init__(self)

        self.running = True
        self.__departure = departure
        self.__current = departure
        self.__arrival = arrival
        self.__sig_update = sig_update

        self.start()

    def run(self):
        ty, tx = self.__arrival  # Target coordinates
        sy, sx = self.__departure  # Start coordinates

        dy, dx = ty - sy, tx - sx

        t = ANIMATION_DURATION / 100

        vy = dy/ANIMATION_DURATION
        vx = dx/ANIMATION_DURATION

        i = 0
        while self.running and i <= 100 and self.__current != self.__arrival:
            y, x = self.__current

            y, x = t * vy + y, t * vx + x

            if abs(ty - y) <= 2 and abs(tx - x) <= 2:
                y, x = ty, tx

            self.__sig_update.emit(y, x)
            self.__current = (y, x)

            sleep(t)  # 10 ms
            i += 1


class ViewTile(QObject):

    sig_move_update = Signal(int, int)

    def __init__(self, row, column, square_size, sig_move_ended):
        """
        Description object, contains the information that needs to be displayed in the associated tile's position

        :param row: row coordinate
        :type row: int
        :param column: column coordinate
        :type column: int
        :param square_size: size of a square in the canvas (used to calculate the real position)
        :type square_size: int
        :param sig_move_ended: Signal to emit when an animated move ends.
        :type sig_move_ended: Signal
        """
        QObject.__init__(self)
        self.firstname = "Toto"
        self.lastname = "AZERTY"

        self.__square_size = square_size

        # Signals
        self.__sig_move_ended = sig_move_ended
        self.sig_move_update.connect(self.__on_move_updated)

        self.animate_thread = None

        # Positions
        self.__grid_pos = ()  # row/column position
        self.__real_pos = ()  # Mouse x/y position
        self.__move_end_pos = ()  # row/column position

        self.__set_position(row, column)

    def move(self, new_row, new_column, animate=False):
        """
        Moves this tile to the specified new position. If the new position is the same as the current one, does nothing.

        :param new_row: new row
        :type new_row: int
        :param new_column: new column
        :type new_column: int
        :param animate: trigger animation between the current position and the new one
        :type animate: bool
        :return if the move operation could be performed
        :rtype: bool
        """
        if self.animate_thread:  # If there is already a move animation, we don't do anything
            return False

        if self.__grid_pos == (new_row, new_column):  # Position is the same
            return False

        if not animate:
            self.__set_position(new_row, new_column)
        else:
            self.__move_end_pos = (new_row, new_column)

            # Convert grid positions into mouse positions for arrival position
            self.animate_thread = MoveAnimationThread(self.real_position(),
                                                      (new_column * self.__square_size, new_row * self.__square_size),
                                                      self.sig_move_update)
        return True

    @Slot(int, int)
    def __on_move_updated(self, y, x):
        """
        Triggered when the animated move position changes

        :param y: new mouse position y coordinate
        :param x: new mouse position x coordinate
        """
        if (x // self.__square_size, y // self.__square_size) == self.__move_end_pos:  # End condition
            self.__process_animation_ended()
        else:
            self.__real_pos = (y, x)

    def __process_animation_ended(self):
        """
        Performs the operations needed when the move animation is finished
        """
        self.__set_position(self.__move_end_pos[0], self.__move_end_pos[1])  # Update final position
        self.__move_end_pos = ()  # Reset move position
        self.__sig_move_ended.emit()

    def abort_animation(self):
        """
        Interrupts the running animation and goes directly to the target position
        """
        if self.animate_thread:
            self.animate_thread.running = False  # Stops the Thread
            self.__process_animation_ended()

    def __set_position(self, row, column):
        """
        Sets the current row and column, and calculates the real position (top-left corner) associated to this position.

        :param row: row coordinate
        :type row: int
        :param column: column coordinate
        :type column: int
        """
        self.__grid_pos = (row, column)
        self.__real_pos = (column * self.__square_size, row * self.__square_size)

    def grid_position(self):
        """
        Gets the GRID position of this tile, the row, column in which it is

        :return: grid position of the tile (row, column)
        :rtype: tuple
        """
        return self.__grid_pos

    def real_position(self):
        """
        Gets the REAL position of this tile given the row/column it represents

        :return: position to draw the tile to (y, x)
        :rtype: tuple
        """
        return self.__real_pos


class ViewCanvas(QWidget):

    sig_move_ended = Signal()

    def __init__(self, config):
        """
        Application's main canvas, in which is drawn desks and student's names.

        :param config: application's parsed configuration
        """
        QWidget.__init__(self)

        self.config = config

        self.square_size = int(config.get('size', 'desk'))
        self.setAutoFillBackground(True)

        self.__tiles = []  # List of all drawn tiles

        self.sig_canvas_click = None  # Signal triggered when a click is performed on a desk
        self.sig_canvas_drag = None  # Signal triggered when a drag operation is performed on the canvas

        # Tracking for drag/drop operation
        self.__click_pos = ()  # Stored (row, column) position
        self.__mouse_pos = ()  # Stored (x, y) mouse position

        # Signals
        self.sig_move_ended.connect(self.on_move_ended)

        self.__running_animations = 0
        self.update_timer = None  # Timer running only during animations to perform the UI update

        nb_rows = int(self.config.get('size', 'default_room_rows'))
        nb_columns = int(self.config.get('size', 'default_room_columns'))
        self.setFixedSize(self.square_size * nb_columns, self.square_size * nb_rows)
        self.__init_style()

    def __init_style(self):
        """
        Sets the background of this canvas widget
        """
        pal = QPalette()
        pal.setColor(QPalette.Background, self.config.get('colors', 'room_bg'))
        self.setPalette(pal)

    def remove_tile(self, row, column):
        """
        Removes the tile at the given row/column position

        :param row: tile's row
        :param column: tile's column
        """
        for t in self.__tiles:
            if t.grid_position() == (row, column):
                self.__tiles.remove(t)
                break

    def new_tile(self, row, column):
        """
        Creates a new tile at the given position.

        :param row: row coordinate
        :type row: int
        :param column: column coordinate
        :type column: int
        """
        self.__tiles.append(ViewTile(row, column, self.square_size, self.sig_move_ended))

    def move_tile(self, current_pos, new_pos, animate=False):
        """
        Moves the specified tile from its original position to the new given one.

        :param current_pos: Current grid's position of the tile (row, column)
        :type current_pos: tuple
        :param new_pos: New grid position (row, column)
        :type new_pos: tuple
        :param animate: trigger animation between the current position and the new one
        :type animate: bool
        """
        # Look for the tile to animate
        ok = False
        for t in self.__tiles:
            if t.grid_position() == current_pos:
                ok = t.move(new_pos[0], new_pos[1], animate)  # Check that the animation is running
                break

        if animate and ok:
            if not self.__running_animations:  # If this is the first animation, start the update timer
                self.update_timer = QTimer(parent=self)
                self.update_timer.timeout.connect(lambda: self.repaint())
                self.update_timer.start(ANIMATE_REFRESH_RATE)

            self.__running_animations += 1
            print("[CANVAS-DEBUG] - Animation started, running:", self.__running_animations)

    @Slot()
    def on_move_ended(self):
        """
        Triggered once a move animation have ended
        """
        self.__running_animations -= 1

        print("[CANVAS-DEBUG] - Animation ended, left:", self.__running_animations)

        if not self.__running_animations:  # once all animations have ended, stop the timer
            self.update_timer.stop()
            self.update_timer = None
            self.repaint()

    def application_closing(self):
        """
        Calls abort processes on tiles in case there are animation running
        """
        if self.__running_animations:
            for t in self.__tiles:
                t.abort_animation()

    def paintEvent(self, event):
        """
        Draws the desks and students' names given the self.tiles list
        """
        super().paintEvent(event)

        # Current tile hovered by the mouse
        tile_hover_pos = self.__convert_point(self.__mouse_pos[0], self.__mouse_pos[1]) if self.__mouse_pos else None
        tile_hover = None

        painter = QPainter(self)
        pen = QPen()
        pen.setColor(QColor(self.config.get('colors', 'tile_text')))
        painter.setPen(pen)

        # Drawing of all the tiles
        for t in self.__tiles:
            y, x = t.real_position()
            if t.grid_position() == self.__click_pos:  # If the tile is selected
                tile_hover = t
                color = QColor(self.config.get('colors', 'selected_tile'))
            elif t.grid_position() == tile_hover_pos:  # If the mouse is hover
                color = QColor(self.config.get('colors', 'hovered_tile'))
            else:  # Regular tile
                color = QColor(self.config.get('colors', 'tile'))
            rect = self.__get_rect_at(y, x)
            painter.fillRect(rect, color)
            painter.drawText(rect, Qt.AlignCenter | Qt.TextWordWrap, f"{t.firstname}\n{t.lastname}")

        # Dragged tile
        if self.__click_pos != tile_hover_pos and tile_hover and self.__mouse_pos:
            # If the mouse is no longer hover the clicked tile we draw the dragged tile
            self.__draw_dragged_tile(painter, tile_hover, self.__mouse_pos[0], self.__mouse_pos[1])

    def __draw_dragged_tile(self, painter, tile, x, y):
        """
        Draws the given tile under the mouse position

        :param painter: painter object
        :param tile: tile data object
        :param x: real mouse position x
        :param y: real mouse position y
        """
        rect = QRect(QPoint(PADDING + y, PADDING + x),
                     QPoint(y + self.square_size - PADDING, x + self.square_size - PADDING))
        painter.fillRect(rect, QColor(self.config.get('colors', 'dragged_tile')))
        painter.drawText(rect, Qt.AlignCenter | Qt.TextWordWrap, f"{tile.firstname}\n{tile.lastname}")

    def mousePressEvent(self, event):
        """
        Intercepts the mousePressEvent in order to get where the user clicked. We will compare this in the
        mouseReleaseEvent to process the event.
        """
        if event.button() == Qt.LeftButton:
            self.__click_pos = self.__convert_point(event.y(), event.x())  # Register the click point

    def mouseMoveEvent(self, event):
        if not self.__click_pos:  # The drag operation is performed only with a left click
            return

        self.__mouse_pos = (event.y(), event.x())
        self.repaint()

    def mouseReleaseEvent(self, event):
        """
        Processes the click operation.
        If the user clicked and released inside the same tile, we consider it a simple click.

        If the user clicked and released in two different tiles, we consider it as a drag/drop operation.
        """

        click_end_pos = self.__convert_point(event.y(), event.x())

        if click_end_pos == self.__click_pos:
            self.sig_canvas_click.emit(self.__convert_point(event.y(), event.x()))
        else:
            print(self.__click_pos, click_end_pos)
            # self.sig_canvas_drag.emit(self.click_pos, click_end_pos)

        self.__click_pos = ()
        self.__mouse_pos = ()
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
        Gets the QRect associated with the given position. The x, y values given corresponds to the top-left corner

        :param x: mouse x
        :param y: mouse y
        :rtype: QRect
        """
        return QRect(QPoint(PADDING + x, PADDING + y), QPoint(x + self.square_size - PADDING,
                                                              y + self.square_size - PADDING))
