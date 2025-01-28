"""Test Module."""

#  Copyright© 2025. Stephen Rigden.
#  Last modified 1/28/25, 8:35 AM by stephen.
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

from dataclasses import dataclass
from unittest.mock import MagicMock

import pytest

import guiwidgets_2
from globalconstants import MovieBag, MovieInteger


# todo This module wil become THE movie test module. Get it organized.


# noinspection PyTypeChecker
def test_as_movie_bag(mock_tk, monkeypatch):
    ef_title = "AMB Title"
    ef_year = "4242"
    mb_year = MovieInteger("4242")
    ef_director = "Sidney Stoneheart, Tina Tatum"
    mb_director = {"Sidney Stoneheart", "Tina Tatum"}
    ef_duration = "42"
    mb_duration = MovieInteger("42")
    ef_notes = "AMB Notes"
    ef_tags = {"Alpha", "Beta"}

    monkeypatch.setattr(guiwidgets_2.AddMovieGUI, "__post_init__", lambda *args: None)

    add_movie = guiwidgets_2.AddMovieGUI(
        mock_tk,
        lambda: None,
        [],
    )
    add_movie.entry_fields = {
        guiwidgets_2.TITLE: DummyWidget(ef_title),
        guiwidgets_2.YEAR: DummyWidget(ef_year),
        guiwidgets_2.DIRECTOR: DummyWidget(ef_director),
        guiwidgets_2.DURATION: DummyWidget(ef_duration),
        guiwidgets_2.NOTES: DummyWidget(ef_notes),
        guiwidgets_2.MOVIE_TAGS: DummyWidget(ef_tags),
    }
    expected_movie_bag = MovieBag(
        title=ef_title,
        year=mb_year,
        duration=mb_duration,
        directors=mb_director,
        notes=ef_notes,
        tags=ef_tags,
    )

    movie_bag = add_movie.as_movie_bag()

    assert movie_bag == expected_movie_bag


# noinspection PyTypeChecker
def test_as_movie_bag_with_bad_key(mock_tk, monkeypatch, log_error):
    bad_key = "garbage"
    monkeypatch.setattr(guiwidgets_2.AddMovieGUI, "__post_init__", lambda *args: None)
    add_movie = guiwidgets_2.AddMovieGUI(mock_tk, lambda: None, [])
    add_movie.entry_fields = {
        bad_key: DummyWidget("Has a current_value"),
    }
    exc_notes = f"{guiwidgets_2.UNEXPECTED_KEY}: {bad_key}"

    with pytest.raises(KeyError, match=exc_notes):
        add_movie.as_movie_bag()
    assert log_error == [((exc_notes,), {})]


# noinspection PyTypeChecker
def test_as_movie_bag_with_blank_input_field(mock_tk, monkeypatch, log_error):
    ef_title = "AMB Title"
    monkeypatch.setattr(guiwidgets_2.AddMovieGUI, "__post_init__", lambda *args: None)
    add_movie = guiwidgets_2.AddMovieGUI(
        mock_tk,
        lambda: None,
        [],
    )
    add_movie.entry_fields = {
        guiwidgets_2.TITLE: DummyWidget(ef_title),
        guiwidgets_2.NOTES: DummyWidget(""),
    }
    expected_movie_bag = MovieBag(
        title=ef_title,
    )

    movie_bag = add_movie.as_movie_bag()

    assert movie_bag == expected_movie_bag


@dataclass
class DummyWidget:
    """Provides a generic test dummy."""

    current_value: str


@pytest.fixture
def mock_tk(monkeypatch):
    # noinspection GrazieInspection
    """Returns a mock of tkinter.

    Use case:
    This is the top level tkinter parent and can be used wherever a parent widget is needed.
    It prevents Tk/Tcl from being started.
    """
    mock = MagicMock(name="mock_tk")
    monkeypatch.setattr(guiwidgets_2, "tk", mock)
    return mock


@pytest.fixture
def log_error(monkeypatch):
    """Logs arguments of calls to logging.error."""
    calls = []
    monkeypatch.setattr(
        guiwidgets_2.logging,
        "error",
        lambda *args, **kwargs: calls.append((args, kwargs)),
    )
    return calls
