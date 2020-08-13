# Salle de classe by Lecluse DevCorp
# file author : Olivier Lecluse
# Licence GPL-v3 - see LICENCE.txt

from PySide2.QtCore import Slot

from src.Model.import_csv import import_csv, process_line

from src.View.popup.view_info_dialog import VInfoDialog
from src.View.popup.view_import_csv import DialogImportCsv
from src.View.popup.view_confirm_dialogs import VConfirmDialog

from src.assets_manager import AssetManager, tr


class GroupController:
    def __init__(self, main_ctrl, bdd):
        """
        Application Group controller.
        """

        self.main_ctrl = main_ctrl
        self.course_ctrl = main_ctrl.course_ctrl
        self.__bdd = bdd

        self.mod_bdd = main_ctrl.mod_bdd

        self.gui = main_ctrl.gui
        self.v_canvas = main_ctrl.v_canvas

    #
    # Signals handling
    #

    @Slot(str)
    def on_student_group_changed(self, new_group: str) -> None:
        """
        Triggered when the self.sig_student_group_changed is emitted. Updates the list of displayed students given
        the new selected group

        :param new_group: Course in which are the students to display
        :type new_group: str
        """
        self.main_ctrl.id_group = self.mod_bdd.get_group_id_by_name(new_group)
        self.gui.sidewidget.students().set_students_list(self.mod_bdd.get_students_in_group(new_group))

        self.course_ctrl.synchronize_canvas_selection_with_side_list()

    @Slot(str)
    def on_create_grp_std(self, new_grp_std: str):
        """
        Creates a new group or a new student with the specified name.

        It is a group if the received string starts with 'grp '. It is a student if it starts with 'std '.
        """
        prefix = new_grp_std[:4]
        name = new_grp_std[4:]

        if prefix == 'grp ':  # Group creation
            self.gui.status_bar.showMessage(f"Creation du groupe {name}", 3000)
            id_group = self.mod_bdd.create_group(name)
            list_id_students = self.gui.sidewidget.students().selected_students()
            for id_std in list_id_students:
                self.mod_bdd.insert_isin(id_std, id_group)
            if name[-1] in ["1", "A", "a"] and VConfirmDialog(self.gui, "confirm_create_complementary_group").exec_():
                namec = name[:-1]
                namec += chr(ord(name[-1])+1)
                # create complementary group
                id_group = self.mod_bdd.create_group(namec)
                # Students are unselected at this point
                list_all_students = self.mod_bdd.get_students_in_group(self.mod_bdd.get_group_name_by_id(self.main_ctrl.id_group))
                for std in list_all_students:
                    if std.id not in list_id_students:
                        self.mod_bdd.insert_isin(std.id, id_group)
            self.show_all_groups()
        elif prefix == 'std ':  # Student creation
            self.gui.status_bar.showMessage(f"Creation de l'élève {name}", 3000)
            lastname, firstname = process_line(name, ";")
            self.mod_bdd.insert_student_in_group_id(firstname, lastname, 0, self.main_ctrl.id_group)
            self.course_ctrl.show_course()
            self.show_all_groups(current=self.main_ctrl.id_group)
        else:  # Student edition
            id_std = int(prefix)
            lastname, firstname = process_line(name, ";")
            self.gui.status_bar.showMessage(f"Renommage de l'élève {firstname} {lastname}", 3000)
            self.mod_bdd.rename_student_by_id(id_std, firstname, lastname)
            self.course_ctrl.show_course()
            self.show_all_groups(current=self.main_ctrl.id_group)

        self.__bdd.commit()

    def on_delete_group(self) -> None:
        """
        Deletes the selected group
        """
        if not VConfirmDialog(self.gui, "confirm_message_delete").exec_():
            return

        self.mod_bdd.delete_group_by_id(self.main_ctrl.id_group)
        self.main_ctrl.id_group = 0
        self.__bdd.commit()
        self.show_all_groups()

    #
    # General methods
    #

    def show_all_groups(self, current=0):
        groups = self.mod_bdd.get_groups()
        if current == 0:
            self.gui.sidewidget.students().students_toolbar.init_groups(groups)
        if groups:
            current_group = groups[0] if current == 0 else self.mod_bdd.get_group_name_by_id(current)
            self.on_student_group_changed(current_group)
            self.mod_bdd.get_group_id_by_name(current_group)
            self.gui.sidewidget.students().students_toolbar.current_group = current_group
        else:
            self.gui.sidewidget.students().set_students_list([])

    def auto_place(self):
        """Autoplacement of students on the free tiles"""
        max_row = int(AssetManager.getInstance().config("size", "default_room_rows"))
        max_col = int(AssetManager.getInstance().config("size", "default_room_columns"))
        group_name = self.mod_bdd.get_group_name_by_id(self.main_ctrl.id_group)
        list_idstd = self.gui.sidewidget.students().selected_students()
        if not list_idstd:
            list_students = self.mod_bdd.get_students_in_group(group_name)
        else:
            list_students = [self.mod_bdd.get_student_by_id(i) for i in list_idstd]

        students_ids = {s.id for s in list_students}

        to_be_placed = len(list_students)
        list_available_desks = []
        list_to_remove = []
        for row in range(max_row):
            for col in range(max_col):
                id_desk = self.mod_bdd.get_desk_id_in_course_by_coords(self.main_ctrl.id_course, row, col)
                if id_desk != 0:
                    student = self.mod_bdd.get_student_by_desk_id(id_desk)
                    if student is None:
                        # We have a free spot
                        list_available_desks.append((id_desk, row, col))
                    else:
                        list_to_remove.append(student.id)
        # Adjust the number of students to place
        for s in list_to_remove:
            if s in students_ids:
                to_be_placed -= 1

        info = None
        if to_be_placed > len(list_available_desks):
            info = str(to_be_placed - len(list_available_desks)) + tr("seats_are_missing")
            self.gui.status_bar.showMessage(info)
        else:
            self.gui.status_bar.showMessage(tr("seats_are_OK"), 3000)

        index_std = 0
        for dsk in list_available_desks:
            while index_std < len(list_students) and list_students[index_std].id in list_to_remove:
                index_std += 1
            if index_std >= len(list_students):
                break
            student = list_students[index_std]
            # update the model
            self.mod_bdd.set_student_in_desk_by_id(student.id, dsk[0])
            # update the view
            self.v_canvas.set_student(dsk[0], student.firstname, student.lastname)
            self.v_canvas.repaint()
            index_std += 1

        self.__bdd.commit()

        if info is not None:
            VInfoDialog(self.gui, info).exec_()

    def import_pronote(self) -> None:
        groups = self.mod_bdd.get_groups()
        dlg = DialogImportCsv(self.gui, ["Nouveau Groupe"] + groups)

        if dlg.exec_():
            name_group = dlg.selected_group()
            file_path = dlg.selected_file()
            if name_group == "Nouveau Groupe":
                f = file_path.split("/")[-1].upper()
                name_group = f[0:f.index(".CSV")]
            csv_sep = AssetManager.getInstance().config("main", "csv_separator")
            names = import_csv(file_path, csv_sep)
            id_group = self.mod_bdd.create_group(name_group)
            order = 0
            for std in names:
                self.mod_bdd.insert_student_in_group_id(std[1], std[0], order, id_group)
                order += 1
            self.__bdd.commit()

            self.show_all_groups()

    def killstudent(self):
        if not VConfirmDialog(self.gui, "confirm_message_delete").exec_():
            return

        self.gui.status_bar.showMessage(tr("grp_action_del_student"), 3000)
        list_id_students = self.gui.sidewidget.students().selected_students()
        for id_std in list_id_students:
            self.mod_bdd.remove_student_from_group(id_std, self.main_ctrl.id_group)
        self.course_ctrl.show_course()
        self.show_all_groups(current=self.main_ctrl.id_group)
        self.__bdd.commit()

    def sort_alpha(self, desc):
        self.gui.status_bar.showMessage(tr("grp_action_alpha_sort"), 3000)
        group_name = self.mod_bdd.get_group_name_by_id(self.main_ctrl.id_group)
        list_students = self.mod_bdd.get_students_in_group(group_name)
        sortlist = [(s.lastname, s.id) for s in list_students]
        sortlist.sort(reverse=desc)
        orderkey = 1
        for s in sortlist:
            self.mod_bdd.update_student_order_with_id(s[1], orderkey)
            orderkey += 1
        self.__bdd.commit()
        self.main_ctrl.on_config_changed()
        self.course_ctrl.synchronize_canvas_selection_with_side_list()
