import sqlite3

from src.View.view_canvas import ViewTile
from PySide2.QtCore import Signal, Slot, QObject

from src.Model.mod_room import ModRoom
from src.View.view_mainframe import ViewMainFrame

from random import randint


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

        # Create the Views
        self.gui = ViewMainFrame(self.sig_quit, self.config)
        self.gui.central_widget.sig_add_tile = self.sig_add_tile
        self.v_canvas = self.gui.central_widget.v_canvas
        # Plugs the signals
        self.gui.sig_quit = self.sig_quit
        self.v_canvas.sig_canvas_click = self.sig_canvas_click

        # Create the Models
        self.m_room = self.show_room("s 314")

        # Signals connection
        self.sig_add_tile.connect(self.create_desk)
        self.sig_quit.connect(self.do_quit)
        self.sig_canvas_click.connect(self.add_desk)


    @Slot()
    def create_desk(self):
        """Create dummy desk at random place"""
        c, cont = 0, True
        while c<10 and cont:
            c += 1
            x = randint(0, 4)
            y = randint(0, 4)
            id = self.m_room.get_desk_id(x, y)
            if id == 0:
                # The place is free, we create the desk
                self.m_room.add_desk(x, y)
                cont = False
                new_tile = ViewTile(x, y)
                self.v_canvas.tiles.append(new_tile)
        self.v_canvas.repaint()

    @Slot(tuple)
    def add_desk(self, coords):
        """Add a new desk at mouse place"""
        x = coords[0]
        y = coords[1]
        id_desk = self.m_room.get_desk_id(x, y)
        if id_desk == 0:
            # The place is free, we create the desk
            id_desk = self.m_room.add_desk(x, y)
            new_tile = ViewTile(x, y)
            self.v_canvas.tiles.append(new_tile)
        self.v_canvas.repaint()

    @Slot()
    def do_quit(self):
        print("Bye")
        self.__bdd.close()

    def show_room(self, room_name):
        room = ModRoom(self.__bdd, room_name)
        all_desks = room.get_all_desks()
        for d in all_desks:
            new_tile = ViewTile(d.cx, d.cy)
            self.v_canvas.tiles.append(new_tile)
        self.v_canvas.repaint()
        return room