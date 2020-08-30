# Salle de classe by Lecluse DevCorp
# file author : Thomas Lecluse
# Licence GPL-v3 - see LICENCE.txt

from PySide2.QtCore import Qt, QSize
from PySide2.QtGui import QColor
from PySide2.QtWidgets import QDialog, QFormLayout, QLabel, QComboBox, QPushButton, QHBoxLayout, QWidget, QVBoxLayout, \
    QLineEdit, QFileDialog, QSpinBox, QColorDialog, QGridLayout

from configparser import ConfigParser

from src.assets_manager import AssetManager, tr, COLOR_DICT, get_stylesheet, get_icon


class SettingsEditionDialog(QDialog):

    languages = {"Français": "fr",
                 "English": "en"}

    def __init__(self):
        QDialog.__init__(self)

        self.setWindowTitle(tr("btn_config"))
        self.setFixedSize(QSize(700, 675))

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

        # Port
        self.wepapp_port = QSpinBox()
        self.wepapp_port.setMinimum(1024)
        self.wepapp_port.setMaximum(65535)
        self.wepapp_port.setValue(int(self.settings['webapp']['port']))

        # Colors
        self.tile_color = ColorChooser(self.settings['colors']['tile'])
        self.hovered_tile_color = ColorChooser(self.settings['colors']['hovered_tile'])
        self.hovered_empty_tile_color = ColorChooser(self.settings['colors']['hovered_empty_tile'])
        self.dragged_tile_color = ColorChooser(self.settings['colors']['dragged_tile'])
        self.drag_selected_tile_color = ColorChooser(self.settings['colors']['drag_selected_tile'])
        self.selected_tile_color = ColorChooser(self.settings['colors']['selected_tile'])
        self.tile_text_color = ColorChooser(self.settings['colors']['tile_text'])
        self.room_bg_color = ColorChooser(self.settings['colors']['room_bg'])
        self.room_grid_color = ColorChooser(self.settings['colors']['room_grid'])
        self.main_bg_color = ColorChooser(self.settings['colors']['main_bg'])
        self.board_bg_color = ColorChooser(self.settings['colors']['board_bg'])

        self.attr_colors = ""  # Chosen colors
        self.attributes_colors_chooser = AttrColorsChooser(self.settings['colors']['attr_colors'].split())

        # Sizes
        # Desk sizes
        self.desk_size_x = QSpinBox()
        self.desk_size_x.setMinimum(10)
        self.desk_size_x.setMaximum(200)
        self.desk_size_x.setValue(int(self.settings['size']['desk_x']))
        self.desk_size_x.setFixedWidth(50)

        self.desk_size_y = QSpinBox()
        self.desk_size_y.setMinimum(10)
        self.desk_size_y.setMaximum(200)
        self.desk_size_y.setValue(int(self.settings['size']['desk_y']))
        self.desk_size_y.setFixedWidth(50)

        # Font size
        self.desk_font_size = QSpinBox()
        self.desk_font_size.setMinimum(4)
        self.desk_font_size.setValue(int(self.settings['size']['font_size']))
        self.desk_font_size.setFixedWidth(50)

        # Grid rows
        self.grid_rows = QSpinBox()
        self.grid_rows.setMinimum(1)
        self.grid_rows.setMaximum(40)
        self.grid_rows.setValue(int(self.settings['size']['default_room_rows']))
        self.grid_rows.setFixedWidth(50)

        # Grid columns
        self.grid_cols = QSpinBox()
        self.grid_cols.setMinimum(1)
        self.grid_cols.setMaximum(40)
        self.grid_cols.setValue(int(self.settings['size']['default_room_columns']))
        self.grid_cols.setFixedWidth(50)

        # --- Buttons ---

        # Confirm button
        self.ok_btn = QPushButton(tr("btn_save"))
        self.ok_btn.clicked.connect(self.accept)
        self.ok_btn.setFixedWidth(200)
        self.ok_btn.setFocus()

        # Cancel button
        self.cancel_btn = QPushButton(tr("btn_cancel"))
        self.cancel_btn.clicked.connect(self.reject)
        self.cancel_btn.setFixedWidth(200)

        # Restore defaults button
        self.restore_btn = QPushButton(tr("btn_restore"))
        self.restore_btn.clicked.connect(self.__restore)
        self.restore_btn.setFixedWidth(200)

        self.__set_layout()

    def __set_layout(self) -> None:
        """
        Sets the dialog layout
        """
        # Main layout
        layout = QVBoxLayout()
        layout.setMargin(0)
        layout.addSpacing(5)

        # Main section
        main_layout = SettingsFormLayout()
        main_layout.addRow(tr("app_version"), self.lab_version)
        main_layout.addRow(tr("language"), self.combo_language)
        main_layout.addRow(tr("csv_sep"), self.csv_sep_edit)
        main_layout.addRow(tr("bdd_path"), self.btn_bdd_path)

        # Web app
        widget_port = QWidget()
        layout_port = QHBoxLayout()
        layout_port.setMargin(0)
        layout_port.addWidget(self.wepapp_port)
        layout_port.addWidget(WarningToolTip("shutdown_required"))
        widget_port.setLayout(layout_port)
        main_layout.addRow(tr("web_port"), widget_port)

        layout.addLayout(main_layout)
        Separator(self.width(), layout)

        # Colors
        colors_layout1 = SettingsFormLayout()
        colors_layout1.addRow(tr("tile"), self.tile_color)
        colors_layout1.addRow(tr("hovered_tile"), self.hovered_tile_color)
        colors_layout1.addRow(tr("hovered_empty_tile"), self.hovered_empty_tile_color)
        colors_layout1.addRow(tr("dragged_tile"), self.dragged_tile_color)
        colors_layout1.addRow(tr("drag_selected_tile"), self.drag_selected_tile_color)
        colors_layout1.addRow(tr("selected_tile"), self.selected_tile_color)

        colors_layout2 = SettingsFormLayout()
        colors_layout2.addRow(tr("tile_text"), self.tile_text_color)
        colors_layout2.addRow(tr("room_bg"), self.room_bg_color)
        colors_layout2.addRow(tr("room_grid"), self.room_grid_color)
        colors_layout2.addRow(tr("main_bg"), self.main_bg_color)
        colors_layout2.addRow(tr("board_bg"), self.board_bg_color)

        colors_layout = QHBoxLayout()
        colors_layout.setMargin(0)
        colors_layout.addLayout(colors_layout1)
        colors_layout.addLayout(colors_layout2)

        layout.addLayout(colors_layout)
        layout.addSpacing(15)

        colors_layout3 = SettingsFormLayout()
        colors_layout3.setMargin(0)
        colors_layout3.addRow(tr("attr_colors"), self.attributes_colors_chooser)
        layout.addLayout(colors_layout3)

        Separator(self.width(), layout)

        # size data
        sizes_layout = SettingsFormLayout()
        sizes_layout.setMargin(0)

        widget_desk = QWidget()
        layout_desk = QHBoxLayout()
        layout_desk.setMargin(0)
        layout_desk.addWidget(self.desk_size_x)
        layout_desk.addWidget(self.desk_size_y)
        layout_desk.addWidget(WarningToolTip("dangerous_parameter"))
        widget_desk.setLayout(layout_desk)
        sizes_layout.addRow(tr("desk_size"), widget_desk)

        sizes_layout.addRow(tr("font_size"), self.desk_font_size)

        widget_rows = QWidget()
        layout_rows = QHBoxLayout()
        layout_rows.setMargin(0)
        layout_rows.addWidget(self.grid_rows)
        layout_rows.addWidget(WarningToolTip("dangerous_parameter"))
        widget_rows.setLayout(layout_rows)
        sizes_layout.addRow(tr("grid_rows"), widget_rows)

        widget_cols = QWidget()
        layout_cols = QHBoxLayout()
        layout_cols.setMargin(0)
        layout_cols.addWidget(self.grid_cols)
        layout_cols.addWidget(WarningToolTip("dangerous_parameter"))
        widget_cols.setLayout(layout_cols)
        sizes_layout.addRow(tr("grid_cols"), widget_cols)

        layout.addLayout(sizes_layout)

        Separator(self.width(), layout)

        # Buttons
        layout_buttons = QHBoxLayout()
        layout_buttons.addWidget(self.ok_btn)
        layout_buttons.addWidget(self.restore_btn)
        layout_buttons.addWidget(self.cancel_btn)

        layout.addLayout(layout_buttons)
        layout.addSpacing(5)
        self.setLayout(layout)

        self.setStyleSheet(get_stylesheet("dialog2"))

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
            if self.btn_bdd_path.text().endswith("sdc_db"):
                settings['main']['bdd_path'] = self.btn_bdd_path.text()
            else:
                settings['main']['bdd_path'] = ""
            self.__restart_needed = True

        # Port
        if str(self.wepapp_port.value()) != settings['webapp']['port']:
            settings['webapp']['port'] = str(self.wepapp_port.value())

        # Colors
        settings['colors']['tile'] = self.tile_color.get_color()
        settings['colors']['hovered_tile'] = self.hovered_tile_color.get_color()
        settings['colors']['hovered_empty_tile'] = self.hovered_empty_tile_color.get_color()
        settings['colors']['dragged_tile'] = self.dragged_tile_color.get_color()
        settings['colors']['drag_selected_tile'] = self.drag_selected_tile_color.get_color()
        settings['colors']['selected_tile'] = self.selected_tile_color.get_color()
        settings['colors']['tile_text'] = self.tile_text_color.get_color()
        settings['colors']['room_grid'] = self.room_grid_color.get_color()

        if self.room_bg_color.get_color() != settings['colors']['room_bg']:
            settings['colors']['room_bg'] = self.room_bg_color.get_color()
            self.__restart_needed = True

        if self.main_bg_color.get_color() != settings['colors']['main_bg']:
            settings['colors']['main_bg'] = self.main_bg_color.get_color()
            self.__restart_needed = True

        if self.board_bg_color.get_color() != settings['colors']['board_bg']:
            settings['colors']['board_bg'] = self.board_bg_color.get_color()
            self.__restart_needed = True

        settings['colors']['attr_colors'] = self.attr_colors

        # Size settings

        if str(self.desk_size_x.value()) != settings['size']['desk_x']:
            settings['size']['desk_x'] = str(self.desk_size_x.value())
            self.__restart_needed = True
        if str(self.desk_size_y.value()) != settings['size']['desk_y']:
            settings['size']['desk_y'] = str(self.desk_size_y.value())
            self.__restart_needed = True
        if str(self.desk_font_size.value()) != settings['size']['font_size']:
            settings['size']['font_size'] = str(self.desk_font_size.value())
            self.__restart_needed = False
        if str(self.grid_rows.value()) != settings['size']['default_room_rows']:
            settings['size']['default_room_rows'] = str(self.grid_rows.value())
            self.__restart_needed = True
        if str(self.grid_cols.value()) != settings['size']['default_room_columns']:
            settings['size']['default_room_columns'] = str(self.grid_cols.value())
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

    def accept(self) -> None:
        """
        Performs actions before calling parent's accept method
        """
        self.attr_colors = self.attributes_colors_chooser.get_colors_to_str()
        super().accept()

    def choose_bdd_path(self) -> None:
        """
        Opens a file chooser to select the bdd path. Then sets the name as button text.
        """
        bdd_path = QFileDialog.getOpenFileName(self, tr("bdd_path"), self.btn_bdd_path.text())[0]

        if bdd_path:
            self.btn_bdd_path.setText(bdd_path)


