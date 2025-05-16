"""Test module."""

#  Copyright© 2025. Stephen Rigden.
#  Last modified 5/8/25, 9:37 AM by stephen.
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

import pytest

from moviebag import MovieBag, MovieInteger
from .moxenstubs import *


def test_timeout_set():
    assert tmdb.tmdbsimple.REQUESTS_TIMEOUT == (2, 5)


def test_api_key_set(monkeypatch):
    # noinspection PyStatementEffect
    tmdb.tmdbsimple.API_KEY == ""
    monkeypatch.setattr("tmdb.tmdbsimple.Search", DummyTMDBSearch)
    monkeypatch.setattr("tmdb.tmdbsimple.Movies", DummyTMDBMovies)
    tmdb.search_tmdb(API_KEY, TITLE_QUERY, tmdb.queue.Queue())
    assert tmdb.tmdbsimple.API_KEY == API_KEY


def test_movie_data_placed_in_work_queue(monkeypatch):
    monkeypatch.setattr("tmdb.tmdbsimple.Search", DummyTMDBSearch)
    monkeypatch.setattr("tmdb.tmdbsimple.Movies", DummyTMDBMovies)
    work_queue = tmdb.queue.Queue()
    tmdb.search_tmdb(API_KEY, TITLE_QUERY, work_queue)

    expected = [
        MovieBag(
            title=TEST_TITLE,
            year=MovieInteger(TEST_RELEASE_DATE[:4]),
            duration=MovieInteger(TEST_RUNTIME),
            directors=set(TEST_DIRECTORS),
            synopsis=TEST_SYNOPSIS,
        )
    ]
    assert work_queue.get() == expected


def test_movie_data_with_no_date_placed_in_work_queue(monkeypatch):
    monkeypatch.setattr("tmdb.tmdbsimple.Search", DummyTMDBSearch)
    monkeypatch.setattr("tmdb.tmdbsimple.Movies", DummyTMDBBlankDateMovie)
    work_queue = tmdb.queue.Queue()
    tmdb.search_tmdb(API_KEY, TITLE_QUERY, work_queue)

    expected = [
        MovieBag(
            title=TEST_TITLE,
            duration=MovieInteger(TEST_RUNTIME),
            directors=set(TEST_DIRECTORS),
            synopsis=TEST_SYNOPSIS,
        )
    ]
    assert work_queue.get() == expected


# noinspection DuplicatedCode
def test_timeout_error_raised(monkeypatch):
    monkeypatch.setattr("tmdb.tmdbsimple.Search", DummyTMDBTimeoutError)
    monkeypatch.setattr("tmdb.tmdbsimple.Movies", DummyTMDBMovies)

    with pytest.raises(tmdb.exception.TMDBConnectionTimeout) as exc:
        tmdb.search_tmdb(API_KEY, TITLE_QUERY, tmdb.queue.Queue())
    assert TEST_TIMEOUT_LOG_MSG in str(exc)


def test_timeout_error_logged(monkeypatch, caplog):
    caplog.set_level("INFO")
    monkeypatch.setattr("tmdb.tmdbsimple.Search", DummyTMDBTimeoutError)
    monkeypatch.setattr("tmdb.tmdbsimple.Movies", DummyTMDBMovies)

    with pytest.raises(tmdb.exception.TMDBConnectionTimeout):
        tmdb.search_tmdb(API_KEY, TITLE_QUERY, tmdb.queue.Queue())
    assert caplog.messages[0] == TEST_TIMEOUT_LOG_MSG


# noinspection DuplicatedCode
def test_http_error_raised(monkeypatch):
    monkeypatch.setattr("tmdb.tmdbsimple.Search", DummyTMDBKeyError)
    monkeypatch.setattr("tmdb.tmdbsimple.Movies", DummyTMDBMovies)

    with pytest.raises(tmdb.exception.TMDBAPIKeyException) as exc:
        tmdb.search_tmdb(API_KEY, TITLE_QUERY, tmdb.queue.Queue())
    assert TEST_BAD_KEY_LOG_MSG in str(exc)


def test_http_error_logged(monkeypatch, caplog):
    caplog.set_level("ERROR")
    monkeypatch.setattr("tmdb.tmdbsimple.Search", DummyTMDBKeyError)
    monkeypatch.setattr("tmdb.tmdbsimple.Movies", DummyTMDBMovies)

    with pytest.raises(tmdb.exception.TMDBAPIKeyException):
        tmdb.search_tmdb(API_KEY, TITLE_QUERY, tmdb.queue.Queue())
    assert caplog.messages[0] == TEST_BAD_KEY_LOG_MSG


# noinspection DuplicatedCode
def test_missing_movie_error_raised(monkeypatch):
    monkeypatch.setattr("tmdb.tmdbsimple.Search", DummyTMDBSearch)
    monkeypatch.setattr("tmdb.tmdbsimple.Movies", DummyTMDBMissingMovie)

    with pytest.raises(tmdb.exception.TMDBMovieIDMissing) as exc:
        tmdb.search_tmdb(API_KEY, TITLE_QUERY, tmdb.queue.Queue())
    assert TEST_MOVIE_NOT_FOUND_EXC_ARGS in str(exc)


def test_missing_movie_error_logged(monkeypatch, caplog):
    caplog.set_level("ERROR")
    monkeypatch.setattr("tmdb.tmdbsimple.Search", DummyTMDBSearch)
    monkeypatch.setattr("tmdb.tmdbsimple.Movies", DummyTMDBMissingMovie)

    with pytest.raises(tmdb.exception.TMDBMovieIDMissing):
        tmdb.search_tmdb(API_KEY, TITLE_QUERY, tmdb.queue.Queue())
    assert caplog.messages[0] == TEST_MOVIE_NOT_FOUND_LOG_MSG


def test_unexpected_http_error_logged(monkeypatch, caplog):
    caplog.set_level("INFO")
    monkeypatch.setattr("tmdb.tmdbsimple.Search", DummyTMDBSearch)
    monkeypatch.setattr("tmdb.tmdbsimple.Movies", DummyUnexpectedHTTPError)

    with pytest.raises(tmdb.requests.exceptions.HTTPError):
        tmdb.search_tmdb(API_KEY, TITLE_QUERY, tmdb.queue.Queue())
    assert caplog.messages == ["HTTPError()"]
