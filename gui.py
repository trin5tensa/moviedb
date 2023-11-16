"""GUI Controller

This module controls all gui activity
"""
#  Copyright (c) 2022-2023. Stephen Rigden.
#  Last modified 11/16/23, 3:26 PM by stephen.
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

import tkinter as tk

import config
import mainwindow


def run():
    """Run the GUI."""
    config.current.tk_root = tk.Tk()
    root = config.current.tk_root
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    mainwindow.MainWindow(root)
    root.mainloop()
