from PySide2.QtWidgets import QDialog, QFileDialog, QGridLayout, QComboBox, QLabel
from PySide2.QtCore import Qt

from src.assets_manager import tr, get_stylesheet


class DialogImportCsv(QDialog):
    def __init__(self, parent, groups: list):
        """
        Displays a Dialog with a file chooser for the .csv to import and a group selection combo.

        :param parent: MainApplication
        """
        QDialog.__init__(self, parent)

        self.setWindowTitle(tr("grp_action_import_csv"))

        # Widgets
        self.fileDialog = QFileDialog(self)
        self.fileDialog.setOption(QFileDialog.DontUseNativeDialog)
        self.fileDialog.setWindowFlags(Qt.Widget)
        self.fileDialog.setNameFilter("Fichiers excel (*.csv)")
        self.fileDialog.finished.connect(self.done)

        self.lab_sep = QLabel()  # Separator
        self.lab_sep.setFixedHeight(3)
        self.lab_sep.setStyleSheet(get_stylesheet("separator"))

        self.lab_group = QLabel(tr("add_to_group"))

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

