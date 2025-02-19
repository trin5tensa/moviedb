"""Test module."""

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


import pytest

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


# # noinspection PyMissingOrEmptyDocstring
# @pytest.fixture
# def dummy_entry_fields():
#     # noinspection PyProtectedMember
#     return dict(tag=guiwidgets_2._EntryField("Tag", ""))


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
