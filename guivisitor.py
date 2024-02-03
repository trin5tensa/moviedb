"""Visitor pattern for tkinter widgets."""
#  Copyright (c) 2024. Stephen Rigden.
#  Last modified 2/2/24, 1:38 PM by stephen.
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

# todo Test this module
# todo Should the widget instantiation be in this module?


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
class InputWidgetBase:
    """This is the base class for a visitor pattern which helps to polymorphise the byzantine
    Tkinter interface.

    Don't use it directly: Instantiate the subclasses.
    """

    label_text: str
    _original_value: str = ""
    observer: Observer = field(default_factory=Observer, init=False, repr=False)

    # todo Can/Should(?) put and get be replaced by a _current_value with getters amd setters?

    # noinspection PyMissingOrEmptyDocstring
    @property
    def original_value(self):
        raise NotImplementedError

    # noinspection PyMissingOrEmptyDocstring
    @original_value.setter
    def original_value(self, value):
        raise NotImplementedError

    def put(self, value):
        """
        This will fill the input field with the value.

        Args:
            value:
        """
        raise NotImplementedError

    def clear(self):
        """
        This will empty the input field.

        The meaning of 'Empty' is peculiar to the subclass.
        """
        raise NotImplementedError

    def get(self) -> Any:
        """This will return the current contents of the field."""
        raise NotImplementedError


@dataclass
class TextVariableWidget(InputWidgetBase):
    """
    This is a visitor pattern subclass which handles tkinter widgets which set and get field
    contents via tkinter's tk.TextVariable.
    """

    widget: ttk.Entry | ttk.Checkbutton = None
    textvariable: tk.StringVar = field(
        default_factory=tk.StringVar, init=False, repr=False
    )

    def __post_init__(self):
        # self.textvariable = tk.StringVar()
        self.textvariable.trace_add("write", self.observer.notify)

    # noinspection PyMissingOrEmptyDocstring
    @property
    def original_value(self):
        return self._original_value

    # noinspection PyMissingOrEmptyDocstring
    @original_value.setter
    def original_value(self, value):
        self._original_value = value
        self.put(value)

    def put(self, value: str):
        """
        This will fill the input field with the value.

        Args:
            value:
        """
        self.textvariable.set(value)

    def clear(self):
        """This will place a blank string in the input field."""
        self.textvariable.set("")

    def get(self) -> str:
        """This will return the current contents of the input field."""
        return self.textvariable.get()


@dataclass
class GetTextWidget(InputWidgetBase):
    """
    This is a visitor pattern subclass which handles the tkinter widgets which use tkinter's
    replace and get methods for the field contents.
    """

    # todo Why isn't this class notifying its observer like TextVariableWidget?
    widget: tk.Text = None

    # noinspection PyMissingOrEmptyDocstring
    @property
    def original_value(self):
        return self._original_value

    # noinspection PyMissingOrEmptyDocstring
    @original_value.setter
    def original_value(self, value):
        self._original_value = value
        self.put(value)

    def put(self, value: str):
        """
        This will replace the contents of the text field with the value.

        Args:
            value:
        """
        self.widget.replace("1.0", "end", value)

    def clear(self):
        """This will place a blank string in the input field."""
        self.widget.replace("1.0", "end", "")

    def get(self) -> str:
        """
        This will get the current contents of the text field.

        The final newline ('\n') is omitted.
        """
        return self.widget.get("1.0", "end-1c")
