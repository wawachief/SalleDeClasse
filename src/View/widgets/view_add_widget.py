from PySide2.QtWidgets import QWidget, QPushButton, QLineEdit, QHBoxLayout, QShortcut
from PySide2.QtCore import QSize, Qt, Signal
from PySide2.QtGui import QKeySequence

from src.assets_manager import get_icon


class ViewAddWidget(QWidget):

    def __init__(self, config):
        """
        Widget proposing an add button, with a text entry that will appear only when the add button is pressed.
        A new click on the add button will cancel the action, and a press on <Enter> will validate.

        :param config: application's parsed configuration
        """
        QWidget.__init__(self)

        self.config = config

        self.setFixedSize(QSize(150, 50))

        self.add_btn = QPushButton()
        self.add_btn.setIcon(get_icon("add"))
        self.add_btn.setIconSize(QSize(35, 35))
        self.add_btn.setToolTip("Créer")

        self.field = QLineEdit()
        self.field.setVisible(False)

        # Current state
        self.is_creating = False

        # Signals
        self.add_btn.clicked.connect(self.__on_add_pressed)
        self.sig_new_element = None  # Signal emitted when a new element is created
        self.field.returnPressed.connect(self.__on_field_enter)
        QShortcut(QKeySequence("Escape"), self.field).activated.connect(lambda: self.__on_add_pressed())  # Cancel

        # Layout
        self.__init_layout()
        self.__init_style()

    def __init_style(self):
        self.add_btn.setStyleSheet("border: none;")

    def __init_layout(self):
        layout = QHBoxLayout()
        layout.setMargin(0)

        layout.addWidget(self.add_btn, alignment=Qt.AlignLeft)
        layout.addWidget(self.field, alignment=Qt.AlignLeft)

        self.setLayout(layout)

    def __on_add_pressed(self):
        """
        Performs the action associated to the add button, given the current state
        """
        self.is_creating = not self.is_creating

        if self.is_creating:
            self.add_btn.setIcon(get_icon("close"))
            self.add_btn.setToolTip("Annuler")

            self.field.setVisible(True)
            self.field.setFocus()
            self.field.setText(self.get_prefix())
        else:
            self.field.clear()
            self.add_btn.setIcon(get_icon("add"))
            self.add_btn.setToolTip("Créer")

            self.field.setVisible(False)

    def get_prefix(self):
        """
        Gets the prefix to put in the field when appears

        :rtype: str
        """
        return ""

    def __on_field_enter(self):
        """
        Triggered when Enter key is pressed on the name field. Emits the creation signal then hides the field.
        """
        if self.field.text():
            self.sig_new_element.emit(self.field.text())

        self.field.clear()
        self.__on_add_pressed()  # Updates the state and hides the entry field


class ViewAddLine(QWidget):

    def __init__(self):
        """
        Widget with a single edit line that can be displayed or hidden at wish. A press on <Enter> displays it, and
        <Escape> hides it.
        """
        QWidget.__init__(self)

        self.sig_create: Signal = None
        self.creator: str = None

        self.create_field = QLineEdit()

        # Shortcuts
        self.create_field.returnPressed.connect(self.__on_create)
        QShortcut(QKeySequence("Escape"), self.create_field).activated.connect(lambda: self.hide_field())  # Cancel

        # Layout
        layout = QHBoxLayout()
        layout.setMargin(0)
        layout.addWidget(self.create_field)
        self.setLayout(layout)

        self.hide_field()

    def show_field(self, origin: str) -> None:
        """
        Shows and focus the creation field

        :param origin: action that triggered the displayal
        """
        self.creator = origin
        self.create_field.setVisible(True)
        self.create_field.setFocus()

        if origin == 'create_group':
            self.create_field.setPlaceholderText("Nom du groupe")
        elif origin == 'create_student':
            self.create_field.setPlaceholderText("Nom/Prénom de l'élève")

    def hide_field(self) -> None:
        """
        Hides the creation field
        """
        self.creator = None
        self.create_field.clear()
        self.create_field.setVisible(False)

    def __on_create(self) -> None:
        """
        Triggered when enter is pressed on the creation field. Emits the entered text with creator action as prefix.
        """
        res = ""

        if self.creator == "create_group":
            res += "grp "
        elif self.creator == "create_student":
            res += "std "

        res += self.create_field.text()
        self.sig_create.emit(res)

        self.hide_field()
