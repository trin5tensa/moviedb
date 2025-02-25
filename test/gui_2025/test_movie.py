"""Test Module."""

#  Copyright© 2025. Stephen Rigden.
#  Last modified 1/30/25, 1:12 PM by stephen.
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

import guiwidgets_2
from globalconstants import MovieBag, MovieInteger


class TestMovieGUI:

    def test_as_movie_bag(self, movie_gui, monkeypatch):
        # Arrange
        ef_title = "AMB Title"
        ef_year = "4242"
        ef_director = "Sidney Stoneheart, Tina Tatum"
        ef_duration = "42"
        ef_notes = "AMB Notes"
        ef_tags = {"Alpha", "Beta"}
        for k, v in [
            ("title", ef_title),
            ("year", ef_year),
            ("director", ef_director),
            ("minutes", ef_duration),
            ("notes", ef_notes),
            ("tags", ef_tags),
        ]:
            widget = MagicMock(name=k)
            widget.current_value = v
            monkeypatch.setitem(movie_gui.entry_fields, k, widget)

        mb_year = MovieInteger("4242")
        mb_director = {"Sidney Stoneheart", "Tina Tatum"}
        mb_duration = MovieInteger("42")
        expected_movie_bag = MovieBag(
            title=ef_title,
            year=mb_year,
            duration=mb_duration,
            directors=mb_director,
            notes=ef_notes,
            tags=ef_tags,
        )

        # Act
        movie_bag = movie_gui.as_movie_bag()

        assert movie_bag == expected_movie_bag

    def test_as_movie_bag_with_bad_key(self, movie_gui, monkeypatch, log_error):
        bad_key = "garbage"
        monkeypatch.setattr(guiwidgets_2.MovieGUI, "__post_init__", lambda *args: None)
        widget = MagicMock(name=bad_key)
        widget.current_value = "Has a current_value"
        monkeypatch.setitem(movie_gui.entry_fields, bad_key, widget)
        exc_notes = f"{guiwidgets_2.UNEXPECTED_KEY}: {bad_key}"

        with check:
            with pytest.raises(KeyError, match=exc_notes):
                movie_gui.as_movie_bag()
        check.equal(log_error, [((exc_notes,), {})])

    def test_as_movie_bag_with_blank_input_field(
        self, movie_gui, monkeypatch, log_error
    ):
        ef_title = "AMB Title"
        for k, v in [("title", ef_title), ("notes", "")]:
            widget = MagicMock(name=k)
            widget.current_value = v
            monkeypatch.setitem(movie_gui.entry_fields, k, widget)

        expected_movie_bag = MovieBag(
            title=ef_title,
        )

        movie_bag = movie_gui.as_movie_bag()

        assert movie_bag == expected_movie_bag


class TestAddMovieGUI:

    def test_commit(self, add_movie_gui, monkeypatch):
        # Arrange
        as_movie_bag = MagicMock(name="as_movie_bag")
        monkeypatch.setattr(guiwidgets_2.MovieGUI, "as_movie_bag", as_movie_bag)
        widget = MagicMock(name="widget")
        monkeypatch.setitem(add_movie_gui.entry_fields, "mock widget", widget)
        items = ["item 1", "item 2"]
        tmdb_treeview = MagicMock(name="tmdb_treeview")
        monkeypatch.setattr(guiwidgets_2.MovieGUI, "tmdb_treeview", tmdb_treeview)
        tmdb_treeview.get_children.return_value = items

        # Act
        add_movie_gui.commit()

        with check:
            # noinspection PyUnresolvedReferences
            add_movie_gui.add_movie_callback.assert_called_once_with(as_movie_bag())
        with check:
            widget.clear_current_value.assert_called_once_with()
        with check:
            tmdb_treeview.delete.assert_called_once_with(*items)


class TestEditMovieGUI:
    def test_commit(self, edit_movie_gui, monkeypatch):
        # Arrange
        as_movie_bag = MagicMock(name="as_movie_bag")
        monkeypatch.setattr(guiwidgets_2.MovieGUI, "as_movie_bag", as_movie_bag)
        destroy = MagicMock(name="destroy")
        monkeypatch.setattr(guiwidgets_2.MovieGUI, "destroy", destroy)

        # Act
        edit_movie_gui.commit()

        with check:
            # noinspection PyUnresolvedReferences
            edit_movie_gui.edit_movie_callback.assert_called_once_with(as_movie_bag())
        with check:
            destroy.assert_called_once_with()


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
    monkeypatch.setattr(guiwidgets_2.EditMovieGUI, "__post_init__", lambda *args: None)
    tmdb_search_callback = MagicMock(name="tmdb_search_callback")
    edit_movie_callback = MagicMock(name="edit_movie_callback")
    obj = guiwidgets_2.EditMovieGUI(
        tk, tmdb_search_callback, [], edit_movie_callback=edit_movie_callback
    )
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
