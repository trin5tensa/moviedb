"""GUI Controller

This module controls all gui activity
"""

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

import config
import mainwindow


def run():
    """Run the GUI."""
    config.app.root_window = mainwindow.MainWindow()
    config.app.root_window.__post_init__()
    config.app.root_window.tk_parent.mainloop()
