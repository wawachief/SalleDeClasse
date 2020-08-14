# Salle de classe by Lecluse DevCorp
# file author : Thomas Lecluse
# Licence GPL-v3 - see LICENCE.txt

from PySide2 import QtCore
from PySide2.QtWidgets import QMainWindow, QWidget, QDockWidget, QGridLayout, QStatusBar, QTabWidget, QFileDialog
from PySide2.QtCore import Qt, Signal, QSize

from src.View.popup.view_about_box import AboutFrame
from src.View.popup.view_settings import SettingsEditionDialog
from src.View.view_canvas import ViewCanvas
from src.View.view_sidepanel import ViewSidePanel
from src.View.widgets.view_board import ViewTeacherDeskLabel
from src.View.widgets.view_toolbar import ViewMainToolBar
from src.View.widgets.view_courses import ViewCoursePanel
from src.View.widgets.view_students import ViewStudentPanel
from src.View.widgets.view_attributes_list import ViewAttributePanel
from src.View.view_attributes_tab import AttributesTab

from src.assets_manager import AssetManager, tr, get_icon

from src.View.popup.view_confirm_dialogs import VConfirmDialog

EXIT_CODE_REBOOT = -11231351


class CentralWidget(QTabWidget):
    sig_move_animation_ended = Signal()

    def __init__(self, status_message, active_tab_changed):
        """
        Application's central widget, contains all the app's widgets.

        :param status_message: Status bar function to call to display a message
        :param active_tab_changed: Method to call when the tab changed, in order to update the content of the toolbar.
        Call with True if the new active tab is the classroom's one.
        """
        QTabWidget.__init__(self)

        # Init
        self.status_message = status_message
        self.is_view_students: bool = None  # Current view
        self.setTabPosition(QTabWidget.South)
        self.setTabsClosable(False)

        # Widgets
        self.classroom_tab = ClassRoomTab(self.sig_move_animation_ended)
        self.attributes_tab = AttributesTab()

        # Callbacks
        self.classroom_tab.view_students.on_click = self.on_perspective_changed
        self.classroom_tab.view_teacher.on_click = self.on_perspective_changed

        # Signals
        self.sig_shuffle = None
        self.sig_enable_animation_btns = None
        # When the move animation ends, we can re-activate the buttons
        self.sig_move_animation_ended.connect(lambda: self.sig_enable_animation_btns.emit(True))
        self.currentChanged.connect(lambda: active_tab_changed(self.currentIndex() == 0))

        self.__set_layout()
        self.on_perspective_changed()  # This will switch the is_view_student flag and display the students' view

    def __set_layout(self):
        """
        Initializes the layout of this widget
        """
        self.addTab(self.classroom_tab, tr("tab_course_plan"))
        self.addTab(self.attributes_tab, tr("tab_attributes"))

    def on_perspective_changed(self):
        """
        Switches the current view perspective and updates boards display and canvas
        """
        if self.is_view_students is None:  # To prevent updating the canvas for the initialization
            self.is_view_students = True
        else:
            self.sig_enable_animation_btns.emit(False)  # Freeze btn for preventing multiple clicks
            self.is_view_students = not self.is_view_students
            self.classroom_tab.v_canvas.perspective_changed()

        if self.is_view_students:
            self.classroom_tab.view_students.set_label_visible(True)
            self.classroom_tab.view_teacher.set_label_visible(False)
            self.status_message(tr("status_bar_active_view_student"), 3000)
        else:
            self.classroom_tab.view_students.set_label_visible(False)
            self.classroom_tab.view_teacher.set_label_visible(True)
            self.status_message(tr("status_bar_active_view_teacher"), 3000)

    def do_shuffle(self):
        if not VConfirmDialog(self.parent(), "confirm_message_shuffle").exec_():
            return

        self.sig_enable_animation_btns.emit(False)
        self.sig_shuffle.emit()


