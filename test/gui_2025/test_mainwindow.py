"""Tests for the MainWindow class.

This module contains tests for the MainWindow class in the gui.mainwindow module.
It verifies that the MainWindow correctly initializes the application window,
including setting the title, geometry, menubar, and key bindings.
"""

#  Copyright© 2025. Stephen Rigden.
#  Last modified 4/25/25, 8:53 AM by stephen.
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

import pytest
from pytest_check import check
from unittest.mock import MagicMock, call

from gui import mainwindow

PROGRAM_NAME = "test name dummy"
PROGRAM_VERSION = "test version dummy"


# noinspection DuplicatedCode
class TestMainWindow:
    """Tests for the MainWindow class initialization.

    This test class verifies that the MainWindow class correctly initializes
    the application window by setting the window title, geometry, menubar,
    and key bindings during the __post_init__ method execution.
    """

    def test_post_init(self, monkeypatch):
        """Tests that MainWindow.__post_init__ correctly initializes the window.

        This test verifies that the __post_init__ method:
        1. Sets the window title to the program name
        2. Sets the window geometry using the return value from set_geometry()
        3. Calls the place_menubar() method
        4. Binds the Escape key and Command-. key to the tk_shutdown method

        Args:
            monkeypatch: Pytest fixture for patching dependencies.
        """
        # Arrange
        # noinspection DuplicatedCode
        parent = MagicMock(name="parent", autospec=True)
        monkeypatch.setattr(mainwindow.tk, "Tk", parent)
        place_menubar = MagicMock(name="place_menubar", autospec=True)
        monkeypatch.setattr(mainwindow.MainWindow, "place_menubar", place_menubar)
        set_geometry = MagicMock(name="set_geometry", autospec=True)
        monkeypatch.setattr(mainwindow.MainWindow, "set_geometry", set_geometry)

        # Act
        with mainwindow_obj(parent, monkeypatch, suppress_init=False) as obj:

            # Assert
            with check:
                parent.title.assert_called_once_with(PROGRAM_NAME)
            with check:
                parent.geometry.assert_called_once_with(set_geometry())
            with check:
                place_menubar.assert_called_once_with()
            check.equal(
                parent.bind_all.call_args_list,
                [
                    call("<Escape>", obj.tk_shutdown),
                    call("<Command-.>", obj.tk_shutdown),
                ],
            )

    @pytest.mark.parametrize(
        "saved, cfg_geometry",
        [
            (None, "900x400+30+30"),
            ("42x42+42+42", "42x42+42+42"),
        ],
    )
    def test_set_geometry(self, saved, cfg_geometry, tk, monkeypatch):
        # Arrange parent
        parent = tk.Tk()

        # Arrange re.search
        regex = (
            "(?P<width>[0-9]+)x"
            "(?P<height>[0-9]+)"
            "(?P<horizontal_offset>[+-]?[0-9]+)"
            "(?P<vertical_offset>[+-]?[0-9]+)"
        )
        regex = mainwindow.re.compile(regex)
        re_search = MagicMock(name="re_search", autospec=True)
        re_geometry = re_search.return_value = MagicMock(name="re_geometry")
        monkeypatch.setattr(mainwindow.re, "search", re_search)

        # Arrange validate_desired_geometry
        validate = MagicMock(name="validate", autospec=True)
        validate.side_effect = [
            ["width", "horizontal_offset"],
            ["height", "vertical_offset"],
        ]
        monkeypatch.setattr(
            mainwindow.MainWindow, "validate_desired_geometry", validate
        )

        # Act
        with mainwindow_obj(parent, monkeypatch) as obj:
            mainwindow.config.persistent.geometry = saved
            geometry = obj.set_geometry()

            # Assert
            with check:
                re_search.assert_called_once_with(regex, cfg_geometry)
                re_geometry.assert_has_calls(
                    [
                        call.group("width"),
                        call.group("horizontal_offset"),
                        call.group("height"),
                        call.group("vertical_offset"),
                    ]
                )
            check.equal(
                validate.call_args_list,
                [
                    call(
                        re_geometry.group(),
                        re_geometry.group(),
                        parent.winfo_screenwidth(),
                    ),
                    call(
                        re_geometry.group(),
                        re_geometry.group(),
                        parent.winfo_screenheight(),
                    ),
                ],
            )
            check.equal(
                geometry,
                "width" + "x" + "height" + "horizontal_offset" + "vertical_offset",
            )

    @pytest.mark.parametrize(
        "length_offset, available",
        [
            (("420", "42"), 100),
            (("42", "42"), 100),
        ],
    )
    def test_validate_desired_geometry(
        self, length_offset, available, tk, monkeypatch, caplog
    ):
        # Arrange
        parent = tk.Tk()
        des_length, des_offset = length_offset
        too_big = available < int(des_length) - int(des_offset)
        msg = (
            f"{mainwindow.GEOMETRY_INVALID} length={des_length}, offset={des_offset}."
            f" available={available}"
        )
        caplog.set_level("INFO")

        with mainwindow_obj(parent, monkeypatch) as obj:
            # Act
            result = obj.validate_desired_geometry(
                des_length,
                des_offset,
                available,
            )

            # Assert
            if too_big:
                check.equal(caplog.messages[0], msg)
                check.equal(result, (str(available), "+0"))
            else:
                check.equal(result, (des_length, f"+{des_offset}"))

    def test_place_menubar(self, monkeypatch):
        # Arrange
        tk = MagicMock(name="tk", autospec=True)
        monkeypatch.setattr(mainwindow, "tk", tk)
        parent = tk.Tk()
        tk_shutdown = MagicMock(name="tk_shutdown", autospec=True)
        monkeypatch.setattr(
            mainwindow.MainWindow,
            "tk_shutdown",
            tk_shutdown,
        )
        event_generate = MagicMock(name="event_generate", autospec=True)
        monkeypatch.setattr(
            mainwindow.MainWindow,
            "event_generate",
            event_generate,
        )
        partial = MagicMock(name="partial", autospec=True)
        monkeypatch.setattr(mainwindow, "partial", partial)

        # Arrange tk_menu
        tk_menu = MagicMock(name="tk_menu", autospec=True)
        menubar = MagicMock(name="menubar", autospec=True)
        moviedb_menu = MagicMock(name="moviedb_menu", autospec=True)
        edit_menu = MagicMock(name="edit_menu", autospec=True)
        movie_menu = MagicMock(name="movie_menu", autospec=True)
        window_menu = MagicMock(name="window_menu", autospec=True)
        tk_menu.side_effect = [
            menubar,
            moviedb_menu,
            edit_menu,
            movie_menu,
            window_menu,
        ]
        monkeypatch.setattr(tk, "Menu", tk_menu)

        # Act
        with mainwindow_obj(parent, monkeypatch) as obj:
            obj.place_menubar()

            # Assert parent, menubar and other general calls
            check.equal(
                parent.mock_calls,
                [
                    call.option_add("*tearOff", False),
                    call.protocol("WM_DELETE_WINDOW", tk_shutdown),
                    call.createcommand("tk::mac::Quit", tk_shutdown),
                    call.createcommand(
                        "tk::mac::ShowPreferences",
                        mainwindow.handlers.sundries.settings_dialog,
                    ),
                    call.config(menu=menubar),
                ],
            )
            check.equal(
                tk.Menu.call_args_list,
                [
                    call(parent, name="menubar"),
                    call(menubar, name="moviedb"),
                    call(menubar, name="edit"),
                    call(menubar, name="movie"),
                    call(menubar, name="window"),
                ],
            )
            check.equal(
                menubar.add_cascade.call_args_list,
                [
                    call(menu=moviedb_menu, label="Moviedb"),
                    call(menu=edit_menu, label="Edit"),
                    call(menu=movie_menu, label="Movie"),
                    call(menu=window_menu, label="Window"),
                ],
            )
            check.equal(
                partial.mock_calls,
                [
                    call(event_generate, "<<Cut>>"),
                    call(event_generate, "<<Copy>>"),
                    call(event_generate, "<<Paste>>"),
                    call(event_generate, "<<SelectAll>>"),
                ],
            )

            # Assert movie_db menu
            check.equal(
                moviedb_menu.mock_calls,
                [
                    call.add_command(
                        label="About "
                        + mainwindow.config.persistent.program_name
                        + "…",
                        command=mainwindow.handlers.sundries.about_dialog,
                    ),
                    call.add_separator(),
                    call.add_command(
                        label="Settings for Moviedb…",
                        command=mainwindow.handlers.sundries.settings_dialog,
                    ),
                    call.add_separator(),
                    call.add_command(label="Quit Moviedb", command=tk_shutdown),
                ],
            )

            # Assert edit menu
            check.equal(
                edit_menu.mock_calls,
                [
                    call.add_command(
                        label="Cut",
                        command=partial(),
                        accelerator="Command+X",
                    ),
                    call.add_command(
                        label="Copy",
                        command=partial(),
                        accelerator="Command+C",
                    ),
                    call.add_command(
                        label="Paste",
                        command=partial(),
                        accelerator="Command+V",
                    ),
                    call.add_command(
                        label="Select All",
                        command=partial(),
                        accelerator="Command+A",
                    ),
                ],
            )

            # Assert movie menu
            check.equal(
                movie_menu.mock_calls,
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
                ],
            )

    def test_event_generate(self, monkeypatch):
        # Arrange
        tk = MagicMock(name="tk", autospec=True)
        monkeypatch.setattr(mainwindow, "tk", tk)
        parent = tk.Tk()
        virtual_event = "test virtual event"

        # Act
        with mainwindow_obj(parent, monkeypatch) as obj:
            obj.event_generate(virtual_event)

            # Assert
            with check:
                parent.focus_get.assert_called_once_with()
            with check:
                parent.focus_get().event_generate.assert_called_once_with(virtual_event)

    def test_tk_shutdown(self, monkeypatch):
        # Arrange
        tk = MagicMock(name="tk", autospec=True)
        monkeypatch.setattr(mainwindow, "tk", tk)
        parent = tk.Tk()
        geometry = "42x42+42+42"
        parent.winfo_geometry.return_value = geometry

        # Act
        with mainwindow_obj(parent, monkeypatch) as obj:
            obj.tk_shutdown()

            # Assert
            check.equal(mainwindow.config.persistent.geometry, geometry)
            with check:
                parent.destroy.assert_called_once_with()


