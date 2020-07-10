from PySide2.QtWidgets import QMainWindow, QWidget, QDockWidget, QGridLayout
from PySide2.QtCore import Qt, Signal

from src.View.view_canvas import ViewCanvas
from src.View.view_sidepanel import ViewSidePanel
from src.View.widgets.view_board import ViewTeacherDeskLabel, ViewTopics
from src.View.widgets.view_toolbar import ViewMainToolBar
from src.View.widgets.view_courses import ViewCoursePanel
from src.View.widgets.view_students import ViewStudentPanel
from src.View.widgets.view_attributes import ViewAttributePanel


class CentralWidget(QWidget):

    sig_move_animation_ended = Signal()

    def __init__(self, config):
        """
        Application's central widget, contains all the app's widgets.

        :param config: application's parsed configuration
        """
        QWidget.__init__(self)

        self.config = config

        self.v_canvas = ViewCanvas(config, self.sig_move_animation_ended)  # Central canvas

        self.view_students = ViewTeacherDeskLabel("Vue élève", config.get('colors', 'board_bg'))
        self.view_teacher = ViewTeacherDeskLabel("Vue prof", config.get('colors', 'board_bg'))
        self.is_view_students: bool = None  # Current view

        self.topic = ViewTopics()

        # Signals
        self.sig_add_tile = None
        self.sig_shuffle = None
        self.sig_enable_animation_btns = None
        # When the move animation ends, we can re-activate the buttons
        self.sig_move_animation_ended.connect(lambda: self.sig_enable_animation_btns.emit(True))

        self.__set_layout()
        self.on_perspective_changed()  # This will switch the is_view_student flag and display the students' view

    def __set_layout(self):
        """
        Initializes the layout of this widget
        """
        layout = QGridLayout()

        # Widgets
        layout.addWidget(self.topic, 0, 0)
        layout.addWidget(self.view_students, 0, 1)
        layout.addWidget(self.v_canvas, 1, 0, 1, 3)
        layout.addWidget(self.view_teacher, 2, 0, 1, 3)

        # Alignments
        layout.setAlignment(self.topic, Qt.AlignLeft)
        layout.setAlignment(self.view_students, Qt.AlignCenter)
        layout.setAlignment(self.v_canvas, Qt.AlignCenter)
        layout.setAlignment(self.view_teacher, Qt.AlignCenter)

        self.setLayout(layout)

    def on_perspective_changed(self):
        """
        Switches the current view perspective and updates boards display and canvas
        """
        if self.is_view_students is None:  # To prevent updating the canvas for the initialization
            self.is_view_students = True
        else:
            self.sig_enable_animation_btns.emit(False)  # Freeze btn for preventing multiple clicks
            self.is_view_students = not self.is_view_students
            self.v_canvas.perspective_changed()

        self.view_students.activate(self.is_view_students)
        self.view_teacher.activate(not self.is_view_students)

    def do_magic(self):
        self.sig_add_tile.emit()

    def do_shuffle(self):
        self.sig_enable_animation_btns.emit(False)
        self.sig_shuffle.emit()


class SideDockWidget(QDockWidget):

    def __init__(self, config):
        """
        Dockable widget containing the Side Panel

        :param config: application's parsed configuration
        """
        QDockWidget.__init__(self)

        self.sidepanel = ViewSidePanel(config)

        self.setWidget(self.sidepanel)
        self.setAllowedAreas(Qt.LeftDockWidgetArea)
        self.setFeatures(QDockWidget.DockWidgetFloatable)

    def courses(self):
        """
        Getter for the courses panel
        :rtype: ViewCoursePanel
        """
        return self.sidepanel.courses_panel

    def students(self):
        """
        Getter for the students panel
        :rtype: ViewStudentPanel
        """
        return self.sidepanel.students_panel

    def attributes(self):
        """
        Getter for the attributes panel
        :rtype: ViewAttributePanel
        """
        return self.sidepanel.attributes_panel


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
        self.central_widget = CentralWidget(config)
        self.sidewidget = SideDockWidget(config)

        self.sidewidget.dockLocationChanged.connect(self.on_side_widget_docked_state_changed)

        self.__init_callbacks()

        # Layout
        self.setCentralWidget(self.central_widget)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.sidewidget)
        self.addToolBar(Qt.RightToolBarArea, self.maintoolbar)

        self.sig_quit = sig_quit

        self.setStyleSheet("QMainWindow {" + f"background-color: {config.get('colors', 'main_bg')};" + "}")

    def __init_callbacks(self):
        """
        Dispatches the callbacks from the toolbar to the handling widgets. Also init the signal triggered to enable
        or disable some buttons.
        """
        self.maintoolbar.on_btn_magic_clicked = self.central_widget.do_magic
        self.maintoolbar.on_btn_perspective_clicked = self.central_widget.on_perspective_changed
        self.maintoolbar.on_btn_shuffle_clicked = self.central_widget.do_shuffle

        self.central_widget.sig_enable_animation_btns = self.maintoolbar.sig_enable_animation_btns

    def on_side_widget_docked_state_changed(self):
        """
        Triggered when the side dockable widget has been docked or undocked
        """
        if self.sidewidget.isFloating():
            self.adjustSize()

    def closeEvent(self, event):
        """
        Triggered on a close operation. Signals to the controller the event
        """
        self.sig_quit.emit()
        event.accept()
