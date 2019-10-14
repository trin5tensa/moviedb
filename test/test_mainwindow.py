"""Test Module."""

#  Copyright© 2019. Stephen Rigden.
#  Last modified 10/14/19, 8:55 AM by stephen.
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
class TestMainWindowInit:
    """Ensure that MainWindow is correctly initialized.."""
    test_title = 'test moviedb'
    root_window = None
    place_menubar = None
    
    def test_parent_initialized(self, class_patches):
        with self.context():
            assert isinstance(self.root_window.parent, InstrumentedTk)
            assert mainwindow.config.app.ttk_main_pane == InstrumentedFrame(parent=InstrumentedTk())
    
    def test_title_set(self, class_patches):
        with self.context():
            assert self.root_window.parent.title_args == self.test_title
    
    def test_tear_off_suppressed(self, class_patches):
        with self.context():
            assert self.root_window.parent.option_add_args == ('*tearOff', False)
    
    def test_geometry_called(self, class_patches):
        with self.context():
            assert self.root_window.parent.geometry_args == ('test geometry args',)
            
    def test_place_menubar_called(self, class_patches):
        with self.context():
            assert self.place_menubar == (mainwindow.MenuBar().menus,)
    
    def test_main_pane_geometry_set(self, class_patches):
        with self.context():
            assert mainwindow.config.app.ttk_main_pane.pack_args == dict(fill='both', expand=True)
    
    def test_tk_shutdown_protocol_set(self, class_patches):
        with self.context():
            assert self.root_window.parent.protocol_args == ('WM_DELETE_WINDOW',
                                                             self.root_window.tk_shutdown)

    # noinspection PyMissingOrEmptyDocstring
    @pytest.fixture()
    def class_patches(self, monkeypatch):
        monkeypatch.setattr(mainwindow.tk, 'Tk', InstrumentedTk)
        monkeypatch.setattr(mainwindow.MainWindow, 'set_geometry', lambda *args: 'test geometry args')
        monkeypatch.setattr(mainwindow.MainWindow, 'place_menubar', self.dummy_place_menubar)
        monkeypatch.setattr(mainwindow.ttk, 'Frame', InstrumentedFrame)
    
    # noinspection PyMissingOrEmptyDocstring
    @contextmanager
    def context(self):
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


@pytest.mark.usefixtures('monkeypatch')
class TestMainWindowGeometry:
    """This suite of geometry tests operate by assuming the user has moved to a machine with a smaller
    monitor of size 2000x1000. The previous window size is stored in app.geometry. For each test the
    previous size s varied to exercise the various exception conditions which the target code should
    intercept and correct."""
    
    def test_default_geometry_accepted(self, class_patches):
        with self.context(desired_geometry=None) as geometry:
            assert geometry == '900x400+30+30'
    
    def test_width_too_large(self, class_patches):
        with self.context('2900x400+30+30') as geometry:
            assert geometry == '2000x400+0+30'
    
    def test_height_too_large(self, class_patches):
        with self.context('900x2400+30+30') as geometry:
            assert geometry == '900x1000+30+0'
    
    def test_width_plus_offset_too_large(self, class_patches):
        with self.context('900x400+2030+30') as geometry:
            assert geometry == '900x400+0+30'
    
    def test_height_plus_offset_too_large(self, class_patches):
        with self.context('900x400+30+1030') as geometry:
            assert geometry == '900x400+30+0'
    
    # noinspection PyMissingOrEmptyDocstring
    @pytest.fixture()
    def class_patches(self, monkeypatch):
        monkeypatch.setattr(mainwindow.tk, 'Tk', InstrumentedTk)
        monkeypatch.setattr(mainwindow.MainWindow, 'place_menubar', lambda *args: None)
        monkeypatch.setattr(mainwindow.ttk, 'Frame', InstrumentedFrame)
    
    # noinspection PyMissingOrEmptyDocstring
    @contextmanager
    def context(self, desired_geometry):
        app_hold = mainwindow.config.app
        mainwindow.config.app = mainwindow.config.Config('test name')
        mainwindow.config.app.geometry = desired_geometry
        self.root_window = mainwindow.MainWindow()
        try:
            yield self.root_window.set_geometry()
        finally:
            mainwindow.config.app = app_hold


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
    
    def protocol(self, *args):
        self.protocol_args = args
    
    @staticmethod
    def winfo_screenwidth():
        return '2000'
    
    @staticmethod
    def winfo_screenheight():
        return '1000'


# noinspection PyMissingOrEmptyDocstring
@dataclass
class InstrumentedFrame:
    parent: InstrumentedTk
    pack_args = None
    
    def pack(self, **kwargs):
        self.pack_args = kwargs
