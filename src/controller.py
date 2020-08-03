import sqlite3

from PySide2.QtCore import QObject, Signal, Slot
from PySide2.QtGui import QColor

from src.Model.mod_bdd import ModBdd
from src.View.view_mainframe import ViewMainFrame
from src.View.widgets.view_menubutton import ViewMenuButton
from src.View.popup.view_import_csv import DialogImportCsv
from src.Model.import_csv import import_csv, process_line

from src.View.popup.view_attribute_edition import VDlgEditText, VDlgEditCounter, VDlgEditMark, VDlgEditColor
from src.View.popup.view_confirm_dialogs import VConfirmDialog
from src.View.popup.view_info_dialog import VInfoDialog
from src.View.popup.view_student_attributes import VStdAttributesDialog

from src.assets_manager import AssetManager
from src.enumerates import EAttributesTypes

from random import shuffle


# noinspection PyUnresolvedReferences
class Controller(QObject):
    # Constants
    SEL_NONE = 0
    SEL_EMPTY = 1
    SEL_OCCUPIED = 2
    SEL_ALL = 3

    # Signals
    sig_select_tile = Signal()
    sig_quit = Signal()
    sig_shuffle = Signal()
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
            "delete_group": self.on_delete_group,

            # Toolbar buttons
            "filter_select": self.change_filter_selection,
            "select": self.select,
            "choix": self.debug,
            "delete": self.delete,
            "lot_change": self.lot_change
        }

        # BDD connection
        self.__bdd = sqlite3.connect("src/SQL/sdc_db")
        self.mod_bdd = ModBdd(self.__bdd)

        # Create the Views
        self.gui = ViewMainFrame(self.sig_quit)
        self.v_canvas = self.gui.central_widget.classroom_tab.v_canvas
        # Plugs the signals
        self.v_canvas.sig_select_tile = self.sig_select_tile
        self.gui.central_widget.sig_shuffle = self.sig_shuffle
        self.gui.sig_quit = self.sig_quit
        self.v_canvas.sig_canvas_click = self.sig_canvas_click
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
        self.sig_select_tile.connect(self.on_attribute_selection_changed)
        self.sig_quit.connect(self.do_quit)
        self.sig_canvas_click.connect(self.add_desk)
        self.sig_canvas_drag.connect(self.move_desk)
        self.sig_canvas_right_click.connect(self.show_student_attributes)
        self.sig_shuffle.connect(self.desk_shuffle)
        self.sig_course_changed.connect(self.on_course_changed)
        self.sig_create_course.connect(self.on_create_course)
        self.sig_topic_changed.connect(self.on_topic_changed)
        self.sig_student_group_changed.connect(self.on_student_group_changed)
        self.sig_action_triggered.connect(self.action_triggered)
        self.sig_TBbutton.connect(self.action_triggered)
        self.sig_create_grp_std.connect(self.on_create_grp_std)
        self.sig_create_attribute.connect(self.on_create_attr)
        self.sig_delete_attributes.connect(self.on_delete_attributes)
        self.sig_delete_course.connect(self.on_delete_course)
        self.sig_attr_selection_changed.connect(self.on_attribute_selection_changed)
        self.sig_attribute_cell_selected.connect(self.on_attribute_cell_selected)

        # properties
        self.id_course = 0
        self.id_group = 0
        self.selection_mode = self.SEL_ALL
        self.filter_selection = False
        self.std_dialog_info: VStdAttributesDialog = None

        self.show_all_courses()
        self.show_all_groups()
        self.show_all_attributes()
        self.gui.update()

    def debug(self):
        self.gui.status_bar.showMessage("ouaf")

    @Slot(tuple)
    def add_desk(self, coords):
        """Add a new desk at mouse place"""
        if self.id_course > 0:
            row = coords[0]
            col = coords[1]
            id_desk = self.mod_bdd.get_desk_id_in_course_by_coords(self.id_course, row, col)
            if id_desk == 0:
                # The place is free, we create the desk
                id_desk = self.mod_bdd.create_new_desk_in_course(row, col, self.id_course)
                self.v_canvas.new_tile(row, col, id_desk)

            self.__bdd.commit()
            self.v_canvas.repaint()
        else:
            self.gui.status_bar.showMessage("Impossible : aucun cours sélectionné !")

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
        for i in range(0, len(all_desks) - 1, 2):
            d1 = all_desks[i]
            d2 = all_desks[i + 1]
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
        if self.id_course > 0:
            all_desks = self.mod_bdd.get_course_all_desks(self.id_course)
            topic_name = self.mod_bdd.get_topic_from_course_id(self.id_course)
            for d in all_desks:
                std = self.mod_bdd.get_student_by_id(d.id_student)
                if std:
                    self.v_canvas.new_tile(d.row, d.col, d.id, firstname=std.firstname, lastname=std.lastname)
                else:
                    self.v_canvas.new_tile(d.row, d.col, d.id)
            # Display course's topic
            self.gui.central_widget.classroom_tab.topic.select_topic(topic_name)
        self.v_canvas.repaint()

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
        if self.id_course == 0 and len(courses) > 0:
            self.id_course = courses[0][0]
        if self.id_course != 0:
            topic_name = self.mod_bdd.get_topic_from_course_id(self.id_course)

            self.gui.sidewidget.courses().init_table(
                list_courses=courses, selected_id=None if self.id_course == 0 else self.id_course)

            self.gui.central_widget.classroom_tab.topic.set_topics(topic_names, topic_name)
        else:
            self.gui.sidewidget.courses().init_table([])
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
        else:
            self.gui.sidewidget.students().set_students_list([])

    def auto_place(self):
        """Autoplacement of students on the free tiles"""
        max_row = int(AssetManager.getInstance().config("size", "default_room_rows"))
        max_col = int(AssetManager.getInstance().config("size", "default_room_columns"))
        group_name = self.mod_bdd.get_group_name_by_id(self.id_group)
        list_idstd = self.gui.sidewidget.students().selected_students()
        if not list_idstd:
            list_students = self.mod_bdd.get_students_in_group(group_name)
        else:
            list_students = [self.mod_bdd.get_student_by_id(i) for i in list_idstd]

        students_ids = {s.id for s in list_students}

        to_be_placed = len(list_students)
        list_available_desks = []
        list_to_remove = []
        for row in range(max_row):
            for col in range(max_col):
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

        info = None
        if to_be_placed > 0:
            info = f"Il manque {to_be_placed} places pour placer tous les élèves"
            self.gui.status_bar.showMessage(info)
        else:
            self.gui.status_bar.showMessage("Tous les élèves sont placés", 3000)
        self.__bdd.commit()

        if info is not None:
            VInfoDialog(self.gui, info).exec_()

    @Slot(int)
    def on_course_changed(self, new_course):
        """
        Triggered when the current course selection changed

        :param new_course: new selected course name
        :type new_course: int
        """
        self.id_course = new_course
        self.show_course()
        self.on_attribute_selection_changed()

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

        def get_desks(is_free):
            all_desks = self.mod_bdd.get_course_all_desks(self.id_course)
            if is_free:
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
        self.selection_mode = (self.selection_mode + 1) % 4
        self.on_attribute_selection_changed()
        self.v_canvas.repaint()

    def delete(self) -> None:
        if not VConfirmDialog(self.gui, "confirm_message_delete").exec_():
            return

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
            lastname, firstname = process_line(name, ";")
            self.mod_bdd.insert_student_in_group_id(firstname, lastname, 0, self.id_group)
            self.show_course()
            self.show_all_groups(current=self.id_group)
        else:  # Student edition
            id_std = int(prefix)
            lastname, firstname = process_line(name, ";")
            self.gui.status_bar.showMessage(f"Renommage de l'élève {firstname} {lastname}", 3000)
            self.mod_bdd.rename_student_by_id(id_std, firstname, lastname)
            self.show_course()
            self.show_all_groups(current=self.id_group)

        self.__bdd.commit()

    def killstudent(self):
        if not VConfirmDialog(self.gui, "confirm_message_delete").exec_():
            return

        self.gui.status_bar.showMessage(f"Suppression d'élèves", 3000)
        list_id_students = self.gui.sidewidget.students().selected_students()
        for id_std in list_id_students:
            self.mod_bdd.remove_student_from_group(id_std, self.id_group)
        self.show_course()
        self.show_all_groups(current=self.id_group)
        self.__bdd.commit()

    def sort_alpha(self, desc):
        self.gui.status_bar.showMessage("Tri alphabétique", 3000)
        group_name = self.mod_bdd.get_group_name_by_id(self.id_group)
        list_students = self.mod_bdd.get_students_in_group(group_name)
        sortlist = [(s.lastname, s.id) for s in list_students]
        sortlist.sort(reverse=desc)
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
        max_row = int(AssetManager.getInstance().config("size", "default_room_rows"))
        max_col = int(AssetManager.getInstance().config("size", "default_room_columns"))
        group_name = self.mod_bdd.get_group_name_by_id(self.id_group)

        sortlist = []
        for row in range(max_row):
            for col in range(max_col):
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
        self.mod_bdd.insert_attribute(attr_name, attr_type)
        self.__bdd.commit()

        self.show_all_attributes()

    def show_all_attributes(self):
        """Initializes the contents of the attributes list"""

        list_attr = self.mod_bdd.get_all_attributes()
        self.gui.sidewidget.attributes().set_attributes_list(list_attr)

    @Slot()
    def on_delete_attributes(self) -> None:
        """
        Deletes all the selected attribtues
        """
        if not VConfirmDialog(self.gui, "confirm_message_delete").exec_():
            return

        for id_a in self.gui.sidewidget.attributes().selected_attributes():
            self.mod_bdd.delete_attribute_with_id(id_a)
        self.__bdd.commit()
        self.show_all_attributes()

    @Slot()
    def on_delete_course(self) -> None:
        """
        Deletes the selected course
        """
        if not VConfirmDialog(self.gui, "confirm_message_delete").exec_():
            return

        self.mod_bdd.delete_course_with_id(self.id_course)
        self.id_course = 0
        self.__bdd.commit()
        self.show_all_courses()

    def on_delete_group(self) -> None:
        """
        Deletes the selected group
        """
        if not VConfirmDialog(self.gui, "confirm_message_delete").exec_():
            return

        self.mod_bdd.delete_group_by_id(self.id_group)
        self.id_group = 0
        self.__bdd.commit()
        self.show_all_groups()

    @Slot()
    def on_attribute_selection_changed(self) -> None:
        """
        Triggered when the attribute selection changed
        - attributes = [(1, "Attr1"), (2, "Attr2") ...]
        - students = [(1, "Thomas Lécluse"), (2, "Pauline Lécluse"), ...]
        - data = {(attr_id, std_id}: cell_data, ...}
        """
        if self.std_dialog_info and self.std_dialog_info.isVisible():
            id_topic = self.mod_bdd.get_topic_id_by_course_id(self.id_course)
            attrs = []
            for attr_id, attr_name, attr_type in self.mod_bdd.get_all_attributes():
                attrs.append((attr_id, attr_name,
                              self.mod_bdd.get_attribute_value(self.std_dialog_info.student.id, attr_id, id_topic)))

            self.std_dialog_info.attributes_updated(attrs)

        list_id_attr = self.gui.sidewidget.attributes().selected_attributes()

        if list_id_attr:
            id_topic = self.mod_bdd.get_topic_id_by_course_id(self.id_course)
            all_attributes = self.mod_bdd.get_all_attributes()
            # all_attributes = list [(id1, attrName1, attrType1), ...]
            # now we filter attributes
            attributes = [(a[0], a[1]) for a in all_attributes if a[0] in list_id_attr]

            # get all students in current course
            students_in_course = self.mod_bdd.get_students_in_course_by_id(self.id_course)
            if self.filter_selection:
                # get desk selection
                desks_id = self.v_canvas.get_selected_tiles()
                id_students_selected = [self.mod_bdd.get_desk_by_id(d).id_student for d in desks_id]
                students = [(s.id, f"{s.lastname} {s.firstname}") for s in students_in_course if
                            s.id in id_students_selected]
            else:
                students = [(s.id, f"{s.lastname} {s.firstname}") for s in students_in_course]
            students.sort(key=lambda x: x[1])

            # get datas
            data = dict()
            for a in attributes:
                for s in students:
                    val = self.mod_bdd.get_attribute_value(s[0], a[0], id_topic)
                    if val:
                        if len(val) == 7 and val[0] == '#':
                            val = QColor(val)
                        data[(a[0], s[0])] = val

            # push the data into the view
            self.gui.central_widget.attributes_tab.set_data(attributes, students, data)
        else:
            self.gui.central_widget.attributes_tab.set_data([], [], {})

    @Slot(int, int)
    def on_attribute_cell_selected(self, attr_id: int, std_id: int) -> None:
        """
        Triggered when a cell is clicked on the attributes table.
        Opens an edition panel, allowing the user to edit the cell content.

        :param attr_id: Attribute ID
        :param std_id: Student ID
        """
        attr_type = self.mod_bdd.get_attribute_type_from_id(attr_id)
        id_topic = self.mod_bdd.get_topic_id_by_course_id(self.id_course)
        val = self.mod_bdd.get_attribute_value(std_id, attr_id, id_topic)

        dlg = None  # QDialog
        if attr_type == EAttributesTypes.TEXT.value:
            dlg = VDlgEditText(self.gui, val)
        elif attr_type == EAttributesTypes.COUNTER.value:
            dlg = VDlgEditCounter(self.gui, val)
        elif attr_type == EAttributesTypes.MARK.value:
            dlg = VDlgEditMark(self.gui, val)
        elif attr_type == EAttributesTypes.COLOR.value:
            dlg = VDlgEditColor(self.gui, val)

        if dlg and dlg.exec_():
            self.mod_bdd.update_attr_with_ids(std_id, attr_id, id_topic, dlg.new_value())
            self.__bdd.commit()
            self.on_attribute_selection_changed()

    def change_filter_selection(self):
        self.filter_selection = not self.filter_selection
        self.on_attribute_selection_changed()

    def lot_change(self):
        list_id_attr = self.gui.sidewidget.attributes().selected_attributes()
        if len(list_id_attr) == 1:
            # Only one attribute is selected, we change it
            id_topic = self.mod_bdd.get_topic_id_by_course_id(self.id_course)
            students_in_course = self.mod_bdd.get_students_in_course_by_id(self.id_course)
            if self.filter_selection:
                # get desk selection
                desks_id = self.v_canvas.get_selected_tiles()
                id_students_selected = [self.mod_bdd.get_desk_by_id(d).id_student for d in desks_id]
                students = [(s.id, f"{s.lastname} {s.firstname}") for s in students_in_course if
                            s.id in id_students_selected]
            else:
                students = [(s.id, f"{s.lastname} {s.firstname}") for s in students_in_course]
            attr_id = list_id_attr[0]
            attr_type = self.mod_bdd.get_attribute_type_from_id(attr_id)

            dlg = None  # QDialog
            val = ""
            if attr_type == EAttributesTypes.TEXT.value:
                dlg = VDlgEditText(self.gui, val)
            elif attr_type == EAttributesTypes.MARK.value:
                dlg = VDlgEditMark(self.gui, val)
            elif attr_type == EAttributesTypes.COLOR.value:
                dlg = VDlgEditColor(self.gui, val)
            elif attr_type == EAttributesTypes.COUNTER.value:
                dlg = VDlgEditCounter(self.gui, val)

            if dlg and dlg.exec_():
                if attr_type == EAttributesTypes.COUNTER.value:
                    for s in students:
                        if dlg.new_value() == 0:
                            val = "0"
                        else:
                            val = self.mod_bdd.get_attribute_value(s[0], attr_id, id_topic)
                            val = str(int(val) + dlg.new_value()) if val else "1"
                        self.mod_bdd.update_attr_with_ids(s[0], attr_id, id_topic, val)
                else:
                    for s in students:
                        val = dlg.new_value()
                        self.mod_bdd.update_attr_with_ids(s[0], attr_id, id_topic, val)

                self.__bdd.commit()
                self.on_attribute_selection_changed()

    @Slot(tuple)
    def show_student_attributes(self, desk_position: tuple) -> None:
        """
        Displays a dialog with all the student's attributes information.

        :param desk_position: student's desk position (where the click was triggered)
        :type desk_position: tuple
        """
        desk_id = self.mod_bdd.get_desk_id_in_course_by_coords(self.id_course, desk_position[0], desk_position[1])
        std = self.mod_bdd.get_student_by_desk_id(desk_id)
        topic = self.mod_bdd.get_topic_id_by_course_id(self.id_course)

        attrs = []
        for attr_id, attr_name, attr_type in self.mod_bdd.get_all_attributes():
            attrs.append((attr_id, attr_name, self.mod_bdd.get_attribute_value(std.id, attr_id, topic)))

        if self.std_dialog_info and self.std_dialog_info.isVisible():  # Closes any opened info dialog
            self.std_dialog_info.close()

        self.std_dialog_info = VStdAttributesDialog(self.gui, self.sig_attribute_cell_selected, std, attrs)

        # We can't use exec_() method, nor make the dialog modal because for some reason, at least on OSX, once closed,
        # most of the HMI does not respond to user interaction.
        # The chosen workaround is to just show() the dialog, and make it always on top. If a new dialog is to be
        # displayed, the previous one would be closed before.
        self.std_dialog_info.show()
