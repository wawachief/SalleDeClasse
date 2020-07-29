from PySide2.QtWidgets import QDialog, QGridLayout, QLabel, QPushButton

from src.assets_manager import AssetManager


class VConfirmDialog(QDialog):

    def __init__(self, parent, message_key: str):
        """
        Confirm dialog for dangerous actions

        :param parent: gui's main window
        :param message_key: Key to the dictionary for the message to display
        """
        QDialog.__init__(self, parent)

        self.setWindowTitle("Confirmation")

        self.question = QLabel(AssetManager.getInstance().get_text(message_key))

        # Quit buttons
        self.ok_btn = QPushButton("Ok")
        self.ok_btn.clicked.connect(self.accept)

        self.cancel_btn = QPushButton("Annuler")
        self.cancel_btn.clicked.connect(self.reject)

        # Layout
        layout = QGridLayout()
        layout.addWidget(self.question, 0, 0, 1, 2)
        layout.addWidget(self.ok_btn, 1, 0)
        layout.addWidget(self.cancel_btn, 1, 1)
        self.setLayout(layout)
