"""Main Window."""

#  Copyright (c) 2022-2022. Stephen Rigden.
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

import logging
import re
import tkinter as tk
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Sequence, Tuple

import config
import handlers

# todo Change module name to guirun.


@dataclass
class MainWindow:
    """Create and manage the menu bar and the application's main window. """
    parent: tk.Tk
    tk_args: Sequence = None
    tk_kwargs: Mapping = None

    # Local variables exposed as attributes for testing
    menubar: tk.Menu = field(default=None, init=False, repr=False)
    apple_menu: tk.Menu = field(default=None, init=False, repr=False)
    moviedb_menu: tk.Menu = field(default=None, init=False, repr=False)
    edit_menu: tk.Menu = field(default=None, init=False, repr=False)
    movie_menu: tk.Menu = field(default=None, init=False, repr=False)

    def __post_init__(self):
        self.parent.title(config.persistent.program_name)
        self.parent.geometry(self.set_geometry())
        self.place_menubar()

        # Set up handling of <Escape> and <Command-.>
        # todo test next three lines
        config.current.escape_key_dict = escape_key_dict = handlers.EscapeKeyDict()
        self.parent.bind_all(key := '<Escape>', escape_key_dict.escape(self.parent, key))
        self.parent.bind_all(key := '<Command-.>', escape_key_dict.escape(self.parent, key))

    def set_geometry(self) -> str:
        """Set window geometry from a default value or app.geometry and make sure it will
        fit on the screen.

        Returns:
            tkinter geometry string.
        """
        if not config.persistent.geometry:
            config.persistent.geometry = '900x400+30+30'
        regex = ("(?P<width>[0-9]+)x"
                 "(?P<height>[0-9]+)"
                 "(?P<horizontal_offset>[+-]?[0-9]+)"
                 "(?P<vertical_offset>[+-]?[0-9]+)")
        regex = re.compile(regex)
        re_geometry = re.search(regex, config.persistent.geometry)
        width, horizontal_offset = self.validate_desired_geometry(
            re_geometry.group('width'), re_geometry.group('horizontal_offset'),
            self.parent.winfo_screenwidth())
        height, vertical_offset = self.validate_desired_geometry(
            re_geometry.group('height'), re_geometry.group('vertical_offset'),
            self.parent.winfo_screenheight())
        geometry = "{}x{}{}{}".format(width, height, horizontal_offset, vertical_offset)
        return geometry

    @staticmethod
    def validate_desired_geometry(length: str, offset: str, available: int) -> Tuple[str, str]:
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
            msg = (f'The saved screen geometry {length=} and {offset=} '
                   f'is too large for this monitor ({available=})')
            logging.info(msg=msg)
            offset = 0
            if length > available:
                length = available
        return str(length), f'{offset:+}'

    def place_menubar(self):
        """Create menubar and menu items.

        An unorthodox menu design.
        The apple menu (aka 'the application menu' but not the apple icon menu) always takes the name of the binary
        which is 'Python'. The only way around this is to rename the binary. The solution adopted here is to accept
        the now inevitable 'Python' menu following the apple icon menu. This is ameliorated with a second 'Moviedb'
        application menu. The 'Moviedb' menu has the items 'About…', 'Settings…', and 'Quit. Neither the 'Quit' nor
        the 'Settings…' items will accept the standard accelerator keys of <Command-Q> or <Command-,> presumably
        because these are reserved for the 'Python' menu. For that reason these two accelerator keys have been
        attached to the 'Python' menu with 'tk::mac::Quit' and 'tk::mac::ShowPreferences'.

        tk_shutdown (Moviedb's final cleanup function)
        The quit accelerator is particularly important as Moviedb's shutdown procedure would not be invoked if the
        user presses <Command-Q>. Of the four different ways of quitting a program which are <Command-Q>,
        Application menu item 'Quit', dock application popup, and close box (red 'x' button at top of window);
        only the first three are intercepted by the command tk::mac::Quit. The close box is intercepted by the
        protocol 'WM_DELETE_WINDOW'.
        """
        # todo test next five lines
        self.parent.option_add('*tearOff', False)
        # Intercept window close button (red 'x')
        self.parent.protocol('WM_DELETE_WINDOW', self.tk_shutdown)
        # Intercept <Command-Q>, Application menu item 'Quit', and dock application popup quit item.
        self.parent.createcommand('tk::mac::Quit', self.tk_shutdown)
        self.parent.createcommand('tk::mac::ShowPreferences', handlers.settings_dialog)
        self.menubar = tk.Menu(self.parent)

        # todo write tests for this new menu
        self.moviedb_menu = tk.Menu(self.menubar)
        self.menubar.add_cascade(menu=self.moviedb_menu, label='Moviedb')
        self.moviedb_menu.add_command(label='About ' + config.persistent.program_name + '…',
                                      command=handlers.about_dialog)
        self.moviedb_menu.add_separator()
        self.moviedb_menu.add_command(label='Settings for Moviedb…', command=handlers.settings_dialog)
        self.moviedb_menu.add_separator()
        self.moviedb_menu.add_command(label='Quit Moviedb', command=self.tk_shutdown)

        self.edit_menu = tk.Menu(self.menubar)
        self.menubar.add_cascade(menu=self.edit_menu, label='Edit')
        self.edit_menu.add_command(label='Cut',  # pragma no branch
                                   command=lambda: self.parent.focus_get().event_generate('<<Cut>>'),
                                   accelerator='Command+X')
        self.edit_menu.add_command(label='Copy',  # pragma no branch
                                   command=lambda: self.parent.focus_get().event_generate('<<Copy>>'),
                                   accelerator='Command+C')
        self.edit_menu.add_command(label='Paste',  # pragma no branch
                                   command=lambda: self.parent.focus_get().event_generate('<<Paste>>'),
                                   accelerator='Command+V')
        self.edit_menu.add_command(label='Clear',  # pragma no branch
                                   command=lambda: self.parent.focus_get().event_generate('<<Clear>>'))

        self.movie_menu = tk.Menu(self.menubar)
        self.menubar.add_cascade(menu=self.movie_menu, label='Movie')
        self.movie_menu.add_command(label='Add Movie…', command=handlers.add_movie)
        self.movie_menu.add_command(label='Edit Movie…', command=handlers.edit_movie)
        self.movie_menu.add_command(label='View Movie…', command=handlers.edit_movie)
        self.movie_menu.add_command(label='Delete Movie…', command=handlers.edit_movie)
        self.movie_menu.add_separator()
        self.movie_menu.add_command(label='Add Tag…', command=handlers.add_tag)
        self.movie_menu.add_command(label='Edit Tag…', command=handlers.edit_tag)
        self.movie_menu.add_command(label='Delete Tag…', command=handlers.edit_tag)

        window_menu = tk.Menu(self.menubar, name='window')
        self.menubar.add_cascade(menu=window_menu, label='Window')

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
