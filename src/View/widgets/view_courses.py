import typing

from PySide2.QtWidgets import QWidget, QTableView, QVBoxLayout, QAbstractItemView, QPushButton, QHeaderView
from PySide2.QtCore import QAbstractTableModel, Qt, QModelIndex

from src.View.widgets.view_toolbar import ViewCourseListToolbar


class ViewCoursePanel(QWidget):

    def __init__(self, config, width):
        """
        Side panel dedicated to courses

        :param config: application's parsed configuration
        :param width: table default width
        :type width: int
        """
        QWidget.__init__(self)

        self.config = config
        self.default_width = width

        # Table configuration
        self.tableview = QTableView()
        self.tableview.verticalHeader().hide()
        self.tableview.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableview.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableview.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tableview.horizontalHeader().setStretchLastSection(True)
        self.tableview.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)

        # Toolbar
        self.courses_toolbar = ViewCourseListToolbar(config)

        # DataModel and additional info
        self.datamodel = None  # TableView datamodel
        self.current_selection = None  # Stores the selected course ID
        self.items = {}  # All the displayed courses items -> {(name, topic): id, ...}

        btn = QPushButton("test")
        btn.clicked.connect(self.debug)
        self.courses_toolbar.addWidget(btn)

        # Signals
        self.sig_course_changed = None
        self.tableview.clicked.connect(self.on_selection_changed)

        # layout
        self.__set_layout()
        self.init_table()

    def debug(self):
        self.init_table([(1, "A315", "Maths"), (2, "C314", "Info"), (3, "B013", "Maths")], 2)

    def __set_layout(self):
        """
        Sets this widget's layout
        """
        layout = QVBoxLayout()
        layout.setMargin(0)

        layout.addWidget(self.courses_toolbar)
        layout.addWidget(self.tableview)

        self.setLayout(layout)

    def resizeEvent(self, event):
        """
        Always keep a 2/3 ratio for the first column size
        """
        self.tableview.setColumnWidth(0, int(self.width()*.66))

    def init_table(self, list_courses=[], selected_id=None):
        """
        Inits the data_model with the specified objects list and sets it to the view.
        An object is represented like this: (course_id, course_name, topic_name)

        :param list_courses: list of objects to add
        :type list_courses: list
        :param selected_id: Id of the course to select
        :type selected_id: int
        """
        self.datamodel = None
        self.items = {}
        data_list = []
        selection = -1

        for course_id, name, topic in list_courses:
            data = (name, topic)
            self.items[data] = course_id
            data_list.append(data)

            if course_id == selected_id:
                selection = len(data_list) - 1

        self.datamodel = CustomTableModel(self.tableview, data_list)
        self.tableview.setCurrentIndex(self.datamodel.index(selection, 0))
        self.current_selection = selected_id

        self.repaint()

    def on_selection_changed(self, item):
        """
        Triggered when a click is performed in the listview

        :param item: selected item (not used, we use the current selection, in order to retrieve the index)
        """
        idx = self.tableview.selectionModel().currentIndex()
        selected_id = self.items[(idx.sibling(idx.row(), 0).data(), idx.sibling(idx.row(), 1).data())]

        if selected_id and selected_id != self.current_selection:
            self.sig_course_changed.emit(selected_id)
            self.current_selection = selected_id


class CustomTableModel(QAbstractTableModel):

    def __init__(self, parent, data_list):
        """
        Custom table model for the courses table view

        :param parent: parent table view object
        :type parent: QTableView
        :param data_list: list of objects to set in this model
        :type data_list: list
        """
        QAbstractTableModel.__init__(self, parent)

        self.data_list = data_list
        self.header = ("Cours", "Discipline")

        parent.setModel(self)

    def rowCount(self, parent: QModelIndex = ...) -> int:
        return len(self.data_list)

    def columnCount(self, parent: QModelIndex = ...) -> int:
        return len(self.header)

    def data(self, index: QModelIndex, role: int = ...) -> typing.Any:
        if not index.isValid() or role != Qt.DisplayRole:
            return None
        return self.data_list[index.row()][index.column()]

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...) -> typing.Any:
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.header[section]
        return None
