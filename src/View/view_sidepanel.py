from PySide2.QtWidgets import QTabWidget
from PySide2.QtCore import QSize

from src.View.widgets.view_courses import ViewCoursePanel
from src.View.widgets.view_students import ViewStudentPanel
from src.View.widgets.view_attributes import ViewAttributePanel

from src.assets_manager import get_icon, get_stylesheet


class ViewSidePanel(QTabWidget):

    def __init__(self, config):
        """
        Application side panel. Contains room, groups and skills lists.

        :param config: application's parsed configuration
        """
        QTabWidget.__init__(self)

        self.config = config

        self.setMinimumSize(QSize(300, 500))

        self.setTabPosition(QTabWidget.South)
        self.setTabsClosable(False)

        self.tabBar().setIconSize(QSize(46, 46))

        # widgets
        self.courses_panel = ViewCoursePanel(config)
        self.students_panel = ViewStudentPanel(config)
        self.attributes_panel = ViewAttributePanel(config)

        # Tabs
        self.addTab(self.courses_panel, get_icon("classroom"), "")
        self.setTabToolTip(0, "Cours")
        self.addTab(self.students_panel, get_icon("magic"), "")
        self.setTabToolTip(1, "Élève")
        self.addTab(self.attributes_panel, get_icon("competence"), "")
        self.setTabToolTip(2, "Attributs")

        self.setStyleSheet(get_stylesheet("tabbar"))
