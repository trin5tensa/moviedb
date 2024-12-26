"""Main Window."""

#  Copyright© 2024. Stephen Rigden.
#  Last modified 12/26/24, 11:22 AM by stephen.
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

import logging
import re
import tkinter as tk
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Tuple

import config

import handlers
import gui_handlers


@dataclass
class MainWindow:
    """Create and manage the menu bar and the application's main window."""

    parent: tk.Tk

    # Expose local variables for test access
    menubar: tk.Menu = field(default=None, init=False, repr=False)
    moviedb_menu: tk.Menu = field(default=None, init=False, repr=False)
    edit_menu: tk.Menu = field(default=None, init=False, repr=False)
    movie_menu: tk.Menu = field(default=None, init=False, repr=False)
    window_menu: tk.Menu = field(default=None, init=False, repr=False)
    cut_command: Callable = field(default=None, init=False, repr=False)
    copy_command: Callable = field(default=None, init=False, repr=False)
    paste_command: Callable = field(default=None, init=False, repr=False)
    clear_command: Callable = field(default=None, init=False, repr=False)

    def __post_init__(self):
        self.parent.title(config.persistent.program_name)
        self.parent.geometry(self.set_geometry())
        self.place_menubar()

        # Set up handling of <Escape> and <Command-.>
        config.current.escape_key_dict = escape_key_dict = (
            gui_handlers.sundries.EscapeKeyDict()
        )
        # noinspection PyTypeChecker
        self.parent.bind_all(
            key := "<Escape>", escape_key_dict.escape(self.parent, key)
        )
        # noinspection PyTypeChecker
        self.parent.bind_all(
            key := "<Command-.>", escape_key_dict.escape(self.parent, key)
        )

    def set_geometry(self) -> str:
        """Set window geometry from a default value or app.geometry and make sure it will
        fit on the screen.

        Returns:
            tkinter geometry string.
        """
        if not config.persistent.geometry:
            config.persistent.geometry = "900x400+30+30"
        regex = (
            "(?P<width>[0-9]+)x"
            "(?P<height>[0-9]+)"
            "(?P<horizontal_offset>[+-]?[0-9]+)"
            "(?P<vertical_offset>[+-]?[0-9]+)"
        )
        regex = re.compile(regex)
        re_geometry = re.search(regex, config.persistent.geometry)
        width, horizontal_offset = self.validate_desired_geometry(
            re_geometry.group("width"),
            re_geometry.group("horizontal_offset"),
            self.parent.winfo_screenwidth(),
        )
        height, vertical_offset = self.validate_desired_geometry(
            re_geometry.group("height"),
            re_geometry.group("vertical_offset"),
            self.parent.winfo_screenheight(),
        )
        geometry = "{}x{}{}{}".format(width, height, horizontal_offset, vertical_offset)
        return geometry

    @staticmethod
    def validate_desired_geometry(
        length: str, offset: str, available: int
    ) -> Tuple[str, str]:
        """Validate the geometry against the available length or height.

        Args:
            length: width or height from tkinter's geometry.
            offset: width or height offset from tkinter's geometry
            available: screen width or height.

        Returns:
            If the geometry will fit onto the screen the length and width are returned
            unchanged. If the geometry is too large the maximum screen dimension is returned
            with a zero offset.
        """
        length = int(length)
        offset = int(offset)
        req_length = length + abs(offset)
        available = int(available)
        if req_length > available:
            msg = (
                f"The saved screen geometry {length=} and {offset=} "
                f"is too large for this monitor ({available=})"
            )
            logging.info(msg=msg)
            offset = 0
            if length > available:
                length = available
        return str(length), f"{offset:+}"

    def place_menubar(self):
        # noinspection GrazieInspection
        """Create menubar and menu items.

        An unorthodox menu design.
        The Apple menu (aka 'the application menu' but not the Apple icon
        menu) always takes the name of the binary which is 'Python'. The
        only way around this is to rename the binary. The solution adopted
        here is to accept the now inevitable 'Python' menu following the
        Apple icon menu. This is ameliorated with a third 'Moviedb'
        application menu. The 'Moviedb' menu has the items 'About…',
        'Settings…', and 'Quit. Neither the 'Quit' nor the 'Settings…'
        items will accept the standard accelerator keys of <Command-Q> or
        <Command-,> presumably because these are reserved for the 'Python'
        menu. For that reason, these two accelerator keys have been attached
        to the 'Python' menu with 'tk::mac::Quit' and
        'tk::mac::ShowPreferences'.

        tk_shutdown is Moviedb's final cleanup function.
        The quit accelerator is particularly important as Moviedb's shutdown
        procedure would not be invoked if the user presses <Command-Q>. Of
        the four different ways of quitting a program which are <Command-Q>,
        Application menu item 'Quit', dock application popup, and close box
        (red 'x' button at top of window); only the first three are
        intercepted by the command tk::mac::Quit. The close box is
        intercepted by the protocol 'WM_DELETE_WINDOW'.
        """
        self.parent.option_add("*tearOff", False)
        # Intercepts the window close button (red 'x')
        self.parent.protocol("WM_DELETE_WINDOW", self.tk_shutdown)
        # Intercepts the <Command-Q> key press, the application menu item 'Quit',
        # and the dock application popup 'Quit' item.
        self.parent.createcommand("tk::mac::Quit", self.tk_shutdown)
        self.parent.createcommand(
            "tk::mac::ShowPreferences", gui_handlers.sundries.settings_dialog
        )
        self.menubar = tk.Menu(self.parent)

        self.moviedb_menu = tk.Menu(self.menubar)
        self.menubar.add_cascade(menu=self.moviedb_menu, label="Moviedb")
        self.moviedb_menu.add_command(
            label="About " + config.persistent.program_name + "…",
            command=gui_handlers.sundries.about_dialog,
        )
        self.moviedb_menu.add_separator()
        self.moviedb_menu.add_command(
            label="Settings for Moviedb…", command=gui_handlers.sundries.settings_dialog
        )
        self.moviedb_menu.add_separator()
        self.moviedb_menu.add_command(label="Quit Moviedb", command=self.tk_shutdown)

        self.edit_menu = tk.Menu(self.menubar)
        self.menubar.add_cascade(menu=self.edit_menu, label="Edit")
        self.cut_command = lambda: self.parent.focus_get().event_generate(
            "<<Cut>>"
        )  # pragma no branch
        self.edit_menu.add_command(
            label="Cut", command=self.cut_command, accelerator="Command+X"
        )
        self.copy_command = lambda: self.parent.focus_get().event_generate(
            "<<Copy>>"
        )  # pragma no branch
        self.edit_menu.add_command(
            label="Copy", command=self.copy_command, accelerator="Command+C"
        )
        self.paste_command = lambda: self.parent.focus_get().event_generate(
            "<<Paste>>"
        )  # pragma no branch
        self.edit_menu.add_command(
            label="Paste", command=self.paste_command, accelerator="Command+V"
        )
        self.clear_command = lambda: self.parent.focus_get().event_generate(
            "<<Clear>>"
        )  # pragma no branch
        self.edit_menu.add_command(label="Clear", command=self.clear_command)

        self.movie_menu = tk.Menu(self.menubar)
        self.menubar.add_cascade(menu=self.movie_menu, label="Movie")
        self.movie_menu.add_command(label="Add Movie…", command=handlers.add_movie)
        self.movie_menu.add_command(label="Edit Movie…", command=handlers.edit_movie)
        self.movie_menu.add_command(label="View Movie…", command=handlers.edit_movie)
        self.movie_menu.add_command(label="Delete Movie…", command=handlers.edit_movie)
        self.movie_menu.add_separator()
        self.movie_menu.add_command(label="Add Tag…", command=handlers.add_tag)
        self.movie_menu.add_command(label="Edit Tag…", command=handlers.edit_tag)
        self.movie_menu.add_command(label="Delete Tag…", command=handlers.edit_tag)

        self.window_menu = tk.Menu(self.menubar, name="window")
        self.menubar.add_cascade(menu=self.window_menu, label="Window")

        self.parent.config(menu=self.menubar)

    # noinspection PyUnusedLocal
    def tk_shutdown(self, *args):
        """Carry out actions needed when main window is closed.

        Args:
            *args: Not used. Required for compatibility with caller
        """
        # Save geometry in config.current for future permanent storage.
        config.persistent.geometry = self.parent.winfo_geometry()
        # Destroy all widgets and end mainloop.
        self.parent.destroy()


def run_tktcl():
    """Run the GUI."""
    config.current.tk_root = tk.Tk()
    root = config.current.tk_root
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    MainWindow(root)
    root.mainloop()
