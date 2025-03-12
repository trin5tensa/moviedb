"""This module contains code for movie maintenance."""

#  Copyright© 2025. Stephen Rigden.
#  Last modified 3/12/25, 6:54 AM by stephen.
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

from globalconstants import MovieBag
from gui import common, tk_facade


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

    def create_tmdb_frame(self, outer_frame: ttk.Frame) -> ttk.Frame:
        """Stub method."""
        pass

    def fill_body(self, body_frame: ttk.Frame):
        """Stub method."""
        pass

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
