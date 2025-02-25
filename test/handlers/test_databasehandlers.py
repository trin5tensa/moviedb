"""Menu handlers test module."""

#  Copyright© 2025. Stephen Rigden.
#  Last modified 1/30/25, 1:41 PM by stephen.
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

from unittest.mock import MagicMock, call

import pytest
from pytest_check import check

import config
from config import MovieKeyTypedDict

from globalconstants import MovieInteger, MovieBag
import handlers


# noinspection
def test_gui_add_movie(monkeypatch, config_current, test_tags):
    mock_add_movie_gui = MagicMock(name="mock_add_movie_gui")
    monkeypatch.setattr(
        handlers.database.guiwidgets_2,
        "AddMovieGUI",
        mock_add_movie_gui,
        # handlers.database.guiwidgets_2, "AddMovieGUI", mock_add_movie_gui
    )
    movie_bag = handlers.database.MovieBag()

    handlers.database.gui_add_movie(prepopulate=movie_bag)

    mock_add_movie_gui.assert_called_once_with(
        handlers.database.config.current.tk_root,
        handlers.sundries._tmdb_io_handler,
        list(test_tags),
        prepopulate=movie_bag,
        add_movie_callback=handlers.database.db_add_movie,
    )


def test_db_add_movie(monkeypatch):
    add_movie = MagicMock(name="add_movie")
    monkeypatch.setattr(handlers.database.tables, "add_movie", add_movie)
    movie_bag = MovieBag(title="Add movie test", year=MovieInteger("4242"))

    handlers.database.db_add_movie(movie_bag)

    add_movie.assert_called_once_with(movie_bag=movie_bag)


# noinspection PyPep8Naming,DuplicatedCode
def test_db_add_movie_handles_NoResultFound_for_missing_tag(
    monkeypatch,
    config_current,
):
    """Attempts to add a movie with a tag that is not in the database"""
    movie_bag = MovieBag(title="Add movie test", year=MovieInteger("4242"))

    db_add_movie = MagicMock(name="mock_add_movie")
    db_add_movie.side_effect = handlers.database.tables.NoResultFound()
    db_add_movie.side_effect.__notes__ = [
        handlers.database.tables.TAG_NOT_FOUND,
        "Note 2",
    ]
    monkeypatch.setattr(handlers.database.tables, "add_movie", db_add_movie)
    gui_add_movie = MagicMock(name="gui_add_movie")
    monkeypatch.setattr(handlers.database, "gui_add_movie", gui_add_movie)
    exc_messagebox = MagicMock(name="exc_messagebox")
    monkeypatch.setattr(handlers.database, "_exc_messagebox", exc_messagebox)

    handlers.database.db_add_movie(movie_bag)

    with check:
        exc_messagebox.assert_called_once_with(db_add_movie.side_effect)
    with check:
        gui_add_movie.assert_called_once_with(prepopulate=movie_bag)


# noinspection DuplicatedCode,PyPep8Naming
def test_db_add_movie_handles_IntegrityError_for_existing_movie(monkeypatch):
    """Attempts to add a movie with a key that is already present in the database."""
    movie_bag = MovieBag(title="Add movie test", year=MovieInteger("4242"))
    db_add_movie = MagicMock(name="mock_add_movie")
    db_add_movie.side_effect = handlers.database.tables.IntegrityError(
        "", "", Exception()
    )
    db_add_movie.side_effect.__notes__ = [
        handlers.database.tables.MOVIE_EXISTS,
        "Note 2",
        "Note 3",
    ]
    monkeypatch.setattr(handlers.database.tables, "add_movie", db_add_movie)
    exc_messagebox = MagicMock(name="exc_messagebox")
    monkeypatch.setattr(handlers.database, "_exc_messagebox", exc_messagebox)
    gui_add_movie = MagicMock(name="gui_add_movie")
    monkeypatch.setattr(handlers.database, "gui_add_movie", gui_add_movie)

    handlers.database.db_add_movie(movie_bag)

    with check:
        exc_messagebox.assert_called_once_with(db_add_movie.side_effect)
    with check:
        gui_add_movie.assert_called_once_with(prepopulate=movie_bag)


