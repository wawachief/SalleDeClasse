from PySide2.QtWidgets import QDialog, QGridLayout, QLineEdit, QPushButton, QTextEdit, QSpinBox, QHBoxLayout
from PySide2.QtCore import QSize, Qt

from src.assets_manager import AssetManager, tr


class VDialogEdit(QDialog):

    def __init__(self, parent, current_val: str):
        """
        Generic class dialog to inherit for the specifics of each edition contexts (text, color, mark or counter)

        :param parent: gui's main window
        :param current_val: current field actual value (to set by default)
        """
        QDialog.__init__(self, parent)

        self.setWindowTitle("Edition")
        self.setWindowFlag(Qt.WindowStaysOnTopHint)

        # Quit buttons
        self.ok_btn = QPushButton("Ok")
        self.ok_btn.clicked.connect(self.accept)

        self.cancel_btn = QPushButton(tr("btn_cancel"))
        self.cancel_btn.clicked.connect(self.reject)

        # Layout
        self.main_layout = QGridLayout()

        self.main_layout.addWidget(self.ok_btn, 10, 0)
        self.main_layout.addWidget(self.cancel_btn, 10, 1)

        self.setLayout(self.main_layout)

    def new_value(self):
        """
        Gets the new value to use for the specified cell
        """
        pass


class VDlgEditText(VDialogEdit):

    def __init__(self, parent, current_val):
        """
        Text field edition dialog

        :param parent: gui's main window
        :param current_val: current field actual value (to set by default)
        """
        VDialogEdit.__init__(self, parent, current_val)

        self.text_edit = QTextEdit()
        self.text_edit.setFixedSize(QSize(300, 100))
        self.text_edit.setPlainText(current_val)

        self.main_layout.addWidget(self.text_edit, 0, 0, 5, 2)

    def new_value(self):
        return self.text_edit.toPlainText()


class VDlgEditCounter(VDialogEdit):

    def __init__(self, parent, current_val):
        """
        Counter editor

        :param parent: gui's main window
        :param current_val: current field actual value (to set by default)
        """
        VDialogEdit.__init__(self, parent, current_val)

        self.spin_box = QSpinBox()
        self.spin_box.setMinimum(-10)
        if current_val:
            self.spin_box.setValue(int(current_val))

        self.main_layout.addWidget(self.spin_box, 0, 0, 1, 2)

    def new_value(self):
        return self.spin_box.value()


class VDlgEditMark(VDialogEdit):

    def __init__(self, parent, current_val):
        """
        Marks editor

        :param parent: gui's main window
        :param current_val: current field actual value (to set by default)
        """
        VDialogEdit.__init__(self, parent, current_val)

        self.line = QLineEdit()
        self.line.setText(current_val)

        self.main_layout.addWidget(self.line, 0, 0, 1, 2)

    def new_value(self):
        return self.line.text()


class VDlgEditColor(VDialogEdit):

    def __init__(self, parent, current_val):
        """
        Colors editor

        :param parent: gui's main window
        :param current_val: current field actual value (to set by default)
        """
        VDialogEdit.__init__(self, parent, current_val)

        self.colors = AssetManager.getInstance().config("colors", "attr_colors").split()
        self.btns = []

        layout = QHBoxLayout()

        for c in self.colors:
            b = ColorButton(c, self.__set_selection, c == current_val.upper())
            self.btns.append(b)
            layout.addWidget(b)

        self.main_layout.addLayout(layout, 0, 0, 1, 2)

    def __set_selection(self, c: str) -> None:
        """
        Calls the selection on all buttons, selects only the one with the given color, and unselects the others

        :param c: color to select
        """
        for btn in self.btns:
            btn.select(c)

    def new_value(self):
        for btn in self.btns:
            if btn.is_selected:
                return btn.color
        return ""


class ColorButton(QPushButton):

    def __init__(self, color: str, callback, selected: bool):
        """
        Button color for the Color edition

        :param color: button's background color
        :param callback: callback method with color as parameter
        :param selected: default selection
        """
        QPushButton.__init__(self)

        self.color = color.upper()
        self.is_selected = False
        self.clicked.connect(lambda: callback(self.color))

        self.select(self.color if selected else "")  # init style

    def select(self, c: str) -> None:
        """
        Changes the border of this button when it is selected

        :param c: new color to select
        """
        self.is_selected = c.upper() == self.color

        if c == self.color:
            self.setStyleSheet(f"background: {self.color}; border: 2px solid black; height: 1.5em; width: 1.5em;")
        else:
            self.setStyleSheet(f"background: {self.color}; border: none; height: 1.5em; width: 1.5em;")
