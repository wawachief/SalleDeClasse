import sqlite3

from PySide2.QtCore import QObject, Signal, Slot, QTimer

from src.Model.mod_bdd import ModBdd
from src.View.view_mainframe import ViewMainFrame
from src.View.widgets.view_menubutton import ViewMenuButton
from src.View.popup.view_import_csv import DialogImportCsv
from src.Model.import_csv import import_csv, process_line

from src.assets_manager import AssetManager

from random import shuffle


class Controller(QObject):
    # Constants
    SEL_NONE = 0
    SEL_EMPTY = 1
    SEL_OCCUPIED = 2
    SEL_ALL = 3

    # Signals
    sig_add_tile = Signal()
    sig_quit = Signal()
    sig_shuffle = Signal()
    sig_canvas_click = Signal(tuple)
    sig_canvas_drag = Signal(tuple, tuple)
    sig_TBbutton = Signal(str)

    sig_course_changed = Signal(int)
    sig_create_course = Signal(str)
    sig_student_group_changed = Signal(str)

    sig_topic_changed = Signal(str)
    sig_action_triggered = Signal(str)

    sig_create_grp_std = Signal(str)

    sig_create_attribute = Signal(str, str)

    def __init__(self):
        """
        Application main controller.
        """
        QObject.__init__(self)

        self.actions_table = {  # Action buttons
                                "import_csv": self.import_pronote,
                                "auto_place": self.auto_place,
                                "sort_asc": self.sort_asc,
                                "sort_desc": self.sort_desc,
                                "sort_desks": self.sort_desks,
                                "killstudent": self.killstudent,

                                # Toolbar buttons
                                "magic": self.debug,
                                "select": self.select,
                                "choix": self.debug,
                                "delete": self.delete
                              }

        # BDD connection
        self.__bdd = sqlite3.connect("src/SQL/sdc_db")
        self.mod_bdd = ModBdd(self.__bdd)

        # Create the Views
        self.gui = ViewMainFrame(self.sig_quit)
        self.v_canvas = self.gui.central_widget.classroom_tab.v_canvas
        # Plugs the signals
        self.gui.central_widget.sig_add_tile = self.sig_add_tile
        self.gui.central_widget.sig_shuffle = self.sig_shuffle
        self.gui.sig_quit = self.sig_quit
        self.v_canvas.sig_canvas_click = self.sig_canvas_click
        self.v_canvas.sig_canvas_drag = self.sig_canvas_drag
        self.gui.sidewidget.courses().sig_course_changed = self.sig_course_changed
        self.gui.sidewidget.courses().courses_toolbar.add_widget.sig_new_element = self.sig_create_course
        self.gui.central_widget.classroom_tab.topic.sig_topic_changed = self.sig_topic_changed
        self.gui.sidewidget.students().students_toolbar.sig_combo_changed = self.sig_student_group_changed
        ViewMenuButton.sig_action = self.sig_action_triggered
        self.gui.maintoolbar.sig_TBbutton = self.sig_TBbutton
        self.gui.sidewidget.students().students_toolbar.create_field.sig_create = self.sig_create_grp_std
        self.gui.sidewidget.attributes().attributes_toolbar.add_widget.sig_new_element = self.sig_create_attribute

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
        self.sig_action_triggered.connect(self.action_triggered)
        self.sig_TBbutton.connect(self.action_triggered)
        self.sig_create_grp_std.connect(self.on_create_grp_std)
        self.sig_create_attribute.connect(self.on_create_attr)

        # properties
        self.id_course = 0
        self.id_group = 0
        self.selection_mode = self.SEL_ALL
        
        self.show_all_courses()
        self.show_all_groups()
        self.show_all_attributes()
        self.gui.update()

    def debug(self):
        self.gui.status_bar.showMessage("ouaf")

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

        max_row = int(AssetManager.getInstance().config("size", "default_room_rows"))
        max_col = int(AssetManager.getInstance().config("size", "default_room_columns"))
        if len(start) == 0:
            return

        id_desk_start = self.mod_bdd.get_desk_id_in_course_by_coords(self.id_course, start[0], start[1])
        if 0 <= end[0] < max_row and 0 <= end[1] < max_col:
            # Destination is in the canvas
            id_desk_end = self.mod_bdd.get_desk_id_in_course_by_coords(self.id_course, end[0], end[1])
            if id_desk_end == 0 and id_desk_start != 0:
                # We just change the coordinates
                self.mod_bdd.move_desk_by_id(id_desk_start, end[0], end[1])
                # We update the view
                self.v_canvas.move_tile(id_desk_start, end)
            elif id_desk_end != 0 and id_desk_start != 0:
                # We swap the two desks
                self.mod_bdd.move_desk_by_id(id_desk_start, end[0], end[1])
                self.mod_bdd.move_desk_by_id(id_desk_end, start[0], start[1])
                # We update the view
                self.v_canvas.move_tile(id_desk_start, end)
                self.v_canvas.move_tile(id_desk_end, start, True)
        else:
            self.mod_bdd.remove_desk_by_id(id_desk_start)
            self.show_course()
        self.__bdd.commit()
        self.v_canvas.repaint()

    def remove_desk_by_id(self, id_desk):
        """Removes the desk designed by id_desk
        - removes the entry in the bdd
        - removes the tile on viewcanvas
        BDD commit MUST be called after removing desks !
        """
        # Desk is out of the caanvas, we remove it
        self.mod_bdd.remove_desk_by_id(id_desk)
        # remove the tile as well
        self.v_canvas.remove_tile(id_desk)

    @Slot()
    def desk_shuffle(self):
        """Shuffle all desktops"""
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
        self.gui.central_widget.classroom_tab.topic.select_topic(topic_name)

    def set_course(self, course_name):
        """Sets current course to course_name
        if course_name does not exisis, creates it, with current topic id
        YOU MUST CALL commit after !
        The new course have topic_id of 1 (main topic)
        """
        self.id_course = self.mod_bdd.create_course_with_name(course_name)
        self.selection_mode = self.SEL_ALL
    
    def show_all_courses(self):
        """Initializes the contents of the widgets :
        - courses list
        - topic list"""

        courses = self.mod_bdd.get_courses()
        topic_names = self.mod_bdd.get_topics_names()
        if self.id_course == 0:
            self.id_course = courses[0][0]
        topic_name = self.mod_bdd.get_topic_from_course_id(self.id_course)

        self.gui.sidewidget.courses().init_table(
            list_courses=courses, selected_id=None if self.id_course == 0 else self.id_course)

        self.gui.central_widget.classroom_tab.topic.set_topics(topic_names, topic_name)
        self.show_course()

    def show_all_groups(self, current=0):
        groups = self.mod_bdd.get_groups()
        if current == 0:
            self.gui.sidewidget.students().students_toolbar.init_groups(groups)
        if groups:
            current_group = groups[0] if current == 0 else self.mod_bdd.get_group_name_by_id(current)
            self.on_student_group_changed(current_group)
            self.mod_bdd.get_group_id_by_name(current_group)
            self.gui.sidewidget.students().students_toolbar.current_group = current_group

    def auto_place(self):
        """Autoplacement of students on the free tiles"""
        maxRow = int(AssetManager.getInstance().config("size", "default_room_rows"))
        maxCol = int(AssetManager.getInstance().config("size", "default_room_columns"))
        group_name = self.mod_bdd.get_group_name_by_id(self.id_group)
        list_idstd = self.gui.sidewidget.students().selected_students()
        if list_idstd == []:
            list_students = self.mod_bdd.get_students_in_group(group_name)
        else:
            list_students = [self.mod_bdd.get_student_by_id(i) for i in list_idstd] 
        
        students_ids = { s.id for s in list_students}

        to_be_placed = len(list_students)
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
        # Adjust the number of students to place
        for s in list_to_remove:
            if s in students_ids:
                to_be_placed -= 1

        index_std = 0
        for dsk in list_available_desks:
            while index_std < len(list_students) and list_students[index_std].id in list_to_remove:
                index_std += 1
                to_be_placed -= 1
            if index_std >= len(list_students):
                break
            student = list_students[index_std]
            # update the model
            self.mod_bdd.set_student_in_desk_by_id(student.id, dsk[0])
            to_be_placed -= 1
            # update the view
            self.v_canvas.set_student(dsk[0], student.firstname, student.lastname)
            self.v_canvas.repaint()
            
            index_std += 1
        
        if to_be_placed > 0 :
            self.gui.status_bar.showMessage(f"Il manque {to_be_placed} places pour placer tous les élèves")
        else:
            self.gui.status_bar.showMessage("Tous les élèves sont placés",3000)
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
            csv_sep = AssetManager.getInstance().config("main", "csv_separator")
            names = import_csv(file_path, csv_sep)
            id_group = self.mod_bdd.create_group(name_group)
            order = 0
            for std in names:
                self.mod_bdd.insert_student_in_group_id(std[1], std[0], order, id_group)
                order += 1
            self.__bdd.commit()

            self.show_all_groups()

    def select(self) -> None:
        """Select Desks, rotate selection mode
        - 3 = all, 
        - 2 = occupied desks, 
        - 1 = empty desks, 
        - 0 = none
        """
        def get_desks(isFree):
            all_desks = self.mod_bdd.get_course_all_desks(self.id_course)
            if isFree:
                return [d.id for d in all_desks if d.id_student == 0]
            else:
                return [d.id for d in all_desks if d.id_student != 0]

        if self.selection_mode == self.SEL_NONE:
            self.v_canvas.select_tiles_to(False)
            self.gui.status_bar.showMessage(f"Déselection de tous les emplacements", 3000)
        elif self.selection_mode == self.SEL_EMPTY:
            self.v_canvas.select_tiles_from_desks_ids(get_desks(True))
            self.gui.status_bar.showMessage(f"Selection des emplacements libres", 3000)
        elif self.selection_mode == self.SEL_OCCUPIED:
            self.v_canvas.select_tiles_from_desks_ids(get_desks(False))
            self.gui.status_bar.showMessage(f"Selection des emplacements occupés", 3000)
        else:
            self.v_canvas.select_tiles_to(True)
            self.gui.status_bar.showMessage(f"Selection de tous les emplacements", 3000)
        self.selection_mode = (self.selection_mode+1) % 4

        self.v_canvas.repaint()
    

    def delete(self) -> None:
        desks_id = self.v_canvas.get_selected_tiles()
        for d in desks_id:
            id_student = self.mod_bdd.get_desk_by_id(d).id_student
            if id_student == 0:
                self.remove_desk_by_id(d)
            else:
                # We free the desk
                self.v_canvas.set_student(d, "", "")
                self.mod_bdd.set_student_in_desk_by_id(0, d)

        self.__bdd.commit()
        self.v_canvas.repaint()

    @Slot(str)
    def on_create_grp_std(self, new_grp_std: str):
        """
        Creates a new group or a new student with the specified name.

        It is a group if the received string starts with 'grp '. It is a student if it starts with 'std '.
        """
        prefix = new_grp_std[:4]
        name = new_grp_std[4:]

        if prefix == 'grp ':  # Group creation
            self.gui.status_bar.showMessage(f"Creation du groupe {name}", 3000)
            id_group = self.mod_bdd.create_group(name)
            list_id_students = self.gui.sidewidget.students().selected_students()
            for id_std in list_id_students:
                self.mod_bdd.insert_isin(id_std, id_group)
            self.show_all_groups()
        elif prefix == 'std ':  # Student creation
            self.gui.status_bar.showMessage(f"Creation de l'élève {name}", 3000)
            lastname, firstname  = process_line(name, ";")
            self.mod_bdd.insert_student_in_group_id(firstname, lastname, 0, self.id_group)
            self.show_course()
            self.show_all_groups(current = self.id_group)
        else:  # Student edition
            id_std = int(prefix)
            lastname, firstname  = process_line(name, ";")
            self.gui.status_bar.showMessage(f"Renommage de l'élève {firstname} {lastname}", 3000)
            self.mod_bdd.rename_student_by_id(id_std, firstname, lastname)
            self.show_course()
            self.show_all_groups(current = self.id_group)

        self.__bdd.commit()

    def killstudent(self):
        self.gui.status_bar.showMessage(f"Suppression d'élèves", 3000)
        list_id_students = self.gui.sidewidget.students().selected_students()
        for id_std in list_id_students:
            # delete student from IsIn
            self.mod_bdd.delete_isin(id_std, self.id_group)
            n = self.mod_bdd.nb_groups_contains_student_by_id(id_std)
            if n == 0:
                # Delete Student from Database
                self.mod_bdd.delete_student_by_id(id_std)
        self.show_course()
        self.show_all_groups(current = self.id_group)
        self.__bdd.commit()

    def sort_alpha(self, desc):
        self.gui.status_bar.showMessage("Tri alphabétique", 3000)
        group_name = self.mod_bdd.get_group_name_by_id(self.id_group)
        list_students = self.mod_bdd.get_students_in_group(group_name)
        sortlist = [(s.lastname, s.id) for s in list_students ]
        sortlist.sort(reverse = desc)
        orderkey = 1
        for s in sortlist:
            self.mod_bdd.update_student_order_with_id(s[1], orderkey)
            orderkey += 1
        self.__bdd.commit()
        self.gui.sidewidget.students().set_students_list(self.mod_bdd.get_students_in_group(group_name))

    def sort_asc(self):
        self.sort_alpha(False)

    def sort_desc(self):
        self.sort_alpha(True)

    def sort_desks(self):
        self.gui.status_bar.showMessage("Tri d'après les places", 3000)
        maxRow = int(AssetManager.getInstance().config("size", "default_room_rows"))
        maxCol = int(AssetManager.getInstance().config("size", "default_room_columns"))
        group_name = self.mod_bdd.get_group_name_by_id(self.id_group)

        sortlist = []
        for row in range(maxRow):
            for col in range(maxCol):
                id_desk = self.mod_bdd.get_desk_id_in_course_by_coords(self.id_course, row, col)
                if id_desk != 0:
                    student = self.mod_bdd.get_student_by_desk_id(id_desk)
                    if student is not None:
                        sortlist.append(student.id)
        
        orderkey = 0
        for s in sortlist:
            self.mod_bdd.update_student_order_with_id(s, orderkey)
            orderkey += 1
        self.__bdd.commit()
        self.gui.sidewidget.students().set_students_list(self.mod_bdd.get_students_in_group(group_name))

    @Slot(str, str)
    def on_create_attr(self, attr_name: str, attr_type: str) -> None:
        """
        Triggers when the user wants to create a new attribute

        :param attr_name: Attribute's name
        :param attr_type: Attribute's type key
        """
        print(attr_name, attr_type)
        self.mod_bdd.insert_attribute(attr_name, attr_type)
        self.__bdd.commit()

        self.show_all_attributes()

        
    def show_all_attributes(self):
        """Initializes the contents of the attributes list"""

        list_attr = self.mod_bdd.get_all_attributes()
        # self.gui.sidewidget.attributes().set_attributes_list([(1, attr_name, attr_type), (2, "toto", "attr_txt"), (3, "tata", "attr_txt")])
        self.gui.sidewidget.attributes().set_attributes_list(list_attr)