# noinspection DuplicatedCode,PyPep8Naming
def test_db_add_movie_handles_IntegrityError_for_invalid_year(monkeypatch):
    """Attempts to add a movie with a key that is already present in the database."""
    movie_bag = MovieBag(title="Add movie test", year=MovieInteger("4242"))
    db_add_movie = MagicMock(name="mock_add_movie")
    db_add_movie.side_effect = handlers.database.tables.IntegrityError(
        "", "", Exception()
    )
    db_add_movie.side_effect.__notes__ = [
        handlers.database.tables.INVALID_YEAR,
        "Note 2",
    ]
    monkeypatch.setattr(handlers.database.tables, "add_movie", db_add_movie)
    exc_messagebox = MagicMock(name="exc_messagebox")
    monkeypatch.setattr(handlers.database, "_exc_messagebox", exc_messagebox)
    gui_add_movie = MagicMock(name="gui_add_movie")
    monkeypatch.setattr(handlers.database, "gui_add_movie", gui_add_movie)

    handlers.database.db_add_movie(movie_bag)

    with check:
        exc_messagebox.assert_called_once_with(db_add_movie.side_effect)
    with check:
        gui_add_movie.assert_called_once_with(prepopulate=movie_bag)


def test_gui_search_movie(monkeypatch, config_current, test_tags):
    mock_search_movie_gui = MagicMock(name="mock_search_movie_gui")
    monkeypatch.setattr(
        handlers.database.guiwidgets, "SearchMovieGUI", mock_search_movie_gui
    )

    handlers.database.gui_search_movie()

    mock_search_movie_gui.assert_called_once_with(
        handlers.database.config.current.tk_root,
        handlers.database.db_match_movies,
        list(test_tags),
    )


def test_gui_select_movie(monkeypatch, config_current):
    select_movie_gui = MagicMock(name="select_movie_gui")
    monkeypatch.setattr(
        handlers.database.guiwidgets, "SelectMovieGUI", select_movie_gui
    )
    movies = [config.MovieUpdateDef(title="", year=0)]

    handlers.database.gui_select_movie(movies=movies)

    select_movie_gui.assert_called_once_with(
        config.current.tk_root, movies, handlers.database.db_select_movies
    )


def test_db_match_movies(monkeypatch, config_current, messagebox):
    # Arrange
    match_movies = MagicMock(name="match_movies", return_value=[])
    monkeypatch.setattr(handlers.database.tables, "match_movies", match_movies)

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

    match = handlers.database.MovieBag(
        title=title,
        year=MovieInteger(year),
        directors={director_1, director_2},
        duration=MovieInteger(minutes),
        notes=notes,
        tags=set(tags),
    )

    monkeypatch.setattr(handlers.database, "gui_search_movie", lambda: None)

    # Act
    handlers.database.db_match_movies(criteria, tags)

    # Assert
    match_movies.assert_called_once_with(match=match)


def test_db_match_movies_with_year_range(monkeypatch, config_current, messagebox):
    match_movies = MagicMock(name="match_movies", return_value=[])
    monkeypatch.setattr(handlers.database.tables, "match_movies", match_movies)
    title = "title search"
    year_1 = "4242"
    year_2 = "4247"
    criteria = config.FindMovieTypedDict(title=title, year=[year_1, year_2])
    tags = ["test tag 1", "test tag 2"]
    match = handlers.database.MovieBag(
        title=title,
        year=(MovieInteger(f"{year_1}-{year_2}")),
        tags=set(tags),
    )
    monkeypatch.setattr(handlers.database, "gui_search_movie", lambda: None)

    handlers.database.db_match_movies(criteria, tags)

    match_movies.assert_called_once_with(match=match)


def test_db_match_movies_returning_0_movies(monkeypatch, config_current, messagebox):
    title = "title search"
    year = "4242"
    criteria = config.FindMovieTypedDict(title=title, year=[year])
    tags = ["test tag 1"]
    match_movies = MagicMock(name="match_movies", return_value=[])
    monkeypatch.setattr(handlers.database.tables, "match_movies", match_movies)
    gui_search_movie = MagicMock(name="gui_search_movie")
    monkeypatch.setattr(handlers.database, "gui_search_movie", gui_search_movie)

    handlers.database.db_match_movies(criteria, tags)

    with check:
        messagebox.assert_called_once_with(
            handlers.database.config.current.tk_root,
            message=handlers.database.tables.MOVIE_NOT_FOUND,
        )
    with check:
        gui_search_movie.assert_called_once_with()


