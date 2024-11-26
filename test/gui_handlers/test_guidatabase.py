"""Menu handlers test module."""

#  Copyright© 2024. Stephen Rigden.
#  Last modified 11/26/24, 12:15 PM by stephen.
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

import config
from globalconstants import MovieTD, MovieInteger, MovieBag
from gui_handlers import (
    guidatabase,
    moviebagfacade,
)


# noinspection
def test_add_movie(monkeypatch, config_current, test_tags):
    mock_add_movie_gui = MagicMock(name="mock_add_movie_gui")
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
    movie_bag = moviebagfacade.convert_from_movie_td(gui_movie)

    guidatabase.add_movie_callback(gui_movie)

    add_movie.assert_called_once_with(movie_bag=movie_bag)


# noinspection PyPep8Naming
def test_add_movie_callback_with_MovieExists_exception(
    monkeypatch, config_current, messagebox
):
    table_add_movie = MagicMock(
        name="table_add_movie",
    )
    message = guidatabase.tables.MOVIE_EXISTS
    title_note = "title note"
    year_note = "year note"
    # noinspection PyTypeChecker
    table_add_movie.side_effect = guidatabase.tables.IntegrityError("", "", "")
    table_add_movie.side_effect.__notes__ = [message, title_note, year_note]
    monkeypatch.setattr(guidatabase.tables, "add_movie", table_add_movie)

    guid_add_movie = MagicMock(name="guid_add_movie")
    monkeypatch.setattr(guidatabase, "add_movie", guid_add_movie)
    gui_movie = MovieTD(title="Add movie test", year="4242")
    # noinspection PyUnresolvedReferences
    movie_bag = moviebagfacade.convert_from_movie_td(gui_movie)

    guidatabase.add_movie_callback(gui_movie)

    with check:
        messagebox.assert_called_once_with(
            guidatabase.config.current.tk_root,
            message=message,
            detail=f"{title_note}, {year_note}.",
        )
    with check:
        guid_add_movie.assert_called_once_with(movie_bag)


# noinspection PyPep8Naming,DuplicatedCode
def test_add_movie_callback_with_InvalidReleaseYear_exception(
    monkeypatch,
    config_current,
    add_movie_setup,
):
    table_add_movie = MagicMock(
        name="table_add_movie",
    )
    message = guidatabase.tables.INVALID_YEAR
    detail = "year note"
    # noinspection PyTypeChecker
    table_add_movie.side_effect = guidatabase.tables.InvalidReleaseYear("", "", "")
    table_add_movie.side_effect.__notes__ = [message, detail]

    monkeypatch.setattr(guidatabase.tables, "add_movie", table_add_movie)
    gui_movie, guid_add_movie, movie_bag, messagebox = add_movie_setup

    guidatabase.add_movie_callback(gui_movie)

    with check:
        messagebox.assert_called_once_with(
            guidatabase.config.current.tk_root, message=message, detail=detail
        )
    with check:
        guid_add_movie.assert_called_once_with(movie_bag)


# noinspection PyPep8Naming
def test_add_movie_callback_with_NoResultFound_exception(
    monkeypatch, config_current, add_movie_setup
):
    table_add_movie = MagicMock(
        name="table_add_movie",
    )
    table_add_movie.side_effect = guidatabase.tables.NoResultFound()
    message = "Oopsie add movie"
    detail = "42"
    table_add_movie.side_effect.__notes__ = [message, detail]

    # noinspection DuplicatedCode
    monkeypatch.setattr(guidatabase.tables, "add_movie", table_add_movie)
    gui_movie, guid_add_movie, movie_bag, messagebox = add_movie_setup

    guidatabase.add_movie_callback(gui_movie)

    with check:
        messagebox.assert_called_once_with(
            guidatabase.config.current.tk_root, message=message, detail=detail
        )
    with check:
        guid_add_movie.assert_called_once_with(movie_bag)


