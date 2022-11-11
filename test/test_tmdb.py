"""Test module."""

#  Copyright (c) 2022-2022. Stephen Rigden.
#  Last modified 11/11/22, 9:07 AM by stephen.
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

from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import List

import pytest

import tmdb


CREDITS = dict(crew=[dict(name='Eric Idle', job='Composer'),
                     dict(name='Terry Gilliam', job='Director'), ])
MOVIES = [dict(id=1, title='forty two dalmatians'), dict(id=2, title='one forty two squadron')]


class TestGetTMDBMovieInfo:
    MOVIE_INFO = dict(id=42, title='Forty Two')
    DIRECTORS = {'Directors': ['Terry Gilliam']}

    def test_concatenated_movie_info_returned(self, monkeypatch):
        api_key = 'dummy api key'
        movie_id = '42'

        monkeypatch.setattr(tmdb, '_get_tmdb_movie_info', lambda *args: self.MOVIE_INFO)
        monkeypatch.setattr(tmdb, '_get_tmdb_directors', lambda *args: self.DIRECTORS)
        with self.get_movie_info_context(api_key, movie_id) as cm:
            # noinspection PyTypeChecker
            assert cm == self.MOVIE_INFO | self.DIRECTORS

    @contextmanager
    def get_movie_info_context(self, api_key: str, movie_id: str):
        hold_api_key = tmdb.tmdbsimple.API_KEY
        yield tmdb.get_tmdb_movie_info(api_key, movie_id)
        tmdb.tmdbsimple.API_KEY = hold_api_key


# noinspection PyPep8Naming
class TestSearchMovies:
    api_key = 'dummy api key'
    title_query = 'forty two'

    def test_api_key_registered(self, monkeypatch):
        monkeypatch.setattr(tmdb.tmdbsimple, 'Search', DummySearch)
        with self.get_search_context(self.api_key, self.title_query):
            assert tmdb.tmdbsimple.API_KEY == self.api_key
            
    def test_search_results_returned(self, monkeypatch):
        monkeypatch.setattr(tmdb.tmdbsimple, 'Search', DummySearch)
        with self.get_search_context(self.api_key, self.title_query) as cm:
            assert tmdb.tmdbsimple.API_KEY == self.api_key
            assert cm == MOVIES

    def test_401_logs_error(self, monkeypatch):
        monkeypatch.setattr(tmdb.tmdbsimple, 'Search', DummySearch401)
        error_args = []
        monkeypatch.setattr(tmdb.logging, 'error', lambda *args: error_args.append(args))
        with pytest.raises(tmdb.TMDBAPIKeyException):
            with self.get_search_context(self.api_key, self.title_query):
                pass
        assert error_args[0][0] == 'API Key error: 401 Client Error: Unauthorized for url'

    def test_401_raises_TMDBAPIKeyException(self, monkeypatch):
        monkeypatch.setattr(tmdb.tmdbsimple, 'Search', DummySearch401)
        monkeypatch.setattr(tmdb.logging, 'error', lambda *args: None)
        with pytest.raises(tmdb.TMDBAPIKeyException) as exc:
            with self.get_search_context(self.api_key, self.title_query):
                pass
        assert exc.value.args[0] == 'API Key error: 401 Client Error: Unauthorized for url'

    def test_unexpected_HTTP_error_logged(self, monkeypatch):
        monkeypatch.setattr(tmdb.tmdbsimple, 'Search', DummySearchUnspecifiedError)
        error_args = []
        monkeypatch.setattr(tmdb.logging, 'error', lambda *args: error_args.append(args))
        with pytest.raises(tmdb.requests.exceptions.HTTPError):
            with self.get_search_context(self.api_key, self.title_query):
                pass
        assert isinstance(error_args[0][0], tmdb.requests.exceptions.HTTPError)
        assert str(error_args[0][0]) == 'Unspecified error:'
        
    def test_unexpected_HTTP_error_reraised(self, monkeypatch):
        monkeypatch.setattr(tmdb.tmdbsimple, 'Search', DummySearchUnspecifiedError)
        monkeypatch.setattr(tmdb.logging, 'error', lambda *args: None)
        with pytest.raises(tmdb.requests.exceptions.HTTPError) as exc:
            with self.get_search_context(self.api_key, self.title_query):
                pass
        assert exc.value.args[0] == f"Unspecified error:"
        
    def test_connection_failure_logged(self, monkeypatch):
        monkeypatch.setattr(tmdb.tmdbsimple, 'Search', DummySearchConnectionError)
        error_args = []
        monkeypatch.setattr(tmdb.logging, 'info', lambda *args: error_args.append(args))
        with pytest.raises(tmdb.TMDBConnectionTimeout):
            with self.get_search_context(self.api_key, self.title_query):
                pass
        assert error_args[0][0] == (f"Unable to connect to TMDB. \n"
                                    f"DummyConnectionPool(args=('Max retries exceeded',))")

    def test_connection_failure_raises_TMDBConnectionTimeout(self, monkeypatch):
        monkeypatch.setattr(tmdb.tmdbsimple, 'Search', DummySearchConnectionError)
        monkeypatch.setattr(tmdb.logging, 'info', lambda *args: None)
        with pytest.raises(tmdb.TMDBConnectionTimeout) as exc:
            with self.get_search_context(self.api_key, self.title_query):
                pass
        assert 'Max retries exceeded' in exc.value.args[0]

    @contextmanager
    def get_search_context(self, api_key: str, title_query: str):
        hold_api_key = tmdb.tmdbsimple.API_KEY
        yield tmdb.search_movies(api_key, title_query)
        tmdb.tmdbsimple.API_KEY = hold_api_key


