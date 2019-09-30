"""Main Window."""

#  Copyright© 2019. Stephen Rigden.
#  Last modified 9/30/19, 9:24 AM by stephen.
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

import tkinter as tk
from typing import Optional


class MainWindow:
    """Create and manage the menu bar and the application's main window. """
    # moviedb-#75 Development Stub based on pigjar
    tk_parent: Optional[tk.Tk] = None

    def __post_init__(self):
        """This is the part of __init__ that handles everything that shouldn't be in __init__."""
        # moviedb-#75
        #   Development Stub based on pigjar
        #   This is the part of pigjar's __init__ that handles everything that shouldn't be
        #   in an __init__
        #   Setup tk
        pass
