"""Menu handlers test module."""

#  Copyright© 2024. Stephen Rigden.
#  Last modified 11/30/24, 12:58 PM by stephen.
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


# noinspection PyPep8Naming,DuplicatedCode
def test_add_movie_callback_handles_NoResultFound_for_missing_tag(
    monkeypatch,
    config_current,
):
    """Attempts to add a movie with a tag that is not in the database"""
    movie_td = guidatabase.MovieTD(
        title="title",
        year="4242",
    )
    movie_bag = moviebagfacade.convert_from_movie_td(movie_td)
    db_add_movie = MagicMock(name="mock_add_movie")
    db_add_movie.side_effect = guidatabase.tables.NoResultFound()
    db_add_movie.side_effect.__notes__ = [
        guidatabase.tables.TAG_NOT_FOUND,
        "Note 2",
    ]
    monkeypatch.setattr(guidatabase.tables, "add_movie", db_add_movie)
    handler_add_movie = MagicMock(name="handler_add_movie")
    monkeypatch.setattr(guidatabase, "add_movie", handler_add_movie)
    exc_messagebox = MagicMock(name="exc_messagebox")
    monkeypatch.setattr(guidatabase, "exc_messagebox", exc_messagebox)

    guidatabase.add_movie_callback(movie_td)

    with check:
        exc_messagebox.assert_called_once_with(db_add_movie.side_effect)

    with check:
        handler_add_movie.assert_called_once_with(movie_bag)


# noinspection DuplicatedCode,PyPep8Naming
def test_add_movie_callback_handles_IntegrityError_for_existing_movie(monkeypatch):
    """Attempts to add a movie with a key that is already present in the database."""
    movie_td = guidatabase.MovieTD(
        title="title",
        year="4242",
    )
    movie_bag = moviebagfacade.convert_from_movie_td(movie_td)
    db_add_movie = MagicMock(name="mock_add_movie")
    db_add_movie.side_effect = guidatabase.tables.IntegrityError("", "", Exception())
    db_add_movie.side_effect.__notes__ = [
        guidatabase.tables.MOVIE_EXISTS,
        "Note 2",
        "Note 3",
    ]
    monkeypatch.setattr(guidatabase.tables, "add_movie", db_add_movie)
    exc_messagebox = MagicMock(name="exc_messagebox")
    monkeypatch.setattr(guidatabase, "exc_messagebox", exc_messagebox)
    handler_add_movie = MagicMock(name="handler_add_movie")
    monkeypatch.setattr(guidatabase, "add_movie", handler_add_movie)

    guidatabase.add_movie_callback(movie_td)

    with check:
        exc_messagebox.assert_called_once_with(db_add_movie.side_effect)

    with check:
        handler_add_movie.assert_called_once_with(movie_bag)


# noinspection DuplicatedCode,PyPep8Naming
def test_add_movie_callback_handles_IntegrityError_for_invalid_year(monkeypatch):
    """Attempts to add a movie with a key that is already present in the database."""
    movie_td = guidatabase.MovieTD(
        title="title",
        year="4242",
    )
    movie_bag = moviebagfacade.convert_from_movie_td(movie_td)
    db_add_movie = MagicMock(name="mock_add_movie")
    db_add_movie.side_effect = guidatabase.tables.IntegrityError("", "", Exception())
    db_add_movie.side_effect.__notes__ = [
        guidatabase.tables.INVALID_YEAR,
        "Note 2",
    ]
    monkeypatch.setattr(guidatabase.tables, "add_movie", db_add_movie)
    exc_messagebox = MagicMock(name="exc_messagebox")
    monkeypatch.setattr(guidatabase, "exc_messagebox", exc_messagebox)
    handler_add_movie = MagicMock(name="handler_add_movie")
    monkeypatch.setattr(guidatabase, "add_movie", handler_add_movie)

    guidatabase.add_movie_callback(movie_td)

    with check:
        exc_messagebox.assert_called_once_with(db_add_movie.side_effect)

    with check:
        handler_add_movie.assert_called_once_with(movie_bag)


def test_search_for_movie(monkeypatch, config_current, test_tags):
    mock_search_movie_gui = MagicMock(name="mock_search_movie_gui")
    monkeypatch.setattr(guidatabase.guiwidgets, "SearchMovieGUI", mock_search_movie_gui)

    guidatabase.search_for_movie()

    mock_search_movie_gui.assert_called_once_with(
        guidatabase.config.current.tk_root,
        guidatabase.search_for_movie_callback,
        list(test_tags),
    )


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
            message=guidatabase.tables.MOVIE_NOT_FOUND,
        )
    with check:
        search_for_movie.assert_called_once_with()


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


