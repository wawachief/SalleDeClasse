from PySide2.QtWidgets import QDialog, QVBoxLayout, QPushButton, QLineEdit, QComboBox
from PySide2.QtCore import Qt, QSize

from src.assets_manager import get_stylesheet, AssetManager


class VTopicSelectionDialog(QDialog):

    def __init__(self, parent, topics: list, current_selection: str, course_name: str):
        """
        Topic selection dialog

        :param parent: gui's main window
        :param topics: List of available topics
        :param current_selection: Currently selected topic
        :param course_name: Current course name
        """
        QDialog.__init__(self, parent)

        self.topics = topics
        self.current_selection = current_selection

        self.setWindowTitle(course_name + " - " + AssetManager.getInstance().get_text("select_topic"))
        self.setFixedSize(QSize(300, 140))

        # Widgets
        self.combo = QComboBox()
        self.combo.addItems(self.topics)
        self.__default_selection(current_selection)

        self.new_topic_line = QLineEdit()
        self.new_topic_line.setPlaceholderText("Créer une nouvelle discipline")
        self.new_topic_line.textChanged.connect(self.__enable_combo)

        # Close button
        self.ok_btn = QPushButton("Ok")
        self.ok_btn.clicked.connect(self.accept)
        self.ok_btn.setFixedSize(QSize(60, 33))

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.combo)
        layout.setAlignment(self.combo, Qt.AlignCenter)
        layout.addWidget(self.new_topic_line)
        layout.addWidget(self.ok_btn)
        layout.setAlignment(self.ok_btn, Qt.AlignCenter)
        self.setLayout(layout)

        self.setStyleSheet(get_stylesheet("dialog"))

    def __default_selection(self, selection: str) -> None:
        """
        Selects the given value in the combo

        :param selection: item to select
        """
        if selection and selection in self.topics:
            self.combo.setCurrentIndex(self.topics.index(selection))

    def __enable_combo(self) -> None:
        """
        The topic selection combo will be enabled only if the user hasn't typed any text in the combo
        """
        self.combo.setEnabled(self.new_topic_line.text() == "")

    def new_topic(self) -> str:
        """
        Gets the current selection (or the new enetered topic if there is one)
        """
        new = self.new_topic_line.text()
        if new:
            return new

        sel = self.combo.currentText()
        if sel != self.current_selection:
            return sel

        return ""
