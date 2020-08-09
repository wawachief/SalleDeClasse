from PySide2.QtWidgets import QWidget, QVBoxLayout
from PySide2.QtCore import QModelIndex

from src.View.widgets.view_toolbar import ViewStudentListToolbar
from src.View.widgets.view_table import CustomTableModel, CustomTableView

from src.assets_manager import tr


class ViewStudentPanel(QWidget):

    def __init__(self):
        """
        Side panel dedicated to students
        """
        QWidget.__init__(self)

        # Widgets
        self.tableview = CustomTableView(False)
        self.tableview.doubleClicked.connect(self.__on_double_clicked)
        self.students_toolbar = ViewStudentListToolbar()

        # DataModel and additional info
        self.datamodel: CustomTableModel = None  # TableView datamodel
        self.students = {}  # All the displayed students items -> {(lastname, firstname): id, ...}

        # layout
        self.__set_layout()
        self.set_students_list([])

    def resizeEvent(self, event):
        """
        Always keep a half ratio for the first column size
        """
        self.tableview.setColumnWidth(0, int(self.width()/2))

    def __on_double_clicked(self, model_index: QModelIndex):
        """
        Displays the creation field in order to edit the double-clicked student
        """
        data = (self.datamodel.index(model_index.row(), 0).data(), self.datamodel.index(model_index.row(), 1).data())
        self.students_toolbar.edit_student(self.students[data], data[0] + " " + data[1])

    def __set_layout(self) -> None:
        """
        Sets this widget's layout
        """
        layout = QVBoxLayout()
        layout.setMargin(0)

        layout.addWidget(self.students_toolbar)
        layout.addWidget(self.tableview)

        self.setLayout(layout)

    def set_students_list(self, students: list) -> None:
        """
        Sets the specified student list inside the table view

        :param students: students list
        :type students: list
        """
        self.datamodel = None
        self.students = {}
        self.tableview.clearSelection()
        data_list = []

        for s in students:
            data = (s.lastname, s.firstname)
            self.students[data] = s.id
            data_list.append(data)

        self.datamodel = CustomTableModel(self.tableview, data_list,
                                          (tr("grp_surname"),
                                           tr("grp_name")))

        self.repaint()

    def selected_students(self) -> list:
        """
        :return: list of all selected students IDs
        :rtype: list
        """
        students_ids = []

        for r in self.tableview.selectionModel().selectedRows():
            data = (self.datamodel.index(r.row(), 0).data(), self.datamodel.index(r.row(), 1).data())
            students_ids.append(self.students[data])

        return students_ids
