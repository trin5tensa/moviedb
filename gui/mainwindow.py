"""Main Window."""

#  Copyright© 2025. Stephen Rigden.
#  Last modified 4/25/25, 2:12 PM by stephen.
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
from dataclasses import dataclass
from functools import partial
from typing import Tuple

import config
import handlers

GEOMETRY_INVALID = f"The saved screen geometry is too large for this monitor."


@dataclass
class MainWindow:
    """Create and manage the menu bar and the application's main window."""

    parent: tk.Tk

    def __post_init__(self):
        self.parent.title(config.persistent.program_name)
        self.parent.geometry(self.set_geometry())
        self.place_menubar()

        # noinspection PyTypeChecker
        self.parent.bind_all("<Escape>", self.tk_shutdown)
        # noinspection PyTypeChecker
        self.parent.bind_all("<Command-.>", self.tk_shutdown)

    def set_geometry(self) -> str:
        """Sets window geometry.

        The geometry is set to the window position saved from the previous
        session or, if the saved position is not available, to the defaults
        - width 900
        - height 400
        - horizontal offset 30
        - vertical offset 30

        If necessary, the geometry will be adjusted to fit on the available
        output device. The authority for teh available output device is
        tkinter's

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
            If the geometry will fit onto the screen the length and width are
            returned unchanged. If the geometry is too large the maximum
            screen dimension is returned with a zero offset.
        """
        length = int(length)
        offset = int(offset)
        req_length = length + abs(offset)
        available = int(available)
        if req_length > available:
            msg = f"{GEOMETRY_INVALID} {length=}, {offset=}." f" {available=}"
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
        # Menubar
        self.parent.option_add("*tearOff", False)
        # Intercepts the window close button (red 'x')
        self.parent.protocol("WM_DELETE_WINDOW", self.tk_shutdown)
        # # Intercepts the <Command-Q> key press, the application menu item 'Quit',
        # # and the dock application popup 'Quit' item.
        self.parent.createcommand("tk::mac::Quit", self.tk_shutdown)
        self.parent.createcommand(
            "tk::mac::ShowPreferences", handlers.sundries.settings_dialog
        )
        menubar = tk.Menu(self.parent, name="menubar")

        # moviedb menu
        moviedb_menu = tk.Menu(menubar, name="moviedb")
        menubar.add_cascade(menu=moviedb_menu, label="Moviedb")
        moviedb_menu.add_command(
            label="About " + config.persistent.program_name + "…",
            command=handlers.sundries.about_dialog,
        )
        moviedb_menu.add_separator()
        moviedb_menu.add_command(
            label="Settings for Moviedb…",
            command=handlers.sundries.settings_dialog,
        )
        moviedb_menu.add_separator()
        moviedb_menu.add_command(label="Quit Moviedb", command=self.tk_shutdown)

        # Edit menu
        edit_menu = tk.Menu(menubar, name="edit")
        menubar.add_cascade(menu=edit_menu, label="Edit")
        edit_menu.add_command(
            label="Cut",
            command=(partial(self.event_generate, "<<Cut>>")),
            accelerator="Command+X",
        )
        edit_menu.add_command(
            label="Copy",
            command=(partial(self.event_generate, "<<Copy>>")),
            accelerator="Command+C",
        )
        edit_menu.add_command(
            label="Paste",
            command=(partial(self.event_generate, "<<Paste>>")),
            accelerator="Command+V",
        )
        edit_menu.add_command(
            label="Select All",
            command=(partial(self.event_generate, "<<SelectAll>>")),
            accelerator="Command+A",
        )

        # Movie menu
        movie_menu = tk.Menu(menubar, name="movie")
        menubar.add_cascade(menu=movie_menu, label="Movie")
        movie_menu.add_command(
            label="Add Movie…",
            command=handlers.database.gui_add_movie,
        )
        movie_menu.add_command(
            label="Edit Movie…",
            command=handlers.database.gui_search_movie,
        )
        movie_menu.add_command(
            label="View Movie…",
            command=handlers.database.gui_search_movie,
        )
        movie_menu.add_command(
            label="Delete Movie…",
            command=handlers.database.gui_search_movie,
        )
        movie_menu.add_separator()
        movie_menu.add_command(
            label="Add Tag…",
            command=handlers.database.gui_add_tag,
        )
        movie_menu.add_command(
            label="Edit Tag…",
            command=handlers.database.gui_search_tag,
        )
        movie_menu.add_command(
            label="Delete Tag…",
            command=handlers.database.gui_search_tag,
        )

        # window_menu = tk.Menu(menubar)
        window_menu = tk.Menu(menubar, name="window")
        menubar.add_cascade(menu=window_menu, label="Window")

        self.parent.config(menu=menubar)

    def event_generate(
        self,
        virtual_event: str,
    ):
        """Executes the specified virtual event.

        On what?
        The virtual event will be executed for the widget which has focus.
        For example, if the widget is an Entry field which contains text and
        the virtual event is <<SelectAll>> then the range of selected contents
        will be set to all of the text.

        Args:
            virtual_event: Used within this class for the Tk/Tcl events <<Cut>>,
            <<Copy>>, <<Paste>>, and <<SelectAll>>
        """
        self.parent.focus_get().event_generate(virtual_event)

    # noinspection PyUnusedLocal
    def tk_shutdown(self, *args):
        """Carry out actions needed when main window is closed.

        Args:
            *args: Not used. Required for compatibility with caller
        """
        # Save geometry in config.persistent for future permanent storage.
        config.persistent.geometry = self.parent.winfo_geometry()
        # Destroy all widgets and end mainloop.
        self.parent.destroy()


def run_tktcl():
    """Run the GUI."""
    # todo move tk_root to somewhere inside gui
    root = config.current.tk_root = tk.Tk()
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    MainWindow(root)
    root.mainloop()
