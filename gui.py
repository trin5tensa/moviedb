"""GUI Controller

This module controls all gui activity
"""

#  Copyright ©2020. Stephen Rigden.
#  Last modified 12/22/20, 8:01 AM by stephen.
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

import config
import mainwindow


def run():
    """Run the GUI."""
    config.tk_root = tk.Tk()
    config.tk_root.columnconfigure(0, weight=1)
    config.tk_root.rowconfigure(0, weight=1)
    config.gui_environment = mainwindow.MainWindow(config.tk_root)
    config.tk_root.mainloop()
