"""Test Module."""

#  Copyright© 2019. Stephen Rigden.
#  Last modified 12/19/19, 8:26 AM by stephen.
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
from dataclasses import dataclass, field

import pytest

import gui


class TestRun:
    
    def test_root_window_initialized(self, class_patches):
        with self.run_gui_context() as app:
            assert isinstance(app.tk_root, DummyTk)
    
    def test_parent_column_configured(self, class_patches):
        with self.run_gui_context() as app:
            assert app.tk_root.columnconfigure_calls == [((0,), dict(weight=1)), ]
    
    def test_parent_row_configured(self, class_patches):
        with self.run_gui_context() as app:
            assert app.tk_root.rowconfigure_calls == [((0,), dict(weight=1)), ]
    
    def test_root_pane_initialized(self, class_patches):
        with self.run_gui_context() as app:
            assert isinstance(app.gui_environment, DummyMainWindow)
    
    def test_mainloop_called(self, class_patches):
        with self.run_gui_context() as app:
            assert app.tk_root.mainloop_called == [True]
    
    # noinspection PyMissingOrEmptyDocstring
    @pytest.fixture()
    def class_patches(self, monkeypatch):
        monkeypatch.setattr(gui.mainwindow, 'MainWindow', DummyMainWindow)
        monkeypatch.setattr(gui.tk, 'Tk', DummyTk)
    
    # noinspection PyMissingOrEmptyDocstring
    @contextmanager
    def run_gui_context(self):
        app_hold = gui.config.app
        try:
            gui.config.app = gui.config.Config('test moviedb', 'test version')
            gui.run()
            yield gui.config.app
        finally:
            gui.config.app = app_hold


@dataclass
class DummyMainWindow:
    """Test dummy for application's main window."""
    parent: 'DummyTk'


# noinspection PyMissingOrEmptyDocstring
@dataclass
class DummyTk:
    """Test dummy for tkinter module."""
    columnconfigure_calls: list = field(default_factory=list, init=False, repr=False, compare=False)
    rowconfigure_calls: list = field(default_factory=list, init=False, repr=False, compare=False)
    mainloop_called: list = field(default_factory=list, init=False, repr=False, compare=False)
    
    def mainloop(self):
        self.mainloop_called.append(True)
    
    def columnconfigure(self, *args, **kwargs):
        print(f"{self.columnconfigure_calls=}")
        self.columnconfigure_calls.append((args, kwargs))
    
    def rowconfigure(self, *args, **kwargs):
        self.rowconfigure_calls.append((args, kwargs))
