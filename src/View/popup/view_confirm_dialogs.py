# Salle de classe by Lecluse DevCorp
# file author : Thomas Lecluse
# Licence GPL-v3 - see LICENCE.txt
from PySide2.QtGui import QImage, QPixmap
from PySide2.QtWidgets import QDialog, QGridLayout, QLabel, QPushButton
from PySide2.QtCore import Qt, QSize
from src.assets_manager import tr, get_stylesheet


class VConfirmDialog(QDialog):

    def __init__(self, parent, message_key: str, img_path: str = None):
        """
        Confirm dialog for dangerous actions

        :param parent: gui's main window
        :param message_key: Key to the dictionary for the message to display
        """
        QDialog.__init__(self, parent)
        if img_path is None:
            self.setFixedSize(QSize(350, 120))

        self.question = QLabel(tr(message_key))
        self.question.setAlignment(Qt.AlignCenter)

        self.lab_img = None
        if img_path is not None:
            self.lab_img = QLabel()
            self.lab_img.setPixmap(QPixmap(QImage(img_path)))

        # Quit buttons
        self.ok_btn = QPushButton("Ok")
        self.ok_btn.clicked.connect(self.accept)
        self.ok_btn.setFixedSize(QSize(60, 33))

        self.cancel_btn = QPushButton(tr("btn_cancel"))
        self.cancel_btn.clicked.connect(self.reject)
        self.cancel_btn.setFixedSize(QSize(90, 33))

        # Layout
        layout = QGridLayout()
        layout.addWidget(self.question, 0, 0, 1, 2)
        if self.lab_img:
            layout.addWidget(self.lab_img, 1, 0, 1, 2)
        layout.addWidget(self.ok_btn, 2, 0, alignment=Qt.AlignCenter)
        layout.addWidget(self.cancel_btn, 2, 1, alignment=Qt.AlignCenter)
        self.setLayout(layout)

        self.setStyleSheet(get_stylesheet("dialog"))
