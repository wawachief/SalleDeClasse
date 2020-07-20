from PySide2.QtWidgets import QToolBar, QPushButton, QComboBox, QWidget, QSizePolicy
from PySide2.QtCore import Signal, Slot, QSize

from src.assets_manager import get_icon, get_stylesheet
from src.View.widgets.view_add_widget import ViewAddWidget, ViewAddLine, ViewAddAttributeWidget
from src.View.widgets.view_menubutton import ViewMenuButton

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

        # Buttons
        self.__btn_magic = ToolBarButton("unkwown", "Abracadabra !", lambda: self.sig_TBbutton.emit("magic"))
        self.__btn_perspective = ToolBarButton("teacher", "Changer de perspective", self.on_btn_perspective_clicked)
        self.__btn_shuffle = ToolBarButton("shuffle", "Mélanger", self.on_btn_shuffle_clicked)
        self.__btn_select = ToolBarButton("selection", "Sélectionner", lambda: self.sig_TBbutton.emit("select"))
        self.__btn_choice = ToolBarButton("choixvolontaire", "Choisir un élève", lambda: self.sig_TBbutton.emit("choix"))
        self.__btn_delete = ToolBarButton("corbeille", "Effacer", lambda: self.sig_TBbutton.emit("delete"))

        self.actions_table = {self.__btn_magic: None, self.__btn_perspective: None, self.__btn_shuffle: None,
                              self.__btn_select: None, self.__btn_choice: None, self.__btn_delete: None}

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
        # self.actions_table[self.__btn_magic].setVisible(is_view_classroom)
        self.actions_table[self.__btn_perspective].setVisible(is_view_classroom)
        self.actions_table[self.__btn_shuffle].setVisible(is_view_classroom)
        self.actions_table[self.__btn_select].setVisible(is_view_classroom)
        self.actions_table[self.__btn_choice].setVisible(is_view_classroom)
        self.actions_table[self.__btn_delete].setVisible(is_view_classroom)

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

    def on_btn_shuffle_clicked(self):
        pass


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
        self.delete_btn.setToolTip("Supprimer")
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

        # Widgets
        self.combo_groups = QComboBox()
        self.create_field = ViewAddLine()
        self.action_menu = ViewMenuButton("Actions", self.create_field.show_field,
                                          [("Import Pronote", "import_csv"),
                                           ("Créer un groupe", "create_group"),
                                           ("Supprimer ce groupe !", "delete_group"),
                                           'sep',
                                           ("Créer un élève", "create_student"),
                                           ("Supprimer un élève", "killstudent"),
                                           'sep',
                                           ("Placement automatique", "auto_place"),
                                           'sep',
                                           ("Tri alphabétique croissant", "sort_asc"),
                                           ("Tri alphabétique décroissant", "sort_desc"),
                                           ("Tri d'après les places", "sort_desks")])

        # Signals
        self.sig_combo_changed: Signal = None
        self.combo_groups.activated.connect(self.on_group_changed)

        # Layout
        self.addWidget(self.combo_groups)
        self.addWidget(self.action_menu)
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
        self.create_field.show_field(str(student_id), student_data)

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
