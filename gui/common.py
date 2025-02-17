""" This module contains common code to support the other gui modules."""

#  Copyright© 2025. Stephen Rigden.
#  Last modified 2/17/25, 1:36 PM by stephen.
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.


from gui import tk_facade


def init_button_enablements(entry_fields: tk_facade.EntryFieldItem):
    """Set the initial enabled state of buttons.

    Calls the notify method of each field. The field's observer will notify
    any registered buttons.

    Args:
        entry_fields:
            k: Field name.
            v: Any TkinterFacade subclass.
    """
    for entry_field in entry_fields.values():
        entry_field.observer.notify()