class SettingsFormLayout(QFormLayout):

    def __init__(self):
        """
        Custom form layout with common initialization
        """
        QFormLayout.__init__(self)
        self.setRowWrapPolicy(QFormLayout.DontWrapRows)
        self.setFieldGrowthPolicy(QFormLayout.FieldsStayAtSizeHint)
        self.setFormAlignment(Qt.AlignHCenter | Qt.AlignTop)
        self.setLabelAlignment(Qt.AlignRight)


class WarningToolTip(QLabel):

    def __init__(self, text_key: str):
        """
        Information point that displays a tooltip when hovered

        :param text_key: tooltip text
        """
        QLabel.__init__(self, "i")
        self.setFixedSize(QSize(20, 20))
        self.setAlignment(Qt.AlignCenter)

        self.setStyleSheet("font-weight: bold; border: 1px solid transparent; border-radius: 10px; "
                           "background-color: orange; color: black;")

        self.setToolTip(tr(text_key))


class Separator(QLabel):

    def __init__(self, width, layout: QVBoxLayout):
        """
        Separator for the config dialog
        """
        QLabel.__init__(self)

        self.setFixedHeight(3)
        self.setFixedWidth(int(width))
        self.setStyleSheet(get_stylesheet("separator"))

        # Layout
        self.setAlignment(Qt.AlignCenter)
        layout.addWidget(self, alignment=Qt.AlignCenter)


