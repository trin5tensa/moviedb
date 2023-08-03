"""Test Module."""

#  Copyright (c) 2020-2022. Stephen Rigden.
#  Last modified 10/15/22, 12:37 PM by stephen.
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
from dataclasses import dataclass
from typing import Any, Dict, Literal, NewType, Optional

import pytest

import mainwindow

TEST_TITLE = 'test moviedb'
TEST_VERSION = 'Test version'
TEST_MENU = 'Test Menu'

tk_state = NewType('tk_state', Literal['mainwindow.tk.DISABLED', 'mainwindow.tk.NORMAL'])


class TestMainWindowGeometry:
    """This suite of geometry tests operate by assuming the user has moved to a machine with a smaller
    monitor of size 2000×1000. The previous window size is stored in app.geometry. For each test the
    previous size s varied to exercise the various exception conditions which the target code should
    intercept and correct."""
    root_pane: mainwindow.MainWindow = None
    logging_msg: str = None
    
    def test_default_geometry_accepted(self, class_patches):
        with self.geometry_context(desired_geometry=None) as geometry:
            assert geometry == '900x400+30+30'
    
    def test_width_too_large(self, class_patches):
        with self.geometry_context('2900x400+30+30') as geometry:
            assert geometry == '2000x400+0+30'
    
    def test_height_too_large(self, class_patches):
        with self.geometry_context('900x2400+30+30') as geometry:
            assert geometry == '900x1000+30+0'
    
    def test_width_plus_offset_too_large(self, class_patches):
        with self.geometry_context('900x400+2030+30') as geometry:
            assert geometry == '900x400+0+30'
    
    def test_height_plus_offset_too_large(self, class_patches):
        with self.geometry_context('900x400+30+1030') as geometry:
            assert geometry == '900x400+30+0'
    
    def test_info_msg_logged(self, class_patches):
        with self.geometry_context('2900x400+30+30'):
            assert self.logging_msg == ("The saved screen geometry length=2900 and offset=30 is "
                                        "too large for this monitor (available=2000)")
    
    # noinspection PyMissingOrEmptyDocstring
    @pytest.fixture()
    def class_patches(self, monkeypatch):
        monkeypatch.setattr(mainwindow.tk, 'Tk', InstrumentedTk)
        monkeypatch.setattr(mainwindow.logging, 'info', self.save_log_message)
        monkeypatch.setattr(mainwindow.MainWindow, 'place_menubar', lambda *args: None)
    
    # noinspection PyMissingOrEmptyDocstring
    @contextmanager
    def geometry_context(self, desired_geometry):
        persistent_hold = mainwindow.config.persistent
        mainwindow.config.persistent = mainwindow.config.PersistentConfig(TEST_TITLE, TEST_VERSION)
        mainwindow.config.persistent.geometry = desired_geometry
        self.root_pane = mainwindow.MainWindow(mainwindow.tk.Tk())
        try:
            yield self.root_pane.set_geometry()
        finally:
            mainwindow.config.persistent = persistent_hold
    
    def save_log_message(self, msg):
        """Save the arguments to the monkeypatched logging call."""
        self.logging_msg = msg


class TestMainWindowShutdown:
    root_window: mainwindow.MainWindow = None
    
    def test_final_geometry_saved_to_config(self, class_patches):
        with self.shutdown_context():
            assert mainwindow.config.persistent.geometry == '42x42+42+42'
    
    def test_destroy_parent_called(self, class_patches):
        with self.shutdown_context():
            assert self.root_window.parent.destroy_called

    # noinspection PyMissingOrEmptyDocstring
    @pytest.fixture()
    def class_patches(self, monkeypatch):
        monkeypatch.setattr(mainwindow.tk, 'Tk', InstrumentedTk)
        monkeypatch.setattr(mainwindow.MainWindow, 'set_geometry', lambda *args: None)
        monkeypatch.setattr(mainwindow.MainWindow, 'place_menubar', lambda *args: None)

    # noinspection PyMissingOrEmptyDocstring,PyTypeChecker
    @contextmanager
    def shutdown_context(self):
        persistent_hold = mainwindow.config.persistent
        mainwindow.config.persistent = mainwindow.config.PersistentConfig(TEST_TITLE, TEST_VERSION)
        self.root_window = mainwindow.MainWindow(InstrumentedTk())
        self.root_window.tk_shutdown()
        try:
            yield
        finally:
            mainwindow.config.persistent = persistent_hold


# noinspection PyMissingOrEmptyDocstring
@dataclass
class InstrumentedTk:
    """Test dummy for Tk."""
    title_args = None
    option_add_args = None
    geometry_args = None
    protocol_args = None
    bind_args = None
    menu = None
    destroy_called = False
    
    def title(self, *args):
        self.title_args, = args

    def option_add(self, *args):
        self.option_add_args = args

    def geometry(self, *args):
        self.geometry_args = args

    def protocol(self, *args):
        self.protocol_args = args

    def bind(self, *args):
        self.bind_args = args

    def config(self, **kwargs):
        self.menu = kwargs.get('menu')

    def destroy(self):
        self.destroy_called = True

    @staticmethod
    def winfo_screenwidth():
        return '2000'
    
    @staticmethod
    def winfo_screenheight():
        return '1000'
    
    @staticmethod
    def winfo_geometry():
        return '42x42+42+42'


# noinspection PyMissingOrEmptyDocstring
@dataclass
class InstrumentedTtkFrame:
    parent: InstrumentedTk
    # pack_args = None
    pack_args: Optional[Dict[str, Any]] = None
    
    def pack(self, **kwargs):
        self.pack_args = kwargs
