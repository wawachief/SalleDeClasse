from PySide2.QtWidgets import QWidget, QListView, QVBoxLayout
from PySide2.QtCore import QSize

from src.View.widgets.view_toolbar import ViewCourseListToolbar


class ViewSidePanel(QWidget):

    def __init__(self, config):
        """
        Application side panel. Contains room, groups and skills lists.

        :param config: application's parsed configuration
        """
        QWidget.__init__(self)

        self.config = config

        self.setMinimumSize(QSize(300, 500))

        # widgets
        self.listview = QListView()
        self.courses_toolbar = ViewCourseListToolbar(config)

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
