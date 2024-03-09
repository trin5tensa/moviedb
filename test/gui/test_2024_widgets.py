"""Test Module."""

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
from contextlib import contextmanager
from unittest.mock import MagicMock, call

import pytest
from pytest_check import check

import guiwidgets_2
from globalconstants import *
from guiwidgets_2 import (
    TITLE_TEXT,
    YEAR_TEXT,
    DIRECTOR_TEXT,
    COMMIT_TEXT,
    DELETE_TEXT,
    MOVIE_DELETE_MESSAGE,
)


class TestAddTagGUI:
    def test_post_init(
        self,
        framing,
    ):
        pass


# noinspection PyMissingOrEmptyDocstring
@pytest.fixture
def mock_tk(monkeypatch):
    monkeypatch.setattr(guiwidgets_2, "tk", mock := MagicMock())
    return mock


# noinspection PyMissingOrEmptyDocstring
@pytest.fixture
def ttk(monkeypatch):
    monkeypatch.setattr(guiwidgets_2, "ttk", mock := MagicMock())
    return mock


# noinspection PyMissingOrEmptyDocstring
@pytest.fixture
def framing(monkeypatch):
    monkeypatch.setattr(guiwidgets_2, "create_input_form_framing", mock := MagicMock())
    mock.return_value = (MagicMock(), MagicMock(), MagicMock())
    return mock


# noinspection PyMissingOrEmptyDocstring
@pytest.fixture
def input_zone(monkeypatch):
    monkeypatch.setattr(guiwidgets_2, "InputZone", mock := MagicMock())
    return mock


# noinspection PyMissingOrEmptyDocstring
@pytest.fixture
def patterns(patterns_entry, patterns_text, patterns_treeview):
    pass


# noinspection PyMissingOrEmptyDocstring
@pytest.fixture
def patterns_entry(monkeypatch):
    monkeypatch.setattr(guiwidgets_2.tk_facade, "Entry", mock := MagicMock())
    return mock


# noinspection PyMissingOrEmptyDocstring
@pytest.fixture
def patterns_text(monkeypatch):
    monkeypatch.setattr(guiwidgets_2.tk_facade, "Text", mock := MagicMock())
    return mock


# noinspection PyMissingOrEmptyDocstring
@pytest.fixture
def patterns_treeview(monkeypatch):
    monkeypatch.setattr(guiwidgets_2.tk_facade, "Treeview", mock := MagicMock())
    return mock


# noinspection PyMissingOrEmptyDocstring
@pytest.fixture
def focus_set(monkeypatch):
    monkeypatch.setattr(guiwidgets_2, "focus_set", mock := MagicMock())
    return mock


# noinspection PyMissingOrEmptyDocstring
@pytest.fixture
def create_button(monkeypatch):
    monkeypatch.setattr(guiwidgets_2, "create_button", mock := MagicMock())
    return mock


# noinspection PyMissingOrEmptyDocstring
@pytest.fixture
def itertools(monkeypatch):
    monkeypatch.setattr(guiwidgets_2, "itertools", mock := MagicMock())
    return mock


# noinspection PyMissingOrEmptyDocstring
@pytest.fixture
def enable_button(monkeypatch):
    monkeypatch.setattr(guiwidgets_2, "enable_button", mock := MagicMock())
    return mock


# noinspection PyMissingOrEmptyDocstring
@pytest.fixture
def messagebox(monkeypatch):
    monkeypatch.setattr(guiwidgets_2, "messagebox", mock := MagicMock())
    return mock
