# Salle de classe by Lecluse DevCorp
# file author : Thomas Lecluse
# Licence GPL-v3 - see LICENCE.txt

from PySide2.QtWidgets import QMenu, QPushButton

from src.assets_manager import get_stylesheet


class ViewMenuButton(QPushButton):

    sig_action = None

    def __init__(self, btn_name: str, show_field, actions_map: list):
        """
        Creates a QPushButton with a dropdown menu on it.

        :param btn_name: Button name (always displayed)
        :type btn_name: str
        :param actions_map: list of actions to put in the dropdown menu [(action_name, action_key), (separator_name), ...]
        :type actions_map: list
        :param show_field: entry field to display on create operations
        :type show_field: function
        """
        QPushButton.__init__(self, btn_name)

        self.menu = QMenu(self)

        for a in actions_map:
            if a == 'sep':  # This is a separator
                self.menu.addSeparator()
            else:  # Regular action
                t, k = a
                if k.startswith('create_'):  # If we have a create feature, we display the entry field
                    self.menu.addAction(t, lambda k=k: show_field(k))
                else:
                    self.menu.addAction(t, lambda k=k: self.sig_action.emit(k))

        self.setMenu(self.menu)
        self.menu.setStyleSheet(get_stylesheet("menu"))
