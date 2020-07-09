from PySide2.QtWidgets import QWidget, QPushButton, QLineEdit, QHBoxLayout
from PySide2.QtCore import QSize, Qt

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
        else:
            self.add_btn.setIcon(get_icon("add"))
            self.add_btn.setToolTip("Créer")

            self.field.setVisible(False)

    def __on_field_enter(self):
        """
        Triggered when Enter key is pressed on the name field. Emits the creation signal then hides the field.
        """
        if self.field.text():
            self.sig_new_element.emit(self.field.text())

        self.field.clear()
        self.__on_add_pressed()  # Updates the state and hides the entry field
