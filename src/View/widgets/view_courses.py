# Salle de classe by Lecluse DevCorp
# file author : Thomas Lecluse
# Licence GPL-v3 - see LICENCE.txt

from PySide2.QtCore import QModelIndex
from PySide2.QtWidgets import QWidget, QVBoxLayout

from src.View.widgets.view_toolbar import ViewCourseListToolbar
from src.View.widgets.view_table import CustomTableModel, CustomTableView
from src.View.popup.view_topic import VTopicSelectionDialog

from src.assets_manager import tr


class ViewCoursePanel(QWidget):

    def __init__(self, width):
        """
        Side panel dedicated to courses

        :param width: table default width
        :type width: int
        """
        QWidget.__init__(self)

        self.default_width = width

        # Table
        self.tableview = CustomTableView()
        self.tableview.setSortingEnabled(True)

        # Toolbar
        self.courses_toolbar = ViewCourseListToolbar()
        self.courses_toolbar.add_widget.get_prefix = self.get_new_course_prefix

        # DataModel and additional info
        self.datamodel: CustomTableModel = None  # TableView datamodel
        self.current_selection: int = None  # Stores the selected course ID
        self.items = {}  # All the displayed courses items -> {(name, topic): id, ...}
        self.topics = []  # All existing topics

        # Signals
        self.sig_course_changed = None
        self.sig_topic_changed = None
        self.tableview.clicked.connect(self.on_selection_changed)
        self.tableview.doubleClicked.connect(self.__on_double_clicked)

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

    def __on_double_clicked(self, model_index: QModelIndex):
        """
        Displays the edition dialog popup for the topic.

        The doubleClicked event is triggered after the "simple" clicked event. So this method will be called after
        the selection changed one.
        """
        if model_index.column() == 1:
            dlg = VTopicSelectionDialog(self, self.topics, self.datamodel.index(model_index.row(), 1).data(),
                                        self.datamodel.index(model_index.row(), 0).data())
            if dlg.exec_():
                new_topic = dlg.new_topic()
                if new_topic:
                    self.sig_topic_changed.emit(new_topic)

    def set_topics(self, topics: list) -> None:
        """
        Registers the given topics
        :param topics: existing topics list
        """
        self.topics = topics

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

        self.datamodel = CustomTableModel(self.tableview, data_list,
                                          (tr("crs_courses"),
                                           tr("crs_topic")))
        self.tableview.selectionModel().selectionChanged.connect(
            lambda: self.courses_toolbar.enable_delete_btn(len(self.tableview.selectionModel().selectedRows()) > 0))

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
