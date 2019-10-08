"""Test Module."""

#  Copyright© 2019. Stephen Rigden.
#  Last modified 10/8/19, 6:57 AM by stephen.
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

from dataclasses import dataclass

import pytest

import gui


@ dataclass
class DummyTk:
    """Test dummy for tkinter module."""
    mainloop_called = False
    
    def mainloop(self):
        """Mock tkinter's main gui loop."""
        self.mainloop_called = True


@dataclass
class DummyMainWindow:
    """Test dummy for application's main window."""
    parent = None
    _tk_init_called = False
    
    def __post_init__(self):
        self.parent = DummyTk()
        self._tk_init_called = True
        

class TestRun:
    @pytest.fixture()
    def test_run_setup(self, monkeypatch):
        monkeypatch.setattr(gui.mainwindow, 'MainWindow', DummyMainWindow)
        gui.config.app = gui.config.Config('test moviedb')
        gui.run()
    
    def test_root_window_initialized(self, test_run_setup):
        assert isinstance(gui.config.app.root_window, DummyMainWindow)
        
    def test_tk_init_called(self, test_run_setup):
        assert gui.config.app.root_window._tk_init_called
        
    def test_mainloop_called(self, test_run_setup):
        assert gui.config.app.root_window.parent.mainloop_called
