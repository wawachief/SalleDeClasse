# Salle de classe by Lecluse DevCorp
# file author : Thomas Lecluse
# Licence GPL-v3 - see LICENCE.txt

from PySide2 import QtPrintSupport
from PySide2.QtCore import Qt
from PySide2.QtGui import QPixmap
from PySide2.QtWidgets import QDialog, QLabel, QFileDialog, QVBoxLayout

from src.assets_manager import tr


class CustomPrinterDialog(QDialog):

    def __init__(self, pixmap: QPixmap):
        QDialog.__init__(self)

        self.pix = pixmap
        self.setWindowTitle(tr("save_dialog_title"))

        # Widgets
        self.fileDialog = QFileDialog(self)
        self.fileDialog.setOption(QFileDialog.DontUseNativeDialog)
        self.fileDialog.setWindowFlags(Qt.Widget)
        self.fileDialog.setNameFilter("Images (*.png)")
        self.fileDialog.selectFile(tr("default_save_name"))
        self.fileDialog.setLabelText(QFileDialog.Accept, tr("btn_save"))
        self.fileDialog.setLabelText(QFileDialog.Reject, tr("btn_cancel"))
        self.fileDialog.finished.connect(self.done)

        self.lab = QLabel()
        self.lab.setPixmap(pixmap)
        self.lab.setFixedSize(pixmap.width() // 1.8, pixmap.height() // 1.8)
        self.lab.setScaledContents(True)

        self.lab_sep = QLabel()  # Separator
        self.lab_sep.setFixedHeight(3)
        self.lab_sep.setFixedWidth(pixmap.width() // 1.3)
        self.lab_sep.setStyleSheet("background: QLinearGradient(x1: 0, y1: 0, x2: 1, y2: 0, "
                                   "stop: 0 #283747, stop: 0.25 #1A5276, stop: 0.5 #2980B9, "
                                   "stop: 0.75 #1A5276, stop: 1 #283747);")

        self.lab_blabla = QLabel(tr("save_dialog_message"))

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.lab)
        layout.setAlignment(self.lab, Qt.AlignCenter)
        layout.addWidget(self.lab_sep)
        layout.setAlignment(self.lab_sep, Qt.AlignCenter)
        layout.addWidget(self.lab_blabla)
        layout.setAlignment(self.lab_blabla, Qt.AlignCenter)
        layout.addWidget(self.fileDialog)
        layout.setAlignment(self.fileDialog, Qt.AlignCenter)
        self.setLayout(layout)

    def save_plan(self) -> None:
        """
        Saves the classroom layout at the specified location
        """
        file = self.fileDialog.selectedFiles()[0] + ".png"
        self.pix.save(file)