class ClassRoomTab(QWidget):

    def __init__(self, sig_move_animation_ended):
        """
        Widget containing the main canvas (classroom), the board's position and topic selection.

        :param sig_move_animation_ended: Signal to trigger when the move animation ended
        """
        QWidget.__init__(self)

        # Widgets
        self.v_canvas = ViewCanvas(sig_move_animation_ended)  # Central canvas
        self.view_students = ViewTeacherDeskLabel(tr("perspective_student_txt"),
                                                  AssetManager.getInstance().config('colors', 'board_bg'))
        self.view_teacher = ViewTeacherDeskLabel(tr("perspective_teacher_txt"),
                                                 AssetManager.getInstance().config('colors', 'board_bg'))

        # Layout
        self.__set_layout()

    def __set_layout(self):
        """
        Initializes the layout of this widget
        """
        layout = QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # Widgets
        layout.addWidget(self.view_students, 0, 1)
        layout.addWidget(self.v_canvas, 1, 0, 1, 3)
        layout.addWidget(self.view_teacher, 2, 0, 1, 3)

        # Alignments
        layout.setAlignment(self.view_students, Qt.AlignCenter)
        layout.setAlignment(self.v_canvas, Qt.AlignCenter)
        layout.setAlignment(self.view_teacher, Qt.AlignCenter)

        self.setLayout(layout)


