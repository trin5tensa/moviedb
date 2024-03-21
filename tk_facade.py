"""Facade pattern for tkinter widgets."""

#  Copyright (c) 2024-2024. Stephen Rigden.
#  Last modified 3/9/24, 9:39 AM by stephen.
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

# This tkinter import method supports accurate test mocking of tk and ttk.
import tkinter as tk
import tkinter.ttk as ttk

type TkParentType = tk.Tk | tk.Toplevel | ttk.Frame
type TkSequence = list[str] | tuple[str, ...]


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
    parent: TkParentType
    _original_value: Any = field(default=None, init=False, repr=False)
    observer: Observer = field(default_factory=Observer, init=False, repr=False)

    @property
    def original_value(self) -> Any:
        """Returns the original value of the tkinter widget."""
        raise NotImplementedError  # pragma nocover

    @original_value.setter
    def original_value(self, value):
        """Sets the original and current value of the tkinter widget."""
        raise NotImplementedError  # pragma nocover

    @property
    def current_value(self) -> Any:
        """Returns the current value of the tkinter widget."""
        raise NotImplementedError  # pragma nocover

    @current_value.setter
    def current_value(self, value):
        """Sets the current value of the tkinter widget."""
        raise NotImplementedError  # pragma nocover

    def clear_current_value(self):
        """Clears the current value of the tkinter widget"""
        raise NotImplementedError  # pragma nocover

    def has_data(self) -> bool:
        """Returns True if the current_value contains data."""
        raise NotImplementedError  # pragma nocover

    def changed(self) -> bool:
        """Compares the original and current value of the tkinter widget."""
        return self.original_value != self.current_value


@dataclass
class Entry(TkinterFacade):
    """This is a visitor pattern subclass for tkinter's ttk.Entry class."""

    widget: ttk.Entry = None
    _original_value: str = field(default="", init=False, repr=False)
    _textvariable: tk.StringVar = field(
        default_factory=lambda: tk.StringVar(), repr=False
    )

    def __post_init__(self):
        self.widget = ttk.Entry(self.parent)
        self.widget.configure(textvariable=self._textvariable)
        self._textvariable.trace_add("write", self.observer.notify)
        self.original_value = ""

    @property
    def original_value(self) -> str:
        return self._original_value

    @original_value.setter
    def original_value(self, value: str):
        self._original_value = self.current_value = str(value)

    @property
    def current_value(self) -> str:
        return self._textvariable.get()

    @current_value.setter
    def current_value(self, value: str):
        self._textvariable.set(value)

    def clear_current_value(self):
        """Clears the current value of the tkinter widget"""
        self.current_value = ""

    def has_data(self) -> bool:
        return self.current_value != ""


@dataclass
class Text(TkinterFacade):
    """This is a visitor pattern subclass for tkinter's tk.Text class."""

    widget: tk.Text = None
    _original_value: str = field(default="", init=False, repr=False)

    def __post_init__(self):
        self.widget = tk.Text(self.parent)
        self.widget.bind("<<Modified>>", self.modified())
        self.original_value = ""

    @property
    def original_value(self) -> str:
        return self._original_value

    # noinspection PyMissingOrEmptyDocstring
    @original_value.setter
    def original_value(self, value: str):
        self._original_value = self.current_value = value

    @property
    def current_value(self) -> str:
        return self.widget.get("1.0", "end-1c")

    @current_value.setter
    def current_value(self, value: str):
        self.widget.replace("1.0", "end", value)

    def clear_current_value(self):
        """Clears the current value of the tkinter widget"""
        self.current_value = ""

    def modified(self) -> Callable:
        """
        Sets up a callback closure which notifies the observer
        whenever the current value changes.
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
            # Tk/Tcl will not generate subsequent <<Modified>> virtual events if
            # the edit_modified flag is not reset.
            self.widget.edit_modified(False)
            self.observer.notify()

        return func

    def has_data(self) -> bool:
        return self.current_value != ""


@dataclass
class Treeview(TkinterFacade):
    """This is a visitor pattern subclass for tkinter's ttk.Treeview class."""

    widget: ttk.Treeview = None
    _original_value: set = field(default_factory=set, init=False, repr=False)

    def __post_init__(self):
        self.widget = ttk.Treeview(self.parent)
        self.widget.bind(
            "<<TreeviewSelect>>", lambda *args, **kwargs: self.observer.notify()
        )
        self.original_value = []

    @property
    def original_value(self) -> set:
        return self._original_value

    # noinspection PyMissingOrEmptyDocstring
    @original_value.setter
    def original_value(self, values: TkSequence):
        self._original_value = set(values)
        self.current_value = values

    @property
    def current_value(self) -> set:
        return set(self.widget.selection())

    @current_value.setter
    def current_value(self, values: TkSequence):
        self.widget.selection_set(values)

    def clear_current_value(self):
        self.current_value = []

    def has_data(self) -> bool:
        """The current selection is inspected and True is returned if any items are selected."""
        return self.current_value != set()


@dataclass
class Checkbutton(TkinterFacade):
    """This is a visitor pattern subclass for tkinter's ttk.Checkbutton class."""

    widget: ttk.Checkbutton = None
    _original_value: bool = field(default=None, init=False, repr=False)
    _variable: tk.IntVar = field(
        default_factory=lambda: tk.IntVar(), init=False, repr=False
    )

    def __post_init__(self):
        self.widget = ttk.Checkbutton(self.parent)
        self.widget.configure(variable=self._variable)
        self._variable.trace_add("write", self.observer.notify)
        self.original_value = False

    @property
    def original_value(self) -> bool:
        return self._original_value

    @original_value.setter
    def original_value(self, value: bool):
        self._original_value = self.current_value = value

    @property
    def current_value(self) -> bool:
        return bool(self._variable.get())

    @current_value.setter
    def current_value(self, value: bool):
        self._variable.set(value)

    def clear_current_value(self):
        """Clears the current value of the tkinter widget"""
        self.current_value = False