# noinspection
def test_search_for_movie(monkeypatch, config_current, test_tags):
    mock_search_movie_gui = MagicMock(name="mock_search_movie_gui")
    monkeypatch.setattr(guidatabase.guiwidgets, "SearchMovieGUI", mock_search_movie_gui)

    guidatabase.search_for_movie()

    mock_search_movie_gui.assert_called_once_with(
        guidatabase.config.current.tk_root,
        guidatabase.search_for_movie_callback,
        list(test_tags),
    )


# noinspection
def test_search_for_movie_callback(monkeypatch, config_current, messagebox):
    # Arrange
    match_movies = MagicMock(name="match_movies", return_value=[])
    monkeypatch.setattr(guidatabase.tables, "match_movies", match_movies)

    title = "title search"
    year = "4242"
    director_1 = "Michael Madison"
    director_2 = "Nancy Nichols"
    minutes = "142"
    notes = "A test note"
    criteria = config.FindMovieTypedDict(
        title=title,
        year=[year],
        director=director_1 + ", " + director_2,
        minutes=[minutes],
        notes=notes,
    )
    tags = ["test tag 1", "test tag 2"]

    match = guidatabase.MovieBag(
        title=title,
        year=MovieInteger(year),
        directors={director_1, director_2},
        duration=MovieInteger(minutes),
        notes=notes,
        movie_tags=set(tags),
    )

    monkeypatch.setattr(guidatabase, "search_for_movie", lambda: None)

    # Act
    guidatabase.search_for_movie_callback(criteria, tags)

    # Assert
    match_movies.assert_called_once_with(match=match)


# noinspection
def test_search_for_movie_callback_with_year_range(
    monkeypatch, config_current, messagebox
):
    # Arrange
    match_movies = MagicMock(name="match_movies", return_value=[])
    monkeypatch.setattr(guidatabase.tables, "match_movies", match_movies)

    title = "title search"
    year_1 = "4242"
    year_2 = "4247"
    criteria = config.FindMovieTypedDict(title=title, year=[year_1, year_2])
    tags = ["test tag 1", "test tag 2"]

    match = guidatabase.MovieBag(
        title=title,
        year=(MovieInteger(f"{year_1}-{year_2}")),
        movie_tags=set(tags),
    )

    monkeypatch.setattr(guidatabase, "search_for_movie", lambda: None)

    # Act
    guidatabase.search_for_movie_callback(criteria, tags)
    # Assert
    match_movies.assert_called_once_with(match=match)


def test_search_for_movie_callback_returning_0_movies(
    monkeypatch, config_current, messagebox
):
    title = "title search"
    year = "4242"
    criteria = config.FindMovieTypedDict(title=title, year=[year])
    tags = ["test tag 1"]

    match_movies = MagicMock(name="match_movies", return_value=[])
    monkeypatch.setattr(guidatabase.tables, "match_movies", match_movies)
    search_for_movie = MagicMock(name="search_for_movie")
    monkeypatch.setattr(guidatabase, "search_for_movie", search_for_movie)

    guidatabase.search_for_movie_callback(criteria, tags)

    with check:
        messagebox.assert_called_once_with(
            guidatabase.config.current.tk_root,
            message=guidatabase.MOVIE_NOT_FOUND,
        )
    with check:
        search_for_movie.assert_called_once_with()


