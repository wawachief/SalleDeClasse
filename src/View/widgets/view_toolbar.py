from PySide2.QtWidgets import QToolBar, QPushButton
from PySide2.QtCore import Signal, Slot


class ViewMainToolBar(QToolBar):

    sig_enable_perspective_btn = Signal(bool)

    def __init__(self, config):
        """
        Main ToolBar, providing features buttons that operates over the canvas.
        The callbacks methods provided by this class should be redirected towards any widget handling the associated
        process.

        :param config: application's parsed configuration
        """
        QToolBar.__init__(self)
        self.config = config

        # Buttons
        self.__btn_magic = QPushButton("** Magic Button **")  # Debug btn
        self.__btn_magic.clicked.connect(self.on_btn_magic_clicked)

        self.__btn_perspective = QPushButton("Switch perspective")  # Perspective view button
        self.__btn_perspective.setToolTip("Changer de perspective")
        self.__btn_perspective.clicked.connect(self.on_btn_perspective_clicked)

        # Signals
        self.sig_enable_perspective_btn.connect(self.enable_perspective_btn)

        # Layout
        self.__set_widgets()
        self.__set_style()

    def __set_widgets(self):
        """
        Adds the widgets to this toolbar
        """
        self.addWidget(self.__btn_magic)
        self.addWidget(self.__btn_perspective)

    def __set_style(self):
        """
        Inits the stylesheet of this widget
        """
        # Toolbar
        grad_toolbar = "background-color:QLinearGradient(x1: 0, y1: 1, x2: 0, y2: 0, stop: 0 #BDBDBD, stop: 1 #AAAAAA);"
        bg_toolbar = "QToolBar { " + grad_toolbar + " border:none; }"

        # Buttons
        btns = "QPushButton:hover {background-color: #CEECF5;} QPushButton {border: none; height: 2em; margin: 5px;}"

        self.setStyleSheet(f"{bg_toolbar} {btns}")

    @Slot(bool)
    def enable_perspective_btn(self, do_enable):
        """
        Enables or disables the change-perspective button to prevent several animation at a time

        :param do_enable: True to enable
        :type do_enable: bool
        """
        self.__btn_perspective.setEnabled(do_enable)

    def on_btn_perspective_clicked(self):
        pass

    def on_btn_magic_clicked(self):
        pass


