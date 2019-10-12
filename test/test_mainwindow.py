"""Test Module."""

#  Copyright© 2019. Stephen Rigden.
#  Last modified 10/12/19, 8:55 AM by stephen.
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

import mainwindow


@pytest.mark.usefixtures('monkeypatch')
class TestMainWindowTkShutdown:
    test_title = 'test moviedb'
    root_window = None
    place_menubar = None
    
    def test_parent_initialized(self, class_patches):
        with self.test_context():
            assert isinstance(self.root_window.parent, InstrumentedTk)
            assert mainwindow.config.app.ttk_main_pane == InstrumentedFrame(parent=InstrumentedTk())
            
    def test_title_set(self, class_patches):
        with self.test_context():
            assert self.root_window.parent.title_args == self.test_title
    
    def test_tear_off_suppressed(self, class_patches):
        with self.test_context():
            assert self.root_window.parent.option_add_args == ('*tearOff', False)
    
    def test_geometry_called(self, class_patches):
        with self.test_context():
            assert self.root_window.parent.geometry_args == ('test geometry args',)
            
    def test_place_menubar_called(self, class_patches):
        with self.test_context():
            assert self.place_menubar == (mainwindow.MenuBar().menus, )
    
    def test_main_pane_geometry_set(self, class_patches):
        with self.test_context():
            assert mainwindow.config.app.ttk_main_pane.pack_args == dict(fill='both', expand=True)
    
    def test_tk_shutdown_protocol_set(self, class_patches):
        with self.test_context():
            assert self.root_window.parent.protocol_args == ('WM_DELETE_WINDOW',
                                                             self.root_window.tk_shutdown)

    # noinspection PyMissingOrEmptyDocstring
    @pytest.fixture()
    def class_patches(self, monkeypatch):
        monkeypatch.setattr(mainwindow.tk, 'Tk', InstrumentedTk)
        monkeypatch.setattr(mainwindow.MainWindow, 'set_geometry', lambda *args: 'test geometry args')
        monkeypatch.setattr(mainwindow.MainWindow, 'place_menubar', self.dummy_place_menubar)
        monkeypatch.setattr(mainwindow.ttk, 'Frame', InstrumentedFrame)

    @contextmanager
    def test_context(self):
        app_hold = mainwindow.config.app
        mainwindow.config.app = mainwindow.config.Config(self.test_title)
        self.root_window = mainwindow.MainWindow()
        try:
            yield
        finally:
            mainwindow.config.app = app_hold

    # noinspection PyMissingOrEmptyDocstring
    def dummy_place_menubar(self, *args):
        self.place_menubar = args


# noinspection PyMissingOrEmptyDocstring
@dataclass
class InstrumentedTk:
    """Test dummy for Tk."""
    title_args = None
    option_add_args = None
    geometry_args = None
    protocol_args = None
    
    def title(self, *args):
        self.title_args, = args
    
    def option_add(self, *args):
        self.option_add_args = args
    
    def geometry(self, *args):
        self.geometry_args = args
    
    def winfo_screenwidth(self, *args):
        pass
    
    def protocol(self, *args):
        self.protocol_args = args


# noinspection PyMissingOrEmptyDocstring
@dataclass
class InstrumentedFrame:
    parent: InstrumentedTk
    pack_args = None
    
    def pack(self, **kwargs):
        self.pack_args = kwargs
