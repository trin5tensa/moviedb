"""Test module."""

#  Copyright ©2021. Stephen Rigden.
#  Last modified 1/15/21, 8:44 AM by stephen.
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

from contextlib import contextmanager
from dataclasses import dataclass, field

import pytest

import tmdb


CREDITS = dict(crew=[dict(name='Eric Idle', job='Composer'),
                     dict(name='Terry Gilliam', job='Director'),])


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
            assert cm[0] == 'Terry Gilliam'
            
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

    def test_unexpected_HTTP_error_reraised(self, monkeypatch):
        monkeypatch.setattr(tmdb.tmdbsimple, 'Movies', DummyMoviesUnspecifiedError)
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
    def get_director_context(self, api_key, movie_id):
        hold_api_key = tmdb.tmdbsimple.API_KEY
        yield tmdb.get_tmdb_directors(api_key, movie_id)
        tmdb.tmdbsimple.API_KEY = hold_api_key


# noinspection PyPep8Naming
class TestGetTMDBMovieInfo:
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
    
    def test_unexpected_HTTP_error_reraised(self, monkeypatch):
        monkeypatch.setattr(tmdb.tmdbsimple, 'Movies', DummyMoviesUnspecifiedError)
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
    def get_movie_info_context(self, api_key, movie_id):
        hold_api_key = tmdb.tmdbsimple.API_KEY
        yield tmdb.get_tmdb_movie_info(api_key, movie_id)
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
    def raise_exception(self):
        msg = '401 Client Error: Unauthorized for url'
        raise tmdb.requests.exceptions.HTTPError(msg)
    
    def info(self, timeout):
        self.raise_exception()
        
    def credits(self, timeout):
        self.raise_exception()
    

@dataclass
class DummyMovies404(DummyMovies):
    """A test dummy for TMDB's Movies class which raises a URL not found exception."""
    def raise_exception(self):
        msg = '404 Client Error: Not Found for url:'
        raise tmdb.requests.exceptions.HTTPError(msg)

    def info(self, timeout):
        self.raise_exception()
        
    def credits(self, timeout):
        self.raise_exception()


@dataclass
class DummyMoviesUnspecifiedError(DummyMovies):
    """A test dummy for TMDB's Movies class which raises an unspecified HTTP error ."""
    def raise_exception(self):
        msg = 'Unspecified error:'
        raise tmdb.requests.exceptions.HTTPError(msg)

    def info(self, timeout):
        self.raise_exception()

    def credits(self, timeout):
        self.raise_exception()

@dataclass
class DummyConnectionPool:
    """A support class for the test dummy DummyMoviesConnectionError."""
    args: tuple = field(default_factory=tuple, init=False)
    
    def __post_init__(self):
        self.args = ('Max retries exceeded', )


@dataclass
class DummyConnectionError:
    """A support class for the test dummy DummyMoviesConnectionError."""
    args: tuple = field(default_factory=tuple, init=False)
    
    def __post_init__(self):
        self.args = (DummyConnectionPool(), )
        
        
@dataclass
class DummyMoviesConnectionError(DummyMovies):
    """A test dummy for TMDB's Movies class which raises a timeout error."""
    def raise_exception(self):
        exception = DummyConnectionError()
        raise tmdb.requests.exceptions.ConnectionError(exception)

    def info(self, timeout):
        self.raise_exception()

    def credits(self, timeout):
        self.raise_exception()