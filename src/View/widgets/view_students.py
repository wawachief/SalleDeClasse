from PySide2.QtWidgets import QWidget, QVBoxLayout
from PySide2.QtCore import Qt, QModelIndex

from src.View.widgets.view_toolbar import ViewStudentListToolbar
from src.View.widgets.view_table import CustomTableModel, CustomTableView


class ViewStudentPanel(QWidget):

    def __init__(self, config):
        """
        Side panel dedicated to students

        :param config: application's parsed configuration
        """
        QWidget.__init__(self)

        self.config = config

        # Widgets
        self.tableview = CustomTableView()
        self.students_toolbar = ViewStudentListToolbar(config)

        # DataModel and additional info
        self.datamodel: CustomTableModel = None  # TableView datamodel
        self.current_selection: int = None  # Stores the selected student ID
        self.students = {}  # All the displayed students items -> {(lastname, firstname): id, ...}

        # Signals
        self.sig_student_changed = None
        self.tableview.clicked.connect(self.on_selection_changed)

        # layout
        self.__set_layout()
        self.set_students_list([])

    def resizeEvent(self, event):
        """
        Always keep a half ratio for the first column size
        """
        self.tableview.setColumnWidth(0, int(self.width()/2))

    def __set_layout(self) -> None:
        """
        Sets this widget's layout
        """
        layout = QVBoxLayout()
        layout.setMargin(0)

        layout.addWidget(self.students_toolbar)
        layout.addWidget(self.tableview)

        self.setLayout(layout)

    def on_selection_changed(self, item):
        """
        Triggered when a click is performed in the tableview

        :param item: selected item (not used, we use the current selection, in order to retrieve the index)
        """
        idx = self.tableview.selectionModel().currentIndex()
        selected_id = self.students[(idx.sibling(idx.row(), 0).data(), idx.sibling(idx.row(), 1).data())]

        if selected_id and selected_id != self.current_selection:
            self.sig_student_changed.emit(selected_id)
            self.current_selection = selected_id

    def set_students_list(self, students: list) -> None:
        """
        Sets the specified student list inside the table view

        :param students: students list
        :type students: list
        """
        self.datamodel = None
        self.students = {}
        self.current_selection = None
        self.tableview.clearSelection()
        data_list = []

        for s in students:
            data = (s.lastname, s.firstname)
            self.students[data] = s.id
            data_list.append(data)

        self.datamodel = CustomTableModel(self.tableview, data_list, ("Nom", "Prénom"))

        self.repaint()


