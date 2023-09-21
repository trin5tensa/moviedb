"""test_mainwindow_pbo

This module contains new tests written after Brian Okken's course and book on pytest in Fall 2022.
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
from unittest.mock import MagicMock, call

import pytest
from pytest_check import check

import mainwindow
from test.dummytk import DummyTk, TkMenu

TEST_TITLE = 'test moviedb'
TEST_VERSION = 'Test version'


class TestMainWindowInit:
    """Ensure that MainWindow is correctly initialized.."""
    def test_main_window_initialization(self, monkeypatch):
        mock_set_geometry = MagicMock()
        monkeypatch.setattr(mainwindow.MainWindow, 'set_geometry', mock_set_geometry)
        mock_place_menubar = MagicMock()
        monkeypatch.setattr(mainwindow.MainWindow, 'place_menubar', mock_place_menubar)
        mock_escape_key_dict = MagicMock()
        monkeypatch.setattr(mainwindow.handlers, 'EscapeKeyDict', mock_escape_key_dict)

        with self.context(monkeypatch) as main_window:
            with check:
                main_window.parent.title.assert_called_once_with(TEST_TITLE)
            with check:
                main_window.parent.geometry.assert_called_once_with(mock_set_geometry())
            with check:
                main_window.place_menubar.assert_called_once_with()
            with check:
                main_window.parent.bind_all.assert_has_calls([call('<Escape>', mock_escape_key_dict().escape()),
                                                              call('<Command-.>', mock_escape_key_dict().escape())])

    # noinspection PyMissingOrEmptyDocstring, PyTypeChecker
    @contextmanager
    def context(self, monkeypatch):
        current_config = mainwindow.config.CurrentConfig()
        current_config.tk_root = MagicMock()
        persistent_config = mainwindow.config.PersistentConfig(TEST_TITLE, TEST_VERSION)

        mock_config = MagicMock()
        mock_config.current = current_config
        mock_config.persistent = persistent_config
        monkeypatch.setattr('mainwindow.config', mock_config)

        yield mainwindow.MainWindow(current_config.tk_root)


class TestPlaceMenubar:
    """This suite tests the place_menubar and place_menu method."""
    tk_root: DummyTk = None
    mock_set_geometry: MagicMock = None
    mock_place_menubar: MagicMock = None
    tk_menu: TkMenu = None

    @pytest.mark.skip
    def test_main_window_initialization(self, monkeypatch):
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
            except ValueError as exc:  # pragma no cover
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
                        ((), {'label': 'View Movie…', 'command': mainwindow.handlers.edit_movie}),
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
