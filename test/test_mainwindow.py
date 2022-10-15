"""Test Module."""

#  Copyright (c) 2020. Stephen Rigden.
#  Last modified 12/3/20, 6:43 AM by stephen.
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
from typing import Any, Callable, Dict, List, Literal, NewType, Optional, Tuple

import pytest

import mainwindow


TEST_TITLE = 'test moviedb'
TEST_VERSION = 'Test version'
TEST_MENU = 'Test Menu'

tk_state = NewType('tk_state', Literal['mainwindow.tk.DISABLED', 'mainwindow.tk.NORMAL'])


class TestMainWindowInit:
    """Ensure that MainWindow is correctly initialized.."""
    root_pane: mainwindow.MainWindow = None
    place_menubar = None
    
    def test_title_set(self, class_patches):
        with self.init_context():
            assert self.root_pane.parent.title_args == TEST_TITLE

    def test_tear_off_suppressed(self, class_patches):
        with self.init_context():
            assert self.root_pane.parent.option_add_args == ('*tearOff', False)

    def test_geometry_called(self, class_patches):
        with self.init_context():
            assert self.root_pane.parent.geometry_args == ('test geometry args',)

    def test_place_menubar_called(self, class_patches):
        with self.init_context():
            assert self.place_menubar == (mainwindow.MenuData().menus,)

    def test_bind_escape(self, class_patches):
        with self.init_context():
            assert self.root_pane.parent.bind_args == ('<Escape>', self.root_pane.tk_shutdown)

    def test_tk_shutdown_protocol_set(self, class_patches):
        with self.init_context():
            assert self.root_pane.parent.protocol_args == ('WM_DELETE_WINDOW',
                                                           self.root_pane.tk_shutdown)

    # noinspection PyMissingOrEmptyDocstring
    @pytest.fixture()
    def class_patches(self, monkeypatch):
        monkeypatch.setattr(mainwindow.tk, 'Tk', InstrumentedTk)
        monkeypatch.setattr(mainwindow.MainWindow, 'set_geometry', lambda *args: 'test geometry args')
        monkeypatch.setattr(mainwindow.MainWindow, 'place_menubar', self.dummy_place_menubar)

    # noinspection PyMissingOrEmptyDocstring, PyTypeChecker
    @contextmanager
    def init_context(self):
        app_hold = mainwindow.config.app
        mainwindow.config.app = mainwindow.config.Config(TEST_TITLE, TEST_VERSION)
        self.tk_root = InstrumentedTk()
        self.root_pane = mainwindow.MainWindow(self.tk_root)
        try:
            yield
        finally:
            mainwindow.config.app = app_hold
    
    # noinspection PyMissingOrEmptyDocstring
    def dummy_place_menubar(self, *args):
        self.place_menubar = args


