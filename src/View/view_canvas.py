from PySide2.QtWidgets import QWidget, QDialog
from PySide2.QtGui import QPainter, QColor, QPen, QPalette, QFont
from PySide2 import QtPrintSupport
from PySide2.QtCore import QPoint, QRect, Qt, Signal, Slot, QTimer, QThread, QObject

from src.assets_manager import AssetManager

from time import sleep

PADDING = 1  # Padding of each tile
ANIMATE_REFRESH_RATE = 10  # In milliseconds
ANIMATION_DURATION = .3  # In seconds


class MoveAnimationThread(QThread):

    def __init__(self, departure, arrival, sig_update, sig_end):
        """
        Handles the move animation of a tile

        :param departure: Tile departure coordinates (y, x)
        :type departure: tuple
        :param arrival: Tile arrival coordinates (y, x)
        :type arrival: tuple
        :param sig_update: Signal to emit when the coordinates changes
        :type sig_update: Signal
        :param sig_update: Signal to emit when the animation is finished
        :type sig_update: Signal
        """
        QThread.__init__(self)

        self.running = True
        self.__departure = departure
        self.__current = departure
        self.__arrival = arrival
        self.__sig_update = sig_update
        self.__sig_end = sig_end

        self.start()

    def run(self):
        ty, tx = self.__arrival  # Target coordinates
        sy, sx = self.__departure  # Start coordinates

        dy, dx = ty - sy, tx - sx

        t = ANIMATION_DURATION / 100

        vy = dy / ANIMATION_DURATION
        vx = dx / ANIMATION_DURATION

        i = 0
        while self.running and i <= 100 and self.__current != self.__arrival:
            sleep(t)
            i += 1

            y, x = self.__current

            y, x = t * vy + y, t * vx + x

            if abs(ty - y) <= 5 and abs(tx - x) <= 5:
                y, x = ty, tx

            self.__sig_update.emit(y, x)
            self.__current = (y, x)

        self.__sig_end.emit()


