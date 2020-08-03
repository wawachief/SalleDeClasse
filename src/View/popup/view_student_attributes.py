from PySide2.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QTableView, QAbstractItemView
from PySide2.QtCore import Qt, QSize, Signal

from src.assets_manager import get_stylesheet

from src.Model.mod_types import Student


class VStdAttributesDialog(QDialog):

    def __init__(self, parent, sig_attribute_edition: Signal, student: Student, attributes: list):
        """
        Confirm dialog for dangerous actions

        :param parent: gui's main window
        :param sig_attribute_edition: Signal to emit in order to edit the selected attribute
        :param student: Current student
        :param attributes: List of attributes
        """
        QDialog.__init__(self, parent)

        self.setFixedSize(QSize(350, 350))

        self.student = student
        self.attributes = attributes
        self.sig_attribute_edition = sig_attribute_edition

        # Widgets
        self.std_info = QLabel(f"{student.firstname} {student.lastname}")

        self.table_attributes = QTableView()
        self.table_attributes.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_attributes.setSelectionMode(QAbstractItemView.SingleSelection)

        # Close button
        self.ok_btn = QPushButton("Ok")
        self.ok_btn.clicked.connect(self.accept)
        self.ok_btn.setFixedSize(QSize(60, 33))

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.std_info)
        layout.setAlignment(self.std_info, Qt.AlignCenter)
        layout.addWidget(self.table_attributes)
        layout.addWidget(self.ok_btn)
        layout.setAlignment(self.ok_btn, Qt.AlignCenter)
        self.setLayout(layout)

        self.setStyleSheet(get_stylesheet("dialog"))

    def attributes_updated(self, attributes: list) -> None:
        """
        Called when an attribute changed and needs to be updated in the tableview

        :param attributes: List of attributes
        """
        self.attributes = attributes
