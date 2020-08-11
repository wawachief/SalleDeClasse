from PySide2.QtWidgets import QToolBar, QPushButton, QComboBox, QWidget, QSizePolicy, QLabel
from PySide2.QtCore import Signal, Slot, QSize

from src.assets_manager import get_icon, get_stylesheet, tr
from src.View.widgets.view_add_widget import ViewAddWidget, ViewAddLine, ViewAddAttributeWidget
from src.View.widgets.view_menubutton import ViewMenuButton
from src.View.widgets.ToggleSwitchButton import ToggleSwitchButton
from src.View.popup.view_about_box import AboutFrame

BUTTON_SIZE = QSize(60, 60)
ICON_SIZE = QSize(45, 45)


class ViewMainToolBar(QToolBar):

    sig_enable_animation_btns = Signal(bool)

    def __init__(self):
        """
        Main ToolBar, providing features buttons that operates over the canvas.
        The callbacks methods provided by this class should be redirected towards any widget handling the associated
        process.
        """
        QToolBar.__init__(self)
        self.sig_TBbutton = None

        self.config_mode = False

        # Buttons
        self.__btn_config = ToggleSwitchButton(self, "unlock", "lock", self.on_config_mode)

        # self.__btn_config = ToolBarButton("fill", tr("btn_config"), self.config_mode_clicked)
        self.__btn_magic = ToolBarButton("unkwown", tr("btn_selection_filter"), lambda: self.sig_TBbutton.emit("filter_select"))
        self.__btn_perspective = ToolBarButton("teacher", tr("btn_change_perspective"), self.on_btn_perspective_clicked)
        self.__btn_shuffle = ToolBarButton("shuffle", tr("btn_shuffle"), self.on_btn_shuffle_clicked)
        self.__btn_select = ToolBarButton("selection", tr("btn_select"), lambda: self.sig_TBbutton.emit("select"))
        self.__btn_choice = ToolBarButton("choixvolontaire", tr("btn_choose_student"), lambda: self.sig_TBbutton.emit("choice"))
        self.__btn_attr_choice = ToolBarButton("choixvolontaire_attr", tr("btn_choose_student_with_attr"), lambda: self.sig_TBbutton.emit("choice_attr"))
        self.__btn_delete = ToolBarButton("corbeille", tr("btn_delete"), lambda: self.sig_TBbutton.emit("delete"))
        self.__btn_lot_change = ToolBarButton("fill", tr("btn_lot_change"), lambda: self.sig_TBbutton.emit("lot_change"))
        self.__btn_pdf = ToolBarButton("print", tr("export_PDF"), lambda: self.sig_TBbutton.emit("print"))
        self.__btn_qr = ToolBarButton("qr-code", tr("btn_qr"), lambda: self.sig_TBbutton.emit("show_qr"))
        self.__btn_about = ToolBarButton("info", tr("btn_about"), self.__open_about_box)

        self.actions_table = {self.__btn_config: None, self.__btn_magic: None, self.__btn_perspective: None,
                              self.__btn_shuffle: None, self.__btn_select: None, self.__btn_choice: None,
                              self.__btn_attr_choice: None, self.__btn_delete: None, self.__btn_lot_change: None,
                              self.__btn_pdf: None, self.__btn_qr: None, self.__btn_about: None}

        # Signals
        self.sig_enable_animation_btns.connect(self.enable_animation_btns)

        self.__init_widgets()
        self.__set_style()

    def __init_widgets(self) -> None:
        """
        Adds the widgets to this toolbar
        :return:
        """
        for btn in self.actions_table:
            self.actions_table[btn] = self.addWidget(btn)

    def set_widgets(self, is_view_classroom: bool) -> None:
        """
        Sets the visibility of widgets given the current view

        :param is_view_classroom: True if the current central panel tab is the classroom's widget
        """
        self.actions_table[self.__btn_config].setVisible(is_view_classroom)
        self.actions_table[self.__btn_magic].setVisible(not is_view_classroom)
        self.actions_table[self.__btn_perspective].setVisible(is_view_classroom)
        self.actions_table[self.__btn_shuffle].setVisible(is_view_classroom)
        self.actions_table[self.__btn_select].setVisible(is_view_classroom)
        self.actions_table[self.__btn_choice].setVisible(is_view_classroom)
        self.actions_table[self.__btn_attr_choice].setVisible(is_view_classroom)
        self.actions_table[self.__btn_delete].setVisible(is_view_classroom)
        self.actions_table[self.__btn_lot_change].setVisible(not is_view_classroom)
        self.actions_table[self.__btn_qr].setVisible(is_view_classroom)
        self.actions_table[self.__btn_pdf].setVisible(True)

    def lock_buttons(self, is_config_mode: bool) -> None:
        """
        Locks buttons that cannot be used when not in config mode
        """
        self.config_mode = is_config_mode

        self.actions_table[self.__btn_shuffle].setEnabled(is_config_mode)
        self.actions_table[self.__btn_delete].setEnabled(is_config_mode)

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
        self.__btn_shuffle.setEnabled(do_enable and self.config_mode)

    def enable_one_attributes_buttons(self, do_enable: bool) -> None:
        """
        Enables or disables buttons that can be used only if exactly one attribute is selected.

        :param do_enable: new enable state
        """
        self.__btn_lot_change.setEnabled(do_enable)
        self.__btn_attr_choice.setEnabled(self.__btn_attr_choice.isEnabled() and do_enable)

    def enable_choices_buttons(self, do_enable: bool, both: bool=True) -> None:
        """
        Enables or disables buttons that can be used only if exactly one attribute is selected.

        :param do_enable: new enable state
        :param both: change state of both buttons
        """
        self.__btn_choice.setEnabled(do_enable)
        if both:
            self.__btn_attr_choice.setEnabled(do_enable)

    def on_btn_perspective_clicked(self) -> None:
        pass

    def on_btn_shuffle_clicked(self) -> None:
        pass

    def on_config_mode(self, is_in_config_mode: bool) -> None:
        pass

    def __open_about_box(self) -> None:
        AboutFrame().exec_()


