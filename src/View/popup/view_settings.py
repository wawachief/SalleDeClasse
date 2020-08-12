from PySide2.QtCore import Qt
from PySide2.QtWidgets import QDialog, QFormLayout, QLabel, QComboBox, QPushButton, QHBoxLayout, QWidget, QVBoxLayout, \
    QLineEdit, QFileDialog

from configparser import ConfigParser

from src.assets_manager import AssetManager, tr


class SettingsEditionDialog(QDialog):

    languages = {"Français": "fr",
                 "English": "en"}

    def __init__(self):
        QDialog.__init__(self)

        # Retrieve current settings
        self.settings = AssetManager.getInstance().config_to_dico(AssetManager.getInstance().get_config_parser())
        self.__restart_needed = False
        self.__restore_required = False

        # Version
        self.lab_version = QLabel(self.settings['main']['version'])

        # Language
        self.combo_language = QComboBox()
        self.combo_language.addItems(list(self.languages.keys()))
        for lang in self.languages:  # Look for the current language to select it
            if self.languages[lang] == self.settings['main']['language']:
                self.combo_language.setCurrentText(lang)
                break

        # CSV separator
        self.csv_sep_edit = QLineEdit()
        self.csv_sep_edit.setMaxLength(2)
        self.csv_sep_edit.setFixedWidth(25)
        self.csv_sep_edit.setAlignment(Qt.AlignCenter)
        self.csv_sep_edit.setText(self.settings['main']['csv_separator'])

        # BDD path
        self.btn_bdd_path = QPushButton(self.settings['main']['bdd_path'])
        self.btn_bdd_path.clicked.connect(self.choose_bdd_path)

        # --- Buttons ---

        # Confirm button
        self.ok_btn = QPushButton(tr("btn_save"))
        self.ok_btn.clicked.connect(self.accept)
        self.ok_btn.setFocus()

        # Cancel button
        self.cancel_btn = QPushButton(tr("btn_cancel"))
        self.cancel_btn.clicked.connect(self.reject)

        # Restore defaults button
        self.restore_btn = QPushButton(tr("btn_restore"))
        self.restore_btn.clicked.connect(self.__restore)

        self.__set_layout()

    def __set_layout(self) -> None:
        """
        Sets the dialog layout
        """
        # Main layout
        layout = QVBoxLayout()

        # Main section
        main_layout = QFormLayout()
        main_layout.addRow(tr("app_version"), self.lab_version)
        main_layout.addRow(tr("language"), self.combo_language)
        main_layout.addRow(tr("csv_sep"), self.csv_sep_edit)
        main_layout.addRow(tr("bdd_path"), self.btn_bdd_path)

        layout.addLayout(main_layout)
        Separator(400, layout)

        # Buttons
        layout_buttons = QHBoxLayout()
        layout_buttons.addWidget(self.ok_btn)
        layout_buttons.addWidget(self.restore_btn)
        layout_buttons.addWidget(self.cancel_btn)

        Separator(400, layout)
        layout.addLayout(layout_buttons)
        self.setLayout(layout)

    def __restore(self) -> None:
        """
        Restore default parameters before closing dialog
        """
        self.__restart_needed = True
        self.__restore_required = True
        self.accept()

    def __new_settings(self) -> dict:
        """
        Retrieves the new settings to use
        """
        settings = self.settings

        # Language
        language = self.languages[self.combo_language.currentText()]
        if language != settings['main']['language']:
            settings['main']['language'] = language
            self.__restart_needed = True

        # CSV separator
        settings['main']['csv_separator'] = self.csv_sep_edit.text()

        # BDD path
        if self.btn_bdd_path.text() != settings['main']['bdd_path']:
            settings['main']['bdd_path'] = self.btn_bdd_path.text()
            self.__restart_needed = True

        return settings

    def new_config(self) -> ConfigParser:
        """
        Retrieves the new config parser object
        """
        conf = ConfigParser()
        conf.read_dict(self.__new_settings())

        return conf

    def need_restart(self):
        return self.__restart_needed

    def restore_default(self) -> bool:
        return self.__restore_required

    def choose_bdd_path(self) -> None:
        """
        Opens a file chooser to select the bdd path. Then sets the name as button text.
        """
        bdd_path = QFileDialog.getOpenFileName(self, tr("bdd_path"), self.btn_bdd_path.text())[0]

        if bdd_path:
            self.btn_bdd_path.setText(bdd_path)


class Separator(QLabel):

    def __init__(self, width, layout: QVBoxLayout):
        """
        Separator for the config dialog
        """
        QLabel.__init__(self)

        self.setFixedHeight(3)
        self.setFixedWidth(int(width))
        self.setStyleSheet("background: QLinearGradient(x1: 0, y1: 0, x2: 1, y2: 0, "
                                   "stop: 0 #283747, stop: 0.25 #1A5276, stop: 0.5 #2980B9, "
                                   "stop: 0.75 #1A5276, stop: 1 #283747);")

        # Layout
        self.setAlignment(Qt.AlignCenter)
        layout.addWidget(self, alignment=Qt.AlignCenter)