class AttrColorsChooser(QWidget):

    MAX_COLORS = 6
    MIN_COLORS = 2
    DEFAULT_COLOR = "#FFFFFF"

    def __init__(self, available_colors: list):
        """
        Widget allowing the user to create between 2 and 6 colors for the Colors typed attributes

        :param available_colors: existing colors to initialize
        """
        QWidget.__init__(self)

        # Widgets
        self.__add_btn = QPushButton()
        self.__add_btn.setIcon(get_icon("add"))
        self.__add_btn.setIconSize(QSize(35, 35))
        self.__add_btn.setToolTip(tr("crs_create_btn_tooltip"))
        self.__add_btn.clicked.connect(self.__add_color)
        self.__add_btn.setStyleSheet("border: none;")

        self.__delete_btn = QPushButton()
        self.__delete_btn.setIcon(get_icon("del"))
        self.__delete_btn.setIconSize(QSize(35, 35))
        self.__delete_btn.setToolTip(tr("btn_suppr"))
        self.__delete_btn.clicked.connect(self.__remove_color)
        self.__delete_btn.setStyleSheet("border: none;")

        self.__btns = []

        for c in available_colors:  # Fill in existing colors
            self.__btns.append(ColorChooser(c, False))

        for i in range(AttrColorsChooser.MAX_COLORS - len(available_colors)):  # Complete with 'empty' colors
            self.__btns.append(ColorChooser(AttrColorsChooser.DEFAULT_COLOR, False))  # Use white as default color
            self.__btns[-1].setVisible(False)

        if len(available_colors) <= AttrColorsChooser.MIN_COLORS:
            self.__delete_btn.setEnabled(False)

            # Displays at least the minimum of buttons
            for i in range(AttrColorsChooser.MIN_COLORS):
                self.__btns[i].setVisible(True)

        elif len(available_colors) >= AttrColorsChooser.MAX_COLORS:
            self.__add_btn.setEnabled(False)

        # Layout
        layout = QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(self.__delete_btn, 0, 0, 2, 1)
        r, c = 0, 1
        for b in self.__btns:
            layout.addWidget(b, r, c)

            c += 1
            if c == 4:
                r, c = 1, 1

        layout.addWidget(self.__add_btn, 0, 4, 2, 1)

        self.setLayout(layout)

    def __add_color(self) -> None:
        """
        Adds a color (at the end)
        """
        n = self.__nb_colors()
        if n < AttrColorsChooser.MAX_COLORS:
            self.__btns[n].setVisible(True)

            if n == AttrColorsChooser.MAX_COLORS - 1:
                self.__add_btn.setEnabled(False)
            self.__delete_btn.setEnabled(True)  # If we were able to add a button, we can then remove it

        self.repaint()

    def __remove_color(self) -> None:
        """
        Removes a color (at the end)
        """
        n = self.__nb_colors()
        if n > AttrColorsChooser.MIN_COLORS:
            self.__btns[n-1].setVisible(False)

            if n == AttrColorsChooser.MIN_COLORS + 1:
                self.__delete_btn.setEnabled(False)
            self.__add_btn.setEnabled(True)  # If we were able to remove a button, we can then add it

        self.repaint()

    def __nb_colors(self) -> int:
        """
        Gets the number of visible colors
        """
        return len([btn for btn in self.__btns if btn.isVisible()])

    def get_colors(self) -> list:
        """
        Gets the list of all colors used for attributes
        """
        return [btn.get_color() for btn in self.__btns if btn.isVisible()]

    def get_colors_to_str(self) -> str:
        """
        Gets the list of all colors in a string, with blank spaces separating colors
        """
        c = ""
        for color in self.get_colors():
            if c:
                c += " "
            c += color
        return c


