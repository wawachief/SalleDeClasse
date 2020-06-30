from View.viewtile import ViewTile
from PySide2.QtCore import Signal, Slot, QObject

from Model.mod_room import ModRoom
from View.viewmainframe import ViewMainFrame

from random import randint


class Controller(QObject):
    sig_add_tile = Signal()

    def __init__(self):
        QObject.__init__(self)

        # BDD connection
        self.__bdd = sqlite3.connect("Model/SQL/sdc_db")
        self.__cursor = self.__bdd.cursor()

        # Create the Views
        self.gui = ViewMainFrame()
        self.gui.central_widget.sig_add_tile = self.sig_add_tile
        self.v_canvas = self.gui.central_widget.v_canvas

        # Create the models
        self.m_room = ModRoom("s 314")

        # Signals connection
        self.sig_add_tile.connect(self.create_desk)


    @Slot()
    def create_desk(self):

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