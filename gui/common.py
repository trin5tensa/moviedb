""" This module contains common code to support gui API modules."""

#  Copyright© 2025. Stephen Rigden.
#  Last modified 2/21/25, 10:26 AM by stephen.
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
from functools import partial
from typing import Literal

import config
from gui import tk_facade

DefaultLiteral = Literal["normal", "active", "disabled"]

type TkParentType = tk.Tk | tk.Toplevel | ttk.Frame


def create_two_frame_form(
    parent: TkParentType, name: str, destroy: Callable
) -> tuple[ttk.Frame, ttk.Frame, ttk.Frame]:
    """Creates the outer frames for an input form.

    outer frame
        - body frame
        - buttonbox

    Note: Do not call this function if the input form has label and entry
    widgets. Use the higher level function create_input_form_framing which
    creates two columns within the body frame.

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
    config.current.escape_key_dict[name] = destroy

    body_frame = ttk.Frame(outer_frame, padding=(10, 25, 10, 0))
    body_frame.grid(column=0, row=0, sticky="n")

    buttonbox = ttk.Frame(outer_frame, padding=(5, 5, 10, 10))
    buttonbox.grid(column=0, row=1, sticky="e")

    return outer_frame, body_frame, buttonbox


def create_columnar_form(
    parent: TkParentType, name: str, destroy: Callable
) -> tuple[ttk.Frame, ttk.Frame, ttk.Frame]:
    """Creates the outer frames for an input form.

    An input body frame has two columns, one for the field labels and one for the
    entry fields.

    Note: For a plain form without columns call the lower level function
    create_body_and_button_frames.

    Args:
        parent: The Tk parent frame.
        name: Name which identifies which moviedb class has the destroy method.
        destroy:

    Returns:
        Outer frame which contains the body and buttonbox frames.
        Body frame
        Buttonbox frame
    """
    outer_frame, body_frame, buttonbox = create_two_frame_form(parent, name, destroy)
    outer_frame.rowconfigure(0, weight=1)
    outer_frame.rowconfigure(1, minsize=35)
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
