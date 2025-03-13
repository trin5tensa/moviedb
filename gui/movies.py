"""This module contains code for movie maintenance."""

#  Copyright© 2025. Stephen Rigden.
#  Last modified 3/13/25, 12:53 PM by stephen.
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
from collections.abc import Callable, Sequence
from dataclasses import dataclass, KW_ONLY, field
import queue

from globalconstants import (
    MovieBag,
    TITLE,
    YEAR,
    DIRECTORS,
    DURATION,
    NOTES,
    MOVIE_TAGS,
)
from gui import common, tk_facade

TITLE_TEXT = "Title"
YEAR_TEXT = "Year"
DIRECTORS_TEXT = "Directors"
DURATION_TEXT = "Runtime"
NOTES_TEXT = "Notes"
MOVIE_TAGS_TEXT = "Tags"


@dataclass
class MovieGUI:
    """This base class for movies creates a standard movies input form."""

    parent: tk.Tk

    _: KW_ONLY
    tmdb_callback: Callable[[str, queue.LifoQueue], None]
    all_tags: Sequence[str]

    prepopulate: MovieBag = field(default_factory=MovieBag, kw_only=True)
    # A more convenient data structure for entry fields.
    entry_fields: dict[
        str,
        tk_facade.Entry | tk_facade.Text | tk_facade.Treeview,
    ] = field(default_factory=dict, init=False, repr=False)

    def __post_init__(self):
        outer_frame, body_frame, buttonbox = common.create_body_and_buttonbox(
            self.parent, type(self).__name__.lower(), self.destroy
        )
        tmdb_frame = self.create_tmdb_frame(outer_frame)
        self.fill_body(body_frame)
        self.populate()
        self.fill_buttonbox(buttonbox)
        self.fill_tmdb(tmdb_frame)
        common.init_button_enablements(self.entry_fields)

    @staticmethod
    def create_tmdb_frame(outer_frame: ttk.Frame) -> ttk.Frame:
        """Creates a frame which will contain movies found in TMDB.

        Args:
            outer_frame:

        Returns:
            tmdb_frame:
        """
        outer_frame.columnconfigure(1, weight=1000)
        tmdb_frame = ttk.Frame(outer_frame, padding=10)
        tmdb_frame.grid(column=1, row=0, sticky="nw")
        tmdb_frame.columnconfigure(0, weight=1, minsize=25)
        return tmdb_frame

    def fill_body(self, body_frame: ttk.Frame):
        """Creates the widgets for the entry form and the data structures for their
        support.

        The widgets are:
            title: ttk.Entry
            year: ttk.Entry
            directors: ttk.Entry
            duration: ttk.Entry
            notes: ttk.Text
            tags: ttk.Treeview

        Args:
            body_frame:
        """
        label_and_field = common.LabelAndField(body_frame)

        # Create entry rows for title, year, director, and duration.
        for name, text in zip(
            (TITLE, YEAR, DIRECTORS, DURATION),
            (TITLE_TEXT, YEAR_TEXT, DIRECTORS_TEXT, DURATION_TEXT),
        ):
            self.entry_fields[name] = tk_facade.Entry(text, body_frame)
            label_and_field.add_entry_row(self.entry_fields[name])

        # Create label and text widget.
        self.entry_fields[NOTES] = tk_facade.Text(NOTES_TEXT, body_frame)
        label_and_field.add_text_row(self.entry_fields[NOTES])

        # Create a label and treeview for movie tags.
        self.entry_fields[MOVIE_TAGS] = tk_facade.Treeview(MOVIE_TAGS_TEXT, body_frame)
        label_and_field.add_treeview_row(self.entry_fields[MOVIE_TAGS], self.all_tags)

        self.entry_fields[TITLE].widget.focus_set()

    def fill_buttonbox(self, buttonbox: ttk.Frame):
        """Stub method."""
        pass

    def fill_tmdb(self, tmdb_frame: ttk.Frame):
        """Stub method."""
        pass

    def populate(self):
        """Stub method."""
        pass

    def destroy(self):
        """Stub method."""
        pass
