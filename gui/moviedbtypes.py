"""Global constants and type definitions."""

#  Copyright© 2025. Stephen Rigden.
#  Last modified 5/16/25, 7:07 AM by stephen.
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
import tkinter.ttk as ttk

type TkParentType = tk.Tk | tk.Toplevel | ttk.Frame
type TkSequence = list[str] | tuple[str, ...]
