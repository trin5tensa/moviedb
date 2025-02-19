""" This module contains common code to support the other gui modules."""

#  Copyright© 2025. Stephen Rigden.
#  Last modified 2/19/25, 7:15 AM by stephen.
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
import tkinter.ttk as ttk
from collections.abc import Callable
from functools import partial
from typing import Literal

from gui import tk_facade

DefaultLiteral = Literal["normal", "active", "disabled"]


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
