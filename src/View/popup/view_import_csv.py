from PySide2.QtWidgets import QDialog, QFileDialog, QGridLayout, QComboBox, QLabel
from PySide2.QtCore import Qt


class DialogImportCsv(QDialog):
    def __init__(self, parent, groups: list):
        """
        Displays a Dialog with a file chooser for the .csv to import and a group selection combo.

        :param parent: MainApplication
        """
        QDialog.__init__(self, parent)

        self.setWindowTitle("Import Pronote")

        # Widgets
        self.fileDialog = QFileDialog(self)
        self.fileDialog.setOption(QFileDialog.DontUseNativeDialog)
        self.fileDialog.setWindowFlags(Qt.Widget)
        self.fileDialog.setNameFilter("Fichiers excel (*.csv)")
        self.fileDialog.finished.connect(self.done)

        self.lab_sep = QLabel()  # Separator
        self.lab_sep.setFixedHeight(3)
        self.lab_sep.setStyleSheet("background: QLinearGradient(x1: 0, y1: 0, x2: 1, y2: 0, "
                                   "stop: 0 #283747, stop: 0.25 #1A5276, stop: 0.5 #2980B9, "
                                   "stop: 0.75 #1A5276, stop: 1 #283747);")

        self.lab_group = QLabel("Ajouter au groupe :")

        self.combo_group = QComboBox()
        self.combo_group.addItems(groups)
        self.combo_group.setFixedWidth(200)

        # Layout
        self.__set_layout()

    def __set_layout(self) -> None:
        """
        Sets this widget's layout
        """
        layout = QGridLayout()

        layout.addWidget(self.fileDialog, 0, 0, 1, 2)
        layout.addWidget(self.lab_sep, 1, 0, 1, 2)
        layout.addWidget(self.lab_group, 2, 0, alignment=Qt.AlignRight)
        layout.addWidget(self.combo_group, 2, 1, alignment=Qt.AlignLeft)

        self.setLayout(layout)

    def selected_group(self) -> str:
        """
        :return: The selected group
        """
        return self.combo_group.currentText()

    def selected_file(self) -> str:
        """
        :return: Selected file (absolute) path
        """
        return self.fileDialog.selectedFiles()[0]

