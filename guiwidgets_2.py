"""GUI Windows.

This module includes windows for presenting data and returning entered data to its callers.
"""

#  Copyright© 2025. Stephen Rigden.
#  Last modified 4/1/25, 8:24 AM by stephen.
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

import itertools
import logging
import queue

from tkinter import filedialog, messagebox

# noinspection PyUnresolvedReferences
from dataclasses import dataclass, field
from typing import (
    Callable,
    Dict,
    Iterable,
    Literal,
    Optional,
    Union,
    Sequence,
)

import config
from gui import tk_facade, common
from globalconstants import *

# noinspection DuplicatedCode
TITLE_TEXT = "Title"
YEAR_TEXT = "Year"
DIRECTORS_TEXT = "Directors"
DURATION_TEXT = "Runtime"
NOTES_TEXT = "Notes"
MOVIE_TAGS_TEXT = "Tags"
SEARCH_TEXT = "Search"
COMMIT_TEXT = "Commit"
SAVE_TEXT = "Save"
DELETE_TEXT = "Delete"
CANCEL_TEXT = "Cancel"

MOVIE_DELETE_MESSAGE = "Do you want to delete this movie?"
TAG_DELETE_MESSAGE = "Do you want to delete this tag?"
NO_MATCH_MESSAGE = "No matches"
NO_MATCH_DETAIL = "There are no matching tags in the database."
UNEXPECTED_KEY = "Unexpected key"

DefaultLiteral = Literal["normal", "active", "disabled"]
StateFlags = Optional[list[Literal["active", "normal", "disabled", "!disabled"]]]


@dataclass
class PreferencesGUI:
    """Create and manage a Tk input form which allows the user to update
    program preferences."""

    parent: tk.Tk

    # Preference fields
    api_key: str
    do_not_ask: bool

    # On commit this callback will be called with the updated preferences.
    save_callback: Callable[[str, bool], None]

    # Internal field names and associated GUI texts.
    api_key_name = "api_key"
    api_key_text = "TMDB API key"
    use_tmdb_name = "use_tmdb"
    use_tmdb_text = "Use TMDB (The Movie Database)"

    toplevel: tk.Toplevel = None
    # A more convenient data structure for entry fields.
    entry_fields: Dict[str, Union[tk_facade.Entry, tk_facade.Checkbutton]] = field(
        default_factory=dict, init=False, repr=False
    )

    # noinspection DuplicatedCode
    def __post_init__(self):
        """Create the widgets and closures required for their operation."""
        # Create a toplevel window
        self.toplevel = tk.Toplevel(self.parent)

        # Create outer frames to hold fields and buttons.
        frames = common.create_body_and_buttonbox(
            self.toplevel, type(self).__name__.lower(), self.destroy
        )
        self.outer_frame, body_frame, buttonbox = frames
        input_zone = common.LabelAndField(body_frame)

        # TMDB API key field
        self.entry_fields[self.api_key_name] = tk_facade.Entry(
            self.api_key_text, body_frame
        )
        self.entry_fields[self.api_key_name].original_value = self.api_key
        input_zone.add_entry_row(self.entry_fields[self.api_key_name])

        # 'Use TMDB' checkbutton
        self.entry_fields[self.use_tmdb_name] = tk_facade.Checkbutton(
            self.use_tmdb_text, body_frame
        )
        self.entry_fields[self.use_tmdb_name].original_value = self.do_not_ask
        input_zone.add_checkbox_row(self.entry_fields[self.use_tmdb_name])

        # Create buttons
        column_num = itertools.count()
        save_button = common.create_button(
            buttonbox,
            SAVE_TEXT,
            column=next(column_num),
            command=self.save,
            default="disabled",
        )
        common.create_button(
            buttonbox,
            CANCEL_TEXT,
            column=next(column_num),
            command=self.destroy,
            default="active",
        )

        # Register the save button callback with its many observers.
        for entry_field in self.entry_fields.values():
            entry_field.observer.register(
                self.enable_save_button(save_button),
            )

    def enable_save_button(self, save_button: ttk.Button) -> Callable:
        """Manages the enabled or disabled state of the save button.

        Args:
            save_button:

        Returns:
            A callable which will be invoked by tkinter whenever the api_key or
            use_tmdb field contents are changed by the user,
        """

        # noinspection PyUnusedLocal
        def func(*args, **kwargs):
            """This function enables or disables the save button depending on the
            state of fields compared to their original values.

            Args:
                *args: Sent by tkinter callback but not used.
                **kwargs: Sent by tkinter callback but not used.
            """
            state = any(  # pragma no branch
                [entry_field.changed() for entry_field in self.entry_fields.values()]
            )
            common.enable_button(save_button, state=state)

        return func

    def save(self):
        """Save the edited preference values to the config file."""
        tmdb_api_key: str = self.entry_fields[self.api_key_name].current_value
        # noinspection PyTypeChecker
        tmdb_do_not_ask_again: bool = self.entry_fields[
            self.use_tmdb_name
        ].current_value
        self.save_callback(tmdb_api_key, tmdb_do_not_ask_again)
        self.destroy()

    def destroy(self):
        """Destroy all widgets of this class."""
        self.toplevel.destroy()


def gui_messagebox(
    parent: TkParentType, message: str, detail: str = "", icon: str = "info"
):
    """Present a Tk messagebox."""
    # noinspection PyTypeChecker
    messagebox.showinfo(parent, message, detail=detail, icon=icon)


def gui_askyesno(
    parent: TkParentType,
    message: str,
    detail: str = "",
    icon: str = "question",
    default="no",
) -> bool:
    """
    Present a Tk askyesno dialog.

    Args:
        default:
        parent:
        message:
        detail:
        icon:

    Returns:
        True if user clicks 'Yes', False if user clicks 'No'
    """
    # noinspection PyTypeChecker
    return messagebox.askyesno(
        parent, message, detail=detail, icon=icon, default=default
    )


# todo remove this unused function
def gui_askopenfilename(
    parent: TkParentType,
    filetypes: Iterable[tuple[str, str | list[str] | tuple[str, ...]]] | None,
):
    """Present a Tk askopenfilename."""
    return filedialog.askopenfilename(parent=parent, filetypes=filetypes)