# noinspection
def test_search_for_movie_callback_returning_1_movie(
    monkeypatch, config_current, test_tags
):
    year = "4242"
    movie_1 = guidatabase.MovieBag(title="Old Movie", year=MovieInteger(year))
    match_movies = MagicMock(name="match_movies", return_value=[movie_1])
    monkeypatch.setattr(guidatabase.tables, "match_movies", match_movies)

    title = "title search"
    criteria = config.FindMovieTypedDict(title=title, year=[year])

    edit_movie_gui = MagicMock(name="edit_movie_gui")
    monkeypatch.setattr(guidatabase.guiwidgets_2, "EditMovieGUI", edit_movie_gui)
    edit_movie_callback = MagicMock(name="edit_movie_callback")
    monkeypatch.setattr(guidatabase, "edit_movie_callback", edit_movie_callback)
    old_movie = guidatabase.convert_to_movie_update_def(movie_1)

    guidatabase.search_for_movie_callback(criteria, list(test_tags))

    with check:
        edit_movie_gui.assert_called_once_with(
            guidatabase.config.current.tk_root,
            guidatabase._tmdb_io_handler,
            list(test_tags),
            old_movie=old_movie,
            edit_movie_callback=guidatabase.edit_movie_callback(old_movie),
            delete_movie_callback=guidatabase.delete_movie_callback,
        )
    with check:
        edit_movie_callback.assert_called_with(old_movie)


def test_search_for_movie_callback_returning_2_movies(monkeypatch, config_current):
    movie_1 = guidatabase.MovieBag(title="Old Movie", year=MovieInteger(4242))
    movie_2 = guidatabase.MovieBag(title="Son of Old Movie", year=MovieInteger(4243))
    movies_found = [
        guidatabase.moviebagfacade.convert_to_movie_update_def(movie_1),
        guidatabase.moviebagfacade.convert_to_movie_update_def(movie_2),
    ]
    monkeypatch.setattr(
        guidatabase.tables,
        "match_movies",
        MagicMock(name="match_movies", return_value=movies_found),
    )
    criteria = config.FindMovieTypedDict()
    tags = []

    select_movie_gui = MagicMock(name="select_movie_gui")
    monkeypatch.setattr(guidatabase.guiwidgets, "SelectMovieGUI", select_movie_gui)
    monkeypatch.setattr(
        guidatabase, "_select_movie_callback", MagicMock(name="select_movie_callback")
    )

    guidatabase.search_for_movie_callback(criteria, tags)

    select_movie_gui.assert_called_once_with(
        guidatabase.config.current.tk_root,
        movies_found,
        guidatabase._select_movie_callback,
    )


# noinspection
def test_edit_movie_callback(monkeypatch, old_movie, new_movie):
    # Arrange
    old_movie_bag = moviebagfacade.convert_from_movie_key_typed_dict(old_movie)
    new_movie_bag = moviebagfacade.convert_from_movie_td(new_movie)
    edit_movie = MagicMock(name="edit_movie")
    monkeypatch.setattr(guidatabase.tables, "edit_movie", edit_movie)

    # Act
    guidatabase.edit_movie_callback(old_movie)(new_movie)

    # Assert
    edit_movie.assert_called_once_with(
        old_movie_bag=old_movie_bag, replacement_fields=new_movie_bag
    )


# noinspection PyPep8Naming
def test_edit_movie_callback_with_MovieNotFound_exception(
    monkeypatch, config_current, old_movie, messagebox
):
    # Arrange
    new_title = "New Title"
    new_year = "4343"
    new_director = "Janis Jackson, Keith Kryzlowski"
    new_duration = "142"
    new_notes = "New Notes"
    new_movie_tags = ["new", "movie", "tags"]
    new_movie = guidatabase.MovieTD(
        title=new_title,
        year=new_year,
        director=new_director,
        duration=new_duration,
        notes=new_notes,
        movie_tags=new_movie_tags,
    )

    edit_movie = MagicMock(
        name="edit_movie", side_effect=guidatabase.tables.MovieNotFound
    )
    monkeypatch.setattr(guidatabase.tables, "edit_movie", edit_movie)

    # Act
    guidatabase.edit_movie_callback(old_movie)(new_movie)

    # Assert
    messagebox.assert_called_once_with(
        guidatabase.config.current.tk_root,
        message=f"{guidatabase.MOVIE_NO_LONGER_PRESENT} {old_movie['title']}, "
        f"{old_movie['year']}",
    )


