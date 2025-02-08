"""Test Module."""

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
from dataclasses import dataclass, field
from typing import Any, Dict, Optional
from unittest.mock import MagicMock

import pytest

from gui import mainwindow

TEST_TITLE = "test moviedb"
TEST_VERSION = "Test version"
TEST_MENU = "Test Menu"


class TestMainWindowGeometry:
    """This suite of geometry tests operate by assuming the user has moved to a machine with a smaller
    monitor of size 2000×1000. The previous window size is stored in app.geometry. For each test the
    previous size s varied to exercise the various exception conditions which the target code should
    intercept and correct."""

    root_pane: mainwindow.MainWindow = None
    logging_msg: str = None

    def test_default_geometry_accepted(self, class_patches):
        with self.geometry_context(desired_geometry=None) as geometry:
            assert geometry == "900x400+30+30"

    def test_width_too_large(self, class_patches):
        with self.geometry_context("2900x400+30+30") as geometry:
            assert geometry == "2000x400+0+30"

    def test_height_too_large(self, class_patches):
        with self.geometry_context("900x2400+30+30") as geometry:
            assert geometry == "900x1000+30+0"

    def test_width_plus_offset_too_large(self, class_patches):
        with self.geometry_context("900x400+2030+30") as geometry:
            assert geometry == "900x400+0+30"

    def test_height_plus_offset_too_large(self, class_patches):
        with self.geometry_context("900x400+30+1030") as geometry:
            assert geometry == "900x400+30+0"

    def test_info_msg_logged(self, class_patches):
        with self.geometry_context("2900x400+30+30"):
            assert self.logging_msg == (
                "The saved screen geometry length=2900 and offset=30 is "
                "too large for this monitor (available=2000)"
            )

    # noinspection PyMissingOrEmptyDocstring
    @pytest.fixture()
    def class_patches(self, monkeypatch):
        monkeypatch.setattr(mainwindow.tk, "Tk", InstrumentedTk)
        monkeypatch.setattr(mainwindow.logging, "info", self.save_log_message)
        monkeypatch.setattr(mainwindow.MainWindow, "place_menubar", lambda *args: None)

    # noinspection PyMissingOrEmptyDocstring
    @contextmanager
    def geometry_context(self, desired_geometry):
        mainwindow.config.current = MagicMock()
        persistent_hold = mainwindow.config.persistent
        mainwindow.config.persistent = mainwindow.config.PersistentConfig(
            TEST_TITLE, TEST_VERSION
        )
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
            assert mainwindow.config.persistent.geometry == "42x42+42+42"

    def test_destroy_parent_called(self, class_patches):
        with self.shutdown_context():
            assert self.root_window.parent.destroy_called

    # noinspection PyMissingOrEmptyDocstring
    @pytest.fixture()
    def class_patches(self, monkeypatch):
        monkeypatch.setattr(mainwindow.tk, "Tk", InstrumentedTk)
        monkeypatch.setattr(mainwindow.MainWindow, "set_geometry", lambda *args: None)
        monkeypatch.setattr(mainwindow.MainWindow, "place_menubar", lambda *args: None)

    # noinspection PyMissingOrEmptyDocstring,PyTypeChecker
    @contextmanager
    def shutdown_context(self):
        persistent_hold = mainwindow.config.persistent
        mainwindow.config.persistent = mainwindow.config.PersistentConfig(
            TEST_TITLE, TEST_VERSION
        )
        current_hold = mainwindow.config.current
        mainwindow.config.current = mainwindow.config.CurrentConfig()
        self.root_window = mainwindow.MainWindow(InstrumentedTk())
        self.root_window.tk_shutdown()
        try:
            yield
        finally:
            mainwindow.config.current = current_hold
            mainwindow.config.persistent = persistent_hold


class TestRun:

    def test_root_window_initialized(self, class_patches):
        with self.run_gui_context() as config_data:
            tk_root = config_data
            assert isinstance(tk_root, DummyTk)

    def test_parent_column_configured(self, class_patches):
        with self.run_gui_context() as config_data:
            tk_root = config_data
            assert tk_root.columnconfigure_calls == [
                ((0,), dict(weight=1)),
            ]

    def test_parent_row_configured(self, class_patches):
        with self.run_gui_context() as config_data:
            tk_root = config_data
            assert tk_root.rowconfigure_calls == [
                ((0,), dict(weight=1)),
            ]

    def test_mainloop_called(self, class_patches):
        with self.run_gui_context() as config_data:
            tk_root = config_data
            assert tk_root.mainloop_called == [True]

    # noinspection PyMissingOrEmptyDocstring
    @pytest.fixture()
    def class_patches(self, monkeypatch):
        monkeypatch.setattr(mainwindow, "MainWindow", DummyMainWindow)
        monkeypatch.setattr(mainwindow.tk, "Tk", DummyTk)

    # noinspection PyMissingOrEmptyDocstring
    @contextmanager
    def run_gui_context(self):
        tk_root_hold = mainwindow.config.current
        try:
            mainwindow.config.current = mainwindow.config.CurrentConfig(tk_root=None)
            mainwindow.run_tktcl()
            yield mainwindow.config.current.tk_root
        finally:
            mainwindow.config.current = tk_root_hold


@dataclass
class DummyMainWindow:
    """Test dummy for application's main window."""

    parent: "DummyTk"


# noinspection PyMissingOrEmptyDocstring
@dataclass
class DummyTk:
    """Test dummy for tkinter module."""

    columnconfigure_calls: list = field(
        default_factory=list, init=False, repr=False, compare=False
    )
    rowconfigure_calls: list = field(
        default_factory=list, init=False, repr=False, compare=False
    )
    mainloop_called: list = field(
        default_factory=list, init=False, repr=False, compare=False
    )

    def mainloop(self):
        self.mainloop_called.append(True)

    def columnconfigure(self, *args, **kwargs):
        self.columnconfigure_calls.append((args, kwargs))

    def rowconfigure(self, *args, **kwargs):
        self.rowconfigure_calls.append((args, kwargs))


# noinspection PyMissingOrEmptyDocstring
@dataclass
class InstrumentedTk:
    """Test dummy for Tk."""

    title_args = None
    option_add_args = None
    geometry_args = None
    protocol_args = None
    bind_args = None
    bind_all_args = None
    menu = None
    destroy_called = False

    def title(self, *args):
        (self.title_args,) = args

    def option_add(self, *args):
        self.option_add_args = args

    def geometry(self, *args):
        self.geometry_args = args

    def protocol(self, *args):
        self.protocol_args = args

    def bind(self, *args):
        self.bind_args = args

    def bind_all(self, *args):
        self.bind_all_args = args

    def config(self, **kwargs):
        self.menu = kwargs.get("menu")

    def destroy(self):
        self.destroy_called = True

    @staticmethod
    def winfo_screenwidth():
        return "2000"

    @staticmethod
    def winfo_screenheight():
        return "1000"

    @staticmethod
    def winfo_geometry():
        return "42x42+42+42"


# noinspection PyMissingOrEmptyDocstring
@dataclass
class InstrumentedTtkFrame:
    parent: InstrumentedTk
    # pack_args = None
    pack_args: Optional[Dict[str, Any]] = None

    def pack(self, **kwargs):
        self.pack_args = kwargs