# noinspection PyPep8Naming
class TestGetTMDBDirectors:
    api_key = 'dummy api key'
    movie_id = '42'
    
    def test_api_key_registered(self, monkeypatch):
        monkeypatch.setattr(tmdb.tmdbsimple, 'Movies', DummyMovies)
        with self.get_director_context(self.api_key, self.movie_id):
            assert tmdb.tmdbsimple.API_KEY == self.api_key
        
    def test_director_returned(self, monkeypatch):
        monkeypatch.setattr(tmdb.tmdbsimple, 'Movies', DummyMovies)
        with self.get_director_context(self.api_key, self.movie_id) as cm:
            assert cm == dict(Director=['Terry Gilliam'])

    def test_401_logs_error(self, monkeypatch):
        monkeypatch.setattr(tmdb.tmdbsimple, 'Movies', DummyMovies401)
        error_args = []
        monkeypatch.setattr(tmdb.logging, 'error', lambda *args: error_args.append(args))
        with pytest.raises(tmdb.TMDBAPIKeyException):
            with self.get_director_context(self.api_key, self.movie_id):
                pass
        assert error_args[0][0] == 'API Key error: 401 Client Error: Unauthorized for url'

    def test_401_raises_TMDBAPIKeyException(self, monkeypatch):
        monkeypatch.setattr(tmdb.tmdbsimple, 'Movies', DummyMovies401)
        monkeypatch.setattr(tmdb.logging, 'error', lambda *args: None)
        with pytest.raises(tmdb.TMDBAPIKeyException) as exc:
            with self.get_director_context(self.api_key, self.movie_id):
                pass
        assert exc.value.args[0] == 'API Key error: 401 Client Error: Unauthorized for url'

    def test_404_logs_error(self, monkeypatch):
        monkeypatch.setattr(tmdb.tmdbsimple, 'Movies', DummyMovies404)
        error_args = []
        monkeypatch.setattr(tmdb.logging, 'error', lambda *args: error_args.append(args))
        with pytest.raises(tmdb.TMDBMovieIDMissing):
            with self.get_director_context(self.api_key, self.movie_id):
                pass
        assert error_args[0][0] == (f"The TMDB id '42' was not found on the TMDB site. \n"
                                    f"404 Client Error: Not Found for url:")

    def test_404_raises_TMDBMovieIDMissing(self, monkeypatch):
        monkeypatch.setattr(tmdb.tmdbsimple, 'Movies', DummyMovies404)
        monkeypatch.setattr(tmdb.logging, 'error', lambda *args: None)
        with pytest.raises(tmdb.TMDBMovieIDMissing) as exc:
            with self.get_director_context(self.api_key, self.movie_id):
                pass
        assert exc.value.args[0] == (f"The TMDB id '42' was not found on the TMDB site. \n"
                                     f"404 Client Error: Not Found for url:")

    def test_unexpected_HTTP_error_logged(self, monkeypatch):
        monkeypatch.setattr(tmdb.tmdbsimple, 'Movies', DummyMoviesUnspecifiedError)
        error_args = []
        monkeypatch.setattr(tmdb.logging, 'error', lambda *args: error_args.append(args))
        with pytest.raises(tmdb.requests.exceptions.HTTPError):
            with self.get_director_context(self.api_key, self.movie_id):
                pass
        assert isinstance(error_args[0][0], tmdb.requests.exceptions.HTTPError)
        assert str(error_args[0][0]) == 'Unspecified error:'

    def test_unexpected_HTTP_error_reraised(self, monkeypatch):
        monkeypatch.setattr(tmdb.tmdbsimple, 'Movies', DummyMoviesUnspecifiedError)
        monkeypatch.setattr(tmdb.logging, 'error', lambda *args: None)
        with pytest.raises(tmdb.requests.exceptions.HTTPError) as exc:
            with self.get_director_context(self.api_key, self.movie_id):
                pass
        assert exc.value.args[0] == f"Unspecified error:"

    def test_connection_failure_logged(self, monkeypatch):
        monkeypatch.setattr(tmdb.tmdbsimple, 'Movies', DummyMoviesConnectionError)
        error_args = []
        monkeypatch.setattr(tmdb.logging, 'info', lambda *args: error_args.append(args))
        with pytest.raises(tmdb.TMDBConnectionTimeout):
            with self.get_director_context(self.api_key, self.movie_id):
                pass
        assert error_args[0][0] == (f"Unable to connect to TMDB. "
                                    f"DummyConnectionPool(args=('Max retries exceeded',))")

    def test_connection_failure_raises_TMDBConnectionTimeout(self, monkeypatch):
        monkeypatch.setattr(tmdb.tmdbsimple, 'Movies', DummyMoviesConnectionError)
        monkeypatch.setattr(tmdb.logging, 'error', lambda *args: None)
        with pytest.raises(tmdb.TMDBConnectionTimeout) as exc:
            with self.get_director_context(self.api_key, self.movie_id):
                pass
        assert 'Max retries exceeded' in exc.value.args[0]

    @contextmanager
    def get_director_context(self, api_key: str, movie_id: str):
        hold_api_key = tmdb.tmdbsimple.API_KEY
        yield tmdb._get_tmdb_directors(api_key, movie_id)
        tmdb.tmdbsimple.API_KEY = hold_api_key


