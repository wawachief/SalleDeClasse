import sqlite3
import platform

from PySide2.QtCore import QObject, Signal, Slot, QTimer

from src.Model.mod_bdd import ModBdd
from src.View.view_mainframe import ViewMainFrame
from src.View.widgets.view_menubutton import ViewMenuButton
from src.View.popup.view_import_csv import DialogImportCsv
from src.Model.import_csv import import_csv

from random import shuffle


class Controller(QObject):

    sig_add_tile = Signal()
    sig_quit = Signal()
    sig_shuffle = Signal()
    sig_canvas_click = Signal(tuple)
    sig_canvas_drag = Signal(tuple, tuple)

    sig_course_changed = Signal(int)
    sig_create_course = Signal(str)
    sig_student_group_changed = Signal(str)
    sig_student_selected = Signal(int)

    sig_topic_changed = Signal(str)
    sig_action_triggered = Signal(str)

    def __init__(self, config):
        """
        Application main controller.

        :param config: application's parsed configuration
        """
        QObject.__init__(self)

        self.config = config

        self.actions_table = {"import_csv": self.import_pronote,
                              "create_group": self.create_group,
                              "auto_place": self.auto_place}

        # BDD connection
        self.__bdd = sqlite3.connect("src/SQL/sdc_db")
        self.mod_bdd = ModBdd(self.__bdd)

        # Create the Views
        self.gui = ViewMainFrame(self.sig_quit, self.config)
        self.v_canvas = self.gui.central_widget.v_canvas
        # Plugs the signals
        self.gui.central_widget.sig_add_tile = self.sig_add_tile
        self.gui.central_widget.sig_shuffle = self.sig_shuffle
        self.gui.sig_quit = self.sig_quit
        self.v_canvas.sig_canvas_click = self.sig_canvas_click
        self.v_canvas.sig_canvas_drag = self.sig_canvas_drag
        self.gui.sidewidget.courses().sig_course_changed = self.sig_course_changed
        self.gui.sidewidget.courses().courses_toolbar.add_widget.sig_new_element = self.sig_create_course
        self.gui.central_widget.topic.sig_topic_changed = self.sig_topic_changed
        self.gui.sidewidget.students().students_toolbar.sig_combo_changed = self.sig_student_group_changed
        self.gui.sidewidget.students().sig_student_changed = self.sig_student_selected
        ViewMenuButton.sig_action = self.sig_action_triggered

        # Signals connection
        self.sig_add_tile.connect(self.test_buttton)
        self.sig_quit.connect(self.do_quit)
        self.sig_canvas_click.connect(self.add_desk)
        self.sig_canvas_drag.connect(self.move_desk)
        self.sig_shuffle.connect(self.desk_shuffle)
        self.sig_course_changed.connect(self.on_course_changed)
        self.sig_create_course.connect(self.on_create_course)
        self.sig_topic_changed.connect(self.on_topic_changed)
        self.sig_student_group_changed.connect(self.on_student_group_changed)
        self.sig_student_selected.connect(self.on_student_selected)
        self.sig_action_triggered.connect(self.action_triggered)

        # properties
        self.id_course = 0
        self.id_group = 0
        
        self.show_all_courses()
        self.gui.update()

        self.test_timer = None  # Initialization in the constructor, even if it used only on OSX
        if "Darwin" in platform.system():
            self.osx_test()

    @Slot()
    def test_buttton(self):
        self.auto_place()
        
    @Slot(tuple)
    def add_desk(self, coords):
        """Add a new desk at mouse place"""
        row = coords[0]
        col = coords[1]
        id_desk = self.mod_bdd.get_desk_id_in_course_by_coords(self.id_course, row, col)
        if id_desk == 0:
            # The place is free, we create the desk
            id_desk = self.mod_bdd.create_new_desk_in_course(row, col, self.id_course)
            self.v_canvas.new_tile(row, col, id_desk)
        
        self.__bdd.commit()
        self.v_canvas.repaint()
    
    @Slot(tuple, tuple)
    def move_desk(self, start, end):
        """Moves a desk from start to end
        if end is out of the screen, we remove the desk"""

        max_row = int(self.config.get("size", "default_room_rows"))
        max_col = int(self.config.get("size", "default_room_columns"))

        id_desk_start = self.mod_bdd.get_desk_id_in_course_by_coords(self.id_course, start[0], start[1])
        if 0 <= end[0] < max_row and 0 <= end[1] < max_col:
            # Destination is in the canvas
            id_desk_end = self.mod_bdd.get_desk_id_in_course_by_coords(self.id_course, end[0], end[1])
            if id_desk_end == 0:
                # We just change the coordinates
                self.mod_bdd.move_desk_by_id(id_desk_start, end[0], end[1])
                # We update the view
                self.v_canvas.move_tile(id_desk_start, end)
            else:
                # We swap the two desks
                self.mod_bdd.move_desk_by_id(id_desk_start, end[0], end[1])
                self.mod_bdd.move_desk_by_id(id_desk_end, start[0], start[1])
                # We update the view
                self.v_canvas.move_tile(id_desk_start, end)
                self.v_canvas.move_tile(id_desk_end, start, True)
        else:
            # Desk is out of the caanvas, we remove it
            self.mod_bdd.remove_desk_by_id(id_desk_start)
            # remove the tile as well
            self.v_canvas.remove_tile(id_desk_start)
        self.__bdd.commit()
        self.v_canvas.repaint()

    @Slot()
    def desk_shuffle(self):
        all_desks = self.mod_bdd.get_course_all_desks(self.id_course)
        shuffle(all_desks)
        for i in range(0,len(all_desks)-1,2):
            d1 = all_desks[i]
            d2 = all_desks[i+1]
            # We swap the two desks
            self.mod_bdd.move_desk_by_id(d1.id, d2.row, d2.col)
            self.mod_bdd.move_desk_by_id(d2.id, d1.row, d1.col)
            # We update the view
            self.v_canvas.move_tile(d1.id, (d2.row, d2.col), True)
            self.v_canvas.move_tile(d2.id, (d1.row, d1.col), True)
        self.__bdd.commit()
        self.v_canvas.repaint()

    @Slot()
    def do_quit(self):
        print("Bye")
        self.v_canvas.application_closing()
        self.__bdd.close()

    @Slot(str)
    def on_topic_changed(self, new_topic):
        """
        Triggered when the topic selection of the current course changed

        :param new_topic: new selected topic
        :type new_topic: str
        """
        self.mod_bdd.set_topic_to_course_id(self.id_course, new_topic)
        self.__bdd.commit()
        self.show_all_courses()

    @Slot(str)
    def on_student_group_changed(self, new_group: str) -> None:
        """
        Triggered when the self.sig_student_group_changed is emitted. Updates the list of displayed students given
        the new selected group

        :param new_group: Course in which are the students to display
        :type new_group: str
        """
        self.id_group = self.mod_bdd.get_group_id_by_name(new_group)
        self.gui.sidewidget.students().set_students_list(self.mod_bdd.get_students_in_group(new_group))

    @Slot(int)
    def on_student_selected(self, student_id: int) -> None:
        """
        Triggered when the student selection changed.

        :param student_id: new selected student id
        :type student_id: int
        """
        print(student_id)

    def show_course(self):
        """DIsplays a the course defined by the id_course property"""
        self.v_canvas.delete_all_tiles()
        all_desks = self.mod_bdd.get_course_all_desks(self.id_course)
        topic_name = self.mod_bdd.get_topic_from_course_id(self.id_course)
        for d in all_desks:
            std = self.mod_bdd.get_student_by_id(d.id_student)
            if std:
                self.v_canvas.new_tile(d.row, d.col, d.id, firstname=std.firstname, lastname=std.lastname)
            else:
                self.v_canvas.new_tile(d.row, d.col, d.id)
        self.v_canvas.repaint()
        # Display course's topic
        self.gui.central_widget.topic.select_topic(topic_name)

    def set_course(self, course_name):
        """Sets current course to course_name
        if course_name does not exisis, creates it, with current topic id
        YOU MUST CALL commit after !
        The new course have topic_id of 1 (main topic)
        """
        self.id_course = self.mod_bdd.create_course_with_name(course_name)
    
    def show_all_courses(self):
        courses = self.mod_bdd.get_courses()
        groups = self.mod_bdd.get_groups()
        topic_names = self.mod_bdd.get_topics_names()
        if self.id_course == 0:
            self.id_course = courses[0][0]
        topic_name = self.mod_bdd.get_topic_from_course_id(self.id_course)

        self.gui.sidewidget.courses().init_table(
            list_courses=courses, selected_id=None if self.id_course == 0 else self.id_course)

        self.gui.sidewidget.students().students_toolbar.init_groups(groups) 
        if groups:
            self.on_student_group_changed(groups[0])
            self.mod_bdd.get_group_id_by_name(groups[0])

        self.gui.central_widget.topic.set_topics(topic_names, topic_name)

    def auto_place(self):
        """Autoplacement of students on the free tiles"""
        maxRow = int(self.config.get("size", "default_room_rows"))
        maxCol = int(self.config.get("size", "default_room_columns"))
        group_name = self.mod_bdd.get_group_name_by_id(self.id_group)
        list_students = self.mod_bdd.get_students_in_group(group_name)
        list_available_desks = []
        list_to_remove = []
        for row in range(maxRow):
            for col in range(maxCol):
                id_desk = self.mod_bdd.get_desk_id_in_course_by_coords(self.id_course, row, col)
                if id_desk != 0:
                    student = self.mod_bdd.get_student_by_desk_id(id_desk)
                    if student is None:
                        # We have a free spot
                        list_available_desks.append((id_desk, row, col))
                    else:
                        list_to_remove.append(student.id)
        index_std = 0
        for dsk in list_available_desks:
            while index_std < len(list_students) and list_students[index_std].id in list_to_remove:
                index_std += 1
            if index_std >= len(list_students):
                break
            student = list_students[index_std]
            # update the model
            self.mod_bdd.set_student_in_desk_by_id(student.id, dsk[0])
            # update the view
            self.v_canvas.set_student(dsk[0], student.firstname, student.lastname)
            self.v_canvas.repaint()
            
            index_std += 1
        
        self.__bdd.commit()

    @Slot(int)
    def on_course_changed(self, new_course):
        """
        Triggered when the current course selection changed

        :param new_course: new selected course name
        :type new_course: int
        """
        self.id_course = new_course
        self.show_course()

    @Slot(str)
    def on_create_course(self, new_course):
        """
        Triggered when a new course is to be created

        :param new_course: new course name to create
        :type new_course: str
        """

        old_course_id = self.id_course
        self.set_course(new_course)
        self.show_all_courses()
        # Manually call the course changed update (manual set to selection does not trigger the signal emit)
        self.on_course_changed(self.id_course)

        # Copy the Desk disposition of the old course_id
        old_desks = self.mod_bdd.get_course_all_desks(old_course_id)
        for d in old_desks:
            id_desk = self.mod_bdd.create_new_desk_in_course(d.row, d.col, self.id_course)
            self.v_canvas.new_tile(d.row, d.col, id_desk)
        
        self.__bdd.commit()
        self.v_canvas.repaint()

    @Slot(str)
    def action_triggered(self, action_key: str) -> None:
        """
        Triggered when an action signal is emitted. Looks in the actions lookup table and calls the associated method.

        :param action_key: action triggered key
        :type action_key: str
        """
        self.actions_table[action_key]()

    def import_pronote(self) -> None:
        groups = self.mod_bdd.get_groups()
        dlg = DialogImportCsv(self.gui, ["Nouveau Groupe"] + groups)

        if dlg.exec_():
            name_group = dlg.selected_group()
            file_path = dlg.selected_file()
            if name_group == "Nouveau Groupe":
                f = file_path.split("/")[-1].upper()
                name_group = f[0:f.index(".CSV")]
            csv_sep = self.config.get("main", "csv_separator")
            names = import_csv(file_path, csv_sep)
            id_group = self.mod_bdd.create_group(name_group)
            order = 0
            for std in names:
                self.mod_bdd.insert_student_in_group_id(std[1], std[0], order, id_group)
                order += 1
            self.__bdd.commit()

            groups = self.mod_bdd.get_groups()
            self.gui.sidewidget.students().students_toolbar.init_groups(groups)
            self.on_student_group_changed(self.mod_bdd.get_group_name_by_id(self.id_group))

    def create_group(self) -> None:
        print("Create group")

    # ------------
    # OSX bug
    # ------------

    def osx_test(self):
        """
        There is a BUG on OSX, where for some reason sometimes the QTimer doesn't start. In that case, QActions can't
        trigger neither, nor animations.

        To see that, we disable the main widget and activated only if the QTimer could start.
        """
        self.gui.setEnabled(False)
        self.gui.repaint()

        self.test_timer = QTimer(parent=self)
        self.test_timer.timeout.connect(self.ready)
        self.test_timer.start(1)

    def ready(self):
        """
        Triggered when the test_timer starts. It will then stop and re-enable the main frame.
        """
        self.test_timer.stop()
        self.test_timer = None
        self.gui.setEnabled(True)
        self.gui.repaint()
