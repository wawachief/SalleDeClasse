from PySide2 import QtPrintSupport
from PySide2.QtCore import Qt, QSize
from PySide2.QtGui import QPixmap
from PySide2.QtWidgets import QDialog, QLabel, QFileDialog, QPushButton, QGridLayout

from src.assets_manager import tr


class CustomPrinterDialog(QDialog):

    def __init__(self, pixmap: QPixmap):
        QDialog.__init__(self)

        self.pix = pixmap

        # Widgets
        self.lab = QLabel()
        self.lab.setPixmap(pixmap)
        self.lab.setScaledContents(True)

        self.save_btn = QPushButton(tr("btn_save"))
        self.save_btn.clicked.connect(self.on_save)
        self.print_btn = QPushButton(tr("btn_print"))
        self.print_btn.clicked.connect(self.on_print)

        # Layout
        layout = QGridLayout()
        layout.addWidget(self.lab, 0, 0, 1, 2)
        layout.setAlignment(self.lab, Qt.AlignCenter)
        layout.addWidget(self.save_btn, 1, 0)
        layout.setAlignment(self.save_btn, Qt.AlignCenter)
        layout.addWidget(self.print_btn, 1, 1)
        layout.setAlignment(self.print_btn, Qt.AlignCenter)
        self.setLayout(layout)

    def on_save(self) -> None:
        """
        Displays a save dialog to save the preview
        """
        file_name = QFileDialog.getSaveFileName(self, tr("btn_save"), "plan_de_classe.png", "Images (*.png)")[0]
        if file_name:
            self.pix.save(file_name)

        self.close()

    def on_print(self) -> None:
        """
        Displays the native print dialog to print the preview
        """
        printer = QtPrintSupport.QPrinter()

        dlg = QtPrintSupport.QPrintDialog(printer, self.lab)
        if dlg.exec_():
            self.lab.render(printer)

        self.close()
