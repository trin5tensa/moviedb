""" This module contains common code to support gui API modules."""

#  Copyright© 2025. Stephen Rigden.
#  Last modified 3/3/25, 12:52 PM by stephen.
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

#  Copyright© 2025. Stephen Rigden.
#  Last modified 2/22/25, 12:30 PM by stephen.
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
from dataclasses import field, dataclass
from functools import partial
from typing import Literal, Iterator, Sequence

import config
from gui import tk_facade

COMMIT_TEXT = "Commit"
CANCEL_TEXT = "Cancel"
DELETE_TEXT = "Delete"
SEARCH_TEXT = "Search"

DefaultLiteral = Literal["normal", "active", "disabled"]

type TkParentType = tk.Tk | tk.Toplevel | ttk.Frame


@dataclass
class LabelAndField:
    """Configures a parent frame with two columns for labels and data
    entry widgets.
    """

    parent: TkParentType
    row: Iterator = field(default=None, init=False, repr=False)

    col_0_width: int = 30
    col_1_width: int = 36

    def __post_init__(self):
        """Create two columns within the parent frame."""
        self.row = itertools.count()

        # Create a column for the labels.
        self.parent.columnconfigure(0, weight=1, minsize=self.col_0_width)
        # Create a column for the fields.
        self.parent.columnconfigure(1, weight=1)
        # Create a column for scrollbars.
        self.parent.columnconfigure(2, weight=1)

    def add_entry_row(self, entry_field: tk_facade.Entry):
        """Adds a label and an entry field as the bottom row in the form.

        Args:
            entry_field:
        """
        row_ix = next(self.row)
        self.create_label(entry_field.label_text, row_ix)
        entry_field.widget.configure(width=self.col_1_width)
        entry_field.widget.grid(column=1, row=row_ix)

    def add_text_row(self, entry_field: tk_facade.Text):
        """Adds a label and a text field as the bottom row in the form.

        Args:
            entry_field:
        """
        row_ix = next(self.row)
        self.create_label(entry_field.label_text, row_ix)

        entry_field.widget.configure(
            width=self.col_1_width - 2,
            height=8,
            wrap="word",
            font="TkTextFont",
            padx=15,
            pady=10,
        )
        entry_field.widget.grid(column=1, row=row_ix, sticky="e")

        scrollbar = ttk.Scrollbar(
            self.parent,
            orient="vertical",
            command=entry_field.widget.yview,
        )
        entry_field.widget.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(column=2, row=row_ix, sticky="ns")

    def add_checkbox_row(self, entry_field: tk_facade.Checkbutton):
        """Adds a label and a checkbox as the bottom row in the form.

        Checkbutton has a 'command' parameter used for callbacks.
        For consistency with other widgets this method will use the text
        variable via link_field_to_neuron. This link is set up by the caller.

        Args:
            entry_field:
        """
        row_ix = next(self.row)
        entry_field.widget.configure(
            text=entry_field.label_text, width=self.col_1_width
        )
        entry_field.widget.grid(column=1, row=row_ix)

    def add_treeview_row(
        self,
        entry_field: tk_facade,
        all_tags: Sequence[str],
    ):
        """Adds a label and a treeview as the bottom row in the form.

        Args:
            entry_field:
            all_tags:
        """
        row_ix = next(self.row)
        self.create_label(entry_field.label_text, row_ix)

        entry_field.widget.configure(
            columns=("tags",),
            height=7,
            selectmode="extended",
            show="tree",
            padding=5,
        )
        entry_field.widget.column("tags", width=127)
        for item in all_tags:
            if item:  # pragma no branch
                entry_field.widget.insert(
                    "",
                    "end",
                    item,
                    text=item,
                    tags="tags",
                )
        entry_field.widget.grid(column=1, row=row_ix, sticky="e")

        scrollbar = ttk.Scrollbar(
            self.parent, orient="vertical", command=entry_field.widget.yview
        )
        entry_field.widget.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(column=2, row=row_ix, sticky="ns")

    def create_label(self, text: str, row_ix: int):
        """Creates a label for the current row.

        Args:
            text:
            row_ix: The row into which the label will be placed.
        """

        label = ttk.Label(self.parent, text=text)
        label.grid(column=0, row=row_ix, sticky="ne", padx=5)


def create_body_and_buttonbox(
    parent: TkParentType, name: str, destroy: Callable
) -> tuple[ttk.Frame, ttk.Frame, ttk.Frame]:
    """Creates the frames for an input form.

    outer frame.
    In row 1: body frame.
    In row 2: buttonbox.

    The outer frame will occupy the full width and height of the parent. The
    buttonbox will be a minimum height of 35 pixels and will occupy the full
    width of the outer frame. The body frame will occupy the full height of
    the remaining space inside the outer frame and its full width.

    Args:
        parent: The Tk parent frame.
        name: Name which identifies which moviedb class has the destroy method.
        destroy:

    Returns:
        Outer frame which contains the body and buttonbox frames.
        Body frame
        Buttonbox frame
    """
    outer_frame = ttk.Frame(parent, name=name)
    outer_frame.grid(column=0, row=0, sticky="nsew")
    outer_frame.columnconfigure(0, weight=1)
    outer_frame.rowconfigure(0, weight=1)
    outer_frame.rowconfigure(1, minsize=35)
    config.current.escape_key_dict[name] = destroy

    body_frame = ttk.Frame(outer_frame, padding=(10, 25, 10, 0))
    body_frame.grid(column=0, row=0, sticky="n")

    buttonbox = ttk.Frame(outer_frame, padding=(5, 5, 10, 10))
    buttonbox.grid(column=0, row=1, sticky="e")

    return outer_frame, body_frame, buttonbox


def create_button(
    buttonbox: ttk.Frame,
    text: str,
    column: int,
    command: Callable,
    default: DefaultLiteral,
) -> ttk.Button:
    """Creates a button.

    Args: The following arguments are the Tkinter arguments for a ttk.Button.
        buttonbox:
        text:
        column:
        command:
        default:

    Returns:
        The TTK.Button object.
    """
    button = ttk.Button(
        buttonbox,
        text=text,
        default=default,
        command=command,
    )
    button.grid(column=column, row=0)
    button.bind("<Return>", partial(invoke_button, button))
    return button


def enable_button(button: ttk.Button, *, state: bool):
    """
    Enable or disable a button.

    Args:
        button:
        state:
    """
    if state:
        button.state(["!disabled"])
        # Highlight the button to show it is enabled
        button.configure(default="active")

    else:
        button.state(["disabled"])
        # Remove the button highlight
        button.configure(default="disabled")


# noinspection PyUnusedLocal
def invoke_button(button: ttk.Button, *args):
    """Invokes the command registered to the button.

    Args:
        button
        args: Not used but needed to match Tkinter's calling signature.
    """
    button.invoke()


def init_button_enablements(entry_fields: tk_facade.EntryFields):
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
