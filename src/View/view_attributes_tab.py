from PySide2.QtWidgets import QTableView, QAbstractItemView, QHeaderView, QWidget, QHBoxLayout
from PySide2.QtCore import QAbstractTableModel, Qt, QModelIndex, Signal
from PySide2.QtGui import QColor
import typing


class AttributesTab(QWidget):

    def __init__(self):
        """
        Widget containing the table summary of all attributes
        """
        QWidget.__init__(self)

        # Data
        self.attributes = {}  # Attributes names to ids -> {attr_name: attr_id, ...}
        self.attr_idx = {}  # Attributes ids to indexes -> {attr_id: attr_idx, ...}
        self.students = {}  # Students names to ids -> {std_name: std_id, ...}
        self.std_idx = {}  # Students ids to indexes -> {std_id: std_idx, ...}
        self.data = {}  # Attributes and students ids to cell data -> {(attr_id, std_id): cell_data, ...}

        self.dm: AttributesTableModel = None

        # Widget
        self.table_attributes = QTableView()
        self.table_attributes.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_attributes.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table_attributes.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.table_attributes.verticalHeader().setFixedWidth(150)

        # Signals
        self.table_attributes.clicked.connect(self.on_cell_clicked)
        self.sig_cell_clicked: Signal = None

        # Layout
        self.__set_layout()

        self.set_data([], [], {})

    def __set_layout(self) -> None:
        layout = QHBoxLayout()
        layout.setSpacing(0)

        layout.addWidget(self.table_attributes)

        self.setLayout(layout)

    def set_data(self, attributes_data: list, students_data: list, data: dict) -> None:
        """
        Sets the data inside the table

        :param attributes_data: Attributes list (needs to be ordered) = [(attr_id, attr_name), ...]
        :param students_data: Students list (needs to be ordered) = [(std_id, std_name), ...]
        :param data: Table's data {(attr_id, std_id}: cell_data, ...}
        """
        self.attributes = {}
        self.attr_idx = {}
        i = 0
        for attr_id, attr_name in attributes_data:
            self.attributes[attr_name] = attr_id
            self.attr_idx[attr_id] = i
            i += 1

        self.students = {}
        self.std_idx = {}
        i = 0
        for std_id, std_name in students_data:
            self.students[std_name] = std_id
            self.std_idx[std_id] = i
            i += 1

        self.data = data
        attr_header = [a[1] for a in attributes_data]
        std_header = [s[1] for s in students_data]

        data_for_model = []
        for _ in range(len(std_header)):
            data_for_model.append([None] * len(attr_header))

        for attr_id, std_id in data:
            data_for_model[self.std_idx[std_id]][self.attr_idx[attr_id]] = data[(attr_id, std_id)]

        self.dm = AttributesTableModel(self.table_attributes, data_for_model, attr_header, std_header)

    def on_cell_clicked(self, item) -> None:
        """
        Triggered when a cell is clicked. Emits a signal with the attribute and student ids
        """
        attr_id = None
        for a in self.attr_idx:
            if self.attr_idx[a] == item.column():
                attr_id = a

        std_id = None
        for s in self.std_idx:
            if self.std_idx[s] == item.row():
                std_id = s

        self.sig_cell_clicked.emit(attr_id, std_id)


class AttributesTableModel(QAbstractTableModel):

    def __init__(self, parent: QTableView, data: list, attr_header: list, std_header: list):
        """
        Custom table model for the attributes table view

        :param parent: parent table view object
        :type parent: QTableView
        :param data: list of objects to set in this model
        :type data: list
        :param attr_header: column names
        :type attr_header: list
        :param std_header: row names
        :type std_header: list
        """
        QAbstractTableModel.__init__(self, parent)

        self.table_data = data
        self.attr_header = attr_header
        self.std_header = std_header

        parent.setModel(self)

    def rowCount(self, parent: QModelIndex = ...) -> int:
        return len(self.std_header)

    def columnCount(self, parent: QModelIndex = ...) -> int:
        return len(self.attr_header)

    def data(self, index: QModelIndex, role: int = ...) -> typing.Any:
        if not index.isValid():
            return None
        d = self.table_data[index.row()][index.column()]

        if role == Qt.DisplayRole:  # Cell data display
            if isinstance(d, QColor):
                return None  # No text for color
            return d

        elif role == Qt.BackgroundRole:  # Cell background
            if isinstance(d, QColor):
                return d
            return None

        elif role == Qt.ForegroundRole:  # Cell text foreground
            if isinstance(d, int) and d == 0:
                return QColor("#FF0000")  # Mark or counter is 0
            return None

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...) -> typing.Any:
        if orientation == Qt.Horizontal and role == Qt.DisplayRole and section < len(self.attr_header):
            return self.attr_header[section]
        elif orientation == Qt.Vertical and role == Qt.DisplayRole and section < len(self.std_header):
            return self.std_header[section]
        return None
