from PySide2.QtWidgets import QDialog, QGridLayout, QComboBox, QLabel, QPushButton
from PySide2.QtCore import Qt


class VDialogEdit(QDialog):

    def __init__(self, parent, current_val):
        """
        Generic class dialog to inherit for the specifics of each edition contexts (text, color, mark or counter)

        :param parent: gui's main window
        :param current_val: current field actual value (to set by default)
        """
        QDialog.__init__(self, parent)

        self.current_val = current_val
        self.new_val = None  # Will contain the future value to use

        # Quit buttons
        self.ok_btn = QPushButton("Ok")
        self.ok_btn.clicked.connect(self.accept)

        self.cancel_btn = QPushButton("Annuler")
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
        return self.new_val


class VDlgEditText(VDialogEdit):

    def __init__(self, parent, current_val):
        """
        Text field edition dialog

        :param parent: gui's main window
        :param current_val: current field actual value (to set by default)
        """
        VDialogEdit.__init__(self, parent, current_val)


