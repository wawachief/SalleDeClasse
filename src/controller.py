import sqlite3
from random import randint

from PySide2.QtCore import QObject, Signal, Slot

from src.Model.mod_bdd import ModBdd
from src.View.view_mainframe import ViewMainFrame


class Controller(QObject):
    sig_add_tile = Signal()
    sig_quit = Signal()
    sig_canvas_click = Signal(tuple)

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

        # Signals connection
        self.sig_add_tile.connect(self.test_buttton)
        self.sig_quit.connect(self.do_quit)
        self.sig_canvas_click.connect(self.add_desk)

        # properties
        self.set_course("Maths_2DE11")
        self.show_course()

    @Slot()
    def test_buttton(self):
        self.auto_place()
        
    @Slot(tuple)
    def add_desk(self, coords):
        """Add a new desk at mouse place"""
        x = coords[0]
        y = coords[1]
        id_desk = self.mod_bdd.get_desk_id_in_course_by_coords(self.id_course, x, y)
        if id_desk == 0:
            # The place is free, we create the desk
            id_desk = self.mod_bdd.create_new_desk_in_course(x, y, self.id_course)
            self.v_canvas.new_tile(x, y)
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
        list_students = self.mod_bdd.get_students_in_course(self.id_course)
        for s in list_students:
            print(s)
        for row in range(maxRow):
            for col in range(maxCol):
                id_desk = self.mod_bdd.get_desk_id_in_course_by_coords(self.id_course, row, col)
                if id_desk != 0:
                    student = self.mod_bdd.get_student_by_desk_id(id_desk)
                    if student is None:
                        # We have a free spot
                        print(row, col)