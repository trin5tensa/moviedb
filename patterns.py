"""Facade pattern for tkinter widgets."""

#  Copyright (c) 2024-2024. Stephen Rigden.
#  Last modified 2/5/24, 8:55 AM by stephen.
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
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any
import tkinter as tk
from tkinter import ttk


@dataclass
class Observer:
    """The classic observer pattern."""

    notifees: list[Callable] = field(default_factory=list, init=False, repr=False)

    def register(self, notifee: Callable):
        """Register a notifee.

        Each registered notifee: Callable will be called whenever the notify method of
        this class is called. The registered notifees will be invoked using the same
        arguments as were supplied to the notify method.

        Args:
            notifee: This callable will be invoked by the notify method with the
            arguments supplied to that method.
        """
        self.notifees.append(notifee)

    def deregister(self, notifee):
        """Remove a notifee.

        Args:
            notifee:
        """
        self.notifees.remove(notifee)

    def notify(self, *args, **kwargs):
        """Call every notifee.

        Args:
            *args: Passed through from triggering event.
            **kwargs: Passed through from triggering event.
        """
        for observer in self.notifees:
            observer(*args, **kwargs)


@dataclass
class TkinterFacade:
    """This is the base class for a visitor pattern which helps to polymorphise the byzantine
    Tkinter interface.

    Don't use it directly: Instantiate the subclasses.

    The facade classes are responsible for:
        Maintaining original and current values. The value is specific to the subclass. For
        subclasses typically used with Ttk.Entry widgets the value may be a string class whereas
        for subclasses typically used with Ttk.Treeview the value may be a the current
        selection list.
        Implementing the Tk/Tcl callback including updating the current value and notifying the
        observer.
    """

    label_text: str
    widget: Any
    _original_value: str = None
    _current_value: str = None
    observer: Observer = field(default_factory=Observer, init=False, repr=False)

    @property
    def original_value(self) -> Any:
        """Returns the original value of the tkinter widget."""
        raise NotImplementedError

    @original_value.setter
    def original_value(self, value):
        """Sets the original value of the tkinter widget."""
        raise NotImplementedError

    @property
    def current_value(self) -> Any:
        """Returns the current value of the tkinter widget."""
        raise NotImplementedError

    @current_value.setter
    def current_value(self, value):
        """Sets the current value of the tkinter widget."""
        raise NotImplementedError

    def clear_current_value(self):
        """Clears the current value of the tkinter widget"""
        raise NotImplementedError

    def changed(self) -> bool:
        """Compares the original and current value of the tkinter widget."""
        return self.original_value != self.current_value


@dataclass
class TextVariableWidget(TkinterFacade):
    """
    This is a visitor pattern subclass which handles tkinter widgets which set and get field
    contents via tkinter's tk.TextVariable.
    """

    widget: ttk.Entry | ttk.Checkbutton
    _textvariable: tk.StringVar = field(
        default_factory=tk.StringVar, init=False, repr=False
    )

    def __post_init__(self):
        self.widget.configure(textvariable=self._textvariable)
        self._textvariable.trace_add("write", self.observer.notify)
        self.original_value = ""
        self.current_value = ""

    @property
    def original_value(self) -> str:
        return self._original_value

    @original_value.setter
    def original_value(self, value: str):
        self._original_value = str(value)
        self.current_value = str(value)

    @property
    def current_value(self) -> str:
        return self._textvariable.get()

    @current_value.setter
    def current_value(self, value: str):
        self._textvariable.set(value)

    def clear_current_value(self):
        self.current_value = ""


@dataclass
class GetTextWidget(TkinterFacade):
    """
    This is a visitor pattern subclass which handles the tkinter widgets which use tkinter's
    replace and get methods for the field contents.
    """

    widget: tk.Text

    def __post_init__(self):
        self.original_value = ""
        self.widget.bind("<<Modified>>", self.changed_callback())

    @property
    def original_value(self) -> str:
        return self._original_value

    # noinspection PyMissingOrEmptyDocstring
    @original_value.setter
    def original_value(self, value: str):
        self._original_value = str(value)
        self.current_value = value

    @property
    def current_value(self) -> str:
        return self.widget.get("1.0", "end-1c")

    @current_value.setter
    def current_value(self, value: str):
        self.widget.replace("1.0", "end", value)

    def clear_current_value(self):
        self.current_value = ""

    def changed_callback(self) -> Callable:
        """
        test_modified sets up a callback closure which notifies the notes observer
        whenever the contents of the notes field change.
        """

        # noinspection PyUnusedLocal
        def func(*args, **kwargs):
            """
            This closure notifies the notes observer whenever the contents of the notes
            field change.

            Args:
                *args: Not used but needed for compatibility with Tk?Tcl caller
                **kwargs: Not used but needed for compatibility with Tk?Tcl caller
            """
            # Tk/Tcl will not generate subsequent <<Modified>> virtual events if edit_modified is
            # not reset.
            self.widget.edit_modified(False)
            self.observer.notify()

        return func
