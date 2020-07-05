from PySide2.QtWidgets import QLabel
from PySide2.QtCore import QSize, Qt


class ViewTeacherDeskLabel(QLabel):

    def __init__(self, text, bg_color):
        """
        Teacher's position in the class. Two possibilities: teacher's view are student's view.

        :param text: Label's text
        :type text: str
        :param bg_color: background color (when activated)
        :type bg_color: QColor
        """
        QLabel.__init__(self, text)

        self.setFixedSize(QSize(200, 30))
        self.setAlignment(Qt.AlignCenter)

        self.setToolTip("Position du tableau")

        self.__is_active = False
        self.__bg_color = bg_color

        self.__additionnal_style = "border-radius: 5px;"

    def paintEvent(self, event):
        """
        Paints this widget whereas it's associated meaning is active or not.
        """
        if self.__is_active:
            super().paintEvent(event)
            self.setStyleSheet(f"{self.__additionnal_style} background: {self.__bg_color};")
        else:
            self.setStyleSheet("background: transparent;")

    def activate(self, do_activate):
        """
        Activates or dis-activates this board

        :type do_activate: bool
        """
        self.__is_active = do_activate
        self.repaint()
