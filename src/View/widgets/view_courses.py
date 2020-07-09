from PySide2.QtWidgets import QWidget, QListView, QVBoxLayout, QAbstractItemView
from PySide2.QtGui import QStandardItemModel, QStandardItem

from src.View.widgets.view_toolbar import ViewCourseListToolbar


class ViewCoursePanel(QWidget):

    def __init__(self, config):
        """
        Side panel dedicated to courses

        :param config: application's parsed configuration
        """
        QWidget.__init__(self)

        self.config = config

        self.listview = QListView()
        self.listview.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.listview.setSelectionMode(QAbstractItemView.SingleSelection)
        self.datamodel = QStandardItemModel(self.listview)

        self.courses_toolbar = ViewCourseListToolbar(config)

        self.init_table()

        self.current_selection = None

        # Signals
        self.sig_course_changed = None
        self.listview.clicked.connect(self.on_selection_changed)

        # layout
        self.__set_layout()

    def __set_layout(self):
        """
        Sets this widget's layout
        """
        layout = QVBoxLayout()
        layout.setMargin(0)

        layout.addWidget(self.courses_toolbar)
        layout.addWidget(self.listview)

        self.setLayout(layout)

    def init_table(self, list_courses=[]):
        """
        Inits the data_model with the specified objects list and sets it to the view

        :param list_courses: list of objects to add
        :type list_courses: list
        """
        self.datamodel.clear()

        for c in list_courses:
            self.add(c)

        self.listview.setModel(self.datamodel)

    def on_selection_changed(self, item):
        """
        Triggered when a click is performed in the listview

        :param item: selected item
        """
        text = item.data()

        if text and text != self.current_selection:
            self.sig_course_changed.emit(text)
            self.current_selection = text

    def select_last(self):
        """
        Select the last row of the model. This is triggered after a new item creation
        """
        self.listview.setCurrentIndex(self.datamodel.index(self.datamodel.rowCount() - 1, 0))
        self.current_selection = self.datamodel.item(self.datamodel.rowCount() - 1, 0).text()

    def add(self, value):
        """
        Adds a course to the list view

        :param value: value to add
        :type value: str
        """
        self.datamodel.appendRow(QStandardItem(value))
