from PySide2.QtCore import Slot

from src.View.popup.view_confirm_dialogs import VConfirmDialog

from src.assets_manager import AssetManager

from random import shuffle


class CourseController:
    def __init__(self, main_ctrl, bdd):
        """
        Application Course controller.
        """
        self.main_ctrl = main_ctrl
        self.attr_ctrl = main_ctrl.attr_ctrl
        self.__bdd = bdd

        self.mod_bdd = main_ctrl.mod_bdd

        self.gui = main_ctrl.gui
        self.v_canvas = main_ctrl.v_canvas

    #
    # Signals handling
    #

    # desks methods

    @Slot(int, bool)
    def on_desk_selection_changed(self, student_id: int, selected: bool) -> None:
        desk_id = self.mod_bdd.get_desk_id_by_student_id_and_course_id(student_id, self.main_ctrl.id_course)
        self.v_canvas.change_desk_selection_by_desk_id(desk_id, selected)
        self.attr_ctrl.on_attribute_selection_changed()
        self.v_canvas.repaint()

    @Slot(tuple)
    def add_desk(self, coords):
        """Add a new desk at mouse place"""
        if self.main_ctrl.id_course > 0:
            row = coords[0]
            col = coords[1]
            id_desk = self.mod_bdd.get_desk_id_in_course_by_coords(self.main_ctrl.id_course, row, col)
            if id_desk == 0:
                # The place is free, we create the desk
                id_desk = self.mod_bdd.create_new_desk_in_course(row, col, self.main_ctrl.id_course)
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

        id_desk_start = self.mod_bdd.get_desk_id_in_course_by_coords(self.main_ctrl.id_course, start[0], start[1])
        if 0 <= end[0] < max_row and 0 <= end[1] < max_col:
            # Destination is in the canvas
            id_desk_end = self.mod_bdd.get_desk_id_in_course_by_coords(self.main_ctrl.id_course, end[0], end[1])
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

    @Slot()
    def desk_shuffle(self):
        """Shuffle all desktops"""
        all_desks = self.mod_bdd.get_course_all_desks(self.main_ctrl.id_course)
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

    # courses methods

    @Slot(str)
    def on_topic_changed(self, new_topic):
        """
        Triggered when the topic selection of the current course changed

        :param new_topic: new selected topic
        :type new_topic: str
        """
        self.mod_bdd.set_topic_to_course_id(self.main_ctrl.id_course, new_topic)
        self.__bdd.commit()
        self.show_all_courses()

    @Slot(int)
    def on_course_changed(self, new_course):
        """
        Triggered when the current course selection changed

        :param new_course: new selected course name
        :type new_course: int
        """
        self.main_ctrl.id_course = new_course
        self.show_course()
        self.attr_ctrl.on_attribute_selection_changed()

    @Slot(str)
    def on_create_course(self, new_course):
        """
        Triggered when a new course is to be created

        :param new_course: new course name to create
        :type new_course: str
        """

        old_course_id = self.main_ctrl.id_course
        self.set_course(new_course)
        self.show_all_courses()
        # Manually call the course changed update (manual set to selection does not trigger the signal emit)
        self.on_course_changed(self.main_ctrl.id_course)

        # Copy the Desk disposition of the old course_id
        old_desks = self.mod_bdd.get_course_all_desks(old_course_id)
        for d in old_desks:
            id_desk = self.mod_bdd.create_new_desk_in_course(d.row, d.col, self.main_ctrl.id_course)
            self.v_canvas.new_tile(d.row, d.col, id_desk)

        self.__bdd.commit()
        self.v_canvas.repaint()

    @Slot()
    def on_delete_course(self) -> None:
        """
        Deletes the selected course
        """
        if not VConfirmDialog(self.gui, "confirm_message_delete").exec_():
            return

        self.mod_bdd.delete_course_with_id(self.main_ctrl.id_course)
        self.main_ctrl.id_course = 0
        self.__bdd.commit()
        self.show_all_courses()

    #
    # General methods
    #

    # desks methods

    def auto_select_desks(self) -> None:
        """Select Desks, rotate selection mode
        - 3 = all,
        - 2 = occupied desks,
        - 1 = empty desks,
        - 0 = none
        """

        def get_desks(is_free):
            all_desks = self.mod_bdd.get_course_all_desks(self.main_ctrl.id_course)
            if is_free:
                return [d.id for d in all_desks if d.id_student == 0]
            else:
                return [d.id for d in all_desks if d.id_student != 0]

        if self.main_ctrl.selection_mode == self.main_ctrl.SEL_NONE:
            self.v_canvas.select_tiles_to(False)
            self.gui.status_bar.showMessage(f"Déselection de tous les emplacements", 3000)
        elif self.main_ctrl.selection_mode == self.main_ctrl.SEL_EMPTY:
            self.v_canvas.select_tiles_from_desks_ids(get_desks(True))
            self.gui.status_bar.showMessage(f"Selection des emplacements libres", 3000)
        elif self.main_ctrl.selection_mode == self.main_ctrl.SEL_OCCUPIED:
            self.v_canvas.select_tiles_from_desks_ids(get_desks(False))
            self.gui.status_bar.showMessage(f"Selection des emplacements occupés", 3000)
        else:
            self.v_canvas.select_tiles_to(True)
            self.gui.status_bar.showMessage(f"Selection de tous les emplacements", 3000)
        self.main_ctrl.selection_mode = (self.main_ctrl.selection_mode + 1) % 4
        self.attr_ctrl.on_attribute_selection_changed()
        self.v_canvas.repaint()

    def sort_desks(self):
        self.gui.status_bar.showMessage("Tri d'après les places", 3000)
        max_row = int(AssetManager.getInstance().config("size", "default_room_rows"))
        max_col = int(AssetManager.getInstance().config("size", "default_room_columns"))
        group_name = self.mod_bdd.get_group_name_by_id(self.main_ctrl.id_group)

        sortlist = []
        for row in range(max_row):
            for col in range(max_col):
                id_desk = self.mod_bdd.get_desk_id_in_course_by_coords(self.main_ctrl.id_course, row, col)
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

    def remove_desk_by_id(self, id_desk):
        """Removes the desk designed by id_desk
        - removes the entry in the bdd
        - removes the tile on viewcanvas
        BDD commit MUST be called after removing desks !
        """
        # Desk is out of the canvas, we remove it
        self.mod_bdd.remove_desk_by_id(id_desk)
        # remove the tile as well
        self.v_canvas.remove_tile(id_desk)

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

    # Course methods

    def show_course(self):
        """Displays a the course defined by the id_course property"""
        self.v_canvas.delete_all_tiles()
        if self.main_ctrl.id_course > 0:
            all_desks = self.mod_bdd.get_course_all_desks(self.main_ctrl.id_course)
            topic_name = self.mod_bdd.get_topic_from_course_id(self.main_ctrl.id_course)
            for d in all_desks:
                std = self.mod_bdd.get_student_by_id(d.id_student)
                if std:
                    self.v_canvas.new_tile(d.row, d.col, d.id, firstname=std.firstname, lastname=std.lastname)
                else:
                    self.v_canvas.new_tile(d.row, d.col, d.id)
            # Display course's topic
            self.gui.central_widget.classroom_tab.topic.select_topic(topic_name)
        self.v_canvas.repaint()

    def show_all_courses(self):
        """Initializes the contents of the widgets :
        - courses list
        - topic list"""

        courses = self.mod_bdd.get_courses()
        topic_names = self.mod_bdd.get_topics_names()
        if self.main_ctrl.id_course == 0 and len(courses) > 0:
            self.main_ctrl.id_course = courses[0][0]
        if self.main_ctrl.id_course != 0:
            topic_name = self.mod_bdd.get_topic_from_course_id(self.main_ctrl.id_course)

            self.gui.sidewidget.courses().init_table(
                list_courses=courses, selected_id=None if self.main_ctrl.id_course == 0 else self.main_ctrl.id_course)

            self.gui.central_widget.classroom_tab.topic.set_topics(topic_names, topic_name)
        else:
            self.gui.sidewidget.courses().init_table([])
        self.show_course()

    def set_course(self, course_name):
        """Sets current course to course_name
        if course_name does not exisis, creates it, with current topic id
        YOU MUST CALL commit after !
        The new course have topic_id of 1 (main topic)
        """
        self.main_ctrl.id_course = self.mod_bdd.create_course_with_name(course_name)
        self.main_ctrl.selection_mode = self.main_ctrl.SEL_ALL
