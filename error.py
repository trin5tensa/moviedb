"""Project errors. """

#  Copyright© 2019. Stephen Rigden.
#  Last modified 9/17/19, 8:09 AM by stephen.
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

# moviedb-#68
#  See 'User defined Exceptions' in 'Errors and Exceptions' in Python docs.
#  User defined errors should be placed in modules

class MoviedbError(Exception):
    """Base class for moviedb's exceptions."""


class MoviedbInvalidImportData(MoviedbError):
    """Exception raised for bad import file data."""
