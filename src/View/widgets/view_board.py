import PySide2
from PySide2.QtWidgets import QLabel, QWidget, QHBoxLayout
from PySide2.QtCore import QSize, Qt

from src.assets_manager import tr


class ViewTeacherDeskLabel(QWidget):

    def __init__(self, text, bg_color):
        """
        Teacher's position in the class. Two possibilities: teacher's view are student's view.

        :param text: Label's text
        :type text: str
        :param bg_color: background color (when activated)
        :type bg_color: QColor
        """
        QWidget.__init__(self)

        self.setFixedSize(QSize(200, 30))

        self.label = QLabel(text)
        self.label.setToolTip(tr("perspective_tootip"))
        self.label.setStyleSheet(f"border-radius: 5px; background: {bg_color}; color: white;")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFixedSize(QSize(200, 30))

        layout = QHBoxLayout()
        layout.setMargin(0)
        layout.addWidget(self.label)
        self.setLayout(layout)

    def set_label_visible(self, b_visible: bool):
        """
        Sets the visibility state of the label

        :param b_visible: True shows the label
        """
        self.label.setVisible(b_visible)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)

        if self.label.isVisible():
            self.on_click()

    def on_click(self):
        pass
