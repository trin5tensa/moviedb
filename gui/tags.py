""" This module contains code for movie tag maintenance."""

#  Copyright© 2025. Stephen Rigden.
#  Last modified 2/27/25, 10:35 AM by stephen.
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

# This tkinter import method supports accurate test mocking of tk and ttk.
import tkinter as tk
import tkinter.ttk as ttk
from dataclasses import dataclass, field

from globalconstants import MOVIE_TAGS
from gui import common
from gui.tk_facade import EntryFields, Entry

MOVIE_TAGS_TEXT = "Tags"


@dataclass
class TagGUI:
    """A base class for tag widgets"""

    parent: tk.Tk
    tag: str = ""

    # The main outer frame of this class.
    outer_frame: ttk.Frame = field(default=None, init=False, repr=False)

    # An internal dictionary to simplify field data management.
    entry_fields: EntryFields = field(
        default_factory=dict,
        init=False,
        repr=False,
    )

    def __post_init__(self):
        """Creates the tag form."""
        self.outer_frame, body_frame, buttonbox = common.create_body_and_buttonbox(
            self.parent, type(self).__name__.lower(), self.destroy
        )
        self.user_input_frame(body_frame)
        self.create_buttons(buttonbox)
        common.init_button_enablements(self.entry_fields)

    def user_input_frame(self, body_frame: tk.Frame):
        """Creates the widgets which will be used to enter data and
        display data retrieved from the user's database.

        Args:
            body_frame: The frame which contains the entry fields.
        """
        input_zone = common.LabelAndField(body_frame)

        self.entry_fields[MOVIE_TAGS] = Entry(MOVIE_TAGS_TEXT, body_frame)
        self.entry_fields[MOVIE_TAGS].original_value = self.tag
        input_zone.add_entry_row(self.entry_fields[MOVIE_TAGS])
        self.entry_fields[MOVIE_TAGS].widget.focus_set()

    def create_buttons(self, buttonbox: tk.Frame):
        """Subclasses should override to create buttons needed for
        the subclass.
        """
        raise NotImplementedError  # pragma nocover

    def destroy(self):
        """Stub method"""
        pass  # pragma nocover
