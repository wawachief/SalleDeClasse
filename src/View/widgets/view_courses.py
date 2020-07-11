from PySide2.QtWidgets import QWidget, QVBoxLayout

from src.View.widgets.view_toolbar import ViewCourseListToolbar
from src.View.widgets.view_table import CustomTableModel, CustomTableView


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

        # Table
        self.tableview = CustomTableView()

        # Toolbar
        self.courses_toolbar = ViewCourseListToolbar(config)
        self.courses_toolbar.add_widget.get_prefix = self.get_new_course_prefix

        # DataModel and additional info
        self.datamodel: CustomTableModel = None  # TableView datamodel
        self.current_selection: int = None  # Stores the selected course ID
        self.items = {}  # All the displayed courses items -> {(name, topic): id, ...}

        # Signals
        self.sig_course_changed = None
        self.tableview.clicked.connect(self.on_selection_changed)

        # layout
        self.__set_layout()
        self.init_table()

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

        self.datamodel = CustomTableModel(self.tableview, data_list, ("Cours", "Discipline"))
        self.tableview.setCurrentIndex(self.datamodel.index(selection, 0))
        self.current_selection = selected_id

        self.repaint()

    def on_selection_changed(self, item):
        """
        Triggered when a click is performed in the tableview

        :param item: selected item (not used, we use the current selection, in order to retrieve the index)
        """
        idx = self.tableview.selectionModel().currentIndex()
        selected_id = self.items[(idx.sibling(idx.row(), 0).data(), idx.sibling(idx.row(), 1).data())]

        if selected_id and selected_id != self.current_selection:
            self.sig_course_changed.emit(selected_id)
            self.current_selection = selected_id

    def get_new_course_prefix(self):
        """
        Gets the prefix to use when creating a new course

        :rtype: str
        """
        current_course: str = None

        for c in self.items:
            if self.items[c] == self.current_selection:
                current_course = c[0]
                break

        if not current_course:
            return ""

        if current_course.startswith('_'):  # remove leading '_'
            current_course = current_course[1:]

        return current_course.split('_')[0] + '_'  # get the first block before any other '_' and add a default '_'