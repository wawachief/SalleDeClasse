from PySide2.QtWidgets import QMainWindow, QWidget, QPushButton, QVBoxLayout
from PySide2.QtCore import Qt, Signal, Slot

from src.View.view_canvas import ViewCanvas
from src.View.widgets.view_board import ViewTeacherDeskLabel
from src.View.widgets.view_toolbar import ViewMainToolBar


class CentralWidget(QWidget):

    sig_move_animation_ended = Signal()

    def __init__(self, config, sig_enable_perspective_btn):
        """
        Application's central widget, contains all the app's widgets.

        :param config: application's parsed configuration
        :param sig_enable_perspective_btn: Signal to emit to update the enable state of the change perspective button
        :type sig_enable_perspective_btn: Signal
        """
        QWidget.__init__(self)

        self.config = config

        self.v_canvas = ViewCanvas(config, self.sig_move_animation_ended)  # Central canvas

        self.view_students = ViewTeacherDeskLabel("Vue élève", config.get('colors', 'board_bg'))
        self.view_teacher = ViewTeacherDeskLabel("Vue prof", config.get('colors', 'board_bg'))
        self.is_view_students = None  # Current view

        self.sig_add_tile = None
        self.sig_enable_perspective_btn = sig_enable_perspective_btn
        # When the move animation ends, we can re-activate the button
        self.sig_move_animation_ended.connect(lambda: self.sig_enable_perspective_btn.emit(True))

        self.__set_layout()
        self.on_perspective_changed()  # This will switch the is_view_student flag and display the students' view

    def __set_layout(self):
        """
        Initializes the layout of this widget
        """
        layout = QVBoxLayout()

        # Widgets
        layout.addWidget(self.view_students)
        layout.addWidget(self.v_canvas)
        layout.addWidget(self.view_teacher)

        # Alignments
        layout.setAlignment(self.view_students, Qt.AlignCenter)
        layout.setAlignment(self.view_teacher, Qt.AlignCenter)

        self.setLayout(layout)

    def on_perspective_changed(self):
        """
        Switches the current view perspective and updates boards display and canvas
        """
        if self.is_view_students is None:  # To prevent updating the canvas for the initialization
            self.is_view_students = True
        else:
            self.sig_enable_perspective_btn.emit(False)  # Freeze btn for preventing multiple clicks
            self.is_view_students = not self.is_view_students
            self.v_canvas.perspective_changed()

        self.view_students.activate(self.is_view_students)
        self.view_teacher.activate(not self.is_view_students)

    def do_magic(self):
        self.sig_add_tile.emit()


class ViewMainFrame(QMainWindow):

    def __init__(self, sig_quit, config):
        """
        Main application's frame

        :param sig_quit: signal to trigger when the application closes
        :param config: application's parsed configuration
        """
        QMainWindow.__init__(self)

        # Widgets
        self.maintoolbar = ViewMainToolBar(config)
        self.central_widget = CentralWidget(config, self.maintoolbar.sig_enable_perspective_btn)

        self.__init_callbacks()

        # Layout
        self.setCentralWidget(self.central_widget)
        self.addToolBar(self.maintoolbar)

        self.sig_quit = sig_quit

        self.setStyleSheet("QMainWindow {" + f"background-color: {config.get('colors', 'main_bg')};" + "}")

    def __init_callbacks(self):
        """
        Dispatches the callbacks from the toolbar to the handling widgets
        """
        self.maintoolbar.on_btn_magic_clicked = self.central_widget.do_magic
        self.maintoolbar.on_btn_perspective_clicked = self.central_widget.on_perspective_changed

    def closeEvent(self, event):
        """
        Triggered on a close operation. Signals to the controller the event
        """
        self.sig_quit.emit()
        event.accept()
