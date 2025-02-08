"""test_mainwindow_pbo

This module contains new tests written after Brian Okken's course and book on pytest in Fall 2022.
"""

#  Copyright© 2025. Stephen Rigden.
#  Last modified 2/8/25, 2:02 PM by stephen.
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

from pytest_check import check

from gui import mainwindow

TEST_TITLE = "test moviedb"
TEST_VERSION = "Test version"


class TestMainWindow:
    """Ensure that MainWindow is correctly initialized."""

    def test_main_window_initialization(self, monkeypatch):
        monkeypatch.setattr(
            mainwindow.MainWindow, "set_geometry", mock_set_geometry := MagicMock()
        )
        monkeypatch.setattr(mainwindow.MainWindow, "place_menubar", MagicMock())
        monkeypatch.setattr(
            mainwindow.handlers.sundries,
            "EscapeKeyDict",
            mock_escape_key_dict := MagicMock(),
        )

        with main_window(monkeypatch) as cut:
            with check:
                cut.parent.title.assert_called_once_with(TEST_TITLE)
            with check:
                cut.parent.geometry.assert_called_once_with(mock_set_geometry())
            with check:
                cut.place_menubar.assert_called_once_with()
            with check:
                cut.parent.bind_all.assert_has_calls(
                    [
                        call("<Escape>", mock_escape_key_dict().escape()),
                        call("<Command-.>", mock_escape_key_dict().escape()),
                    ]
                )

    # noinspection PyUnresolvedReferences
    def test_place_menubar(self, monkeypatch):
        """Strategy: Menu construction is tested by checking that each
        expected menu item is present and in the correct order. Meta calls
        connecting the menu system to tkinter are also tested.
        """
        with main_window(monkeypatch) as cut:
            # Meta
            with check:
                cut.parent.option_add.assert_called_once_with("*tearOff", False)
            with check:
                cut.parent.protocol.assert_called_once_with(
                    "WM_DELETE_WINDOW", cut.tk_shutdown
                )
            with check:
                cut.parent.createcommand.assert_has_calls(
                    [
                        call("tk::mac::Quit", cut.tk_shutdown),
                        call(
                            "tk::mac::ShowPreferences",
                            mainwindow.handlers.sundries.settings_dialog,
                        ),
                    ]
                )
            with check:
                cut.parent.config.assert_called_once_with(menu=cut.menubar)

            # Menubar
            check.equal(cut.menubar.add_cascade.call_count, 4)
            with check:
                cut.menubar.add_cascade.assert_has_calls(
                    [
                        call(menu=cut.moviedb_menu, label="Moviedb"),
                        call(menu=cut.edit_menu, label="Edit"),
                        call(menu=cut.movie_menu, label="Movie"),
                        call(menu=cut.window_menu, label="Window"),
                    ]
                )

            # Moviedb menu
            check.equal(cut.moviedb_menu.add_command.call_count, 3)
            check.equal(cut.moviedb_menu.add_separator.call_count, 2)
            with check:
                cut.moviedb_menu.assert_has_calls(
                    [
                        call.add_command(
                            label="About " + TEST_TITLE + "…",
                            command=mainwindow.handlers.sundries.about_dialog,
                        ),
                        call.add_separator(),
                        call.add_command(
                            label="Settings for Moviedb…",
                            command=mainwindow.handlers.sundries.settings_dialog,
                        ),
                        call.add_separator(),
                        call.add_command(label="Quit Moviedb", command=cut.tk_shutdown),
                    ]
                )

            # Edit menu
            check.equal(cut.edit_menu.add_command.call_count, 4)
            with check:
                cut.edit_menu.assert_has_calls(
                    [
                        call.add_command(
                            label="Cut",
                            command=cut.cut_command,
                            accelerator="Command+X",
                        ),
                        call.add_command(
                            label="Copy",
                            command=cut.copy_command,
                            accelerator="Command+C",
                        ),
                        call.add_command(
                            label="Paste",
                            command=cut.paste_command,
                            accelerator="Command+V",
                        ),
                        call.add_command(label="Clear", command=cut.clear_command),
                    ]
                )

            # Movie menu
            check.equal(cut.movie_menu.add_command.call_count, 7)
            with check:
                cut.movie_menu.assert_has_calls(
                    [
                        call.add_command(
                            label="Add Movie…",
                            command=mainwindow.handlers.database.gui_add_movie,
                        ),
                        call.add_command(
                            label="Edit Movie…",
                            command=mainwindow.handlers.database.gui_search_movie,
                        ),
                        call.add_command(
                            label="View Movie…",
                            command=mainwindow.handlers.database.gui_search_movie,
                        ),
                        call.add_command(
                            label="Delete Movie…",
                            command=mainwindow.handlers.database.gui_search_movie,
                        ),
                        call.add_separator(),
                        call.add_command(
                            label="Add Tag…",
                            command=mainwindow.handlers.database.gui_add_tag,
                        ),
                        call.add_command(
                            label="Edit Tag…",
                            command=mainwindow.handlers.database.gui_search_tag,
                        ),
                        call.add_command(
                            label="Delete Tag…",
                            command=mainwindow.handlers.database.gui_search_tag,
                        ),
                    ]
                )


# noinspection PyMissingOrEmptyDocstring, PyTypeChecker
@contextmanager
def main_window(monkeypatch):
    current_config = mainwindow.config.CurrentConfig()
    current_config.tk_root = MagicMock()
    persistent_config = mainwindow.config.PersistentConfig(TEST_TITLE, TEST_VERSION)

    monkeypatch.setattr(mainwindow, "config", mock_config := MagicMock())
    mock_config.current = current_config
    mock_config.persistent = persistent_config
    monkeypatch.setattr(mainwindow, "tk", MagicMock())

    # Give each of the many calls to tk.Menu a unique Mock() for testing.
    mainwindow.tk.Menu.side_effect = lambda *args, **kwargs: MagicMock()
    yield mainwindow.MainWindow(current_config.tk_root)