def test_db_match_movies_returning_1_movie(monkeypatch, config_current, test_tags):
    year = "4242"
    title = "title search"
    movie_1 = handlers.database.MovieBag(title=title, year=MovieInteger(year))
    match_movies = MagicMock(name="match_movies")
    match_movies.return_value = [movie_1]
    monkeypatch.setattr(handlers.database.tables, "match_movies", match_movies)
    gui_edit_movie = MagicMock(name="gui_edit_movie")
    monkeypatch.setattr(handlers.database, "gui_edit_movie", gui_edit_movie)
    criteria = config.FindMovieTypedDict(title=title, year=[year])
    old_movie = handlers.moviebagfacade.convert_to_movie_update_def(movie_1)

    handlers.database.db_match_movies(criteria, list(test_tags))

    gui_edit_movie.assert_called_once_with(old_movie, prepopulate=movie_1)


def test_db_match_movies_returning_2_movies(monkeypatch, config_current):
    movie_1 = handlers.database.MovieBag(
        title="Old Movie",
        year=MovieInteger(4242),
    )
    movie_2 = handlers.database.MovieBag(
        title="Son of Old Movie", year=MovieInteger(4243)
    )
    movies_found = [
        handlers.moviebagfacade.convert_to_movie_update_def(movie_1),
        handlers.moviebagfacade.convert_to_movie_update_def(movie_2),
    ]
    monkeypatch.setattr(
        handlers.database.tables,
        "match_movies",
        MagicMock(name="match_movies", return_value=movies_found),
    )
    criteria = config.FindMovieTypedDict()
    tags = []
    gui_select_movie = MagicMock(name="gui_select_movie")
    monkeypatch.setattr(handlers.database, "gui_select_movie", gui_select_movie)

    handlers.database.db_match_movies(criteria, tags)

    gui_select_movie.assert_called_once_with(movies=movies_found)


def test_db_edit_movie(monkeypatch, old_movie, new_movie):
    # Arrange
    old_movie_bag = handlers.moviebagfacade.convert_from_movie_key_typed_dict(old_movie)
    db_edit_movie = MagicMock(name="db_edit_movie")
    monkeypatch.setattr(handlers.database.tables, "edit_movie", db_edit_movie)

    # Act
    handlers.database.db_edit_movie(old_movie, new_movie)

    # Assert
    db_edit_movie.assert_called_once_with(
        old_movie_bag=old_movie_bag, replacement_fields=new_movie
    )


# noinspection PyPep8Naming
def test_db_edit_movie_handles_NoResultFound_for_missing_tag(monkeypatch):
    exception = handlers.database.tables.NoResultFound()
    exc_context = handlers.database.tables.TAG_NOT_FOUND
    edit_movie_exception_handler(exception, exc_context, monkeypatch)


# noinspection PyPep8Naming
def test_db_edit_movie_handles_NoResultFound_for_missing_movie(monkeypatch):
    exception = handlers.database.tables.NoResultFound()
    exc_context = handlers.database.tables.MOVIE_NOT_FOUND
    edit_movie_exception_handler(exception, exc_context, monkeypatch)


# noinspection PyPep8Naming
def test_db_edit_movie_handles_IntegrityError_for_duplicate_movie(monkeypatch):
    exception = handlers.database.tables.IntegrityError("", "", Exception())
    exc_context = handlers.database.tables.MOVIE_EXISTS
    edit_movie_exception_handler(exception, exc_context, monkeypatch)


# noinspection PyPep8Naming
def test_db_edit_movie_handles_IntegrityError_for_invalid_year(monkeypatch):
    exception = handlers.database.tables.IntegrityError("", "", Exception())
    exc_context = handlers.database.tables.INVALID_YEAR
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

    # Patch call to database
    db_edit_movie = MagicMock(name="db_edit_movie")
    monkeypatch.setattr(handlers.database.tables, "edit_movie", db_edit_movie)
    db_edit_movie.side_effect = exception
    db_edit_movie.side_effect.__notes__ = [exc_context, "Note 2", "Note 3"]

    # Patch call to handlers.database.gui_edit_movie
    gui_edit_movie = MagicMock(name="gui_edit_movie")
    monkeypatch.setattr(handlers.database, "gui_edit_movie", gui_edit_movie)

    # Patch call to messagebox
    exc_messagebox = MagicMock(name="exc_messagebox")
    monkeypatch.setattr(handlers.database, "_exc_messagebox", exc_messagebox)

    handlers.database.db_edit_movie(old_movie, new_movie_bag)

    with check:
        exc_messagebox.assert_called_once_with(db_edit_movie.side_effect)
    with check:
        gui_edit_movie.assert_called_once_with(
            old_movie,
            prepopulate=new_movie_bag,
        )


