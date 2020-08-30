# Salle de classe by Lecluse DevCorp
# file author : Thomas Lecluse
# Licence GPL-v3 - see LICENCE.txt

from PySide2.QtWidgets import QDialog, QVBoxLayout, QLabel
from PySide2.QtCore import Qt, QSize
from PySide2.QtGui import QPixmap, QImage

import pyqrcode
import socket
import tempfile

from src.assets_manager import AssetManager, tr


class VQRCode(QDialog):

    def __init__(self, parent):
        """
        Confirm dialog for dangerous actions

        :param parent: gui's main window
        """
        QDialog.__init__(self, parent)

        # QR Code
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.has_internet = True

        try:
            s.connect(('8.8.8.8', 1))  # connect() for UDP do not send packets, this will require an internet connection

            # IP and Port
            local_ip_address = s.getsockname()[0]
            s.close()
            port = AssetManager.getInstance().config('webapp', 'port')

            # get tmp folder
            qr_path = tempfile.mktemp()

            s = f"http://{local_ip_address}:{port}/mobile"  # String which represents the QR code
            self.url = pyqrcode.create(s)  # Generate QR code
            self.url.png(qr_path, scale=6)  # Create and save the QR png file

            # Widget
            self.qr = QLabel()  # Label that contains the QR
            pix = QPixmap(QImage(qr_path))
            self.qr.setPixmap(pix)

            # Layout
            layout = QVBoxLayout()
            layout.setMargin(0)
            layout.addWidget(self.qr, alignment=Qt.AlignCenter)
            layout.addWidget(InfoToolTip("qr_tip"), alignment=Qt.AlignCenter)
            layout.addSpacing(5)
            self.setLayout(layout)

            self.setStyleSheet("background: white;")
        except OSError:
            self.has_internet = False


class InfoToolTip(QLabel):

    def __init__(self, text_key: str):
        """
        Information point that displays a tooltip when hovered

        :param text_key: tooltip text
        """
        QLabel.__init__(self, "i")
        self.setFixedSize(QSize(28, 28))
        self.setAlignment(Qt.AlignCenter)

        self.setStyleSheet("font-weight: bold; border: 1px solid transparent; border-radius: 14px; "
                           "background-color: lightblue; color: black;")

        self.setToolTip(tr(text_key))