# noinspection PyPep8Naming
class TestGetTMDBMovieInfoPrivate:
    api_key = 'dummy api key'
    movie_id = '42'

    def test_api_key_registered(self, monkeypatch):
        monkeypatch.setattr(tmdb.tmdbsimple, 'Movies', DummyMovies)
        with self.get_movie_info_context(self.api_key, self.movie_id):
            assert tmdb.tmdbsimple.API_KEY == self.api_key

    def test_movie_info_returned(self, monkeypatch):
        monkeypatch.setattr(tmdb.tmdbsimple, 'Movies', DummyMovies)
        with self.get_movie_info_context(self.api_key, self.movie_id) as cm:
            assert cm == self.movie_id
    
    def test_401_logs_error(self, monkeypatch):
        monkeypatch.setattr(tmdb.tmdbsimple, 'Movies', DummyMovies401)
        error_args = []
        monkeypatch.setattr(tmdb.logging, 'error', lambda *args: error_args.append(args))
        with pytest.raises(tmdb.TMDBAPIKeyException):
            with self.get_movie_info_context(self.api_key, self.movie_id):
                pass
        assert error_args[0][0] == 'API Key error: 401 Client Error: Unauthorized for url'
    
    def test_401_raises_TMDBAPIKeyException(self, monkeypatch):
        monkeypatch.setattr(tmdb.tmdbsimple, 'Movies', DummyMovies401)
        monkeypatch.setattr(tmdb.logging, 'error', lambda *args: None)
        with pytest.raises(tmdb.TMDBAPIKeyException) as exc:
            with self.get_movie_info_context(self.api_key, self.movie_id):
                pass
        assert exc.value.args[0] == 'API Key error: 401 Client Error: Unauthorized for url'
    
    def test_404_logs_error(self, monkeypatch):
        monkeypatch.setattr(tmdb.tmdbsimple, 'Movies', DummyMovies404)
        error_args = []
        monkeypatch.setattr(tmdb.logging, 'error', lambda *args: error_args.append(args))
        with pytest.raises(tmdb.TMDBMovieIDMissing):
            with self.get_movie_info_context(self.api_key, self.movie_id):
                pass
        assert error_args[0][0] == (f"The TMDB id '42' was not found on the TMDB site. \n"
                                    f"404 Client Error: Not Found for url:")
    
    def test_404_raises_TMDBMovieIDMissing(self, monkeypatch):
        monkeypatch.setattr(tmdb.tmdbsimple, 'Movies', DummyMovies404)
        monkeypatch.setattr(tmdb.logging, 'error', lambda *args: None)
        with pytest.raises(tmdb.TMDBMovieIDMissing) as exc:
            with self.get_movie_info_context(self.api_key, self.movie_id):
                pass
        assert exc.value.args[0] == (f"The TMDB id '42' was not found on the TMDB site. \n"
                                     f"404 Client Error: Not Found for url:")
    
    def test_unexpected_HTTP_error_logged(self, monkeypatch):
        monkeypatch.setattr(tmdb.tmdbsimple, 'Movies', DummyMoviesUnspecifiedError)
        error_args = []
        monkeypatch.setattr(tmdb.logging, 'error', lambda *args: error_args.append(args))
        with pytest.raises(tmdb.requests.exceptions.HTTPError):
            with self.get_movie_info_context(self.api_key, self.movie_id):
                pass
        assert isinstance(error_args[0][0], tmdb.requests.exceptions.HTTPError)
        assert str(error_args[0][0]) == 'Unspecified error:'

    def test_unexpected_HTTP_error_reraised(self, monkeypatch):
        monkeypatch.setattr(tmdb.tmdbsimple, 'Movies', DummyMoviesUnspecifiedError)
        monkeypatch.setattr(tmdb.logging, 'error', lambda *args: None)
        with pytest.raises(tmdb.requests.exceptions.HTTPError) as exc:
            with self.get_movie_info_context(self.api_key, self.movie_id):
                pass
        assert exc.value.args[0] == f"Unspecified error:"
    
    def test_connection_failure_logged(self, monkeypatch):
        monkeypatch.setattr(tmdb.tmdbsimple, 'Movies', DummyMoviesConnectionError)
        error_args = []
        monkeypatch.setattr(tmdb.logging, 'info', lambda *args: error_args.append(args))
        with pytest.raises(tmdb.TMDBConnectionTimeout):
            with self.get_movie_info_context(self.api_key, self.movie_id):
                pass
        assert error_args[0][0] == (f"Unable to connect to TMDB. "
                                    f"DummyConnectionPool(args=('Max retries exceeded',))")
    
    def test_connection_failure_raises_TMDBConnectionTimeout(self, monkeypatch):
        monkeypatch.setattr(tmdb.tmdbsimple, 'Movies', DummyMoviesConnectionError)
        monkeypatch.setattr(tmdb.logging, 'error', lambda *args: None)
        with pytest.raises(tmdb.TMDBConnectionTimeout) as exc:
            with self.get_movie_info_context(self.api_key, self.movie_id):
                pass
        assert 'Max retries exceeded' in exc.value.args[0]

    @contextmanager
    def get_movie_info_context(self, api_key: str, movie_id: str):
        hold_api_key = tmdb.tmdbsimple.API_KEY
        yield tmdb._get_tmdb_movie_info(api_key, movie_id)
        tmdb.tmdbsimple.API_KEY = hold_api_key
        

