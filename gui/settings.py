"""GUI Windows.

This module includes windows for presenting data and returning entered data
to its callers.
"""

#  Copyright© 2025. Stephen Rigden.
#  Last modified 5/6/25, 10:57 AM by stephen.
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
from dataclasses import dataclass, KW_ONLY, field
from functools import partial
import itertools
from typing import (
    Callable,
    Dict,
)

from gui.constants import *
from gui import tk_facade, common


@dataclass
class Settings:
    """Create and manage a Tk input form which allows the user to update
    program preferences."""

    parent: tk.Tk

    _: KW_ONLY
    # Preference fields
    tmdb_api_key: str
    use_tmdb: bool

    # On commit this callback will be called with the updated preferences.
    save_callback: Callable[[str, bool], None]

    toplevel: tk.Toplevel = None
    # A more convenient data structure for entry fields.
    entry_fields: Dict[str, tk_facade.Entry | tk_facade.Checkbutton] = field(
        default_factory=dict, init=False, repr=False
    )

    # noinspection DuplicatedCode
    def __post_init__(self):
        """Create the widgets and closures required for their operation."""
        self.toplevel = tk.Toplevel(self.parent)
        self.toplevel.title(WINDOW_TITLE)
        frames = common.create_body_and_buttonbox(
            self.toplevel, type(self).__name__.lower()
        )
        _, body_frame, buttonbox = frames
        self.create_fields(body_frame)
        self.create_buttons(buttonbox)
        if not self.tmdb_api_key:
            self.toplevel.after(100, self.tmdb_help, None)

    def create_fields(self, body_frame: ttk.Frame):
        """Creates labels and entry fields for the settings dialog.

        Args:
            body_frame:
        """
        input_zone = common.LabelAndField(body_frame)

        # TMDB API key field
        key_field = tk_facade.Entry(API_KEY_TEXT, body_frame)
        self.entry_fields[API_KEY_NAME] = key_field
        key_field.original_value = self.tmdb_api_key
        input_zone.add_entry_row(key_field)
        key_field.widget.bind("<Enter>", self.tmdb_help)

        # 'Use TMDB' checkbutton
        self.entry_fields[USE_TMDB_NAME] = tk_facade.Checkbutton(
            USE_TMDB_TEXT, body_frame
        )
        self.entry_fields[USE_TMDB_NAME].original_value = self.use_tmdb
        input_zone.add_checkbox_row(self.entry_fields[USE_TMDB_NAME])

    # noinspection PyUnusedLocal
    @staticmethod
    def tmdb_help(event):
        """Displays an info dialog explaining how to access TMDB for integrated
        internet access.

        Args:
            event: Not used but needed to match the Tk/Tcl calling signature.
        """
        common.showinfo(API_KEY_TEXT, detail=TMDB_HELP)

    def create_buttons(self, buttonbox: ttk.Frame):
        """Creates buttons for the settings dialog.

        Args:
            buttonbox:
        """
        # noinspection DuplicatedCode
        column_num = itertools.count()
        save_button = common.create_button(
            buttonbox,
            SAVE_TEXT,
            column=next(column_num),
            command=self.save,
            default="disabled",
        )
        common.bind_key(self.toplevel, "<Return>", save_button)
        common.bind_key(self.toplevel, "<KP_Enter>", save_button)

        cancel_button = common.create_button(
            buttonbox,
            CANCEL_TEXT,
            column=next(column_num),
            command=self.destroy,
            default="active",
        )
        common.bind_key(self.toplevel, "<Escape>", cancel_button)
        common.bind_key(self.toplevel, "<Command-.>", cancel_button)

        # Register the save button callback with its many observers.
        for entry_field in self.entry_fields.values():
            entry_field.observer.register(
                partial(self.enable_save_button, save_button),
            )

    # noinspection PyUnusedLocal
    def enable_save_button(self, save_button: ttk.Button, *args, **kwargs):
        """Manages the enabled or disabled state of the save button.

        Args:
            save_button:
            args and kwargs: Needed to match redundant arguments from tkinter.
        """
        state = any(  # pragma no branch
            [entry_field.changed() for entry_field in self.entry_fields.values()]
        )
        common.enable_button(save_button, state=state)

    def save(self):
        """Save the edited preference values to the config file."""
        tmdb_api_key = self.entry_fields[API_KEY_NAME].current_value
        use_tmdb = self.entry_fields[USE_TMDB_NAME].current_value
        # noinspection PyTypeChecker
        self.save_callback(tmdb_api_key, use_tmdb)
        self.destroy()

    def destroy(self):
        """Destroy all widgets of this class."""
        self.toplevel.destroy()