class ViewTile(QObject):
    sig_move_update = Signal(int, int)
    sig_thread_finished = Signal()

    def __init__(self, row, column, square_size, sig_move_ended, sig_select_tile, desk_id):
        """
        Description object, contains the information that needs to be displayed in the associated tile's position.
        This is the UI twin of Model's Desk object.

        :param row: row coordinate
        :type row: int
        :param column: column coordinate
        :type column: int
        :param square_size: size of a square in the canvas (used to calculate the real position)
        :type square_size: int
        :param sig_move_ended: Signal to emit when an animated move ends.
        :type sig_move_ended: Signal
        :param desk_id: unique identifier
        :type desk_id: int
        """
        QObject.__init__(self)

        self.__firstname = ""
        self.__lastname = ""

        self.__desk_id = desk_id

        self.__square_size = square_size

        self.__is_selected = False

        # Signals
        self.sig_select_tile = sig_select_tile
        self.__sig_move_ended = sig_move_ended
        self.sig_move_update.connect(self.__on_move_updated)
        self.sig_thread_finished.connect(self.__process_animation_ended)

        self.animate_thread = None

        # Positions
        self.__grid_pos = ()  # row/column position
        self.__real_pos = ()  # Mouse x/y position
        self.__move_end_pos = ()  # row/column position

        self.__set_position(row, column)

    def __str__(self):
        return f"ID: {self.id()}, First name: {self.firstname()}, Last name: {self.lastname()}, " \
               f"Grid Position: {self.grid_position()}"

    def set_student(self, firstname, lastname):
        """
        Sets the student data inside this tile

        :param firstname: Student's first name
        :type firstname: str
        :param lastname: Student's last name
        :type lastname: str
        """
        self.__firstname = firstname
        self.__lastname = lastname

    def toggle_selection(self):
        """
        Switches the current selection value
        """
        self.__is_selected = not self.__is_selected
        self.sig_select_tile.emit()

    def set_selection(self, value):
        """
        sets the current selection value
        """
        self.__is_selected = value
        self.sig_select_tile.emit()

    def is_selected(self):
        """
        :return: True if this tile is selected
        """
        return self.__is_selected

    def firstname(self):
        """
        :return: Student's first name
        """
        return self.__firstname

    def lastname(self):
        """
        :return: Student's last name
        """
        return self.__lastname

    def id(self):
        """
        :return: Desk id
        """
        return self.__desk_id

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
        if self.__grid_pos == (new_row, new_column):  # Position is the same
            return False

        if not animate:
            self.__set_position(new_row, new_column)
        else:
            if self.animate_thread:  # If there is already a move animation, we don't do anything
                print("[TILE-DEBUG] - Can't move, an animation is still in motion:", self)
                return False

            self.__move_end_pos = (new_row, new_column)

            # Convert grid positions into mouse positions for arrival position
            self.animate_thread = MoveAnimationThread(self.real_position(),
                                                      (new_column * self.__square_size, new_row * self.__square_size),
                                                      self.sig_move_update, self.sig_thread_finished)
            self.animate_thread.finished.connect(self.animate_thread_finished)

        return True

    @Slot(int, int)
    def __on_move_updated(self, y, x):
        """
        Triggered when the animated move position changes

        :param y: new mouse position y coordinate
        :param x: new mouse position x coordinate
        """
        self.__real_pos = (y, x)

    @Slot()
    def __process_animation_ended(self):
        """
        Performs the operations needed when the move animation is finished
        """
        self.__set_position(self.__move_end_pos[0], self.__move_end_pos[1])  # Update final position
        self.__move_end_pos = ()  # Reset move position
        self.__sig_move_ended.emit()

    @Slot()
    def animate_thread_finished(self):
        self.animate_thread = None

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

    def __init__(self, sig_move_animation_ended):
        """
        Application's main canvas, in which is drawn desks and student's names.

        :param sig_move_animation_ended: signal to trigger when the move animation ends
        :type sig_move_animation_ended: Signal
        """
        QWidget.__init__(self)

        self.square_size = int(AssetManager.getInstance().config('size', 'desk'))
        self.setAutoFillBackground(True)

        self.__tiles = {}  # All drawn tiles
        self.tmp = {}
        self.hovered = False

        self.is_view_students = True
        self.__do_switch = False
        self.__is_config = False

        self.sig_canvas_click = None  # Signal triggered when a click is performed on a desk
        self.sig_desk_selected = None  # Signal triggered when a non empty desk is selected
        self.sig_canvas_drag = None  # Signal triggered when a drag operation is performed on the canvas
        self.sig_select_tile = None  # pushed by the controller. emits when tile selection change.
        self.sig_tile_info = None  # Signal triggered when a right-click is performed on a desk. Info is to be displayed
        self.sig_move_animation_ended = sig_move_animation_ended

        # Tracking for drag/drop operation
        self.__click_pos = ()  # Stored (row, column) position
        self.__mouse_pos = ()  # Stored (x, y) mouse position

        # Signals
        self.sig_move_ended.connect(self.on_move_ended)

        self.__running_animations = 0
        self.update_timer = None  # Timer running only during animations to perform the UI update

        self.nb_rows = int(AssetManager.getInstance().config('size', 'default_room_rows'))
        self.nb_columns = int(AssetManager.getInstance().config('size', 'default_room_columns'))
        self.setFixedSize(self.square_size * self.nb_columns, self.square_size * self.nb_rows)
        self.__init_style()

    def __init_style(self):
        """
        Sets the background of this canvas widget
        """
        color = AssetManager.getInstance().config('colors', 'room_bg') if self.__is_config else "white"

        pal = QPalette()
        pal.setColor(QPalette.Background, QColor(color))
        self.setPalette(pal)

    def config_mode(self, is_config: bool) -> None:
        """
        Switches the config mode flag
        """
        self.__is_config = is_config
        self.__init_style()
        self.repaint()

    def remove_tile(self, desk_id):
        """
        Removes the tile at the given row/column position

        :param desk_id: tile's ID
        :type desk_id: int
        """
        self.__tiles.pop(desk_id)

    def delete_all_tiles(self):
        """
        Removes the tile at the given row/column position

        :param desk_id: 
        :type desk_id:
        """
        self.__tiles = {}

    def new_tile(self, row, column, desk_id, firstname="", lastname=""):
        """
        Creates a new tile at the given position.

        :param row: row coordinate
        :type row: int
        :param column: column coordinate
        :type column: int
        :param desk_id: desk id
        :type desk_id: int
        :param firstname: Student's first name
        :type firstname: str
        :param lastname: Student's last name
        :type lastname: str
        """
        new_tile = ViewTile(row, column, self.square_size, self.sig_move_ended, self.sig_select_tile, desk_id)
        new_tile.set_student(firstname, lastname)

        self.__tiles[desk_id] = new_tile

    def set_student(self, desk_id, firstname, lastname):
        """
        Sets the student's information at the given position

        :param desk_id: desk id
        :type desk_id: int
        :param firstname: Student's first name
        :type firstname: str
        :param lastname: Student's last name
        :type lastname: str
        """
        self.__tiles[desk_id].set_student(firstname, lastname)

    def move_tile(self, desk_id, new_pos, animate=False):
        """
        Moves the specified tile from its original position to the new given one.

        :param desk_id: Tile's associated id
        :type desk_id: int
        :param new_pos: New grid position (row, column)
        :type new_pos: tuple
        :param animate: trigger animation between the current position and the new one
        :type animate: bool
        """
        # Look for the tile to animate
        ok = self.__tiles[desk_id].move(new_pos[0], new_pos[1], animate)  # Check that the animation is running

        if animate and ok:
            if not self.__running_animations:  # If this is the first animation, start the update timer
                self.update_timer = QTimer(parent=self)
                self.update_timer.timeout.connect(lambda: self.repaint())
                self.update_timer.start(ANIMATE_REFRESH_RATE)

            self.__running_animations += 1
            # print("[CANVAS-DEBUG] - Animation started, running:", self.__running_animations)

    @Slot()
    def on_move_ended(self):
        """
        Triggered once a move animation have ended
        """
        self.__running_animations -= 1

        # print("[CANVAS-DEBUG] - Animation ended, left:", self.__running_animations)

        if not self.__running_animations:  # once all animations have ended, stop the timer
            sleep(ANIMATE_REFRESH_RATE / 1000)

            if self.__do_switch:

                self.is_view_students = not self.is_view_students  # Switch the flag

                # Put the tiles to their regular coordinates
                for t in list(self.__tiles.values()):
                    self.move_tile(t.id(), self.__relative_grid_position(t.grid_position(), True))

                self.__do_switch = False

            self.update_timer.stop()
            self.update_timer = None

            self.sig_move_animation_ended.emit()
            self.repaint()

    def application_closing(self):
        """
        Calls abort processes on tiles in case there are animation running
        """
        if self.__running_animations:
            for t in list(self.__tiles.values()):
                t.abort_animation()

    def paintEvent(self, event):
        """
        Draws the desks and students' names given the self.tiles list
        """
        painter = QPainter(self)
        color = AssetManager.getInstance().config('colors', 'room_grid') if self.__is_config else "white"

        pen = QPen()
        pen.setColor(QColor(color))
        pen.setWidth(2)
        painter.setPen(pen)

        # Draw the grid
        for r in range(self.nb_rows):
            painter.drawLine(QPoint(0, r * self.square_size),
                             QPoint(self.square_size * self.nb_columns, r * self.square_size))

        for c in range(self.nb_columns):
            painter.drawLine(QPoint(c * self.square_size, 0),
                             QPoint(c * self.square_size, self.square_size * self.nb_rows))

        # Update painter color and font size for tiles
        pen.setColor(QColor(AssetManager.getInstance().config('colors', 'tile_text')))
        painter.setPen(pen)

        font = QFont()
        font.setPixelSize(10)
        painter.setFont(font)

        # Current tile selected by the mouse
        tile_selected_pos = self.__convert_point(self.__mouse_pos[0], self.__mouse_pos[1]) if self.__mouse_pos else None
        tile_selected = None
        self.hovered = False

        # Drawing of all the tiles
        for t in list(self.__tiles.values()):
            y, x = self.__relative_mouse_position(t.real_position())
            if self.__relative_grid_position(t.grid_position()) == self.__click_pos and self.__is_config:  # If the tile is selected
                tile_selected = t
                color = QColor(AssetManager.getInstance().config('colors', 'drag_selected_tile'))
            elif self.__relative_grid_position(t.grid_position()) == tile_selected_pos and self.__is_config:  # If the mouse is hover
                self.hovered = True
                color = QColor(AssetManager.getInstance().config('colors', 'hovered_tile'))
            elif t.is_selected():
                color = QColor(AssetManager.getInstance().config('colors', 'selected_tile'))
            else:  # Regular tile
                color = QColor(AssetManager.getInstance().config('colors', 'tile'))
            rect = self.__get_rect_at(y, x)
            painter.fillRect(rect, color)
            painter.drawText(rect, Qt.AlignCenter | Qt.TextWordWrap, f"{t.lastname()}\n{t.firstname()}")

        # Dragged tile
        if self.__click_pos != self.__relative_grid_position(tile_selected_pos) \
                and tile_selected and self.__mouse_pos and self.__is_config:
            # If the mouse is no longer hover the clicked tile we draw the dragged tile
            self.__draw_dragged_tile(painter, tile_selected, self.__mouse_pos[0], self.__mouse_pos[1])

    def __draw_dragged_tile(self, painter, tile, x, y):
        """
        Draws the given tile under the mouse position

        :param painter: painter object
        :param tile: tile data object
        :param x: real mouse position x
        :param y: real mouse position y
        """
        if not self.hovered:  # If there is no tile under the dragged one, we draw a light gray rect below it
            # Convert x and y to get the hovered empty tile position
            hov_x = x // self.square_size * self.square_size
            hov_y = y // self.square_size * self.square_size
            hov_rect = self.__get_rect_at(hov_y, hov_x)
            painter.fillRect(hov_rect, QColor(AssetManager.getInstance().config('colors', 'hovered_empty_tile')))

        rect = QRect(QPoint(PADDING + y - self.square_size / 2, PADDING + x - self.square_size / 2),
                     QPoint(y + self.square_size / 2 - PADDING, x + self.square_size / 2 - PADDING))
        painter.fillRect(rect, QColor(AssetManager.getInstance().config('colors', 'dragged_tile')))
        painter.drawText(rect, Qt.AlignCenter | Qt.TextWordWrap, f"{tile.lastname()}\n{tile.firstname()}")

    def get_selected_tiles(self):
        """
        Gets the list of all selected tiles

        :return: Selected tiles IDs (using the ID_Desk that was used for their creation)
        :rtype list
        """
        ids = []
        for t in list(self.__tiles.values()):
            if t.is_selected():
                ids.append(t.id())

        return ids

    def select_tiles_to(self, value):
        """sets tiles selection to value"""
        for t in list(self.__tiles.values()):
            t.set_selection(value)

    def change_desk_selection_by_desk_id(self, desk_id, selected):
        """sets desk (of desk_id) selection to selected"""
        self.__tiles[desk_id].set_selection(selected)

    def select_tiles_from_desks_ids(self, d_ids):
        """select tiles according to desk ids"""
        for t in list(self.__tiles.values()):
            t.set_selection(t.id() in d_ids)

    def mousePressEvent(self, event):
        """
        Intercepts the mousePressEvent in order to get where the user clicked. We will compare this in the
        mouseReleaseEvent to process the event.
        """
        if event.button() == Qt.LeftButton and not self.__running_animations:  # We don't allow clicks during animations
            self.__click_pos = self.__convert_point(event.y(), event.x())  # Register the click point
        elif event.button() == Qt.RightButton and not self.__running_animations:
            self.sig_tile_info.emit(self.__relative_grid_position(self.__convert_point(event.y(), event.x())))

    def mouseMoveEvent(self, event):
        """
        Updates the mouse position
        """
        if not self.__click_pos or not self.__is_config:  # The drag operation is performed only with a left click
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

        rel_end_pos = self.__relative_grid_position(click_end_pos)
        rel_start_pos = self.__relative_grid_position(self.__click_pos)

        if rel_end_pos == rel_start_pos:
            selected_tile = None
            for t in list(self.__tiles.values()):
                # Check if the click position is on an existing tile
                if t.grid_position() == rel_end_pos:
                    selected_tile = t
                    break

            # We emit the signal only if we clicked on an empty tile (e.g. no tile is selected)
            if not selected_tile and self.__is_config:
                self.sig_canvas_click.emit(rel_end_pos)
            elif selected_tile:
                selected_tile.toggle_selection()
                self.sig_desk_selected.emit(selected_tile.id(), selected_tile.is_selected())
        elif self.__is_config:  # Drag/Drop operation
            self.sig_canvas_drag.emit(rel_start_pos, rel_end_pos)

        self.__click_pos = ()
        self.__mouse_pos = ()
        self.repaint()

    def perspective_changed(self):
        """
        Changes the view perspective of the class
        """
        # In case there is no tiles, no move will be performed, hence no animation, so the switch would not be done.
        if not self.__tiles:
            self.is_view_students = not self.is_view_students  # Switch the flag
            self.sig_move_animation_ended.emit()
        else:
            # Perform the swicth animation
            self.__do_switch = True

            for t in list(self.__tiles.values()):
                self.tmp[t.id()] = t.grid_position()
                self.move_tile(t.id(), self.__relative_grid_position(t.grid_position(), True), True)

    def __relative_mouse_position(self, mouse_pos):
        """
        Gets the relative position of the mouse given the inversion of the tiles.

        If we are in student's view, nothing is changed.

        :param mouse_pos: mouse coordinates (y, x)
        :type mouse_pos: tuple
        """
        if not mouse_pos or self.is_view_students:
            return mouse_pos

        y, x = mouse_pos

        # Calculate reversed position using the canvas' dimensions
        return self.square_size * (self.nb_columns - 1) - y, self.square_size * (self.nb_rows - 1) - x

    def __relative_grid_position(self, grid_pos, get_opposite=False):
        """
        Gets the relative position inside the grid given the inversion of the tiles.

        If we are in student's view, nothing is changed.

        :param grid_pos: grid coordinates (row, column)
        :type grid_pos: tuple
        :param get_opposite: 'Overrides' the view checks and always returns the opposite coordinates as if the
        perspective was changed
        :type get_opposite: bool
        """
        if not get_opposite and (not grid_pos or self.is_view_students):
            return grid_pos
        row, column = grid_pos

        # Calculate reversed positions given the number of rows and columns
        return self.nb_rows - 1 - row, self.nb_columns - 1 - column

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
        return QRect(QPoint(PADDING + x, PADDING + y), QPoint(x + self.square_size - PADDING - 1,
                                                              y + self.square_size - PADDING - 1))
    def print_pdf(self):
        printer = QtPrintSupport.QPrinter()
        print_dpi = int(AssetManager.getInstance().config('size', 'print_dpi'))
        printer.setResolution(print_dpi)
        dialog = QtPrintSupport.QPrintDialog(printer, self)
        if dialog.exec_() == QtPrintSupport.QPrintDialog.Accepted:
            self.render(printer)