@dataclass
class DummyMovies:
    """A test dummy for TMDB's Movies class."""
    tmdb_movie_id: str

    def info(self, timeout):
        assert timeout == tmdb.TIMEOUT
        return self.tmdb_movie_id
    
    def credits(self, timeout):
        assert timeout == tmdb.TIMEOUT
        return CREDITS


@dataclass
class DummyMovies401(DummyMovies):
    """A test dummy for TMDB's Movies class which raises an API key failure."""
    @staticmethod
    def raise_exception():
        msg = '401 Client Error: Unauthorized for url'
        raise tmdb.requests.exceptions.HTTPError(msg)
    
    def info(self, timeout):
        self.raise_exception()
        
    def credits(self, timeout):
        self.raise_exception()
    

@dataclass
class DummyMovies404(DummyMovies):
    """A test dummy for TMDB's Movies class which raises a URL not found exception."""
    @staticmethod
    def raise_exception():
        msg = '404 Client Error: Not Found for url:'
        raise tmdb.requests.exceptions.HTTPError(msg)

    def info(self, timeout):
        self.raise_exception()
        
    def credits(self, timeout):
        self.raise_exception()


@dataclass
class DummyMoviesUnspecifiedError(DummyMovies):
    """A test dummy for TMDB's Movies class which raises an unspecified HTTP error."""
    @staticmethod
    def raise_exception():
        msg = 'Unspecified error:'
        raise tmdb.requests.exceptions.HTTPError(msg)

    def info(self, timeout):
        self.raise_exception()

    def credits(self, timeout):
        self.raise_exception()