class ColorChooser(QWidget):

    def __init__(self, default_color: str, show_pretty_name: bool=True):
        """
        Color chooser widget

        :param default_color: current color to set
        :param show_pretty_name: shows the pretty name of the color next to its hexa value
        """
        QWidget.__init__(self)

        # Convert 'regular' name colors into QColor to retrieve their hexa code
        self.color = QColor(default_color).name().lower()
        self.show_pretty_name = show_pretty_name

        # Widgets
        self.lab = QLabel()
        self.lab.setStyleSheet("color: black; font-style: italic;")

        self.btn = QPushButton(self.color.upper())
        self.btn.clicked.connect(self.__change_color)

        # Layout
        layout = QHBoxLayout()
        layout.setMargin(0)
        layout.addWidget(self.btn)
        if self.show_pretty_name:
            layout.addWidget(self.lab)
        self.setLayout(layout)

        self.update_bg()

    def update_bg(self) -> None:
        """
        Updates the background color given the button's name and looks for the color's display name
        """
        self.btn.setStyleSheet(f"background: {self.btn.text()}; color: black;")

        if self.btn.text().lower() in COLOR_DICT:
            pretty_name = COLOR_DICT[self.btn.text().lower()]
            if self.show_pretty_name:
                self.lab.setText(pretty_name)
            else:
                self.btn.setToolTip(pretty_name)
        else:
            if self.show_pretty_name:
                self.lab.clear()
            else:
                self.btn.setToolTip(None)

    def __change_color(self) -> None:
        """
        Displays the color chooser dialog to select a new color, then updates this widget
        """
        dlg = QColorDialog(self.color)
        if dlg.exec_():
            self.color = self.closest_color(dlg.currentColor().name())
            self.btn.setText(self.color.upper())
            self.update_bg()

    def get_color(self) -> str:
        """
        Retrieves the selected color to HEX format
        """
        return self.color

    def get_distance_color(self, c1, c2):
        """returns the distance between 2 colors"""
        def hex2dec(h):
            return int("0x"+h, 16)
        
        # normalize input format
        if c1[0] == "#":
            c1 = c1[1:]
        if c2[0] == "#":
            c2 = c2[1:]
        r1 = hex2dec(c1[0:2])
        g1 = hex2dec(c1[2:4])
        b1 = hex2dec(c1[4:6])
        r2 = hex2dec(c2[0:2])
        g2 = hex2dec(c2[2:4])
        b2 = hex2dec(c2[4:6])
        return (r2-r1)**2 + (b2-b1)**2 + (g2-g1)**2
    
    def closest_color(self, c):
        min_d = 1000000
        for c1 in COLOR_DICT:
            d = self.get_distance_color(c, c1)
            if d == 0:
                return c1
            if d < min_d:
                min_c = c1
                min_d = d
        return min_c