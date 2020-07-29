from PySide2.QtWidgets import QDialog, QGridLayout, QLabel, QPushButton
from PySide2.QtCore import Qt, QSize

from src.assets_manager import AssetManager, get_stylesheet


class VConfirmDialog(QDialog):

    def __init__(self, parent, message_key: str):
        """
        Confirm dialog for dangerous actions

        :param parent: gui's main window
        :param message_key: Key to the dictionary for the message to display
        """
        QDialog.__init__(self, parent)

        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setFixedSize(QSize(350, 80))

        self.question = QLabel(AssetManager.getInstance().get_text(message_key))
        self.question.setAlignment(Qt.AlignCenter)

        # Quit buttons
        self.ok_btn = QPushButton("Ok")
        self.ok_btn.clicked.connect(self.accept)
        self.ok_btn.setFixedSize(QSize(60, 33))

        self.cancel_btn = QPushButton("Annuler")
        self.cancel_btn.clicked.connect(self.reject)
        self.cancel_btn.setFixedSize(QSize(90, 33))

        # Layout
        layout = QGridLayout()
        layout.addWidget(self.question, 0, 0, 1, 2)
        layout.addWidget(self.ok_btn, 1, 0)
        layout.setAlignment(self.ok_btn, Qt.AlignCenter)
        layout.addWidget(self.cancel_btn, 1, 1)
        layout.setAlignment(self.cancel_btn, Qt.AlignLeft)
        self.setLayout(layout)

        self.setStyleSheet(get_stylesheet("dialog"))
