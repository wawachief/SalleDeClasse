from PySide2.QtWidgets import QWidget, QVBoxLayout
from PySide2.QtCore import Signal

from src.View.widgets.view_toolbar import ViewAttributeListToolbar
from src.View.widgets.view_table import CustomTableModel, CustomTableView

from src.assets_manager import AssetManager


class ViewAttributePanel(QWidget):

    def __init__(self):
        """
        Side panel dedicated to attributes
        """
        QWidget.__init__(self)

        # Widgets
        self.tableview = CustomTableView(False)
        self.tableview.clicked.connect(self.on_selection_changed)
        self.attributes_toolbar = ViewAttributeListToolbar()

        # DataModel and additional info
        self.datamodel: CustomTableModel = None  # TableView datamodel
        self.current_selection: int = None  # Stores the selected attribute ID
        self.attributes = {}  # All the displayed attributes items -> {(attribute_name, attribute_type): id, ...}

        # Signals
        self.sig_selection_changed: Signal = None

        # layout
        self.__set_layout()
        self.set_attributes_list([])

    def resizeEvent(self, event):
        """
        Always keep a 2/3 ratio for the first column size
        """
        self.tableview.setColumnWidth(0, int(self.width()*.66))

    def __set_layout(self) -> None:
        """
        Sets this widget's layout
        """
        layout = QVBoxLayout()
        layout.setMargin(0)

        layout.addWidget(self.attributes_toolbar)
        layout.addWidget(self.tableview)

        self.setLayout(layout)

    def set_attributes_list(self, attributes: list) -> None:
        """
        Sets the specified attributes list inside the table view. Attributes list is built that way:
        [(id, name, type), ...]

        :param attributes: attributes list
        :type attributes: list
        """
        self.datamodel = None
        self.attributes = {}
        self.tableview.clearSelection()
        data_list = []

        for id, name, type in attributes:
            data = (name, AssetManager.getInstance().get_text(type))
            self.attributes[data] = id
            data_list.append(data)

        self.datamodel = CustomTableModel(self.tableview, data_list, ("Nom", "Type"))
        self.tableview.selectionModel().selectionChanged.connect(
            lambda: self.attributes_toolbar.add_widget.enable_delete_btn(
                len(self.tableview.selectionModel().selectedRows()) > 0))

        self.repaint()

    def selected_attributes(self) -> list:
        """
        :return: list of all selected attributes IDs
        :rtype: list
        """
        attributes_ids = []

        for r in self.tableview.selectionModel().selectedRows():
            data = (self.datamodel.index(r.row(), 0).data(), self.datamodel.index(r.row(), 1).data())
            attributes_ids.append(self.attributes[data])

        return attributes_ids

    def on_selection_changed(self, item):
        """
        Triggered when the table selection changed
        """
        self.sig_selection_changed.emit()
