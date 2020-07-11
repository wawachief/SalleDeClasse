from PySide2.QtWidgets import QDialog, QFileDialog, QVBoxLayout, QComboBox
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

        self.combo_group = QComboBox()
        self.combo_group.addItems(groups)

        # Layout
        self.__set_layout()

    def __set_layout(self) -> None:
        """
        Sets this widget's layout
        """
        layout = QVBoxLayout()

        layout.addWidget(self.fileDialog)
        layout.addWidget(self.combo_group)

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