class SideDockWidget(QDockWidget):

    def __init__(self):
        """
        Dockable widget containing the Side Panel
        """
        QDockWidget.__init__(self)

        self.sidepanel = ViewSidePanel()

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

    def __init__(self, sig_quit: Signal, sig_config_mode_changed: Signal, sig_export_csv: Signal):
        """
        Main application's frame

        :param sig_quit: signal to trigger when the application closes
        :param sig_config_mode_changed: signal to trigger when the configuration mode changes
        :param sig_export_csv: signal to emit with the filepath to perform the export to CSV
        """
        QMainWindow.__init__(self)

        self.setWindowTitle(f"{tr('app_title')} | {AssetManager.getInstance().config('main', 'version')}")
        self.setWindowIcon(get_icon("sdc", ".ico"))
        self.setContextMenuPolicy(Qt.PreventContextMenu)

        self.bdd_version: str = ""  # For the about box

        self.reboot_requested = False

        # Widgets
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet("QStatusBar {background: lightgrey; color: black;}")
        self.maintoolbar = ViewMainToolBar()
        self.sidewidget = SideDockWidget()
        self.central_widget = CentralWidget(self.status_bar.showMessage, self.__active_tab_changed)

        self.sidewidget.dockLocationChanged.connect(self.on_side_widget_docked_state_changed)

        self.__config_mode = False  # Config mode flag, should be initialized to False in all widgets
        self.__init_callbacks()

        # Layout
        self.setCentralWidget(self.central_widget)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.sidewidget)
        self.addToolBar(Qt.RightToolBarArea, self.maintoolbar)
        self.setStatusBar(self.status_bar)

        # Signals
        self.sig_quit = sig_quit
        self.sig_config_mode_changed = sig_config_mode_changed
        self.sig_export_csv = sig_export_csv

        self.setStyleSheet(
            "QMainWindow {" + f"background-color: {AssetManager.getInstance().config('colors', 'main_bg')};" + "}")

    def restart(self):
        return QtCore.QCoreApplication.exit(EXIT_CODE_REBOOT)

    def set_bdd_version(self, bdd_version: str) -> None:
        """
        Sets the current BDD version. Used in the About box
        """
        self.bdd_version = bdd_version

    def __init_callbacks(self):
        """
        Dispatches the callbacks from the toolbar to the handling widgets. Also init the signal triggered to enable
        or disable some buttons.
        """
        self.maintoolbar.on_btn_perspective_clicked = self.central_widget.on_perspective_changed
        self.maintoolbar.on_btn_shuffle_clicked = self.central_widget.do_shuffle
        self.maintoolbar.on_config_mode = self.on_config_mode
        self.maintoolbar.on_export_csv = self.on_export_csv
        self.maintoolbar.on_edit_config = self.on_edit_config
        self.maintoolbar.open_about_box = lambda: AboutFrame(self.bdd_version).exec_()

        self.central_widget.sig_enable_animation_btns = self.maintoolbar.sig_enable_animation_btns

        self.sidewidget.attributes().attributes_selection_changed = self.maintoolbar.enable_one_attributes_buttons

    def __active_tab_changed(self, is_view_classroom: bool) -> None:
        """
        Triggered when the active tab changed.
        Updates main toolbar widgets

        :param is_view_classroom: View classroom or view table attributes
        """
        self.maintoolbar.set_widgets(is_view_classroom)

        # Manually update buttons enable state given the number of selected attributes
        self.maintoolbar.enable_one_attributes_buttons(self.sidewidget.attributes().get_selected_rows_count() == 1)

        self.sidewidget.sidepanel.tabBar().setTabEnabled(0, is_view_classroom)  # Courses
        self.sidewidget.sidepanel.tabBar().setTabEnabled(1, is_view_classroom)  # Students

    def on_config_mode(self, is_in_config_mode: bool) -> None:
        """
        Switches the current mode. If in config mode, almost all features are made available, whereas in 'secured'
        mode, some features will be inaccessible to prevent the user from doing critic modification actions.
        """
        self.__config_mode = is_in_config_mode

        self.maintoolbar.lock_buttons(self.__config_mode)
        self.central_widget.classroom_tab.v_canvas.config_mode(self.__config_mode)
        self.sidewidget.courses().courses_toolbar.setVisible(self.__config_mode)
        self.sidewidget.attributes().attributes_toolbar.setVisible(self.__config_mode)
        self.sidewidget.students().students_toolbar.switch_config_mode(self.__config_mode)

        self.sig_config_mode_changed.emit()

    def get_config(self) -> bool:
        """
        Getter for the config mode

        :return: True if the user is in Configuration mode
        """
        return self.__config_mode

    def on_side_widget_docked_state_changed(self) -> None:
        """
        Triggered when the side dockable widget has been docked or undocked
        """
        if self.sidewidget.isFloating():
            self.adjustSize()

    def on_export_csv(self) -> None:
        """
        Displays a save dialog to select a file path for the export csv of the attributes table.
        Then signals this path to the controller
        """
        file_path = QFileDialog.getSaveFileName(self, tr("export_dialog_title"), "untitled", "(*.csv)")[0]
        if file_path:
            self.sig_export_csv.emit(file_path)

    def on_edit_config(self) -> None:
        """
        Displays the edition dialog for application settings
        """
        dlg = SettingsEditionDialog()

        if dlg.exec_():
            if dlg.restore_default():
                AssetManager.getInstance().restore_default_settings()
            else:
                AssetManager.getInstance().save_config(dlg.new_config())

            self.status_bar.showMessage(tr("acknowledge_changes"), 3000)
            self.repaint()

            if dlg.need_restart():
                restart_confirm = VConfirmDialog(self, "need_restart")
                restart_confirm.ok_btn.setText(tr("restart_now"))
                restart_confirm.ok_btn.setFixedSize(QSize(105, 33))
                restart_confirm.cancel_btn.setText(tr("restart_later"))
                restart_confirm.cancel_btn.setFixedSize(QSize(105, 33))

                if restart_confirm.exec_():
                    self.reboot_requested = True
                    self.close()
                    self.restart()

    def closeEvent(self, event):
        """
        Triggered on a close operation. Signals to the controller the event
        """
        if self.reboot_requested:
            self.reboot_requested = False
            self.sig_quit.emit(EXIT_CODE_REBOOT)
        else:
            self.sig_quit.emit(0)
        event.accept()
