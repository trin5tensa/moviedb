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
from dataclasses import dataclass
from typing import Sequence, Tuple

import config
import handlers


# The quit item needs special processing.
QUIT_ITEM = 'Quit'


@dataclass
class MainWindow:
    """Create and manage the menu bar and the application's main window. """
    parent: tk.Tk
    tk_args: Sequence = None
    tk_kwargs: Mapping = None
    
    def __post_init__(self):
        self.parent.title(config.persistent.program_name)
        self.parent.geometry(self.set_geometry())
        self.place_menubar()
        self.parent.protocol('WM_DELETE_WINDOW', self.tk_shutdown)

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
        """Create menubar."""
        self.parent.option_add('*tearOff', False)

        menubar = tk.Menu(self.parent)

        apple_menu = tk.Menu(menubar, name='apple')
        menubar.add_cascade(menu=apple_menu)
        apple_menu.add_command(label='About ' + config.persistent.program_name + '…', command=handlers.about_dialog)
        self.parent.createcommand('tk::mac::ShowPreferences', handlers.settings_dialog)
        apple_menu.add_separator()

        edit_menu = tk.Menu(menubar)
        menubar.add_cascade(menu=edit_menu, label='Edit')
        # todo find out if these events do everything needed to implement the edit functions.
        # todo All except Undo and Redo appear to be functioning correctly. Why aren't they working?
        edit_menu.add_command(label='Undo', command=lambda: self.parent.focus_get().event_generate('<<Undo>>'),
                              accelerator='Command+Z')
        edit_menu.add_command(label='Redo', command=lambda: self.parent.focus_get().event_generate('<<Redo>>'),
                              accelerator='Command+Ctrl+Z')
        edit_menu.add_separator()
        edit_menu.add_command(label='Cut', command=lambda: self.parent.focus_get().event_generate('<<Cut>>'),
                              accelerator='Command+X')
        edit_menu.add_command(label='Copy', command=lambda: self.parent.focus_get().event_generate('<<Copy>>'),
                              accelerator='Command+C')
        edit_menu.add_command(label='Paste', command=lambda: self.parent.focus_get().event_generate('<<Paste>>'),
                              accelerator='Command+V')
        edit_menu.add_command(label='Clear', command=lambda: self.parent.focus_get().event_generate('<<Clear>>'))

        movie_menu = tk.Menu(menubar)
        menubar.add_cascade(menu=movie_menu, label='Movie')
        movie_menu.add_command(label='Add Movie…', command=handlers.add_movie)
        movie_menu.add_command(label='Edit Movie…', command=handlers.edit_movie)
        movie_menu.add_command(label='Delete Movie…', command=handlers.edit_movie)
        movie_menu.add_separator()
        movie_menu.add_command(label='Add Tag…', command=handlers.add_tag)
        movie_menu.add_command(label='Edit Tag…', command=handlers.edit_tag)
        movie_menu.add_command(label='Delete Tag…', command=handlers.edit_tag)

        window_menu = tk.Menu(menubar, name='window')
        menubar.add_cascade(menu=window_menu, label='Window')

        # todo add help screen otherwise remove the help menu altogether.
        help_menu = tk.Menu(menubar, name='help')
        menubar.add_cascade(menu=help_menu, label='Help')
        # Todo find out why 'search' can't find anything.
        # self.parent.createcommand('tk::mac::ShowHelp', <<code to display on-line(?) help>>)

        self.parent.config(menu=menubar)

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