def test_exc_messagebox_with_one_note(messagebox, config_current):
    item_1 = "item_1"

    try:
        raise Exception
    except Exception as exc:
        exc.add_note(item_1)
        handlers.database._exc_messagebox(exc)

    messagebox.assert_called_once_with(
        handlers.database.config.current.tk_root,
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
        handlers.database._exc_messagebox(exc)

    messagebox.assert_called_once_with(
        handlers.database.config.current.tk_root,
        message=item_1,
        detail=f"{item_2}, {item_3}.",
    )


def test_db_delete_movie_callback(monkeypatch):
    title = "test_delete_movie_callback title"
    year = 42
    movie = handlers.database.config.FindMovieTypedDict(title=title, year=[str(year)])
    movie_bag = MovieBag(title=title, year=MovieInteger(year))
    delete_movie = MagicMock(name="delete movie")
    monkeypatch.setattr(handlers.database.tables, "delete_movie", delete_movie)

    handlers.database.db_delete_movie(movie)

    delete_movie.assert_called_once_with(movie_bag=movie_bag)


def test_db_select_movies(monkeypatch):
    title = "test title for test_select_movie_callback"
    year = 42
    movie = config.MovieKeyTypedDict(title=title, year=year)
    movie_bag = MovieBag(title=title, year=MovieInteger(year))

    select_movie = MagicMock(name="select_movie")
    monkeypatch.setattr(handlers.database.tables, "select_movie", select_movie)
    select_movie.return_value = movie_bag

    gui_edit_movie = MagicMock(name="gui_edit_movie")
    monkeypatch.setattr(handlers.database, "gui_edit_movie", gui_edit_movie)

    handlers.database.db_select_movies(movie)

    with check:
        select_movie.assert_called_once_with(movie_bag=movie_bag)
    with check:
        gui_edit_movie.assert_called_once_with(movie, prepopulate=movie_bag)


def test_db_select_movies_handles_missing_movie_exception(
    monkeypatch, messagebox, config_current
):
    title = "test title for test_select_movie_callback"
    year = 42
    movie = config.MovieKeyTypedDict(title=title, year=year)
    notes_0 = handlers.database.tables.MOVIE_NOT_FOUND
    notes_1 = "note 1"
    notes_2 = "note 2"
    select_movie = MagicMock(name="select_movie")
    select_movie.side_effect = handlers.database.tables.NoResultFound()
    select_movie.side_effect.__notes__ = [notes_0, notes_1, notes_2]
    monkeypatch.setattr(handlers.database.tables, "select_movie", select_movie)

    handlers.database.db_select_movies(movie)

    messagebox.assert_called_once_with(
        handlers.database.config.current.tk_root,
        message=notes_0,
        detail=f"{notes_1}, {notes_2}.",
    )


def test_gui_add_tag(monkeypatch, config_current):
    add_tag_gui = MagicMock(name="add_tag_gui")
    monkeypatch.setattr(handlers.database.guiwidgets_2, "AddTagGUI", add_tag_gui)

    handlers.database.gui_add_tag()

    add_tag_gui.assert_called_once_with(
        config.current.tk_root, add_tag_callback=handlers.database.db_add_tag
    )


def test_gui_search_tag(monkeypatch, config_current):
    search_tag_gui = MagicMock(name="search_tag_gui")
    monkeypatch.setattr(
        handlers.database.guiwidgets_2,
        "SearchTagGUI",
        search_tag_gui,
    )

    handlers.database.gui_search_tag()

    search_tag_gui.assert_called_once_with(
        config.current.tk_root,
        search_tag_callback=handlers.database.db_match_tags,
    )


def test_gui_edit_tag(monkeypatch, config_current):
    widget_edit_tag = MagicMock(name="widget_edit_tag")
    monkeypatch.setattr(handlers.database.guiwidgets_2, "EditTagGUI", widget_edit_tag)
    tag = "old_tag"
    partial = MagicMock(name="partial")
    monkeypatch.setattr(handlers.database, "partial", partial)

    handlers.database.gui_edit_tag(tag)

    check.equal(
        partial.mock_calls,
        [
            call(handlers.database.db_edit_tag, tag),
            call(handlers.database.db_delete_tag, tag),
        ],
    )
    with check:
        widget_edit_tag.assert_called_once_with(
            config.current.tk_root,
            edit_tag_callback=partial(),
            delete_tag_callback=partial(),
            tag=tag,
        )


def test_gui_select_tag(monkeypatch, config_current):
    select_tag_gui = MagicMock(name="select_tag_gui")
    monkeypatch.setattr(handlers.database.guiwidgets_2, "SelectTagGUI", select_tag_gui)
    tags = {"tag 1", "tag 2"}

    handlers.database.gui_select_tag(tags=tags)

    select_tag_gui.assert_called_once_with(
        config.current.tk_root,
        select_tag_callback=handlers.database.gui_edit_tag,
        tags_to_show=list(tags),
    )


def test_db_add_tag(monkeypatch):
    tag_text = "test_add_tag_callback"
    add_tag = MagicMock(name="add_tag")
    monkeypatch.setattr(handlers.database.tables, "add_tag", add_tag)

    handlers.database.db_add_tag(tag_text)

    add_tag.assert_called_once_with(tag_text=tag_text)


def test_db_match_tags_finding_nothing(monkeypatch, config_current):
    messagebox = MagicMock(name="messagebox")
    monkeypatch.setattr(handlers.database.guiwidgets_2, "gui_messagebox", messagebox)
    gui_search_tag = MagicMock(name="gui_search_tag")
    monkeypatch.setattr(handlers.database, "gui_search_tag", gui_search_tag)
    match_tags = MagicMock(name="match_tags")
    match_tags.return_value = {}
    monkeypatch.setattr(handlers.database.tables, "match_tags", match_tags)
    match = "match pattern"

    handlers.database.db_match_tags(match)

    messagebox.assert_called_once_with(
        config.current.tk_root, message=handlers.database.tables.TAG_NOT_FOUND
    )
    gui_search_tag.assert_called_once_with(prepopulate=match)


def test_db_match_tags_finding_one_match(monkeypatch, config_current):
    gui_edit_tag = MagicMock(name="gui_edit_tag")
    monkeypatch.setattr(handlers.database, "gui_edit_tag", gui_edit_tag)
    match_tags = MagicMock(name="match_tags")
    tag_found = "tag_found"
    match_tags.return_value = {tag_found}
    monkeypatch.setattr(handlers.database.tables, "match_tags", match_tags)
    match = "Something, anything"

    handlers.database.db_match_tags(match)

    gui_edit_tag.assert_called_once_with(tag_found, prepopulate=match)


def test_db_match_tags_finding_multiple_matches(monkeypatch, config_current):
    gui_select_tag = MagicMock(name="gui_select_tag")
    monkeypatch.setattr(handlers.database, "gui_select_tag", gui_select_tag)
    tags = {"tag 1", "tag 2"}
    match_tags = MagicMock(name="match_tags")
    match_tags.return_value = tags
    monkeypatch.setattr(handlers.database.tables, "match_tags", match_tags)
    match = "match pattern"

    handlers.database.db_match_tags(match)

    gui_select_tag.assert_called_once_with(tags=tags)


def test_db_edit_tag(monkeypatch):
    old_tag_text = "old_tag_text"
    new_tag_text = "new_tag_text"
    db_edit_tag = MagicMock(name="db_edit_tag")
    monkeypatch.setattr(handlers.database.tables, "edit_tag", db_edit_tag)

    handlers.database.db_edit_tag(old_tag_text, new_tag_text)

    db_edit_tag.assert_called_once_with(
        old_tag_text=old_tag_text, new_tag_text=new_tag_text
    )


# noinspection DuplicatedCode
def test_db_edit_tag_with_old_tag_not_found(monkeypatch, messagebox, config_current):
    old_tag_text = "old_tag_text"
    new_tag_text = notes_1 = "new_tag_text"
    db_edit_tag = MagicMock(name="db_edit_tag")
    monkeypatch.setattr(handlers.database.tables, "edit_tag", db_edit_tag)
    db_edit_tag.side_effect = handlers.database.tables.NoResultFound
    notes_0 = handlers.database.tables.TAG_NOT_FOUND
    db_edit_tag.side_effect.__notes__ = [notes_0, notes_1]
    gui_search_tag = MagicMock(name="gui_search_tag")
    monkeypatch.setattr(handlers.database, "gui_search_tag", gui_search_tag)

    handlers.database.db_edit_tag(old_tag_text, new_tag_text)

    with check:
        messagebox.assert_called_once_with(
            handlers.database.config.current.tk_root,
            message=notes_0,
            detail=f"{notes_1}.",
        )
    with check:
        gui_search_tag.assert_called_once_with(prepopulate=old_tag_text)


# noinspection DuplicatedCode
def test_db_edit_tag_with_duplicate_new_tag(monkeypatch, messagebox, config_current):
    # Arrange
    old_tag_text = "old_tag_text"
    new_tag_text = notes_1 = "new_tag_text"
    db_edit_tag = MagicMock(name="db_edit_tag")
    monkeypatch.setattr(handlers.database.tables, "edit_tag", db_edit_tag)
    db_edit_tag.side_effect = handlers.database.tables.IntegrityError(
        "",
        "",
        Exception(),
    )
    notes_0 = handlers.database.tables.TAG_EXISTS
    db_edit_tag.side_effect.__notes__ = [notes_0, notes_1]

    # Act
    handlers.database.db_edit_tag(old_tag_text, new_tag_text)

    # Assert
    with check:
        messagebox.assert_called_once_with(
            handlers.database.config.current.tk_root,
            message=notes_0,
            detail=f"{notes_1}.",
        )


def test_db_delete_tag(monkeypatch):
    tag_text = "tag_text"
    delete_tag = MagicMock(name="delete_tag")
    monkeypatch.setattr(handlers.database.tables, "delete_tag", delete_tag)

    handlers.database.db_delete_tag(tag_text)

    delete_tag.assert_called_once_with(tag_text=tag_text)


def test_gui_edit_movie(monkeypatch, config_current, test_tags):
    widget_edit_movie = MagicMock(name="widget_edit_movie")
    monkeypatch.setattr(
        handlers.database.guiwidgets_2, "EditMovieGUI", widget_edit_movie
    )
    db_edit_movie = MagicMock(name="db_edit_movie")
    monkeypatch.setattr(handlers.database, "db_edit_movie", db_edit_movie)
    old_movie = MovieKeyTypedDict(title="test gui movie title", year=42)
    partial = MagicMock(name="partial")
    monkeypatch.setattr(handlers.database, "partial", partial)

    handlers.database.gui_edit_movie(old_movie)

    with check:
        partial.assert_called_once_with(db_edit_movie, old_movie)
    with check:
        widget_edit_movie.assert_called_once_with(
            config.current.tk_root,
            handlers.sundries._tmdb_io_handler,
            list(handlers.database.tables.select_all_tags()),
            prepopulate=None,
            edit_movie_callback=partial(),
            delete_movie_callback=handlers.database.db_delete_movie,
        )


@pytest.fixture(scope="function")
def config_current(monkeypatch):
    """This fixture patches a call to current.tk_root to suppress initiation of tk/tcl.

    Args:
        monkeypatch:
    """
    monkeypatch.setattr(handlers.database.config, "current", MagicMock(name="current"))


@pytest.fixture(scope="function")
def test_tags(monkeypatch):
    """This fixture mocks a call to handlers.database.tables.select_all_tags and
    returns a set of test tags.

    Args:
        monkeypatch:

    Returns:
        {"tag 1", "tag 2", "tag 3"}
    """
    test_tags = {"tag 1", "tag 2", "tag 3"}
    mock_select_tags = MagicMock(name="mock_select_tags", return_value=test_tags)
    monkeypatch.setattr(handlers.database.tables, "select_all_tags", mock_select_tags)
    return test_tags


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
        A MovieBag
    """
    new_title = "New Title"
    new_year = "4343"
    new_directors = {"Janis Jackson", "Keith Kryzlowski"}
    new_duration = "142"
    new_notes = "New Notes"
    new_movie_tags = {"new", "movie", "tags"}
    return handlers.database.MovieBag(
        title=new_title,
        year=MovieInteger(new_year),
        directors=new_directors,
        duration=MovieInteger(new_duration),
        notes=new_notes,
        tags=new_movie_tags,
    )


@pytest.fixture(scope="function")
def messagebox(monkeypatch):
    """This fixture patches handlers.database.guiwidgets_2.gui_messagebox

    Args:
        monkeypatch:

    Returns:
        A mock of handlers.database.guiwidgets_2.gui_messagebox
    """
    mock = MagicMock(name="messagebox")
    monkeypatch.setattr(handlers.database.guiwidgets_2, "gui_messagebox", mock)
    return mock
