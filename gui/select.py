"""This module contains widget windows for selecting a record from a list."""

#  Copyright© 2025. Stephen Rigden.
#  Last modified 3/6/25, 8:18 AM by stephen.
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
from collections.abc import Callable
from dataclasses import dataclass, KW_ONLY

from gui import common

BAD_TITLES_AND_WIDTHS = (
    "Column titles and widths must be same length and greater than zero length."
)


@dataclass
class SelectGUI:
    """A base class for selection windows where a table is presented to the
    user. The user may select any row or click on the 'Cancel' button.

    It may not be called directly. Call subclasses which are specialized for
    different record types such as tags or movies.
    """

    parent: tk.Tk
    _: KW_ONLY
    selection_callback: Callable
    titles: list[str]
    widths: list[int]
    rows: list[str | dict[str, str]]

    def __post_init__(self):
        """Contains common methods for specialized selection subclasses."""
        # Ensure subclasses have titles and widths with matching
        # non-zero lengths.
        if not self.titles or not self.widths or len(self.titles) != len(self.widths):
            raise ValueError(
                BAD_TITLES_AND_WIDTHS, f"{len(self.widths)=}. {len(self.titles)=}"
            )

        _, body_frame, buttonbox = common.create_body_and_buttonbox(
            self.parent,
            type(self).__name__.lower(),
            self.destroy,
        )
        self.treeview(body_frame)
        self.columns()
        self.populate()
        common.create_button(
            buttonbox,
            text=common.CANCEL_TEXT,
            column=0,
            command=self.destroy,
            default="active",
        )

    def treeview(self, body_frame: ttk.Frame):
        """Stub method"""
        pass

    def columns(self):
        """Stub method"""
        pass

    def populate(self):
        """Stub method"""
        pass

    def destroy(self):
        """Stub method"""
        pass


"""
BaseClass SelectGUI
-------------------
Attributes: 
rows: list[dict[str, str]] - require. contains list of rows each with 
    (k) column names and (v) data for display.
selection_callback: Callable

__post_init__
    Log and raise ValueError if len(rows) != len(widths)
    Call common.create_body_and_buttonbox
    Call treeview
    Call columns (override required.)
    Call populate (override required.)
    Call create_button
treeview create, grid, and bind (move height to 'columns')
columns (override required.)
populate (override required.)
selection_callback
destroy

SelectTagGUI
------------
Attributes: All constants
titles: = ["test col 1",]
widths: = [42,]
rows: list[str] = [{"tag 1", "tag 2"},]

columns
populate

SelectMovieGUI
--------------
Attributes: All constants
titles = ["test col 1", "test col 2"]
widths = [42, 43]
rows:  
    [{"title": "movie 1", "year": 1942}, {"title": "movie 2", "year": 1943}]

columns
populate
"""
