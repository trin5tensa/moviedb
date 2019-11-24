"""Main Window."""

#  Copyright© 2019. Stephen Rigden.
#  Last modified 11/24/19, 12:40 PM by stephen.
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

import logging
import re
import tkinter as tk
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Callable, List, Sequence, Tuple, Union

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
        """This is the part of __init__ that handles everything that shouldn't be in __init__."""
        self.parent.title(config.app.name)
        self.parent.option_add('*tearOff', False)
        self.parent.geometry(self.set_geometry())
        self.place_menubar(MenuData().menus)
        self.parent.protocol('WM_DELETE_WINDOW', self.tk_shutdown)

    def set_geometry(self) -> str:
        """Set window geometry from a default value or app.geometry and make sure it will
        fit on the screen.

        Returns:
            tkinter geometry string.
        """
        if not config.app.geometry:
            config.app.geometry = '900x400+30+30'
        regex = ("(?P<width>[0-9]+)x"
                 "(?P<height>[0-9]+)"
                 "(?P<horizontal_offset>[+-]?[0-9]+)"
                 "(?P<vertical_offset>[+-]?[0-9]+)")
        regex = re.compile(regex)
        re_geometry = re.search(regex, config.app.geometry)
        width, horizontal_offset = self.validate_desired_geometry(
            re_geometry.group('width'), re_geometry.group('horizontal_offset'),
            self.parent.winfo_screenwidth())
        height, vertical_offset = self.validate_desired_geometry(
            re_geometry.group('height'), re_geometry.group('vertical_offset'),
            self.parent.winfo_screenheight())
        geometry = "{}x{}{}{}".format(width, height, horizontal_offset, vertical_offset)
        return geometry
    
    @staticmethod
    def validate_desired_geometry(length: str, offset: str, available: str) -> Tuple[str, str]:
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

    def place_menubar(self, menus: List['Menu']):
        """Create menubar."""
        menubar = tk.Menu(self.parent)
        self.parent.config(menu=menubar)
        for menu in menus:
            self.place_menu(menubar, menu)
    
    def place_menu(self, menubar: tk.Menu, menu: 'Menu'):
        """Create a menu with its menu items.

        Args:
            menubar: Parent menu bar.
            menu:
        """
        # Create a Tk menu for building the Tk menu object.
        cascade = tk.Menu(menubar)
        
        for menu_item_ix, menu_item in enumerate(menu.menu_items):
            # Add a separator
            if isinstance(menu_item, str):
                cascade.add_separator()

            # Create the program exit item
            elif menu_item.name == QUIT_ITEM:
                cascade.add_command(label=f"{QUIT_ITEM} {config.app.name.title()}",
                                    command=self.tk_shutdown, state=tk.NORMAL)

            # Add a menu item which has a handler
            elif callable(menu_item.selection_handler):
                cascade.add_command(label=menu_item.name, command=menu_item.selection_handler)
                if menu_item.active:
                    cascade.entryconfig(menu_item_ix, state=tk.NORMAL)
                else:
                    cascade.entryconfig(menu_item_ix, state=tk.DISABLED)

            # Add a disabled menu item if there is no handler.
            elif not menu_item.selection_handler:
                cascade.add_command(label=menu_item.name, state=tk.DISABLED)

            # Unhandled conditions: Not a separator and with a non callable selection_handler.
            else:
                msg = (f"The menu item '{menu_item.name=}' is not a separator and does not "
                       f"contain a callable handler.")
                logging.error(msg=msg)
                cascade.add_command(label=menu_item.name, state=tk.DISABLED)

        # Add menu to menubar
        menubar.add_cascade(label=menu.name, menu=cascade)

    def tk_shutdown(self):
        """Carry out actions needed when main window is closed."""
        # Save geometry in config.app for future permanent storage.
        config.app.geometry = self.parent.winfo_geometry()
        # Destroy all widgets and end mainloop.
        self.parent.destroy()


# noinspection PyUnresolvedReferences
@dataclass
class MenuItem:
    """Data describing a menu item.
    
    Attributes:
        name: User visible label of menu item.
        selection_handler: Handler called when menu item is selected.
        active: Initial active (True) or inactive (False) tk state
    """
    name: str
    selection_handler: Callable = None
    active: bool = True


# noinspection PyUnresolvedReferences
@dataclass
class Menu:
    """Data describing a menu.
    
    Attributes:
        name:
        menu_items:
    """
    name: str
    menu_items: Sequence[Union[MenuItem, str]]


@dataclass
class MenuData:
    """Data for construction and management of the menu."""
    
    def __post_init__(self):
        """Initialize the applications menu bar data.
        
        Menu separators: Use '-' or any other character of type str.
        """

        self.menus = [
                Menu('Moviedb', [
                        MenuItem('About…', handlers.about_dialog),
                        MenuItem(QUIT_ITEM), ]),
                Menu('File', [
                        MenuItem('New…'),
                        MenuItem('Open…'),
                        MenuItem('Save As…'),
                        '-',
                        MenuItem('Import csv'), ]),
                Menu('Edit', [
                        MenuItem('Cut'),
                        MenuItem('Copy'),
                        MenuItem('Paste'), ]),
                Menu('Movie', [
                        MenuItem('Add Movie…', handlers.add_movie),
                        MenuItem('Import…', handlers.import_movies), ]),
                ]
