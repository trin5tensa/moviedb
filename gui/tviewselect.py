"""This module contains widget windows for selecting a record from a list."""

#  Copyright© 2025. Stephen Rigden.
#  Last modified 3/8/25, 8:16 AM by stephen.
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
from functools import partial
from collections.abc import Callable
from dataclasses import dataclass, KW_ONLY, field

from globalconstants import MovieBag
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
    # todo subclasses should override with either str or Movie Bag
    selection_callback: Callable[[str | MovieBag], None]
    titles: list[str]
    widths: list[int]
    # The index of self.rows list is also the treeview index.
    # todo subclasses should override with either list[str] or list[dict[str, MovieBag]]
    rows: list[str | dict[str, MovieBag]]

    outer_frame: ttk.Frame = None

    def __post_init__(self):
        """Contains common methods for specialized selection subclasses."""
        # Ensure subclasses have titles and widths with matching
        # non-zero lengths
        if not self.titles or not self.widths or len(self.titles) != len(self.widths):
            raise ValueError(
                BAD_TITLES_AND_WIDTHS, f"{len(self.widths)=}. {len(self.titles)=}"
            )

        self.outer_frame, body_frame, buttonbox = common.create_body_and_buttonbox(
            self.parent,
            type(self).__name__.lower(),
            self.destroy,
        )
        tree = self.treeview(body_frame)
        self.columns(tree)
        self.populate(tree)
        common.create_button(
            buttonbox,
            text=common.CANCEL_TEXT,
            column=0,
            command=self.destroy,
            default="active",
        )

    def treeview(self, body_frame: ttk.Frame):
        """Creates, grids, and binds a treeview.

        Args:
            body_frame:
        """
        tree = ttk.Treeview(body_frame, selectmode="browse")
        tree.grid(column=0, row=0, sticky="w")
        tree.bind("<<TreeviewSelect>>", func=partial(self.treeview_callback, tree))
        return tree

    def treeview_callback(self, tree: ttk.Treeview):
        """Handles the <<TreeviewSelect>> event of the treeview.

        It retrieves the selection id from the treeview. That is used as an index of
        self.rows to select and return the selected row to self.selection_callback.

        Args:
            tree:
        """
        ix = int(tree.selection()[0])
        tag_text = self.rows[ix]
        self.parent.after(0, self.selection_callback, tag_text)
        self.destroy()

    def columns(self, tree: ttk.Treeview):
        """Sets up the internal structure of the table.

        This includes column titles, column widths, and the number of rows to display.
        """
        raise NotImplementedError

    def populate(self, tree: ttk.Treeview):
        """Adds data from self.rows to the displayed table."""
        raise NotImplementedError

    def destroy(self):
        """Destroys this widget."""
        self.outer_frame.destroy()


@dataclass
class SelectTagGUI(SelectGUI):
    """Creates and manages a widget for selecting one of a list of tags."""

    _: KW_ONLY
    selection_callback: Callable[[str], None]
    titles: list[str] = field(default_factory=list)
    widths: list[int] = field(default_factory=list)
    # The index of self.rows list is also the treeview index.
    rows: list[str]

    def __post_init__(self):
        self.titles += [common.MOVIE_TAGS_TEXT]
        self.widths += [350, 42]
        super().__post_init__()

    def columns(self, tree: ttk.Treeview):
        """Sets up the internal structure of the treeview.

        This includes column titles, column widths, and the number of rows to display.

        Args:
            tree:
        """
        tree.column("#0", width=self.widths[0])
        tree.heading("#0", text=self.titles[0])
        tree.configure(height=10)

    def populate(self, tree: ttk.Treeview):
        """Populates the treeview with data.

        Args:
            tree:
        """
        for ix, tag_text in enumerate(self.rows):
            tree.insert("", "end", iid=str(ix), text=tag_text, values=[])


"""
Notes for SelectMovieGUI
------------------------
Attributes: All constants
titles = ["test col 1", "test col 2"]
widths = [42, 43]
rows:  
    [{"title": "movie 1", "year": 1942}, {"title": "movie 2", "year": 1943}]

columns
populate
"""
