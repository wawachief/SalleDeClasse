import PySide2
from PySide2.QtWidgets import QLabel, QWidget, QComboBox, QHBoxLayout
from PySide2.QtCore import QSize, Qt

from src.assets_manager import AssetManager


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
        self.label.setToolTip(AssetManager.getInstance().get_text("perspective_tootip"))
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


class ViewTopics(QWidget):

    def __init__(self):
        """
        Widget displaying a combo with all available topics
        """
        QWidget.__init__(self)

        self.setFixedWidth(200)

        # Widgets
        self.label = QLabel(AssetManager.getInstance().get_text("select_topic"))
        self.combo = QComboBox()

        # Signal
        self.sig_topic_changed = None
        self.combo.activated.connect(self.__on_topic_changed)

        # Init
        self.current_topic: str = None
        self.topics: list = []
        self.set_topics([])

        self.__init_layout()
        self.__init_style()

    def __init_layout(self) -> None:
        """
        Sets this widget's layout: label next to combo
        """
        layout = QHBoxLayout()
        layout.setMargin(0)

        layout.addWidget(self.label)
        layout.addWidget(self.combo)

        self.setLayout(layout)

    def __init_style(self) -> None:
        """
        Inits this widget's style
        """
        self.setStyleSheet("QLabel {color: black;}")

    def set_topics(self, topics: list, selection: str=None) -> None:
        """
        Sets the given topics in the combo box

        :param topics: topics to set
        :param selection: topic selection (topic name)
        """
        self.topics = topics

        self.combo.clear()
        self.combo.addItems(self.topics)

        if selection:
            self.select_topic(selection)

        self.repaint()

    def select_topic(self, selection: str) -> None:
        """
        Selects the given topic name

        :param selection: topic selection (topic name)
        """
        self.combo.setCurrentIndex(self.topics.index(selection))

    def __on_topic_changed(self) -> None:
        """
        Triggered when the combo is activated. Emits only if the value changed
        """
        text = self.combo.currentText()
        if text != self.current_topic:
            self.current_topic = text
            self.sig_topic_changed.emit(text)
