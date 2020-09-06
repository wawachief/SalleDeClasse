# Salle de classe by Lecluse DevCorp
# file author : Thomas Lecluse
# Licence GPL-v3 - see LICENCE.txt

import typing

from PySide2.QtGui import QColor, QPixmap
from PySide2.QtWidgets import QDialog, QLabel, QPushButton, QTableView, QAbstractItemView, QHeaderView, QGridLayout, \
    QFormLayout
from PySide2.QtCore import Qt, QSize, Signal, QAbstractTableModel, QModelIndex

from src.assets_manager import get_stylesheet, get_student_img, tr

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
        self.setWindowFlag(Qt.WindowStaysOnTopHint)

        self.student = student
        self.attributes = attributes

        # Widgets
        self.std_photo = QLabel()
        self.std_photo.setPixmap(QPixmap(get_student_img(student.id)))

        self.table_attributes = QTableView()
        self.table_attributes.setFixedWidth(300)
        self.table_attributes.horizontalHeader().setStretchLastSection(True)
        self.table_attributes.horizontalHeader().hide()
        self.table_attributes.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_attributes.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table_attributes.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.table_attributes.verticalHeader().setFixedWidth(150)

        self.dm: AttributesTableModel = None
        self.attr_idx = {}  # Attributes ids to indexes -> {attr_id: attr_idx, ...}

        # Close button
        self.ok_btn = QPushButton("Ok")
        self.ok_btn.clicked.connect(self.accept)
        self.ok_btn.setFixedSize(QSize(60, 33))

        # Signals
        self.sig_attribute_edition = sig_attribute_edition
        self.table_attributes.clicked.connect(self.on_attr_clicked)

        # Layout
        std_info_layout = QFormLayout()
        std_info_layout.addRow(tr("grp_name") + " :", QLabel(student.firstname))
        std_info_layout.addRow(tr("grp_surname") + " :", QLabel(student.lastname))
        std_info_layout.addRow(tr("std_nb") + " :", QLabel(str(student.id)))

        layout = QGridLayout()
        layout.addWidget(self.std_photo, 0, 0, alignment=Qt.AlignCenter)
        layout.addLayout(std_info_layout, 0, 1, alignment=Qt.AlignCenter)
        layout.addWidget(self.table_attributes, 1, 0, 1, 2, alignment=Qt.AlignCenter)
        layout.addWidget(self.ok_btn, 2, 0, 1, 2, alignment=Qt.AlignCenter)
        self.setLayout(layout)

        self.setStyleSheet(get_stylesheet("dialog"))

        # Initialization with the given attributes
        self.attributes_updated(self.attributes)

    def attributes_updated(self, attributes: list) -> None:
        """
        Called when an attribute changed and needs to be updated in the tableview

        :param attributes: List of attributes
        """
        self.attributes = attributes

        header = [a[1] for a in attributes]  # Table Header
        data_for_model = [a[2] for a in attributes]  # Table data

        # Save indexes
        self.attr_idx = {}
        i = 0
        for attr_id, _, _ in attributes:
            self.attr_idx[attr_id] = i
            i += 1

        # Create the table model
        self.dm = AttributesTableModel(self.table_attributes, data_for_model, header)

    def on_attr_clicked(self, item) -> None:
        """
        Triggered when a cell is clicked. Emits a signal with the attribute and student ids
        """
        attr_id = None
        for a in self.attr_idx:
            if self.attr_idx[a] == item.row():
                attr_id = a

        self.sig_attribute_edition.emit(attr_id, self.student.id)


class AttributesTableModel(QAbstractTableModel):

    def __init__(self, parent: QTableView, data: list, attr_header: list):
        """
        Custom table model for the attributes table view

        :param parent: parent table view object
        :type parent: QTableView
        :param data: list of objects to set in this model
        :type data: list
        :param attr_header: rows names
        :type attr_header: list
        """
        QAbstractTableModel.__init__(self, parent)

        self.table_data = data
        self.attr_header = attr_header

        parent.setModel(self)

    def rowCount(self, parent: QModelIndex = ...) -> int:
        return len(self.attr_header)

    def columnCount(self, parent: QModelIndex = ...) -> int:
        return 1

    def data(self, index: QModelIndex, role: int = ...) -> typing.Any:
        if not index.isValid():
            return None
        d = self.table_data[index.row()]

        if role == Qt.DisplayRole:  # Cell data display
            if isinstance(d, QColor) or len(d) == 7 and d[0] == '#':
                return None  # No text for color
            return d

        elif role == Qt.BackgroundRole:  # Cell background
            if len(d) == 7 and d[0] == '#':
                return QColor(d)
            elif isinstance(d, QColor):
                return d
            return None

        elif role == Qt.ForegroundRole:  # Cell text foreground
            if isinstance(d, int) and d == 0:
                return QColor("#FF0000")  # Mark or counter is 0
            return None

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...) -> typing.Any:
        if orientation == Qt.Vertical and role == Qt.DisplayRole and section < len(self.attr_header):
            return self.attr_header[section]
        return None
