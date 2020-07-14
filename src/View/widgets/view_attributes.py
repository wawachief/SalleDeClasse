from PySide2.QtWidgets import QWidget, QListView, QVBoxLayout

from src.View.widgets.view_toolbar import ViewAttributeListToolbar


class ViewAttributePanel(QWidget):

    def __init__(self):
        """
        Side panel dedicated to attributes
        """
        QWidget.__init__(self)

        self.listview = QListView()
        self.attributes_toolbar = ViewAttributeListToolbar()

        # layout
        self.__set_layout()

    def __set_layout(self):
        """
        Sets this widget's layout
        """
        layout = QVBoxLayout()
        layout.setMargin(0)

        layout.addWidget(self.attributes_toolbar)
        layout.addWidget(self.listview)

        self.setLayout(layout)