class TestMainWindowGeometry:
    """This suite of geometry tests operate by assuming the user has moved to a machine with a smaller
    monitor of size 2000x1000. The previous window size is stored in app.geometry. For each test the
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
        app_hold = mainwindow.config.app
        mainwindow.config.app = mainwindow.config.Config(TEST_TITLE, TEST_VERSION)
        mainwindow.config.app.geometry = desired_geometry
        self.root_pane = mainwindow.MainWindow(mainwindow.tk.Tk())
        try:
            yield self.root_pane.set_geometry()
        finally:
            mainwindow.config.app = app_hold
    
    def save_log_message(self, msg):
        """Save the arguments to the monkeypatched logging call."""
        self.logging_msg = msg


class TestMainWindowPlaceMenuBar:
    """This suite tests the place_menubar and place_menu methods. A dummy menu list is
    used to every option available."""
    root_pane: mainwindow.MainWindow = None
    logging_msg: str = None
    
    def test_tk_menubar_added_to_parent(self, class_patches):
        with self.menu_context():
            # Is the menubar an InstrumentedTkMenu object?
            assert isinstance(self.root_pane.parent.menu, InstrumentedTkMenu)
            # Does the menubar have tk.Tk as its parent?
            assert self.root_pane.parent.menu.menu.parent == self.root_pane.parent.menu
    
    def test_add_separator_called(self, class_patches):
        with self.menu_context():
            assert self.root_pane.parent.menu.menu.add_separator_called
    
    def test_add_command_called_for_menu_item_with_handler(self, class_patches):
        with self.menu_context():
            label, command, _ = self.root_pane.parent.menu.menu.menu_items[1]
            assert label == 'Item 1'
            assert command() == 'Item 1 handler'
    
    def test_entryconfig_called_for_active_menu_item(self, class_patches):
        with self.menu_context():
            _, _, state = self.root_pane.parent.menu.menu.menu_items[1]
            assert state == 'normal'
    
    def test_entryconfig_called_for_inactive_menu_item(self, class_patches):
        with self.menu_context():
            label, command, state = self.root_pane.parent.menu.menu.menu_items[2]
            assert label == 'Item 2'
            assert command() == 'Item 2 handler'
            assert state == 'disabled'
    
    def test_add_command_called_for_menu_item_without_handler(self, class_patches):
        with self.menu_context():
            label, command, state = self.root_pane.parent.menu.menu.menu_items[3]
            assert label == 'Item 3'
            assert command is None
            assert state == 'disabled'

    def test_add_command_called_for_menu_item_with_uncallable_handler(self, class_patches):
        with self.menu_context():
            label, command, state = self.root_pane.parent.menu.menu.menu_items[4]
            assert label == 'Item 4'
            assert command is None
            assert state == 'disabled'
            assert self.logging_msg == ("The menu item 'menu_item.name='Item 4'' is not a separator "
                                        "and does not contain a callable handler.")

    def test_add_command_called_for_quit_menu_item(self, class_patches):
        with self.menu_context():
            label, command, state = self.root_pane.parent.menu.menu.menu_items[5]
            assert label == 'Quit Test Moviedb'
            assert command == self.root_pane.tk_shutdown
            assert state == 'normal'

    def test_menu_added_to_menubar(self, class_patches):
        with self.menu_context():
            assert self.root_pane.parent.menu.label == TEST_MENU

    # noinspection PyMissingOrEmptyDocstring
    @pytest.fixture()
    def class_patches(self, monkeypatch):
        monkeypatch.setattr(mainwindow.tk, 'Tk', InstrumentedTk)
        monkeypatch.setattr(mainwindow.tk, 'Menu', InstrumentedTkMenu)
        monkeypatch.setattr(mainwindow, 'MenuData', DummyMenuData)
        monkeypatch.setattr(mainwindow.tk, 'NORMAL', 'normal')
        monkeypatch.setattr(mainwindow.tk, 'DISABLED', 'disabled')
        monkeypatch.setattr(mainwindow.MainWindow, 'set_geometry', lambda *args: None)
        monkeypatch.setattr(mainwindow.logging, 'error', self.save_log_message)
    
    # noinspection PyMissingOrEmptyDocstring
    @contextmanager
    def menu_context(self):
        app_hold = mainwindow.config.app
        mainwindow.config.app = mainwindow.config.Config(TEST_TITLE, TEST_VERSION)
        self.root_pane = mainwindow.MainWindow(mainwindow.tk.Tk())
        try:
            yield
        finally:
            mainwindow.config.app = app_hold
    
    def save_log_message(self, msg):
        """Save the arguments to the monkeypatched logging call."""
        self.logging_msg = msg


class TestMainWindowShutdown:
    root_window: mainwindow.MainWindow = None
    
    def test_final_geometry_saved_to_config(self, class_patches):
        with self.shutdown_context():
            assert mainwindow.config.app.geometry == '42x42+42+42'
    
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
        app_hold = mainwindow.config.app
        mainwindow.config.app = mainwindow.config.Config(TEST_TITLE, TEST_VERSION)
        self.root_window = mainwindow.MainWindow(InstrumentedTk())
        self.root_window.tk_shutdown()
        try:
            yield
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


# noinspection PyMissingOrEmptyDocstring
@dataclass
class InstrumentedTkMenu:
    """Note: This simplified test dummy for Tk.Menu does not attempt to replicate its hierarchy of
    menubar and the 'cascades' of subordinate menus."""
    parent: InstrumentedTk
    add_separator_called = False
    label: str = None
    menu: 'InstrumentedTkMenu' = None
    menu_items: List[Tuple[str, Optional[Callable], Optional[tk_state]]] = field(default_factory=list)
    
    def add_separator(self):
        self.add_separator_called = True
        self.menu_items.append(tuple())
    
    def add_cascade(self, label: str, menu: 'InstrumentedTkMenu'):
        self.label = label
        self.menu = menu
    
    def add_command(self, label: str, command: Optional[Callable] = None,
                    state: Optional[tk_state] = None):
        self.menu_items.append((label, command, state))
    
    def entryconfig(self, item_index: int, state: tk_state):
        label, command, _ = self.menu_items[item_index]
        self.menu_items[item_index] = label, command, state


@dataclass
class DummyMenuData:
    """Dummy menu."""
    
    def __post_init__(self):
        # noinspection PyTypeChecker
        self.menus = [mainwindow.Menu(TEST_MENU, [
                '-',
                mainwindow.MenuItem('Item 1', lambda: 'Item 1 handler'),
                mainwindow.MenuItem('Item 2', lambda: 'Item 2 handler', active=False),
                mainwindow.MenuItem('Item 3'),
                mainwindow.MenuItem('Item 4', 42),
                mainwindow.MenuItem(mainwindow.QUIT_ITEM),
                ])]
