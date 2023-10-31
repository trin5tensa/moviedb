"""Exceptions for the modules of moviesdb. """


#  Copyright (c) 2022-2023. Stephen Rigden.
#  Last modified 10/31/23, 7:57 AM by stephen.
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


class MovieDBException(Exception):
    """Base class for moviedb exceptions."""


class DatabaseException(MovieDBException):
    """Base class for database exceptions."""


class MovieDBConstraintFailure(DatabaseException):
    """Exception raised for title and year constraint violation."""
    msg = 'Database constraint failure.'
    detail = 'A movie with this title and year is already present in the database.'


class MovieYearConstraintFailure(DatabaseException):
    """Exception raised for invalid year constraint violation."""
    # When this exception is raised during normal running the exc.args[0] from the database manager is
    # reported to the user. This 'args' attribute supplies a dummy fpr testing.
    # moviedb-#262 Invalid year crashes the program
    # This bug makes it impossible to carry out integration testing. It is possible that the presence of the
    # `args` attribute blocks retrieval of the exact cause of error from exc.args[0].
    # todo Write code to simulate this problem and see if a 'test' attribute steps on the args raised by the
    #  exception mechanism
    args = ('test msg', )


class MovieDBMovieNotFound(DatabaseException):
    """Exception raised for movie not found in database."""


class DatabaseSearchFoundNothing(DatabaseException):
    """Exception raised when a search found no records."""


class MovieSearchInvalidCount(DatabaseException):
    """Exception raised when count is not a positive integer."""


# noinspection PyMissingOrEmptyDocstring
class TMDBException(Exception):
    pass


# noinspection PyMissingOrEmptyDocstring
class TMDBAPIKeyException(TMDBException):
    pass


# noinspection PyMissingOrEmptyDocstring
class TMDBMovieIDMissing(TMDBException):
    pass


# noinspection PyMissingOrEmptyDocstring
class TMDBNoRecordsFound(TMDBException):
    pass


# noinspection PyMissingOrEmptyDocstring
class TMDBConnectionTimeout(TMDBException):
    pass


