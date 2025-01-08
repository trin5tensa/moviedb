"""Menu handlers.

Menu handlers connect the user menu items with the functions which effect
the user's commands.

Historical Note 12/23/2024:
A single handler module was originally located at the top level of the
movie project. It contained handler functions for every menu item, as they
were not permitted to call any other module directly. It also contained the
callbacks needed to complete tasks outside the scope of the called
module. It was connecting everything to everything and was every bit as
bad as that sounds.

For example, the 'Add Movie' function needed to call a widget in the GUI
module. It supplied a callback function to be used when the user
clicked the 'Commit' button in the widget. The callback function further
called a function in the database module to commit the record to the
database. If the commit was successful, the process ended. If not, the
database module function would raise an exception. This was handled
within the GUI module, which meant the GUI module needed to have knowledge
of the database module. Mixing 'knowledge' of the database into the GUI
created major problems for the DB1 database upgrade in 2024.

As part of the DB1 upgrade, all database 'knowledge' was moved to the
database module and the new handlers.databasehandlers module. All functions
and callbacks dealing with data that is bound for the database have been
removed from the original handler module and rewritten for the handlers'
database module. Any database exceptions are handled inside the handler
module.

The functionally redundant database knowledge within the GUI will be
removed as part of the next GUI upgrade.
"""

#  Copyright© 2025. Stephen Rigden.
#  Last modified 1/8/25, 1:01 PM by stephen.
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


from . import sundries, database, moviebagfacade
