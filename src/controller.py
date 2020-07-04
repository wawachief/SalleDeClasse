import sqlite3
from random import randint

from PySide2.QtCore import QObject, Signal, Slot

from src.Model.mod_bdd import ModBdd
from src.View.view_mainframe import ViewMainFrame


class Controller(QObject):
    sig_add_tile = Signal()
    sig_quit = Signal()
    sig_canvas_click = Signal(tuple)
    sig_canvas_drag = Signal(tuple, tuple)

    def __init__(self, config):
        """
        Application main controller.

        :param config: application's parsed configuration
        """
        QObject.__init__(self)

        self.config = config

        # BDD connection
        self.__bdd = sqlite3.connect("src/SQL/sdc_db")
        self.mod_bdd = ModBdd(self.__bdd)

        # Create the Views
        self.gui = ViewMainFrame(self.sig_quit, self.config)
        self.gui.central_widget.sig_add_tile = self.sig_add_tile
        self.v_canvas = self.gui.central_widget.v_canvas
        # Plugs the signals
        self.gui.sig_quit = self.sig_quit
        self.v_canvas.sig_canvas_click = self.sig_canvas_click
        self.v_canvas.sig_canvas_drag = self.sig_canvas_drag

        # Signals connection
        self.sig_add_tile.connect(self.test_buttton)
        self.sig_quit.connect(self.do_quit)
        self.sig_canvas_click.connect(self.add_desk)
        self.sig_canvas_drag.connect(self.move_desk)

        # properties
        self.set_course("Maths_2DE3")
        self.show_course()

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
            self.v_canvas.new_tile(row, col)
        self.v_canvas.repaint()
    
    @Slot(tuple, tuple)
    def move_desk(self, start, end):
        """Moves a desk from start to end"""

        id_desk_start = self.mod_bdd.get_desk_id_in_course_by_coords(self.id_course, start[0], start[1])
        if id_desk_start == 0:
            # Houston, we have a situation
            print("Houston, we have a situation")
            return None
        id_desk_end = self.mod_bdd.get_desk_id_in_course_by_coords(self.id_course, end[0], end[1])
        if id_desk_end == 0:
            # We just change the coordinates
            self.mod_bdd.move_desk_by_id(id_desk_start, end[0], end[1])
            # We update the view
            self.v_canvas.move_tile(start, end)
        else:
            # We swap the two desks
            self.mod_bdd.move_desk_by_id(id_desk_start, end[0], end[1])
            self.mod_bdd.move_desk_by_id(id_desk_end, start[0], start[1])
            # We update the view
            self.v_canvas.move_tile(start, (0, 0))
            self.v_canvas.move_tile(end, start, True)
            self.v_canvas.move_tile((0, 0), end)
        self.v_canvas.repaint()

    @Slot()
    def do_quit(self):
        print("Bye")
        self.v_canvas.application_closing()
        self.__bdd.close()

    def show_course(self):
        all_desks = self.mod_bdd.get_course_all_desks(self.id_course)
        for d in all_desks:
            std = self.mod_bdd.get_student_by_id(d.id_student)
            if std :
                self.v_canvas.new_tile(d.row, d.col, firstname=std.firstname, lastname=std.lastname)
            else:
                self.v_canvas.new_tile(d.row, d.col)
        self.v_canvas.repaint()

    def set_course(self, course_name):
        self.id_course = self.mod_bdd.create_course_with_name(course_name)

    def auto_place(self):
        """Autoplacement of students on the free tiles"""
        maxRow = int(self.config.get("size", "default_room_rows"))
        maxCol = int(self.config.get("size", "default_room_columns"))
        list_students = self.mod_bdd.get_students_in_class(self.id_course)
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
            self.v_canvas.set_student((dsk[1], dsk[2]), student.firstname, student.lastname)
            self.v_canvas.repaint()
            
            index_std += 1