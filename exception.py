"""Exceptions for the modules of moviesdb. """


#  Copyright© 2020. Stephen Rigden.
#  Last modified 4/6/20, 7:40 AM by stephen.
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


class MovieDBException(Exception):
    """Base class for moviedb exceptions."""


class DatabaseException(MovieDBException):
    """Base class for database exceptions."""


class MovieDBConstraintFailure(DatabaseException):
    """Exception raised for title and year constraint violation."""


class MovieSearchFoundNothing(DatabaseException):
    """Exception raised when a search found no records."""


class MovieSearchInvalidCount(DatabaseException):
    """Exception raised when count is not a positive integer."""
