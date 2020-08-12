from PySide2.QtCore import Slot
from PySide2.QtGui import QColor

from src.View.popup.view_confirm_dialogs import VConfirmDialog
from src.View.popup.view_attribute_edition import VDlgEditText, VDlgEditCounter, VDlgEditMark, VDlgEditColor
from src.View.popup.view_student_attributes import VStdAttributesDialog
from src.assets_manager import AssetManager, COLOR_DICT
from src.enumerates import EAttributesTypes

import csv


class AttrController:
    def __init__(self, main_ctrl, bdd):
        """
        Application Attr controller.
        """

        self.main_ctrl = main_ctrl
        self.__bdd = bdd

        self.mod_bdd = main_ctrl.mod_bdd

        self.gui = main_ctrl.gui
        self.v_canvas = main_ctrl.v_canvas

    #
    # Signals handling
    #

    @Slot(str, str)
    def on_create_attr(self, attr_name: str, attr_type: str) -> None:
        """
        Triggers when the user wants to create a new attribute

        :param attr_name: Attribute's name
        :param attr_type: Attribute's type key
        """
        self.mod_bdd.insert_attribute(attr_name, attr_type)
        self.__bdd.commit()

        self.show_all_attributes()

    @Slot()
    def on_delete_attributes(self) -> None:
        """
        Deletes all the selected attribtues
        """
        if not VConfirmDialog(self.gui, "confirm_message_delete").exec_():
            return

        for id_a in self.gui.sidewidget.attributes().selected_attributes():
            self.mod_bdd.delete_attribute_with_id(id_a)
        self.__bdd.commit()
        self.show_all_attributes()

    @Slot()
    def on_attribute_selection_changed(self) -> None:
        """
        Triggered when the attribute selection changed
        - attributes = [(1, "Attr1"), (2, "Attr2") ...]
        - students = [(1, "Thomas Lécluse"), (2, "Pauline Lécluse"), ...]
        - data = {(attr_id, std_id}: cell_data, ...}
        """
        if self.main_ctrl.std_dialog_info and self.main_ctrl.std_dialog_info.isVisible():
            id_topic = self.mod_bdd.get_topic_id_by_course_id(self.main_ctrl.id_course)
            attrs = []
            for attr_id, attr_name, attr_type in self.mod_bdd.get_all_attributes():
                attrs.append((attr_id, attr_name,
                              self.mod_bdd.get_attribute_value(self.main_ctrl.std_dialog_info.student.id, attr_id, id_topic)))

            self.main_ctrl.std_dialog_info.attributes_updated(attrs)

        # update the choice button status
        self.main_ctrl.course_ctrl.get_unselected_occupied_desks_id()

        # gets the data into the list view
        attributes, students, data = self.get_attributes_matrix()
        self.gui.central_widget.attributes_tab.set_data(attributes, students, data)

    @Slot(int, int)
    def on_attribute_cell_selected(self, attr_id: int, std_id: int) -> None:
        """
        Triggered when a cell is clicked on the attributes table.
        Opens an edition panel, allowing the user to edit the cell content.

        :param attr_id: Attribute ID
        :param std_id: Student ID
        """
        attr_type = self.mod_bdd.get_attribute_type_from_id(attr_id)
        id_topic = self.mod_bdd.get_topic_id_by_course_id(self.main_ctrl.id_course)
        val = self.mod_bdd.get_attribute_value(std_id, attr_id, id_topic)

        dlg = None  # QDialog
        if attr_type == EAttributesTypes.TEXT.value:
            dlg = VDlgEditText(self.gui, val)
        elif attr_type == EAttributesTypes.COUNTER.value:
            dlg = VDlgEditCounter(self.gui, val)
        elif attr_type == EAttributesTypes.MARK.value:
            dlg = VDlgEditMark(self.gui, val)
        elif attr_type == EAttributesTypes.COLOR.value:
            dlg = VDlgEditColor(self.gui, val)

        if dlg and dlg.exec_():
            self.mod_bdd.update_attr_with_ids(std_id, attr_id, id_topic, dlg.new_value())
            self.__bdd.commit()
            self.on_attribute_selection_changed()

    @Slot(tuple)
    def show_student_attributes(self, desk_position: tuple) -> None:
        """
        Displays a dialog with all the student's attributes information.

        :param desk_position: student's desk position (where the click was triggered)
        :type desk_position: tuple
        """
        desk_id = self.mod_bdd.get_desk_id_in_course_by_coords(self.main_ctrl.id_course, desk_position[0], desk_position[1])
        std = self.mod_bdd.get_student_by_desk_id(desk_id)
        topic = self.mod_bdd.get_topic_id_by_course_id(self.main_ctrl.id_course)

        attrs = []
        if std is not None:
            for attr_id, attr_name, attr_type in self.mod_bdd.get_all_attributes():
                attrs.append((attr_id, attr_name, self.mod_bdd.get_attribute_value(std.id, attr_id, topic)))

            if self.main_ctrl.std_dialog_info and self.main_ctrl.std_dialog_info.isVisible():  # Closes any opened info dialog
                self.main_ctrl.std_dialog_info.close()

            self.main_ctrl.std_dialog_info = VStdAttributesDialog(self.gui, self.main_ctrl.sig_attribute_cell_selected, std, attrs)

            # We can't use exec_() method, nor make the dialog modal because for some reason, at least on OSX, once closed,
            # most of the HMI does not respond to user interaction.
            # The chosen workaround is to just show() the dialog, and make it always on top. If a new dialog is to be
            # displayed, the previous one would be closed before.
            self.main_ctrl.std_dialog_info.show()

    @Slot(str)
    def export_csv(self, file_path: str) -> None:
        """
        Saves the attributes table in a CSV format at the specified file path
        """
        attributes, students, data = self.get_attributes_matrix()

        # build the attribute type dict
        attr_type = dict()
        for a in attributes:
            attr_type[a[0]] = self.mod_bdd.get_attribute_type_from_id(a[0])

        # generate CSV file
        with open(file_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, 
                delimiter=AssetManager.getInstance().config("main", "csv_separator"), 
                quoting=csv.QUOTE_MINIMAL)
            # Write first row
            first_row = ['Nom Prenom']
            for a in attributes:
                first_row.append(a[1])
            writer.writerow(first_row)

            # Write datas
            for s in students:
                row = [s[1]]
                for a in attributes:
                    id_a, id_s = a[0], s[0]
                    if (id_a, id_s) in data:
                        # We have a data to export
                        if attr_type[id_a] == EAttributesTypes.TEXT.value:
                            row.append(data[(id_a, id_s)])
                        elif attr_type[id_a] == EAttributesTypes.MARK.value:
                            mark_list = data[(id_a, id_s)].split()
                            try:
                                somme = sum(map(int, mark_list))
                                row.append(somme/len(mark_list))
                            except:
                                row.append("")
                        elif attr_type[id_a] == EAttributesTypes.COLOR.value:
                            hexcol = data[(id_a, id_s)].name()[1:].upper()
                            col_name = COLOR_DICT[hexcol] if hexcol in COLOR_DICT else hexcol
                            row.append(col_name)
                        elif attr_type[id_a] == EAttributesTypes.COUNTER.value:
                            row.append(int(data[(id_a, id_s)]))
                    else:
                        # No data in this cell
                        row.append("")
                # write current row
                writer.writerow(row)

    #
    # General methods
    #

    def show_all_attributes(self):
        """Initializes the contents of the attributes list"""

        list_attr = self.mod_bdd.get_all_attributes()
        self.gui.sidewidget.attributes().set_attributes_list(list_attr)

    def change_filter_selection(self):
        self.main_ctrl.filter_selection = not self.main_ctrl.filter_selection
        self.on_attribute_selection_changed()

    def lot_change(self):
        list_id_attr = self.gui.sidewidget.attributes().selected_attributes()
        if len(list_id_attr) == 1:
            # Only one attribute is selected, we change it
            id_topic = self.mod_bdd.get_topic_id_by_course_id(self.main_ctrl.id_course)
            students_in_course = self.mod_bdd.get_students_in_course_by_id(self.main_ctrl.id_course)
            if self.main_ctrl.filter_selection:
                # get desk selection
                desks_id = self.v_canvas.get_selected_tiles()
                id_students_selected = [self.mod_bdd.get_desk_by_id(d).id_student for d in desks_id]
                students = [(s.id, f"{s.lastname} {s.firstname}") for s in students_in_course if
                            s.id in id_students_selected]
            else:
                students = [(s.id, f"{s.lastname} {s.firstname}") for s in students_in_course]
            attr_id = list_id_attr[0]
            attr_type = self.mod_bdd.get_attribute_type_from_id(attr_id)

            dlg = None  # QDialog
            if attr_type == EAttributesTypes.TEXT.value:
                dlg = VDlgEditText(self.gui, "")
            elif attr_type == EAttributesTypes.MARK.value:
                dlg = VDlgEditMark(self.gui, "")
            elif attr_type == EAttributesTypes.COLOR.value:
                dlg = VDlgEditColor(self.gui, "")
            elif attr_type == EAttributesTypes.COUNTER.value:
                dlg = VDlgEditCounter(self.gui, "1")

            if dlg and dlg.exec_():
                if attr_type == EAttributesTypes.COUNTER.value:
                    if dlg.new_value() == 0 and not VConfirmDialog(self.gui, "confirm_message_RAZ").exec_():
                        return
                    for s in students:
                        if dlg.new_value() == 0:
                            val = "0"
                        else:
                            val = self.mod_bdd.get_attribute_value(s[0], attr_id, id_topic)
                            val = str(int(val) + dlg.new_value()) if val else str(dlg.new_value())
                        self.mod_bdd.update_attr_with_ids(s[0], attr_id, id_topic, val)
                else:
                    for s in students:
                        val = dlg.new_value()
                        self.mod_bdd.update_attr_with_ids(s[0], attr_id, id_topic, val)

                self.__bdd.commit()
                self.on_attribute_selection_changed()

    def get_attributes_matrix(self):
        list_id_attr = self.gui.sidewidget.attributes().selected_attributes()
        if list_id_attr:
            id_topic = self.mod_bdd.get_topic_id_by_course_id(self.main_ctrl.id_course)
            all_attributes = self.mod_bdd.get_all_attributes()
            # all_attributes = list [(id1, attrName1, attrType1), ...]
            # now we filter attributes
            attributes = [(a[0], a[1]) for a in all_attributes if a[0] in list_id_attr]

            # get all students in current course
            students_in_course = self.mod_bdd.get_students_in_course_by_id(self.main_ctrl.id_course)
            if self.main_ctrl.filter_selection:
                # get desk selection
                desks_id = self.v_canvas.get_selected_tiles()
                id_students_selected = [self.mod_bdd.get_desk_by_id(d).id_student for d in desks_id]
                students = [(s.id, f"{s.lastname} {s.firstname}") for s in students_in_course if
                            s.id in id_students_selected]
            else:
                students = [(s.id, f"{s.lastname} {s.firstname}") for s in students_in_course]
            students.sort(key=lambda x: x[1])

            # get datas
            data = dict()
            for a in attributes:
                for s in students:
                    val = self.mod_bdd.get_attribute_value(s[0], a[0], id_topic)
                    if val:
                        if len(val) == 7 and val[0] == '#':
                            val = QColor(val)
                        data[(a[0], s[0])] = val

            return attributes, students, data
        else:
            return [], [], {}
