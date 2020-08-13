# Salle de classe by Lecluse DevCorp
# file author : Thomas Lecluse
# Licence GPL-v3 - see LICENCE.txt

from PySide2.QtWidgets import QTabWidget
from PySide2.QtCore import QSize

from src.View.widgets.view_courses import ViewCoursePanel
from src.View.widgets.view_students import ViewStudentPanel
from src.View.widgets.view_attributes_list import ViewAttributePanel

from src.assets_manager import get_icon, get_stylesheet, tr


class ViewSidePanel(QTabWidget):

    def __init__(self):
        """
        Application side panel. Contains room, groups and skills lists.

        :param config: application's parsed configuration
        """
        QTabWidget.__init__(self)

        self.setMinimumSize(QSize(300, 500))

        self.setTabPosition(QTabWidget.South)
        self.setTabsClosable(False)

        self.tabBar().setIconSize(QSize(46, 46))

        # widgets
        self.courses_panel = ViewCoursePanel(self.minimumWidth())
        self.students_panel = ViewStudentPanel()
        self.attributes_panel = ViewAttributePanel()

        # Tabs
        self.addTab(self.courses_panel, get_icon("classroom"), "")
        self.setTabToolTip(0, tr("crs_tab_tooltip"))
        self.addTab(self.students_panel, get_icon("magic"), "")
        self.setTabToolTip(1, tr("grp_tab_tooltip"))
        self.addTab(self.attributes_panel, get_icon("competence"), "")
        self.setTabToolTip(2, tr("attr_tab_tooltip"))

        self.setStyleSheet(get_stylesheet("tabbar"))