def test_edit_movie_callback(monkeypatch, old_movie, new_movie):
    # Arrange
    old_movie_bag = moviebagfacade.convert_from_movie_key_typed_dict(old_movie)
    new_movie_bag = moviebagfacade.convert_from_movie_td(new_movie)
    db_edit_movie = MagicMock(name="db_edit_movie")
    monkeypatch.setattr(guidatabase.tables, "edit_movie", db_edit_movie)

    # Act
    guidatabase.edit_movie_callback(old_movie)(new_movie)

    # Assert
    db_edit_movie.assert_called_once_with(
        old_movie_bag=old_movie_bag, replacement_fields=new_movie_bag
    )


# noinspection PyPep8Naming
def test_edit_movie_callback_handles_NoResultFound_for_missing_tag(monkeypatch):
    exception = guidatabase.tables.NoResultFound()
    exc_context = guidatabase.tables.TAG_NOT_FOUND
    edit_movie_exception_handler(exception, exc_context, monkeypatch)


# noinspection PyPep8Naming
def test_edit_movie_callback_handles_NoResultFound_for_missing_movie(monkeypatch):
    exception = guidatabase.tables.NoResultFound()
    exc_context = guidatabase.tables.MOVIE_NOT_FOUND
    edit_movie_exception_handler(exception, exc_context, monkeypatch)


# noinspection PyPep8Naming
def test_edit_movie_callback_handles_IntegrityError_for_duplicate_movie(monkeypatch):
    exception = guidatabase.tables.IntegrityError("", "", Exception())
    exc_context = guidatabase.tables.MOVIE_EXISTS
    edit_movie_exception_handler(exception, exc_context, monkeypatch)


# noinspection PyPep8Naming
def test_edit_movie_callback_handles_IntegrityError_for_invalid_year(monkeypatch):
    exception = guidatabase.tables.IntegrityError("", "", Exception())
    exc_context = guidatabase.tables.INVALID_YEAR
    edit_movie_exception_handler(exception, exc_context, monkeypatch)


def edit_movie_exception_handler(
    exception: Exception,
    exc_context: str,
    monkeypatch,
):
    """This exception helper provides common code for all the edit movie
    callback exceptions.

    Args:
        exception: The original exception raised by SQLAlchemy.
        exc_context: The contextual exception added by tables.py.
        monkeypatch:
    """
    old_movie = config.MovieKeyTypedDict(title="Old Movie Title", year=4200)
    new_title = "New Movie Title"
    new_year = 4201
    new_movie_bag = MovieBag(title=new_title, year=MovieInteger(new_year))
    # noinspection PyTypeChecker
    new_movie = MovieTD(title=new_title, year=new_year)

    # Patch call to database
    db_edit_movie = MagicMock(name="db_edit_movie")
    monkeypatch.setattr(guidatabase.tables, "edit_movie", db_edit_movie)
    db_edit_movie.side_effect = exception
    db_edit_movie.side_effect.__notes__ = [exc_context, "Note 2", "Note 3"]

    # Patch call to guidatabase._edit_movie
    gui_edit_movie = MagicMock(name="gui_edit_movie")
    monkeypatch.setattr(guidatabase, "_edit_movie", gui_edit_movie)

    # Patch call to messagebox
    exc_messagebox = MagicMock(name="exc_messagebox")
    monkeypatch.setattr(guidatabase, "exc_messagebox", exc_messagebox)

    guidatabase.edit_movie_callback(old_movie)(new_movie)

    with check:
        exc_messagebox.assert_called_once_with(db_edit_movie.side_effect)
    with check:
        gui_edit_movie.assert_called_once_with(old_movie, new_movie_bag)


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


def test_exc_messagebox_with_one_note(messagebox, config_current):
    item_1 = "item_1"

    try:
        raise Exception
    except Exception as exc:
        exc.add_note(item_1)
        guidatabase.exc_messagebox(exc)

    messagebox.assert_called_once_with(
        guidatabase.config.current.tk_root,
        message=item_1,
    )


def test_exc_messagebox_with_multiple_notes(messagebox, config_current):
    item_1 = "item_1"
    item_2 = "item_2"
    item_3 = "item_3"

    try:
        raise Exception
    except Exception as exc:
        exc.add_note(item_1)
        exc.add_note(item_2)
        exc.add_note(item_3)
        guidatabase.exc_messagebox(exc)

    messagebox.assert_called_once_with(
        guidatabase.config.current.tk_root,
        message=item_1,
        detail=f"{item_2}, {item_3}.",
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