# noinspection PyPep8Naming
def test_edit_movie_callback_with_NoResultFound_exception(
    monkeypatch,
    config_current,
    old_movie,
    test_tags,
    messagebox,
    new_movie,
    edit_movie_gui_call,
):
    new_movie_bag = moviebagfacade.convert_from_movie_td(new_movie)
    edit_movie = MagicMock(name="edit_movie")
    edit_movie.side_effect = guidatabase.tables.NoResultFound
    message = "Oopsie edit movie"
    detail = "42"
    edit_movie.side_effect.__notes__ = [message, detail]
    monkeypatch.setattr(guidatabase.tables, "edit_movie", edit_movie)

    guidatabase.edit_movie_callback(old_movie)(new_movie)

    with check:
        messagebox.assert_called_once_with(
            guidatabase.config.current.tk_root,
            message=message,
            detail=detail,
        )
    common_edit_movie_gui_test(edit_movie_gui_call, test_tags, old_movie, new_movie_bag)


# noinspection PyPep8Naming,DuplicatedCode
def test_edit_movie_callback_with_MovieExists_exception(
    monkeypatch,
    config_current,
    old_movie,
    new_movie,
    messagebox,
    test_tags,
    edit_movie_gui_call,
):
    new_movie_bag = moviebagfacade.convert_from_movie_td(new_movie)
    edit_movie = MagicMock(
        name="edit_movie",
        side_effect=guidatabase.tables.MovieExists("statement", "params", Exception()),
    )
    monkeypatch.setattr(guidatabase.tables, "edit_movie", edit_movie)

    guidatabase.edit_movie_callback(old_movie)(new_movie)

    with check:
        messagebox.assert_called_once_with(
            guidatabase.config.current.tk_root,
            message=f"{guidatabase.TITLE_AND_YEAR_EXISTS_MSG}. {new_movie_bag['title']}, "
            f"{new_movie_bag['year']}",
        )
    common_edit_movie_gui_test(edit_movie_gui_call, test_tags, old_movie, new_movie_bag)


# noinspection DuplicatedCode,PyPep8Naming
def test_edit_movie_callback_with_InvalidReleaseYear_exception(
    monkeypatch,
    config_current,
    old_movie,
    new_movie,
    messagebox,
    test_tags,
    edit_movie_gui_call,
):
    new_movie_bag = moviebagfacade.convert_from_movie_td(new_movie)
    edit_movie = MagicMock(
        name="edit_movie",
        side_effect=guidatabase.tables.InvalidReleaseYear(
            "statement", "params", Exception()
        ),
    )
    monkeypatch.setattr(guidatabase.tables, "edit_movie", edit_movie)

    guidatabase.edit_movie_callback(old_movie)(new_movie)

    with check:
        messagebox.assert_called_once_with(
            guidatabase.config.current.tk_root,
            message=f"{guidatabase.INVALID_RELEASE_YEAR_MSG}. {new_movie_bag['title']}, "
            f"{new_movie_bag['year']}",
        )
    common_edit_movie_gui_test(edit_movie_gui_call, test_tags, old_movie, new_movie_bag)


def test_delete_movie_callback():
    # Arrange

    # Act
    pass

    # Assert

    # Cleanup
    # assert False


def common_edit_movie_gui_test(
    call, test_tags: set, old_movie, new_movie_bag: MovieBag
):
    """This function contains common code assertion code.

    The call to EditMovieGUI recurses into the function under test so the
    parameters to the call have to be individually tested.
    Args:
        call:
        test_tags:
        old_movie:
        new_movie_bag:
    """
    args = call[0][0]
    # noinspection PyProtectedMember
    check.equal(
        args,
        (
            guidatabase.config.current.tk_root,
            guidatabase._tmdb_io_handler,
            list(test_tags),
        ),
    )

    kwargs = call[0][1]
    check.equal(kwargs["old_movie"], old_movie)
    check.equal(kwargs["edited_movie_bag"], new_movie_bag)
    check.equal(
        kwargs["edit_movie_callback"].__qualname__[:19],
        "edit_movie_callback",
    )
    check.equal(
        kwargs["delete_movie_callback"],
        guidatabase.delete_movie_callback,
    )


