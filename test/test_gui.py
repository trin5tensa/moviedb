"""Test Module."""

#  Copyright© 2019. Stephen Rigden.
#  Last modified 11/12/19, 5:07 PM by stephen.
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

from contextlib import contextmanager
from dataclasses import dataclass

import pytest

import gui


class TestRun:
    
    def test_root_window_initialized(self, main_window_patch):
        with self.test_context():
            assert isinstance(gui.config.app.tk_root, DummyTk)

    def test_root_pane_initialized(self, main_window_patch):
        with self.test_context():
            assert isinstance(gui.config.app.root_pane, DummyMainWindow)

    def test_mainloop_called(self, main_window_patch):
        with self.test_context():
            assert gui.config.app.tk_root.mainloop_called

    # noinspection PyMissingOrEmptyDocstring
    @pytest.fixture()
    def main_window_patch(self, monkeypatch):
        monkeypatch.setattr(gui.mainwindow, 'MainWindow', DummyMainWindow)
        monkeypatch.setattr(gui.tk, 'Tk', DummyTk)

    @contextmanager
    def test_context(self):
        app_hold = gui.config.app
        gui.config.app = gui.config.Config('test moviedb', 'test version')
        try:
            yield gui.run()
        finally:
            gui.config.app = app_hold


@dataclass
class DummyMainWindow:
    """Test dummy for application's main window."""
    parent: 'DummyTk'
    
    def __post_init__(self):
        self.parent = DummyTk()


@dataclass
class DummyTk:
    """Test dummy for tkinter module."""
    mainloop_called = False
    
    def mainloop(self):
        """Mock tkinter's main gui loop."""
        self.mainloop_called = True
