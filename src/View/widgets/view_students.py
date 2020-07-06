from PySide2.QtWidgets import QWidget, QListView, QVBoxLayout

from src.View.widgets.view_toolbar import ViewStudentListToolbar


class ViewStudentPanel(QWidget):

    def __init__(self, config):
        """
        Side panel dedicated to students

        :param config: application's parsed configuration
        """
        QWidget.__init__(self)

        self.config = config

        self.listview = QListView()
        self.students_toolbar = ViewStudentListToolbar(config)

        # layout
        self.__set_layout()

    def __set_layout(self):
        """
        Sets this widget's layout
        """
        layout = QVBoxLayout()
        layout.setMargin(0)

        layout.addWidget(self.students_toolbar)
        layout.addWidget(self.listview)

        self.setLayout(layout)
