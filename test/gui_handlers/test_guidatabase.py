"""Menu handlers test module."""

#  Copyright© 2024. Stephen Rigden.
#  Last modified 10/5/24, 4:20 PM by stephen.
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


from globalconstants import MovieTD
from gui_handlers import (
    guidatabase,
    moviebagfacade,
)


def test_add_movie(monkeypatch):
    mock_name = test_add_movie.__name__
    monkeypatch.setattr(guidatabase.config, "current", MagicMock(name=mock_name))
    test_tags = {"tag 1", "tag 2", "tag 3"}
    mock_select_tags = MagicMock(name=mock_name, return_value=test_tags)
    monkeypatch.setattr(guidatabase.tables, "select_all_tags", mock_select_tags)
    mock_add_movie_gui = MagicMock(name=mock_name)
    monkeypatch.setattr(guidatabase.guiwidgets_2, "AddMovieGUI", mock_add_movie_gui)
    movie_bag = guidatabase.MovieBag()

    guidatabase.add_movie(movie_bag)

    mock_add_movie_gui.assert_called_once_with(
        guidatabase.config.current.tk_root,
        guidatabase._tmdb_io_handler,
        list(test_tags),
        movie_bag=movie_bag,
        add_movie_callback=guidatabase.add_movie_callback,
    )


def test_add_movie_callback(monkeypatch):
    add_movie = MagicMock(name="add_movie")
    monkeypatch.setattr(guidatabase.tables, "add_movie", add_movie)
    gui_movie = MovieTD(title="Add movie test", year="4242")
    # noinspection PyUnresolvedReferences
    movie_bag = moviebagfacade.MovieBagFacade.from_movie_td(gui_movie)

    guidatabase.add_movie_callback(gui_movie)

    add_movie.assert_called_once_with(movie_bag=movie_bag)


# noinspection PyPep8Naming
def test_add_movie_callback_with_MovieExists_exception(monkeypatch):
    # noinspection PyTypeChecker
    table_add_movie = MagicMock(
        name="table_add_movie",
        side_effect=guidatabase.tables.MovieExists("", "", Exception),
    )
    monkeypatch.setattr(guidatabase.tables, "add_movie", table_add_movie)
    guid_add_movie = MagicMock(name="guid_add_movie")
    monkeypatch.setattr(guidatabase, "add_movie", guid_add_movie)
    gui_movie = MovieTD(title="Add movie test", year="4242")
    # noinspection PyUnresolvedReferences
    movie_bag = moviebagfacade.MovieBagFacade.from_movie_td(gui_movie)

    guidatabase.add_movie_callback(gui_movie)

    guid_add_movie.assert_called_once_with(movie_bag)


# noinspection PyPep8Naming
def test_add_movie_callback_with_InvalidReleaseYear_exception(monkeypatch):
    # noinspection PyTypeChecker
    table_add_movie = MagicMock(
        name="table_add_movie",
        side_effect=guidatabase.tables.InvalidReleaseYear("", "", Exception),
    )
    monkeypatch.setattr(guidatabase.tables, "add_movie", table_add_movie)
    guid_add_movie = MagicMock(name="guid_add_movie")
    monkeypatch.setattr(guidatabase, "add_movie", guid_add_movie)
    gui_movie = MovieTD(title="Add movie test", year="4242")
    # noinspection PyUnresolvedReferences
    movie_bag = moviebagfacade.MovieBagFacade.from_movie_td(gui_movie)

    guidatabase.add_movie_callback(gui_movie)

    guid_add_movie.assert_called_once_with(movie_bag)


# noinspection PyPep8Naming
def test_add_movie_callback_with_TagNotFound_exception(monkeypatch):
    table_add_movie = MagicMock(
        name="table_add_movie",
        side_effect=guidatabase.tables.TagNotFound,
    )
    monkeypatch.setattr(guidatabase.tables, "add_movie", table_add_movie)
    guid_add_movie = MagicMock(name="guid_add_movie")
    monkeypatch.setattr(guidatabase, "add_movie", guid_add_movie)
    gui_movie = MovieTD(title="Add movie test", year="4242")
    # noinspection PyUnresolvedReferences
    movie_bag = moviebagfacade.MovieBagFacade.from_movie_td(gui_movie)

    guidatabase.add_movie_callback(gui_movie)

    guid_add_movie.assert_called_once_with(movie_bag)


def test_edit_movie(monkeypatch):
    mock_name = test_add_movie.__name__
    monkeypatch.setattr(guidatabase.config, "current", MagicMock(name=mock_name))
    test_tags = {"tag 1", "tag 2", "tag 3"}
    mock_select_tags = MagicMock(name=mock_name, return_value=test_tags)
    monkeypatch.setattr(guidatabase.tables, "select_all_tags", mock_select_tags)
    mock_search_movie_gui = MagicMock(name=mock_name)
    monkeypatch.setattr(guidatabase.guiwidgets, "SearchMovieGUI", mock_search_movie_gui)

    guidatabase.edit_movie()

    mock_search_movie_gui.assert_called_once_with(
        guidatabase.config.current.tk_root,
        guidatabase._search_movie_callback,
        list(test_tags),
    )