class ViewCourseListToolbar(QToolBar):

    def __init__(self):
        """
        Toolbar for the Room list side panel tab
        """
        QToolBar.__init__(self)

        # Widgets
        self.delete_btn = QPushButton()
        self.delete_btn.setIcon(get_icon("del"))
        self.delete_btn.setIconSize(QSize(35, 35))
        self.delete_btn.setToolTip(tr("btn_suppr"))
        self.delete_btn.setEnabled(False)

        self.add_widget = ViewAddWidget(self.delete_btn)

        self.sig_delete: Signal = None
        self.delete_btn.clicked.connect(lambda: self.sig_delete.emit())

        # Layout
        self.addWidget(self.add_widget)
        # Empty space to align the about button to the right
        spacer = QWidget()
        spacer.setStyleSheet("background-color: transparent;")
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.addWidget(spacer)

        self.addWidget(self.delete_btn)

        self.__set_style()

    def __set_style(self) -> None:
        """
        Inits the stylesheet of this widget
        """
        # Toolbar
        self.setStyleSheet(get_stylesheet("toolbar"))
        self.delete_btn.setStyleSheet("border: none;")

    def enable_delete_btn(self, do_enable: bool) -> None:
        """
        Enables or disables the delete button

        :param do_enable: True to enable
        """
        self.delete_btn.setEnabled(do_enable)


class ViewStudentListToolbar(QToolBar):

    def __init__(self):
        """
        Toolbar for the students list side panel tab
        """
        QToolBar.__init__(self)
        self.current_group: str = None
        self.__config_mode = False

        # Widgets
        self.combo_groups = QComboBox()
        self.create_field = ViewAddLine()
        self.config_action_menu = ViewMenuButton("Actions", self.create_field.show_field,
                                          [(tr("grp_action_import_csv"), "import_csv"),
                                           (tr("grp_action_create_group"), "create_group"),
                                           (tr("grp_action_del_group"), "delete_group"),
                                           'sep',
                                           (tr("grp_action_create_student"), "create_student"),
                                           (tr("grp_action_del_student"), "killstudent"),
                                           'sep',
                                           (tr("grp_action_auto_placement"), "auto_place")])

        self.sort_actions_menu = ViewMenuButton("Tri", self.create_field.show_field,
                                                 [(tr("grp_action_sort_asc"), "sort_asc"),
                                                  (tr("grp_action_sort_desc"), "sort_desc"),
                                                  (tr("grp_action_sort_by_place") + " Z", "sort_desks_Z"),
                                                  (tr("grp_action_sort_by_place") + " 2", "sort_desks_2"),
                                                  (tr("grp_action_sort_by_place") + " W", "sort_desks_W"),
                                                  (tr("grp_action_sort_by_place") + " U", "sort_desks_U"),
                                                  ])

        # Signals
        self.sig_combo_changed: Signal = None
        self.combo_groups.activated.connect(self.on_group_changed)

        # Layout
        self.a_combo = self.addWidget(self.combo_groups)
        self.a_conf_menu = self.addWidget(self.config_action_menu)
        self.a_sort_menu = self.addWidget(self.sort_actions_menu)
        self.addWidget(self.create_field)

        self.__set_style()

    def __set_style(self) -> None:
        """
        Inits the stylesheet of this widget
        """
        # Toolbar
        self.setStyleSheet(get_stylesheet("toolbar"))

    def edit_student(self, student_id: int, student_data: str) -> None:
        """
        Shows the creation field, with the student data (last name + first name) that can be edited.

        :param student_id: student id
        :param student_data: student last name + first name
        """
        if self.__config_mode:
            self.create_field.show_field(str(student_id), student_data)

    def switch_config_mode(self, is_config_mode: bool) -> None:
        self.__config_mode = is_config_mode

        self.a_combo.setVisible(self.__config_mode)
        self.a_conf_menu.setVisible(self.__config_mode)
        self.a_sort_menu.setVisible(not self.__config_mode)

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

    def __init__(self):
        """
        Toolbar for the attributes list side panel tab
        """
        QToolBar.__init__(self)

        self.add_widget = ViewAddAttributeWidget()

        self.addWidget(self.add_widget)

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