@dataclass
class DummyConnectionPool:
    """A support class for ConnectionError test dummies."""
    args: tuple = field(default_factory=tuple, init=False)
    
    def __post_init__(self):
        self.args = ('Max retries exceeded', )


@dataclass
class DummyConnectionError:
    """A support class for ConnectionError test dummies."""
    args: tuple = field(default_factory=tuple, init=False)
    
    def __post_init__(self):
        self.args = (DummyConnectionPool(), )
        
        
@dataclass
class DummyMoviesConnectionError(DummyMovies):
    """A test dummy for TMDB's Movies class which raises a timeout error."""
    @staticmethod
    def raise_exception():
        exception = DummyConnectionError()
        raise tmdb.requests.exceptions.ConnectionError(exception)

    def info(self, timeout):
        self.raise_exception()

    def credits(self, timeout):
        self.raise_exception()


@dataclass
class DummySearch:
    """A test dummy for TMDB's Search class."""
    results: List[dict] = field(default_factory=list, init=False)
    
    def __post_init__(self):
        if not self.results:
            self.results = MOVIES
    
    def movie(self, query: str = None, **kwargs):
        pass


@dataclass
class DummySearch401(DummySearch):
    """A test dummy for TMDB's Movies class which raises an API key failure."""
    def movie(self, query: str = None, **kwargs):
        msg = '401 Client Error: Unauthorized for url'
        raise tmdb.requests.exceptions.HTTPError(msg)


@dataclass
class DummySearchUnspecifiedError(DummySearch):
    """A test dummy for TMDB's Movies class which raises an unspecified HTTP error."""
    def movie(self, query: str = None, **kwargs):
        msg = 'Unspecified error:'
        raise tmdb.requests.exceptions.HTTPError(msg)


@dataclass
class DummySearchConnectionError(DummySearch):
    """A test dummy for TMDB's Movies class which raises a timeout error."""
    def movie(self, query: str = None, **kwargs):
        exception = DummyConnectionError()
        raise tmdb.requests.exceptions.ConnectionError(exception)
