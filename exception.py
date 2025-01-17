"""Exceptions for the modules of moviesdb. """

#  Copyright© 2025. Stephen Rigden.
#  Last modified 1/17/25, 12:36 PM by stephen.
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
