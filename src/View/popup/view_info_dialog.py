from PySide2.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
from PySide2.QtCore import Qt, QSize

from src.assets_manager import get_stylesheet


class VInfoDialog(QDialog):

    def __init__(self, parent, message: str):
        """
        Confirm dialog for dangerous actions

        :param parent: gui's main window
        :param message: Message to display
        """
        QDialog.__init__(self, parent)

        self.setFixedSize(QSize(350, 80))

        self.info = QLabel(message)
        self.info.setAlignment(Qt.AlignCenter)

        # Quit buttons
        self.ok_btn = QPushButton("Ok")
        self.ok_btn.clicked.connect(self.accept)
        self.ok_btn.setFixedSize(QSize(60, 33))

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.info)
        layout.addWidget(self.ok_btn)
        layout.setAlignment(self.ok_btn, Qt.AlignCenter)
        self.setLayout(layout)

        self.setStyleSheet(get_stylesheet("dialog"))
