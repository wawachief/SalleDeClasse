from PySide2.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
from PySide2.QtCore import Qt, QSize, QPoint, QRect

from src.assets_manager import get_stylesheet


class VInfoDialog(QDialog):

    def __init__(self, parent, message: str):
        """
        Confirm dialog for dangerous actions

        :param parent: gui's main window
        :param message: Message to display
        """
        QDialog.__init__(self, parent)

        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setFixedSize(QSize(350, 80))

        # Center the dialog
        rec = parent.window().windowHandle().screen().geometry()
        size = self.minimumSize()
        topLeft = QPoint((rec.width() // 2) - (size.width() // 2), (rec.height() // 2) - (size.height() // 2))
        self.setGeometry(QRect(topLeft, size))

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
