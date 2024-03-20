"""Test module."""

#  Copyright (c) 2022-2024. Stephen Rigden.
#  Last modified 3/20/24, 2:31 PM by stephen.
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

from contextlib import contextmanager
from typing import Callable, Optional, Type
from unittest.mock import Mock

import pytest

import guiwidgets
import guiwidgets_2
from test.dummytk import (
    DummyTk,
    TkStringVar,
    TkToplevel,
    TtkButton,
    TtkCheckbutton,
    TtkEntry,
    TtkFrame,
    TtkLabel,
    TtkScrollbar,
    TtkTreeview,
)

Exc = Type[Optional[guiwidgets_2.exception.DatabaseSearchFoundNothing]]


# noinspection PyMissingOrEmptyDocstring
@pytest.mark.usefixtures("patch_tk")
class TestFocusSet:
    def test_focus_set_calls_focus_set_on_entry(self, patch_tk):
        with self.focus_set_context() as entry:
            # noinspection PyUnresolvedReferences
            assert entry.focus_set_calls == [True]

    def test_focus_set_calls_select_range_on_entry(self, patch_tk):
        with self.focus_set_context() as entry:
            # noinspection PyUnresolvedReferences
            assert entry.select_range_calls == [(0, "end")]

    def test_focus_set_calls_icursor_on_entry(self, patch_tk):
        with self.focus_set_context() as entry:
            # noinspection PyUnresolvedReferences
            assert entry.icursor_calls == [("end",)]

    @contextmanager
    def focus_set_context(self):
        # noinspection PyTypeChecker
        entry = guiwidgets_2.ttk.Entry(DummyTk())
        guiwidgets_2.focus_set(entry)
        yield entry


# noinspection PyMissingOrEmptyDocstring
@pytest.mark.usefixtures("patch_tk")
class TestCreateButton:
    def test_create_button_grid(self):
        with self.button_context() as button:
            assert button.grid_calls == [dict(column=0, row=0)]

    def test_create_button_bind(self):
        with self.button_context() as button:
            assert button.bind_calls[0][0] == "<Return>"
            assert isinstance(button.bind_calls[0][1], Callable)

    def test_disable_at_initialization(self):
        with self.button_context(default="disabled") as button:
            assert button.default == "disabled"

    @contextmanager
    def button_context(self, default: guiwidgets_2.DefaultLiteral = None):
        buttonbox = TtkFrame(DummyTk())
        text = "Dummy Button"
        column = 0
        # noinspection PyTypeChecker
        yield guiwidgets_2.create_button(
            buttonbox, text, column, lambda: None, default=default
        )


def test_gui_messagebox(monkeypatch):
    calls = []
    monkeypatch.setattr(
        guiwidgets_2.messagebox,
        "showinfo",
        lambda *args, **kwargs: calls.append((args, kwargs)),
    )
    parent = DummyTk()
    message = "test message"
    detail = "test detail"
    # noinspection PyTypeChecker
    guiwidgets_2.gui_messagebox(parent, message, detail)
    assert calls == [((parent, message), dict(detail=detail, icon="info"))]


def test_gui_askopenfilename(monkeypatch):
    calls = []
    monkeypatch.setattr(
        guiwidgets_2.filedialog,
        "askopenfilename",
        lambda **kwargs: calls.append(kwargs),
    )
    parent = DummyTk()
    filetypes = (("test filetypes",),)
    # noinspection PyTypeChecker
    guiwidgets_2.gui_askopenfilename(parent, filetypes)
    assert calls == [(dict(parent=parent, filetypes=filetypes))]


# noinspection PyMissingOrEmptyDocstring
@pytest.fixture
def dummy_entry_fields():
    # noinspection PyProtectedMember
    return dict(tag=guiwidgets_2._EntryField("Tag", ""))


# noinspection PyMissingOrEmptyDocstring
class DummyActivateButton:
    state = None

    def __call__(self, state):
        self.state = state


# noinspection PyMissingOrEmptyDocstring,DuplicatedCode
@pytest.fixture()
def patch_tk(monkeypatch):
    monkeypatch.setattr(guiwidgets_2.tk, "Tk", DummyTk)
    monkeypatch.setattr(guiwidgets_2.tk, "Toplevel", TkToplevel)
    monkeypatch.setattr(guiwidgets_2.tk, "StringVar", TkStringVar)
    monkeypatch.setattr(guiwidgets_2.ttk, "Frame", TtkFrame)
    monkeypatch.setattr(guiwidgets_2.ttk, "Label", TtkLabel)
    monkeypatch.setattr(guiwidgets_2.ttk, "Entry", TtkEntry)
    monkeypatch.setattr(guiwidgets_2.ttk, "Checkbutton", TtkCheckbutton)
    monkeypatch.setattr(guiwidgets_2.ttk, "Button", TtkButton)
    monkeypatch.setattr(guiwidgets_2.ttk, "Treeview", TtkTreeview)
    monkeypatch.setattr(guiwidgets_2.ttk, "Scrollbar", TtkScrollbar)
