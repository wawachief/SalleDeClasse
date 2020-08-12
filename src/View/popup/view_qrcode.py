from PySide2.QtWidgets import QDialog, QVBoxLayout, QLabel
from PySide2.QtCore import Qt
from PySide2.QtGui import QPixmap, QImage

import pyqrcode
import socket
import tempfile

from src.assets_manager import AssetManager


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
            s.connect(('8.8.8.8', 1))  # connect() for UDP doesn't send packets, this will require an internet connection

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
            layout.addWidget(self.qr)
            layout.setAlignment(self.qr, Qt.AlignCenter)
            self.setLayout(layout)
        except OSError:
            self.has_internet = False