@pytest.fixture(scope="function")
def config_current(monkeypatch):
    """This fixture patches a call to current.tk_root to suppress initiation of tk/tcl.

    Args:
        monkeypatch:
    """
    monkeypatch.setattr(guidatabase.config, "current", MagicMock(name="current"))


@pytest.fixture(scope="function")
def test_tags(monkeypatch):
    """This fixture mocks a call to guidatabase.tables.select_all_tags and
    returns a set of test tags.

    Args:
        monkeypatch:

    Returns:
        {"tag 1", "tag 2", "tag 3"}
    """
    test_tags = {"tag 1", "tag 2", "tag 3"}
    mock_select_tags = MagicMock(name="mock_select_tags", return_value=test_tags)
    monkeypatch.setattr(guidatabase.tables, "select_all_tags", mock_select_tags)
    return test_tags


@pytest.fixture(scope="function")
def add_movie_setup(monkeypatch):
    """This fixture provides common code associated with the add_movie_callback tests.

    Args:
        monkeypatch:

    Returns:
        A test movie dict.
        A mock of guidatabase.add_movie.
        A conversion of the test movie dict into MovieBag format.
        A mock of guidatabase.guiwidgets_2.gui_messagebox.
    """
    guid_add_movie = MagicMock(name="guid_add_movie")
    monkeypatch.setattr(guidatabase, "add_movie", guid_add_movie)
    messagebox = MagicMock(name="messagebox")
    monkeypatch.setattr(guidatabase.guiwidgets_2, "gui_messagebox", messagebox)
    gui_movie = MovieTD(title="Add movie test", year="4242")
    # noinspection PyUnresolvedReferences
    movie_bag = moviebagfacade.convert_from_movie_td(gui_movie)
    return (
        gui_movie,
        guid_add_movie,
        movie_bag,
        messagebox,
    )


@pytest.fixture(scope="function")
def old_movie():
    """This fixture provides an original movie for tests of movie
    editing functions.

    Returns:
        A MovieKeyTypedDict with dummy original values for title and year.
    """
    old_title = "Old Title"
    old_year = 4242
    return config.MovieKeyTypedDict(title=old_title, year=old_year)


@pytest.fixture(scope="function")
def new_movie():
    """This fixture provides a movie dict for tests of movie editing
    functions.

    Returns:
        A MovieTD
    """
    new_title = "New Title"
    new_year = "4343"
    new_director = "Janis Jackson, Keith Kryzlowski"
    new_duration = "142"
    new_notes = "New Notes"
    new_movie_tags = ["new", "movie", "tags"]
    return guidatabase.MovieTD(
        title=new_title,
        year=new_year,
        director=new_director,
        duration=new_duration,
        notes=new_notes,
        movie_tags=new_movie_tags,
    )


@pytest.fixture(scope="function")
def messagebox(monkeypatch):
    """This fixture patches guidatabase.guiwidgets_2.gui_messagebox

    Args:
        monkeypatch:

    Returns:
        A mock of guidatabase.guiwidgets_2.gui_messagebox
    """
    mock = MagicMock(name="messagebox")
    monkeypatch.setattr(guidatabase.guiwidgets_2, "gui_messagebox", mock)
    return mock


@pytest.fixture(scope="function")
def edit_movie_gui_call(monkeypatch):
    """This fixture mocks guidatabase.guiwidgets_2.EditMovieGUI

    Args:
        monkeypatch:

    Returns:
        A list of tuples for each call to EditMovieGUI. Each tuple contains
        the arguments for the call.
    """
    call = []
    monkeypatch.setattr(
        guidatabase.guiwidgets_2,
        "EditMovieGUI",
        lambda *args_, **kwargs_: call.append((args_, kwargs_)),
    )
    return call