def test_run_tktcl(monkeypatch):
    # Arrange
    tk = MagicMock(name="tk", autospec=True)
    monkeypatch.setattr(mainwindow, "tk", tk)
    root = tk.Tk()
    hold_config_current = mainwindow.config.current
    mainwindow.config.current = mainwindow.config.CurrentConfig()
    main_window = MagicMock(name="main_window", autospec=True)
    monkeypatch.setattr(mainwindow, "MainWindow", main_window)

    # Act
    mainwindow.run_tktcl()

    # Assert
    check.equal(mainwindow.config.current.tk_root, root)
    check.equal(
        root.mock_calls,
        [
            call.columnconfigure(0, weight=1),
            call.rowconfigure(0, weight=1),
            call.mainloop(),
            call.__eq__(root),
        ],
    )
    with check:
        main_window.assert_called_once_with(root)

    # Cleanup
    mainwindow.config.current = hold_config_current


@contextmanager
def mainwindow_obj(parent, monkeypatch, suppress_init: bool = True):
    """Creates a MainWindow instance with test configuration for use in tests.

    This context manager temporarily replaces the persistent configuration
    with dummy values, creates and yields a MainWindow instance, and restores the
    original configuration after the test.
    Running the __post_init__ method is an option. This is useful for either
    testing the __post_init__method or other methods of the MainWindow class.

    Args:
        parent: The parent Tk instance (or mock) for the MainWindow.
        monkeypatch: The pytest.monkeypatch fixture created by the caller.
        suppress_init: If the default value of True then the __post_init__
        method will not run.

    Yields:
        A MainWindow instance configured with test values.
    """
    # Arrange
    hold_persistent = mainwindow.config.persistent
    mainwindow.config.persistent = mainwindow.config.PersistentConfig(
        program_name=PROGRAM_NAME, program_version=PROGRAM_VERSION
    )
    if suppress_init:
        monkeypatch.setattr(
            mainwindow.MainWindow,
            "__post_init__",
            lambda *args: None,
        )

    # Act
    yield mainwindow.MainWindow(parent)

    # Cleanup
    mainwindow.config.persistent = hold_persistent
