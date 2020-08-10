from PySide2.QtWidgets import QWidget, QPushButton, QLineEdit, QHBoxLayout, QShortcut, QComboBox
from PySide2.QtCore import QSize, Qt, Signal
from PySide2.QtGui import QKeySequence

from src.assets_manager import get_icon, tr

from src.enumerates import EAttributesTypes


class ViewAddWidget(QWidget):

    def __init__(self, btn_to_disable: QPushButton):
        """
        Widget proposing an add button, with a text entry that will appear only when the add button is pressed.
        A new click on the add button will cancel the action, and a press on <Enter> will validate.

        :param btn_to_disable: button to disable when the creation field is shown
        """
        QWidget.__init__(self)

        self.setFixedSize(QSize(150, 50))

        self.add_btn = QPushButton()
        self.add_btn.setIcon(get_icon("add"))
        self.add_btn.setIconSize(QSize(35, 35))
        self.add_btn.setToolTip(tr("crs_create_btn_tooltip"))

        self.field = QLineEdit()
        self.field.setVisible(False)

        # Current state
        self.is_creating = False
        self.btn_to_disable = btn_to_disable

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
        self.btn_to_disable.setEnabled(not self.is_creating)

        if self.is_creating:
            self.add_btn.setIcon(get_icon("close"))
            self.add_btn.setToolTip(tr("btn_cancel"))

            self.field.setVisible(True)
            self.field.setFocus()
            self.field.setText(self.get_prefix())
        else:
            self.field.clear()
            self.add_btn.setIcon(get_icon("add"))
            self.add_btn.setToolTip(tr("crs_create_btn_tooltip"))

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

    def show_field(self, origin: str, default_text: str=None) -> None:
        """
        Shows and focus the creation field

        :param origin: action that triggered the displayal
        :param default_text: default text to display in the field
        """
        self.creator = origin
        self.create_field.setVisible(True)
        self.create_field.setFocus()

        if origin == 'create_group':
            self.create_field.setPlaceholderText(tr("group_name"))
        elif origin == 'create_student':
            self.create_field.setPlaceholderText(tr("std_name"))
        else:  # We are editing a student, the origin is the student id
            self.create_field.setText(default_text)

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
        else:  # Student edition: we put the id in prefix
            res += self.creator + (4 - len(self.creator)) * ' '  # We use a 4-length string for the id

        res += self.create_field.text()
        # If we don't have text, we don't send anything
        if self.create_field.text():
            self.sig_create.emit(res)

        self.hide_field()


class ViewAddAttributeWidget(QWidget):

    def __init__(self):
        """
        Widget proposing an add button, with a text entry that will appear only when the add button is pressed. The
        attribute type selection combo will also appear next to it.
        We also display a remove button, that will be shown only when the other fields are not.

        A new click on the add button (or an <Escape> press) will cancel the action, and a press on <Enter> will
        validate.
        """
        QWidget.__init__(self)

        self.setFixedSize(QSize(290, 50))

        self.attr_types_dico = {}
        for attr_type in [t.value for t in EAttributesTypes]:
            self.attr_types_dico[tr(attr_type)] = attr_type

        self.add_btn = QPushButton()
        self.add_btn.setIcon(get_icon("add"))
        self.add_btn.setIconSize(QSize(35, 35))
        self.add_btn.setToolTip(tr("crs_create_btn_tooltip"))

        self.field = QLineEdit()
        self.field.setVisible(False)

        self.combo = QComboBox()
        self.combo.setFixedWidth(105)
        self.combo.addItems(list(self.attr_types_dico.keys()))
        self.combo.setVisible(False)

        self.ok_btn = QPushButton()
        self.ok_btn.setIcon(get_icon("valid"))
        self.ok_btn.setIconSize(QSize(35, 35))
        self.ok_btn.setToolTip(tr("crs_create_btn_tooltip"))
        self.ok_btn.setVisible(False)

        self.delete_btn = QPushButton()
        self.delete_btn.setIcon(get_icon("del"))
        self.delete_btn.setIconSize(QSize(35, 35))
        self.delete_btn.setToolTip(tr("btn_suppr"))
        self.delete_btn.setEnabled(False)

        # Current state
        self.is_creating = False

        # Signals
        self.ok_btn.clicked.connect(self.__on_field_enter)
        self.add_btn.clicked.connect(self.__on_add_pressed)
        self.sig_new_element = None  # Signal emitted when a new element is created
        self.sig_delete = None  # Signal emitted when the delete button is clicked
        self.field.returnPressed.connect(self.__on_field_enter)
        QShortcut(QKeySequence("Escape"), self.field).activated.connect(lambda: self.__on_add_pressed())  # Cancel
        self.delete_btn.clicked.connect(lambda: self.sig_delete.emit())

        # Layout
        self.__init_layout()
        self.__init_style()

    def __init_style(self) -> None:
        self.setStyleSheet("QPushButton { border: none; }")

    def __init_layout(self) -> None:
        layout = QHBoxLayout()
        layout.setMargin(0)

        layout.addWidget(self.add_btn, alignment=Qt.AlignLeft)
        layout.addWidget(self.field, alignment=Qt.AlignLeft)
        layout.addWidget(self.combo, alignment=Qt.AlignLeft)
        layout.addWidget(self.ok_btn, alignment=Qt.AlignRight)
        layout.addWidget(self.delete_btn, alignment=Qt.AlignRight)

        self.setLayout(layout)

    def __on_add_pressed(self) -> None:
        """
        Performs the action associated to the add button, given the current state
        """
        self.is_creating = not self.is_creating

        if self.is_creating:
            self.add_btn.setIcon(get_icon("close"))
            self.add_btn.setToolTip(tr("btn_cancel"))

            self.delete_btn.setVisible(False)
            self.field.setVisible(True)
            self.field.setFocus()
            self.combo.setVisible(True)
            self.ok_btn.setVisible(True)
        else:
            self.field.clear()
            self.add_btn.setIcon(get_icon("add"))
            self.add_btn.setToolTip(tr("crs_create_btn_tooltip"))

            self.field.setVisible(False)
            self.combo.setVisible(False)
            self.ok_btn.setVisible(False)
            self.delete_btn.setVisible(True)

    def enable_delete_btn(self, do_enable: bool):
        """
        Enables or disables the delete button

        :param do_enable: True to enable
        """
        self.delete_btn.setEnabled(do_enable)

    def __on_field_enter(self) -> None:
        """
        Triggered when Enter key is pressed on the name field. Emits the creation signal then hides the field.
        """
        if self.field.text():
            self.sig_new_element.emit(self.field.text(), self.attr_types_dico[self.combo.currentText()])

        self.field.clear()
        self.__on_add_pressed()  # Updates the state and hides the entry field
