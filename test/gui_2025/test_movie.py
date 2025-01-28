"""Test Module."""

#  Copyright© 2025. Stephen Rigden.
#  Last modified 1/28/25, 2:39 PM by stephen.
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
from pytest_check import check

import guiwidgets_2
from globalconstants import MovieBag, MovieInteger


class TestMovieGUI:

    def test_as_movie_bag(self, tk, monkeypatch):
        ef_title = "AMB Title"
        ef_year = "4242"
        mb_year = MovieInteger("4242")
        ef_director = "Sidney Stoneheart, Tina Tatum"
        mb_director = {"Sidney Stoneheart", "Tina Tatum"}
        ef_duration = "42"
        mb_duration = MovieInteger("42")
        ef_notes = "AMB Notes"
        ef_tags = {"Alpha", "Beta"}

        monkeypatch.setattr(guiwidgets_2.MovieGUI, "__post_init__", lambda *args: None)
        tmdb_search_callback = MagicMock(name="tmdb_search_callback")
        movie = guiwidgets_2.MovieGUI(
            tk,
            tmdb_search_callback,
            [],
        )
        # todo Why aren't we using Magic Mocks to fool the type checker?
        #  See test_commit
        movie.entry_fields = {
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

        movie_bag = movie.as_movie_bag()

        assert movie_bag == expected_movie_bag

    def test_as_movie_bag_with_bad_key(self, tk, monkeypatch, log_error):
        bad_key = "garbage"
        monkeypatch.setattr(guiwidgets_2.MovieGUI, "__post_init__", lambda *args: None)
        tmdb_search_callback = MagicMock(name="tmdb_search_callback")
        movie = guiwidgets_2.MovieGUI(tk, tmdb_search_callback, [])
        movie.entry_fields = {
            bad_key: DummyWidget("Has a current_value"),
        }
        exc_notes = f"{guiwidgets_2.UNEXPECTED_KEY}: {bad_key}"

        with check:
            with pytest.raises(KeyError, match=exc_notes):
                movie.as_movie_bag()
        check.equal(log_error, [((exc_notes,), {})])

    def test_as_movie_bag_with_blank_input_field(self, tk, monkeypatch, log_error):
        ef_title = "AMB Title"
        monkeypatch.setattr(guiwidgets_2.MovieGUI, "__post_init__", lambda *args: None)
        tmdb_search_callback = MagicMock(name="tmdb_search_callback")
        movie = guiwidgets_2.MovieGUI(
            tk,
            tmdb_search_callback,
            [],
        )
        # todo Why aren't we using Magic Mocks to fool the type checker?
        #  See test_commit
        movie.entry_fields = {
            guiwidgets_2.TITLE: DummyWidget(ef_title),
            guiwidgets_2.NOTES: DummyWidget(""),
        }
        expected_movie_bag = MovieBag(
            title=ef_title,
        )

        movie_bag = movie.as_movie_bag()

        assert movie_bag == expected_movie_bag


class TestAddMovieGUI:

    def test_commit(self, tk, monkeypatch):
        monkeypatch.setattr(
            guiwidgets_2.AddMovieGUI, "__post_init__", lambda *args: None
        )
        tmdb_search_callback = MagicMock(name="tmdb_search_callback")
        add_movie_callback = MagicMock(name="add_movie_callback")
        add_movie_gui = guiwidgets_2.AddMovieGUI(
            tk, tmdb_search_callback, [], add_movie_callback=add_movie_callback
        )
        as_movie_bag = MagicMock(name="as_movie_bag")
        monkeypatch.setattr(guiwidgets_2.MovieGUI, "as_movie_bag", as_movie_bag)
        widget = MagicMock(name="widget")
        monkeypatch.setitem(
            add_movie_gui.entry_fields,
            "mock widget",
            widget,
        )
        items = ["item 1", "item 2"]
        tmdb_treeview = MagicMock(name="tmdb_treeview")
        monkeypatch.setattr(guiwidgets_2.MovieGUI, "tmdb_treeview", tmdb_treeview)
        tmdb_treeview.get_children.return_value = items

        add_movie_gui.commit()

        with check:
            add_movie_callback.assert_called_once_with(as_movie_bag())
        with check:
            widget.clear_current_value.assert_called_once_with()
        with check:
            tmdb_treeview.delete.assert_called_once_with(*items)


@dataclass
class DummyWidget:
    """Provides a generic test dummy widget."""

    current_value: str


@pytest.fixture
def tk(monkeypatch):
    # noinspection GrazieInspection
    """Returns a mock of tkinter.

    Use case:
    This is the top level tkinter parent and can be used wherever a parent widget is needed.
    It prevents Tk/Tcl from being started.
    """
    mock = MagicMock(name="tk")
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
