from PySide2.QtCore import Qt
from PySide2.QtWidgets import QDialog, QFormLayout, QLabel, QComboBox, QPushButton, QHBoxLayout, QWidget, QVBoxLayout

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

        # Confirm button
        self.ok_btn = QPushButton(tr("btn_save"))
        self.ok_btn.clicked.connect(self.accept)

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
        layout = QFormLayout()
        layout.setFormAlignment(Qt.AlignCenter)
        layout.setAlignment(Qt.AlignCenter)

        # Main section
        layout.addRow(tr("app_version"), self.lab_version)
        layout.addRow(tr("language"), self.combo_language)

        # Buttons
        layout_buttons = QHBoxLayout()
        layout_buttons.addWidget(self.ok_btn)
        layout_buttons.addWidget(self.restore_btn)
        layout_buttons.addWidget(self.cancel_btn)

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.addLayout(layout)
        main_layout.addLayout(layout_buttons)
        self.setLayout(main_layout)

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
        if language != self.settings['main']['language']:
            settings['main']['language'] = language
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

