"""test_handlers_pbo

This module contains new tests written after Brian Okken's course and book on pytest in Fall 2022.

Test strategies are noted for each class.
"""
#  Copyright (c) 2023. Stephen Rigden.
#  Last modified 3/15/23, 8:13 AM by stephen.
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
from unittest.mock import MagicMock

import mainwindow
from test.dummytk import DummyTk

TEST_TITLE = 'test moviedb'
TEST_VERSION = 'Test version'


class TestMainWindowInit:
    """Ensure that MainWindow is correctly initialized.."""
    tk_root: DummyTk = None
    mock_set_geometry: MagicMock = None
    mock_place_menubar: MagicMock = None

    def test_main_window_initialization(self, monkeypatch, check):
        with self.main_window_context(monkeypatch) as main_window:
            check.equal(self.tk_root.title_calls, [TEST_TITLE])
            check.equal(self.tk_root.geometry_calls, [main_window.set_geometry()])
            check.equal(self.place_menubar.call_count, 1)
            check.equal(self.tk_root.protocol_calls, [('WM_DELETE_WINDOW', main_window.tk_shutdown)])

    # noinspection PyMissingOrEmptyDocstring, PyTypeChecker
    @contextmanager
    def main_window_context(self, monkeypatch):
        persistent_hold = mainwindow.config.persistent
        mainwindow.config.persistent = mainwindow.config.PersistentConfig(TEST_TITLE, TEST_VERSION)
        self.tk_root = DummyTk()
        self.mock_set_geometry = MagicMock()
        monkeypatch.setattr('mainwindow.MainWindow.set_geometry', self.mock_set_geometry)
        self.place_menubar = MagicMock()
        monkeypatch.setattr('mainwindow.MainWindow.place_menubar', self.place_menubar)
        try:
            yield mainwindow.MainWindow(self.tk_root)
        finally:
            mainwindow.config.persistent = persistent_hold


class TestPlaceMenubar:
    """This suite tests the place_menubar and place_menu method."""
    ...
