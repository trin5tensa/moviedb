"""Test Module."""

#  Copyright© 2025. Stephen Rigden.
#  Last modified 4/1/25, 8:24 AM by stephen.
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

from unittest.mock import MagicMock

import pytest
from pytest_check import check

import guiwidgets
import guiwidgets_2
from globalconstants import MovieBag, MovieInteger


class TestSearchMovieGUI:
    def test_as_movie_bag(self, search_movie_gui):
        # Arrange
        return_fields = {
            "title": "Tam Title",
            "year": "",
            "director": "Tam Director, Two Director",
            "minutes": "",
            "notes": "Tam Notes",
            "year_min": "4240",
            "year_max": "4242",
            "minutes_min": "40",
            "minutes_max": "42",
        }
        search_movie_gui.selected_tags = ("Tam 1", "Tam 2", "Tam 3")
        expected = MovieBag(
            title=return_fields["title"],
            year=MovieInteger("4240-4242"),
            duration=MovieInteger("40-42"),
            directors={"Tam Director", "Two Director"},
            notes="Tam Notes",
            tags={"Tam 1", "Tam 2", "Tam 3"},
        )

        # Act
        movie_bag = search_movie_gui.as_movie_bag(return_fields)

        # Assert
        assert movie_bag == expected

    def test_as_movie_bag_raises_key_error(self, search_movie_gui, log_error):
        # Arrange
        bad_key = "garbage"
        return_fields = {bad_key: "garbage"}
        exc_notes = f"{guiwidgets_2.UNEXPECTED_KEY}: {bad_key}"

        # Act
        with check:
            with pytest.raises(KeyError, match=exc_notes):
                search_movie_gui.as_movie_bag(return_fields)

        # Assert
        check.equal(log_error, [((exc_notes,), {})])

    @pytest.mark.parametrize(
        # Arrange
        "value, expected",
        [
            (["4240"], {4240}),
            (["4240", "4242"], {4240, 4241, 4242}),
            (["4242", "4240"], {4240, 4241, 4242}),
        ],
    )
    def test__range_converter(self, search_movie_gui, value, expected):
        # Act
        result = search_movie_gui._range_converter(value)

        # Assert
        assert result._values == expected

    def test__range_converter_with_invalid_length(self, search_movie_gui):
        value = ["1", "2", "3"]
        with pytest.raises(ValueError):
            search_movie_gui._range_converter(value)


@pytest.fixture
def movie_gui(monkeypatch, tk):
    # noinspection GrazieInspection
    """Returns a mock of MovieGUI."""
    monkeypatch.setattr(guiwidgets_2.MovieGUI, "__post_init__", lambda *args: None)
    tmdb_search_callback = MagicMock(name="tmdb_search_callback")
    obj = guiwidgets_2.MovieGUI(
        tk,
        tmdb_search_callback,
        [],
    )
    return obj


@pytest.fixture
def add_movie_gui(monkeypatch, tk):
    # noinspection GrazieInspection
    """Returns a mock of AddMovieGUI."""
    monkeypatch.setattr(guiwidgets_2.AddMovieGUI, "__post_init__", lambda *args: None)
    tmdb_search_callback = MagicMock(name="tmdb_search_callback")
    add_movie_callback = MagicMock(name="add_movie_callback")
    obj = guiwidgets_2.AddMovieGUI(
        tk, tmdb_search_callback, [], add_movie_callback=add_movie_callback
    )
    return obj


@pytest.fixture
def edit_movie_gui(monkeypatch, tk):
    # noinspection GrazieInspection
    """Returns a mock of EditMovieGUI."""
    monkeypatch.setattr(
        guiwidgets_2.EditMovieGUI,
        "__post_init__",
        lambda *args: None,
    )
    tmdb_search_callback = MagicMock(name="tmdb_search_callback")
    edit_movie_callback = MagicMock(name="edit_movie_callback")
    delete_movie_callback = MagicMock(name="delete_movie_callback")
    obj = guiwidgets_2.EditMovieGUI(
        tk,
        tmdb_search_callback,
        [],
        edit_movie_callback=edit_movie_callback,
        delete_movie_callback=delete_movie_callback,
    )
    return obj


@pytest.fixture
def search_movie_gui(monkeypatch, tk):
    # noinspection GrazieInspection
    """Returns a mock of EditMovieGUI."""
    monkeypatch.setattr(
        guiwidgets.SearchMovieGUI,
        "__post_init__",
        lambda *args: None,
    )
    db_match_movies = MagicMock(name="db_match_movies")
    obj = guiwidgets.SearchMovieGUI(tk, callback=db_match_movies, all_tags=[])
    return obj


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
