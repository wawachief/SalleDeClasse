import PySide2
from PySide2.QtGui import QColor
from PySide2.QtWidgets import QTableView, QAbstractItemView, QHeaderView
from PySide2.QtCore import QAbstractTableModel, Qt, QModelIndex

import typing
import operator


class CustomTableModel(QAbstractTableModel):

    def __init__(self, parent, data_list, header):
        """
        Custom table model for the table view

        :param parent: parent table view object
        :type parent: QTableView
        :param data_list: list of objects to set in this model
        :type data_list: list
        :param header: column names
        :type header: tuple
        """
        QAbstractTableModel.__init__(self, parent)

        self.data_list = data_list
        self.header = header
        self.light_selection: list = []

        parent.setModel(self)

    def rowCount(self, parent: QModelIndex = ...) -> int:
        return len(self.data_list)

    def columnCount(self, parent: QModelIndex = ...) -> int:
        return len(self.header)

    def data(self, index: QModelIndex, role: int = ...) -> typing.Any:
        if not index.isValid():
            return None

        if role == Qt.ForegroundRole:
            d = ""  # Current data, a complete row, with columns separated by a blank space
            for i in range(len(self.header)):
                if d:
                    d += " "
                d += self.data_list[index.row()][i]

            return QColor("green") if d in self.light_selection else None

        elif role == Qt.DisplayRole:
            return self.data_list[index.row()][index.column()]

        return None

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...) -> typing.Any:
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.header[section]
        return None

    def sort(self, column: int, order: PySide2.QtCore.Qt.SortOrder = ...):
        self.layoutAboutToBeChanged.emit()
        self.data_list = sorted(self.data_list, key=operator.itemgetter(column), reverse=order != Qt.AscendingOrder)
        self.layoutChanged.emit()
        self.parent().clearSelection()

    def update_light_selection(self, light_selection: list) -> None:
        """
        Light selection items will appear with a different foreground color than regular items

        :param light_selection: items with different foreground
        """
        self.layoutAboutToBeChanged.emit()
        self.light_selection = light_selection
        self.layoutChanged.emit()


class CustomTableView(QTableView):

    def __init__(self, single_selection: bool=True):
        """
        Common TableView used in side panels

        :param single_selection: disable multi-selection (True by default)
        :type single_selection: bool
        """
        QTableView.__init__(self)
        self.verticalHeader().hide()
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSelectionMode(QAbstractItemView.SingleSelection if single_selection else QAbstractItemView.MultiSelection)
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
