from PySide2.QtWidgets import QWidget, QVBoxLayout
from PySide2.QtCore import Signal, Qt

from src.View.widgets.view_toolbar import ViewAttributeListToolbar
from src.View.widgets.view_table import CustomTableModel, CustomTableView

from src.assets_manager import tr


class ViewAttributePanel(QWidget):

    def __init__(self):
        """
        Side panel dedicated to attributes
        """
        QWidget.__init__(self)

        # Widgets
        self.tableview = CustomTableView(False)
        self.tableview.setSortingEnabled(True)
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
            data = (name, tr(type))
            self.attributes[data] = id
            data_list.append(data)

        self.datamodel = CustomTableModel(self.tableview, data_list, (tr("attr_col"), tr("attr_type")))
        self.tableview.selectionModel().selectionChanged.connect(self.on_selection_changed)

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

    def on_selection_changed(self, item=None) -> None:
        """
        Enables the delete button when at least an attribute is selected and emits the selection changed signal
        """
        self.attributes_toolbar.add_widget.enable_delete_btn(self.get_selected_rows_count() > 0)

        self.sig_selection_changed.emit()

        # Call the method to enable/disable toolbar buttons
        self.attributes_selection_changed(self.get_selected_rows_count() == 1)

    def get_selected_rows_count(self) -> int:
        """
        Gets the number of selected rows
        """
        return len(self.tableview.selectionModel().selectedRows())

    def attributes_selection_changed(self, do_enable: bool) -> None:
        """
        Override to enable/disable toolbar buttons

        :param do_enable: new enable state
        """
        pass
