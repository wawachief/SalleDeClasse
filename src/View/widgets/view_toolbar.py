from PySide2.QtWidgets import QToolBar, QPushButton, QComboBox
from PySide2.QtCore import Signal, Slot, QSize

from src.assets_manager import get_icon, get_stylesheet
from src.View.widgets.view_add_widget import ViewAddWidget
from src.View.widgets.view_menubutton import ViewMenuButton

BUTTON_SIZE = QSize(60, 60)
ICON_SIZE = QSize(45, 45)


class ViewMainToolBar(QToolBar):

    sig_enable_animation_btns = Signal(bool)

    def __init__(self, config):
        """
        Main ToolBar, providing features buttons that operates over the canvas.
        The callbacks methods provided by this class should be redirected towards any widget handling the associated
        process.

        :param config: application's parsed configuration
        """
        QToolBar.__init__(self)
        self.config = config

        # Buttons
        self.__btn_magic = ToolBarButton("magic", "Abracadabra !", self.on_btn_magic_clicked)  # Debug btn
        self.__btn_perspective = ToolBarButton("teacher", "Changer de perspective", self.on_btn_perspective_clicked)
        self.__btn_shuffle = ToolBarButton("shuffle", "Mélanger", self.on_btn_shuffle_clicked)

        # Signals
        self.sig_enable_animation_btns.connect(self.enable_animation_btns)

        # Layout
        self.__set_widgets()
        self.__set_style()

    def __set_widgets(self):
        """
        Adds the widgets to this toolbar
        """
        self.addWidget(self.__btn_magic)
        self.addWidget(self.__btn_perspective)
        self.addWidget(self.__btn_shuffle)

    def __set_style(self):
        """
        Inits the stylesheet of this widget
        """
        self.setStyleSheet(get_stylesheet("toolbar"))

    @Slot(bool)
    def enable_animation_btns(self, do_enable):
        """
        Enables or disables the change-perspective and shuffle buttons to prevent several animation at a time

        :param do_enable: True to enable
        :type do_enable: bool
        """
        self.__btn_perspective.setEnabled(do_enable)
        self.__btn_shuffle.setEnabled(do_enable)

    def on_btn_perspective_clicked(self):
        pass

    def on_btn_magic_clicked(self):
        pass

    def on_btn_shuffle_clicked(self):
        pass


class ViewCourseListToolbar(QToolBar):

    def __init__(self, config):
        """
        Toolbar for the Room list side panel tab

        :param config: application's parsed configuration
        """
        QToolBar.__init__(self)
        self.config = config

        self.add_widget = ViewAddWidget(config)

        self.addWidget(self.add_widget)

        self.__set_style()

    def __set_style(self):
        """
        Inits the stylesheet of this widget
        """
        # Toolbar
        self.setStyleSheet(get_stylesheet("toolbar"))


class ViewStudentListToolbar(QToolBar):

    def __init__(self, config):
        """
        Toolbar for the students list side panel tab

        :param config: application's parsed configuration
        """
        QToolBar.__init__(self)
        self.config = config
        self.current_group: str = None

        # Widgets
        self.combo_groups = QComboBox()
        self.action_menu = ViewMenuButton("Actions", [("Import Pronote", "import_csv"),
                                                      ("Créer un sous-groupe", "create_subgroup")])

        self.addWidget(self.combo_groups)
        self.addWidget(self.action_menu)

        # Signals
        self.sig_combo_changed: Signal = None
        self.combo_groups.activated.connect(self.on_group_changed)

        self.__set_style()

    def __set_style(self) -> None:
        """
        Inits the stylesheet of this widget
        """
        # Toolbar
        self.setStyleSheet(get_stylesheet("toolbar"))

    def on_group_changed(self) -> None:
        """
        Triggered when the combo selection changed, emits the signal if the selected group was updated.
        """
        text = self.combo_groups.currentText()

        if text and text != self.current_group:
            self.current_group = text
            self.sig_combo_changed.emit(text)

    def init_groups(self, groups: list) -> None:
        """
        Resets the combo box before adding all the groups to the combo.

        :param groups: groups names list
        :type groups: list
        """
        self.reset_groups()
        self.__add_groups(groups)
        self.repaint()

    def __add_groups(self, list_groups: list) -> None:
        """
        Adds the list of all specified groups inside the combo.

        :param list_groups: All the groups to add
        :type list_groups: list
        """
        self.combo_groups.addItems(list_groups)

    def reset_groups(self) -> None:
        """
        Resets the groups combo (clears it)
        """
        self.combo_groups.clear()


class ViewAttributeListToolbar(QToolBar):

    def __init__(self, config):
        """
        Toolbar for the attributes list side panel tab

        :param config: application's parsed configuration
        """
        QToolBar.__init__(self)
        self.config = config

        self.__set_style()

    def __set_style(self):
        """
        Inits the stylesheet of this widget
        """
        # Toolbar
        self.setStyleSheet(get_stylesheet("toolbar"))


class ToolBarButton(QPushButton):

    def __init__(self, icon, tooltip, callback):
        """
        Button widget for the toolbar
        """
        QPushButton.__init__(self)

        self.setIcon(get_icon(icon))
        self.setToolTip(tooltip)
        self.setFixedSize(BUTTON_SIZE)
        self.setIconSize(ICON_SIZE)
        self.clicked.connect(callback)

        self.setStyleSheet("QPushButton:hover {background-color: #E0F2F7;} QPushButton {border: none; margin: 5px;}")
