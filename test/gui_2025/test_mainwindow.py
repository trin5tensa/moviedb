"""Tests for the MainWindow class.

This module contains tests for the MainWindow class in the gui.mainwindow module.
It verifies that the MainWindow correctly initializes the application window,
including setting the title, geometry, menubar, and key bindings.
"""

#  Copyright© 2025. Stephen Rigden.
#  Last modified 4/19/25, 11:48 AM by stephen.
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
from pytest_check import check
from unittest.mock import MagicMock, call

from gui import mainwindow

PROGRAM_NAME = "test name dummy"
PROGRAM_VERSION = "test version dummy"


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
        with mainwindow_obj(parent) as obj:

            # Assert
            with check:
                parent.title.assert_called_once_with(PROGRAM_NAME)
            with check:
                parent.geometry.assert_called_once_with(set_geometry())
            with check:
                place_menubar.assert_called_once_with()
            with check:
                parent.bind_all.assert_has_calls(
                    [
                        call("<Escape>", obj.tk_shutdown),
                        call("<Command-.>", obj.tk_shutdown),
                    ]
                )


@contextmanager
def mainwindow_obj(parent):
    """Creates a MainWindow instance with test configuration for use in tests.

    This context manager temporarily replaces the persistent configuration
    with test values, creates a MainWindow instance, and restores the
    original configuration after the test.

    Args:
        parent: The parent Tk instance (or mock) for the MainWindow.

    Yields:
        A MainWindow instance configured with test values.
    """
    # Arrange
    hold_persistent = mainwindow.config.persistent
    mainwindow.config.persistent = mainwindow.config.PersistentConfig(
        program_name=PROGRAM_NAME, program_version=PROGRAM_VERSION
    )

    # Act
    yield mainwindow.MainWindow(parent)

    # Cleanup
    mainwindow.config.persistent = hold_persistent
