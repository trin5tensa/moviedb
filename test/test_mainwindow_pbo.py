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
from test.dummytk import DummyTk, TkMenu

TEST_TITLE = 'test moviedb'
TEST_VERSION = 'Test version'


class TestMainWindowInit:
    """Ensure that MainWindow is correctly initialized.."""
    tk_root: DummyTk = None
    mock_set_geometry: MagicMock = None
    mock_place_menubar: MagicMock = None

    def test_main_window_initialization(self, monkeypatch, check):
        # todo Add meaningful exception messages
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
    tk_root: DummyTk = None
    mock_set_geometry: MagicMock = None
    mock_place_menubar: MagicMock = None
    tk_menu: TkMenu = None

    def test_main_window_initialization(self, monkeypatch, check):
        with self.main_window_context(monkeypatch) as main_window:
            msg = "The menu '*tearOff' suppression option is missing."
            check.equal(self.tk_root.option_add_calls, [('*tearOff', (False,))], msg),
            msg = f'\n\n{main_window.__class__.__name__}.menubar called with unexpected arguments.'
            check.equal(main_window.menubar, self.tk_menu(self.tk_root), msg)
            check.equal(main_window.menubar.add_cascade_calls, [
                ((), {'menu': TkMenu(parent=TkMenu(parent=DummyTk(), name=None), name='apple')}),
                ((), {'menu': TkMenu(parent=TkMenu(parent=DummyTk(), name=None), name=None), 'label': 'Edit'}),
                ((), {'menu': TkMenu(parent=TkMenu(parent=DummyTk(), name=None), name=None), 'label': 'Movie'}),
                ((), {'menu': TkMenu(parent=TkMenu(parent=DummyTk(), name=None), name='window'), 'label': 'Window'}),
                ], "\nActual menus do not match the expected menus.")

            # Application (apple) menu item
            check.equal(main_window.apple_menu.add_command_calls, [
                ((), {'label': 'About test moviedb…', 'command': mainwindow.handlers.about_dialog}),
                ((), {'label': 'Settings for Moviedb…', 'command': mainwindow.handlers.settings_dialog})],
                        "\nActual application menu items do not match the expected menu items.")
            msg = "\nCreate 'ShowPreferences' command called with unexpected arguments."
            check.equal(main_window.parent.createcommand_calls, [
                ('tk::mac::ShowPreferences', mainwindow.handlers.settings_dialog)], msg)

            # Edit menu item
            # Tests of add_command have to be broken down into components as lambda calls cannot be tested directly.
            expected = [{'label': 'Cut', 'accelerator': 'Command+X'},
                        {'label': 'Copy', 'accelerator': 'Command+C'},
                        {'label': 'Paste', 'accelerator': 'Command+V'},
                        {'label': 'Clear', }, ]
            try:
                for actual, label_and_accelerator in zip(main_window.edit_menu.add_command_calls, expected,
                                                         strict=True):
                    _, actual = actual
                    for k in ['label', 'accelerator']:
                        msg = f"Menu item {k} is not {label_and_accelerator.get(k)}"
                        check.equal(actual.get(k), label_and_accelerator.get(k), msg)
            except ValueError as exc:
                if exc.args[0][:14] == 'zip() argument':
                    msg = (f"{len(expected)} Calls to the edit menu's add_command method were expected. "
                           f"A different number of calls were made.")
                    check.is_true(False, msg)
                else:
                    raise

            # Movie menu item
            check.equal(main_window.movie_menu.add_command_calls, [
                        ((), {'label': 'Add Movie…', 'command': mainwindow.handlers.add_movie}),
                        ((), {'label': 'Edit Movie…', 'command': mainwindow.handlers.edit_movie}),
                        ((), {'label': 'Delete Movie…', 'command': mainwindow.handlers.edit_movie}),
                        ((), {'label': 'Add Tag…', 'command': mainwindow.handlers.add_tag}),
                        ((), {'label': 'Edit Tag…', 'command': mainwindow.handlers.edit_tag}),
                        ((), {'label': 'Delete Tag…', 'command': mainwindow.handlers.edit_tag})],
                        "\nActual movie menu items do not match the expected menu items.")
            check.equal(main_window.movie_menu.add_separator_count, 1, 'Unexpected number of separators on this menu.')

            # Insertion into parent window
            msg = '\nThe menubar was not attached to its window in the manner expected.'
            check.equal(main_window.parent.config_calls, [{'menu': TkMenu(parent=DummyTk(), name=None)}], msg)

    # noinspection PyMissingOrEmptyDocstring, PyTypeChecker
    @contextmanager
    def main_window_context(self, monkeypatch):
        persistent_hold = mainwindow.config.persistent
        mainwindow.config.persistent = mainwindow.config.PersistentConfig(TEST_TITLE, TEST_VERSION)
        self.tk_root = DummyTk()
        self.mock_set_geometry = MagicMock()
        monkeypatch.setattr('mainwindow.MainWindow.set_geometry', self.mock_set_geometry)
        self.tk_menu = TkMenu
        monkeypatch.setattr(mainwindow.tk, 'Menu', self.tk_menu)

        try:
            yield mainwindow.MainWindow(self.tk_root)
        finally:
            mainwindow.config.persistent = persistent_hold
