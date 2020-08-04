import sqlite3

from PySide2.QtCore import QObject, Signal, Slot

# Secondary controllers
from src.Controllers.course_controller import CourseController
from src.Controllers.group_controller import GroupController
from src.Controllers.attr_controller import AttrController

# Views
from src.Model.mod_bdd import ModBdd
from src.View.view_mainframe import ViewMainFrame
from src.View.widgets.view_menubutton import ViewMenuButton
from src.View.popup.view_student_attributes import VStdAttributesDialog

# web sockets
import socketio



class MainController(QObject):
    # Constants
    SEL_NONE = 0
    SEL_EMPTY = 1
    SEL_OCCUPIED = 2
    SEL_ALL = 3

    # Signals
    sig_select_tile = Signal()
    sig_quit = Signal()
    sig_shuffle = Signal()
    sig_desk_selected = Signal(int, bool)
    sig_canvas_click = Signal(tuple)
    sig_canvas_drag = Signal(tuple, tuple)
    sig_canvas_right_click = Signal(tuple)
    sig_TBbutton = Signal(str)

    sig_course_changed = Signal(int)
    sig_create_course = Signal(str)
    sig_student_group_changed = Signal(str)

    sig_topic_changed = Signal(str)
    sig_action_triggered = Signal(str)

    sig_create_grp_std = Signal(str)

    sig_create_attribute = Signal(str, str)
    sig_delete_attributes = Signal()
    sig_delete_course = Signal()

    sig_attr_selection_changed = Signal()
    sig_attribute_cell_selected = Signal(int, int)

    sig_flask_desk_selection_changed = Signal(int, bool)

    def __init__(self):
        """
        Application main controller.
        """
        QObject.__init__(self)


        # BDD connection
        self.__bdd = sqlite3.connect("src/SQL/sdc_db")
        self.mod_bdd = ModBdd(self.__bdd)

        # Create the Views
        self.gui = ViewMainFrame(self.sig_quit)
        self.v_canvas = self.gui.central_widget.classroom_tab.v_canvas

        # Create secondary controllers
        self.attr_ctrl = AttrController(self, self.__bdd)
        self.course_ctrl = CourseController(self, self.__bdd)
        self.group_ctrl = GroupController(self, self.__bdd)

        # Plugs the signals into the views
        self.v_canvas.sig_select_tile = self.sig_select_tile
        self.gui.central_widget.sig_shuffle = self.sig_shuffle
        self.gui.sig_quit = self.sig_quit
        self.v_canvas.sig_canvas_click = self.sig_canvas_click
        self.v_canvas.sig_desk_selected = self.sig_desk_selected
        self.v_canvas.sig_canvas_drag = self.sig_canvas_drag
        self.v_canvas.sig_tile_info = self.sig_canvas_right_click
        self.gui.sidewidget.courses().sig_course_changed = self.sig_course_changed
        self.gui.sidewidget.courses().courses_toolbar.add_widget.sig_new_element = self.sig_create_course
        self.gui.central_widget.classroom_tab.topic.sig_topic_changed = self.sig_topic_changed
        self.gui.sidewidget.students().students_toolbar.sig_combo_changed = self.sig_student_group_changed
        ViewMenuButton.sig_action = self.sig_action_triggered
        self.gui.maintoolbar.sig_TBbutton = self.sig_TBbutton
        self.gui.sidewidget.students().students_toolbar.create_field.sig_create = self.sig_create_grp_std
        self.gui.sidewidget.attributes().attributes_toolbar.add_widget.sig_new_element = self.sig_create_attribute
        self.gui.sidewidget.attributes().attributes_toolbar.add_widget.sig_delete = self.sig_delete_attributes
        self.gui.sidewidget.courses().courses_toolbar.sig_delete = self.sig_delete_course
        self.gui.sidewidget.attributes().sig_selection_changed = self.sig_attr_selection_changed
        self.gui.central_widget.attributes_tab.sig_cell_clicked = self.sig_attribute_cell_selected

        # Signals connection
        self.sig_select_tile.connect(self.attr_ctrl.on_attribute_selection_changed)
        self.sig_quit.connect(self.do_quit)
        self.sig_canvas_click.connect(self.course_ctrl.add_desk)
        self.sig_desk_selected.connect(self.course_ctrl.on_desk_selection_changed_on_app)
        self.sig_canvas_drag.connect(self.course_ctrl.move_desk)
        self.sig_canvas_right_click.connect(self.attr_ctrl.show_student_attributes)
        self.sig_shuffle.connect(self.course_ctrl.desk_shuffle)
        self.sig_course_changed.connect(self.course_ctrl.on_course_changed)
        self.sig_create_course.connect(self.course_ctrl.on_create_course)
        self.sig_topic_changed.connect(self.course_ctrl.on_topic_changed)
        self.sig_student_group_changed.connect(self.group_ctrl.on_student_group_changed)
        self.sig_action_triggered.connect(self.action_triggered)
        self.sig_TBbutton.connect(self.action_triggered)
        self.sig_create_grp_std.connect(self.group_ctrl.on_create_grp_std)
        self.sig_create_attribute.connect(self.attr_ctrl.on_create_attr)
        self.sig_delete_attributes.connect(self.attr_ctrl.on_delete_attributes)
        self.sig_delete_course.connect(self.course_ctrl.on_delete_course)
        self.sig_attr_selection_changed.connect(self.attr_ctrl.on_attribute_selection_changed)
        self.sig_attribute_cell_selected.connect(self.attr_ctrl.on_attribute_cell_selected)
        self.sig_flask_desk_selection_changed.connect(self.course_ctrl.on_desk_selection_changed_on_web)

        self.actions_table = {  # Action buttons
            "import_csv": self.group_ctrl.import_pronote,
            "auto_place": self.group_ctrl.auto_place,
            "sort_asc": self.group_ctrl.sort_asc,
            "sort_desc": self.group_ctrl.sort_desc,
            "sort_desks": self.course_ctrl.sort_desks,
            "killstudent": self.group_ctrl.killstudent,
            "delete_group": self.group_ctrl.on_delete_group,

            # Toolbar buttons
            "filter_select": self.attr_ctrl.change_filter_selection,
            "select": self.course_ctrl.auto_select_desks,
            "choice": self.course_ctrl.student_random_pick,
            "choice_attr": self.debug,
            "delete": self.course_ctrl.delete,
            "lot_change": self.attr_ctrl.lot_change,
            "test": self.debug,
        }

        # properties
        self.id_course = 0
        self.id_group = 0
        self.selection_mode = self.SEL_ALL
        self.filter_selection = False
        self.std_dialog_info: VStdAttributesDialog = None

        # initialize the views
        self.course_ctrl.show_all_courses()
        self.group_ctrl.show_all_groups()
        self.attr_ctrl.show_all_attributes()
        self.gui.update()

        # initialize connection to flask server
        self.flask_client = socketio.Client()
        self.flask_client.connect('http://localhost:5000')


    #
    # Signals handling
    #

    @Slot(str)
    def action_triggered(self, action_key: str) -> None:
        """
        Triggered when an action signal is emitted. Looks in the actions lookup table and calls the associated method.

        :param action_key: action triggered key
        :type action_key: str
        """
        self.actions_table[action_key]()

    @Slot()
    def do_quit(self):
        self.v_canvas.application_closing()
        self.__bdd.close()

    #
    # General methods
    #

    def debug(self):
        self.gui.status_bar.showMessage("ouaf")
