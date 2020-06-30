from View.viewtile import ViewTile
from View.viewmainframe import ViewMainFrame
from PySide2.QtCore import Signal, Slot, QObject
from random import randint


class Controller(QObject):
    sig_add_tile = Signal()

    def __init__(self):
        QObject.__init__(self)
        self.gui = ViewMainFrame()
        self.sig_add_tile.connect(self.create_tile)
        self.gui.central_widget.sig_add_tile = self.sig_add_tile
        self.v_canvas = self.gui.central_widget.v_canvas

    @Slot()
    def create_tile(self):
        self.v_canvas.tiles.clear()

        generated = []

        while len(generated) < 5:
            x = randint(0, 4)
            y = randint(0, 4)

            if (x, y) not in generated:
                generated.append((x, y))

        for x, y in generated:
            self.v_canvas.tiles.append(ViewTile(x, y))

        self.v_canvas.repaint()