"""Test Module."""

#  Copyright© 2025. Stephen Rigden.
#  Last modified 2/17/25, 1:36 PM by stephen.
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

from unittest.mock import MagicMock

import pytest
from pytest_check import check

import globalconstants
from gui import tk_facade


# noinspection PyMissingOrEmptyDocstring
class TestEntry:
    def test_focus_set(self, monkeypatch, tk):
        # Arrange
        entry_focus_set = MagicMock(name="entry_focus_set")
        entry_select_range = MagicMock(name="entry_select_range")
        entry_icursor = MagicMock(name="entry_icursor")

        monkeypatch.setattr(tk_facade.Entry, "__post_init__", lambda *args: None)
        entry = tk_facade.Entry("", tk)
        entry.widget = MagicMock(name="widget")
        entry.widget.focus_set = entry_focus_set
        entry.widget.select_range = entry_select_range
        entry.widget.icursor = entry_icursor

        # Act
        entry.focus_set()

        # Assert
        with check:
            entry_focus_set.assert_called_once_with()
        with check:
            entry_select_range.assert_called_once_with(0, tk_facade.tk.END)
        with check:
            entry_icursor.assert_called_with(tk_facade.tk.END)


# noinspection PyMissingOrEmptyDocstring
@pytest.fixture
def tk(monkeypatch):
    monkeypatch.setattr(tk_facade, "tk", tk := MagicMock())
    return tk


# noinspection PyMissingOrEmptyDocstring
@pytest.fixture
def ttk(monkeypatch):
    monkeypatch.setattr(tk_facade, "ttk", ttk := MagicMock())
    return ttk


# noinspection PyMissingOrEmptyDocstring
@pytest.fixture
def tk_parent_type(monkeypatch):
    monkeypatch.setattr(globalconstants, "TkParentType", tk_parent_type := MagicMock)
    return tk_parent_type
