"""Test module."""
#  Copyright (c) 2022-2022. Stephen Rigden.
#  Last modified 12/14/22, 7:59 AM by stephen.
#  This program_name is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#  This program_name is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License
#  along with this program_name.  If not, see <https://www.gnu.org/licenses/>.

from dataclasses import dataclass, field
from typing import Final

import tmdb

API_KEY: Final = 'test_api_key'
TITLE_QUERY: Final = 'test_title_query'
TMDB_MOVIE_ID: Final = '42'
TEST_TITLE: Final = 'My Test Movie'
TEST_RELEASE_DATE: Final = '2042-06-06'
TEST_BLANK_RELEASE_DATE: Final = ''
TEST_RUNTIME: Final = '424'
TEST_NOTES: Final = 'It was a good test wot I wrote.'
TEST_DIRECTORS: Final = ['Immaterial']
TEST_DIRECTOR: Final = TEST_DIRECTORS[0]
TEST_TIMEOUT_EXC_ARGS: Final = 'It is I, 42 I'
TEST_TIMEOUT_LOG_MSG: Final = f'Unable to connect to TMDB. {TEST_TIMEOUT_EXC_ARGS}'
TEST_BAD_KEY_EXC_ARGS: Final = '401 Client Error: Unauthorized for url test_garbage_url'
TEST_BAD_KEY_LOG_MSG: Final = f'API Key error: {TEST_BAD_KEY_EXC_ARGS}'
TEST_MOVIE_NOT_FOUND_EXC_ARGS: Final = '404 Client Error: Not Found for url:'
TEST_MOVIE_NOT_FOUND_LOG_MSG: Final = (f"The TMDB id '42' was not found on the TMDB site. \n"
                                       f"{TEST_MOVIE_NOT_FOUND_EXC_ARGS}")


# noinspection PyMissingOrEmptyDocstring
@dataclass
class DummyTMDBSearch:
    results: list = field(default_factory=list, init=False, repr=False)

    def movie(self, **kwargs):
        self.results = [dict(id=TMDB_MOVIE_ID)]


# noinspection PyMissingOrEmptyDocstring
@dataclass
class DummyTMDBTimeoutError(DummyTMDBSearch):
    def movie(self, **kwargs):
        raise tmdb.requests.exceptions.ConnectionError(DummyExcArgs(TEST_TIMEOUT_EXC_ARGS))


# noinspection PyMissingOrEmptyDocstring
@dataclass
class DummyExcArgs:
    exc: str
    args: list = field(default_factory=list, init=False)

    def __post_init__(self):
        self.args = [self.exc]


# noinspection PyMissingOrEmptyDocstring
@dataclass
class DummyTMDBKeyError(DummyTMDBSearch):
    def movie(self, **kwargs):
        raise tmdb.requests.exceptions.HTTPError(TEST_BAD_KEY_EXC_ARGS)


# noinspection PyMissingOrEmptyDocstring
@dataclass
class DummyTMDBMovies:
    movie_id: str

    def __post_init__(self):
        """A failure of this assertion indicates that the movie_id 'found' by DummyTMDBSearch.movie has not been
        correctly used in the call to DummyTMDBMovies."""
        assert self.movie_id == TMDB_MOVIE_ID

    @staticmethod
    def info():
        return dict(
            title=TEST_TITLE,
            release_date=TEST_RELEASE_DATE,
            runtime=TEST_RUNTIME,
            overview=TEST_NOTES
            )

    @staticmethod
    def credits():
        return dict(crew=[dict(name=TEST_DIRECTOR, job='Director')])


# noinspection PyMissingOrEmptyDocstring
@dataclass
class DummyTMDBBlankDateMovie(DummyTMDBMovies):
    def info(self, **kwargs):
        return dict(
            title=TEST_TITLE,
            release_date=TEST_BLANK_RELEASE_DATE,
            runtime=TEST_RUNTIME,
            overview=TEST_NOTES
            )


# noinspection PyMissingOrEmptyDocstring
@dataclass
class DummyTMDBMissingMovie(DummyTMDBMovies):
    def info(self, **kwargs):
        raise tmdb.requests.exceptions.HTTPError(TEST_MOVIE_NOT_FOUND_EXC_ARGS)


# noinspection PyMissingOrEmptyDocstring
@dataclass
class DummyUnexpectedHTTPError(DummyTMDBMovies):
    def info(self, **kwargs):
        raise tmdb.requests.exceptions.HTTPError
