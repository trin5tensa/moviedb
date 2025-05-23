"""Menu handlers for the database."""

#  Copyright© 2025. Stephen Rigden.
#  Last modified 5/16/25, 1:30 PM by stephen.
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

from functools import partial
import logging

from gui import movies, common, tags, tviewselect

from database import tables
from moviebag import MovieBag
from handlers.sundries import _tmdb_io_handler


TITLE_AND_YEAR_EXISTS_MSG = (
    "The title and release date clash with a movie already in the database"
)
INVALID_RELEASE_YEAR_MSG = "The release year is too early or too late."
MOVIE_NO_LONGER_PRESENT = "The original movie is no longer present in the database."
MISSING_EXPLANATORY_NOTES = (
    "Exception raised without explanatory notes needed for user alert."
)


def gui_add_movie(*, prepopulate: MovieBag = None):
    """Presents a GUI form for adding a new movie.

    Args:
        prepopulate:
            This argument can be used to prepopulate the movie widget. This
            is useful if the initial attempt to add a movie caused an
            exception. It gives the user the opportunity to fix input errors.
            If present, the item "prepopulate['tags']" contains the
            tag selection.
    """
    all_tags = tables.select_all_tags()
    if not prepopulate:
        prepopulate = MovieBag()
    movies.AddMovieGUI(
        common.tk_root,
        tmdb_callback=_tmdb_io_handler,
        all_tags=all_tags,
        prepopulate=prepopulate,
        database_callback=db_add_movie,
    )


# noinspection PyUnusedLocal
def gui_search_movie(*, prepopulate: MovieBag = None):
    """Presents a GUI form for movie searches.

    Args:
        prepopulate:
            This argument can be used to prepopulate the movie widget. This
            is useful if the initial attempt to search for a movie caused
            an exception. It gives the user the opportunity to fix
            input errors.
    """
    all_tags = tables.select_all_tags()
    if not prepopulate:
        prepopulate = MovieBag()
    movies.SearchMovieGUI(
        common.tk_root,
        database_callback=db_match_movies,
        tmdb_callback=_tmdb_io_handler,
        all_tags=all_tags,
        prepopulate=prepopulate,
    )


def gui_select_movie(*, movie_bags: list[MovieBag]):
    """Presents a user dialog for selecting a movie from a list.

    Args:
        movie_bags:
    """
    tviewselect.SelectMovieGUI(
        common.tk_root,
        selection_callback=db_select_movie,
        rows=movie_bags,
    )


def gui_edit_movie(old_movie: MovieBag, *, prepopulate: MovieBag = None):
    """Presents a GUI form for editing movies from the database.

    Args:
        old_movie: The old movie will be retrieved from the database and
            updated.
        prepopulate:
            This argument can be used to prepopulate the movie widget. This
            is useful if the initial attempt to edit a movie caused an
            exception. It gives the user the opportunity to fix input errors.
            If the key "prepopulate['tags']" is present, it will contain the tag
            selection.
    """
    all_tags = tables.select_all_tags()
    movies.EditMovieGUI(
        common.tk_root,
        tmdb_callback=_tmdb_io_handler,
        all_tags=all_tags,
        prepopulate=prepopulate,
        database_callback=partial(db_edit_movie, old_movie),
        delete_movie_callback=partial(db_delete_movie, old_movie),
    )


def db_add_movie(movie_bag: MovieBag):
    """Adds user supplied movie data to the database.

    A user alert is raised with diagnostic information if the database
    module rejects the addition. Then the user is presented with an
    'add movie' input screen populated with her previously entered data.

    Args:
        movie_bag:
    """
    try:
        tables.add_movie(movie_bag=movie_bag)

    except (tables.IntegrityError, tables.NoResultFound) as exc:
        if exc.__notes__[0] in (
            tables.MOVIE_EXISTS,
            tables.INVALID_YEAR,
            tables.TAG_NOT_FOUND,
        ):
            _exc_messagebox(exc)
            gui_add_movie(prepopulate=movie_bag)
        else:  # pragma nocover
            raise

    else:
        gui_add_movie()


def db_match_movies(criteria: MovieBag):
    """Selects movies from the database which match user-entered
    criteria and tags.

    Subsequent actions depend on the number of movies found. The user is
    informed if no movies are found before being returned to an input
    form which allows her to continue her search for a movie to edit.

    A single movie is presented to the user ready for her edits.

    In the case where multiple movies match the criteria, then they'll
    be listed for the user to select one for editing.

    Args:
        criteria:
    """
    # Removes empty items because SQL treats them as meaningful.
    criteria = {k: v for k, v in criteria.items() if v != ""}  # pragma nocover

    movies_found = tables.match_movies(match=MovieBag(**criteria))
    match len(movies_found):
        case 0:
            # Informs user and represents the search window.
            common.showinfo(tables.MOVIE_NOT_FOUND)
            gui_search_movie(prepopulate=MovieBag(**criteria))

        case 1:
            # Presents an Edit/View/Delete window to user
            movie_bag = movies_found[0]
            gui_edit_movie(movie_bag, prepopulate=movie_bag)

        case _:
            # Presents a selection window showing the multiple compliant movies.
            gui_select_movie(movie_bags=movies_found)


def db_select_movie(movie_bag: MovieBag):
    """Selects a single movie and presents a GUI edit form.

    If the movie is not found this function assumes the movie was deleted
    by another process. A user alert is given and the process aborts.

    Args:
        movie_bag: The movie title and year are used to select a movie.
    """
    try:
        movie_bag = tables.select_movie(movie_bag=movie_bag)

    except tables.NoResultFound as exc:
        if exc.__notes__[0] == tables.MOVIE_NOT_FOUND:
            _exc_messagebox(exc)
        else:  # pragma nocover
            raise

    else:
        gui_edit_movie(movie_bag, prepopulate=movie_bag)


def db_edit_movie(old_movie: MovieBag, new_movie: MovieBag):
    """Changes a movie and its links in database with new user supplied data.

    A user alert is raised with diagnostic information if the database
    module rejects the addition. Then the user is presented with an
    'edit movie' input screen populated with previously entered data.

    Args:
        old_movie: The old movie key.
        new_movie: Fields with either original values or values modified by the user.
    """
    try:
        tables.edit_movie(old_movie_bag=old_movie, replacement_fields=new_movie)

    except (tables.NoResultFound, tables.IntegrityError) as exc:
        if exc.__notes__[0] in (
            tables.TAG_NOT_FOUND,
            tables.MOVIE_NOT_FOUND,
            tables.MOVIE_EXISTS,
            tables.INVALID_YEAR,
        ):
            _exc_messagebox(exc)
            gui_edit_movie(old_movie, prepopulate=new_movie)
        else:  # pragma nocover
            raise


def db_delete_movie(old_movie: MovieBag):
    """Deletes a movie from the database.

    No action will be taken if the movie does not exist.

    Args:
        old_movie: The old movie. Directors and stars must be included to
        ensure correct deletion of related and 'orphaned' records.
    """
    tables.delete_movie(movie_bag=old_movie)


def gui_add_tag():
    """Presents a GUI form for adding a new movie."""
    tags.AddTagGUI(
        common.tk_root,
        add_tag_callback=db_add_tag,
    )


def gui_select_all_tags():
    """Presents a user dialog for selecting a tag from a list."""
    tviewselect.SelectTagGUI(
        common.tk_root,
        selection_callback=gui_edit_tag,
        rows=list(tables.select_all_tags()),
    )


# noinspection PyUnusedLocal
def gui_edit_tag(tag: str, *, prepopulate: str = None):
    """Presents a GUI form for editing tags.

    Args:
        tag:
        prepopulate:
            This argument can be used to prepopulate the tag widget. This
            is useful if the initial attempt to edit a tag caused
            an exception. It gives the user the opportunity to fix
            input errors.
    """
    tags.EditTagGUI(
        common.tk_root,
        edit_tag_callback=partial(db_edit_tag, tag),
        delete_tag_callback=partial(db_delete_tag, tag),
        tag=tag,
    )


def db_add_tag(tag_text: str):
    """Calls the database to add a new tag.

    Args:
        tag_text:
    """
    tables.add_tag(tag_text=tag_text)


def db_delete_tag(tag_text: str):
    """Deletes a tag.

    Args:
        tag_text:
    """
    tables.delete_tag(tag_text=tag_text)


def db_edit_tag(old_tag_text: str, new_tag_text: str):
    """Changes a tag text from old_tag_text to new_tag_text.

        The user will be alerted if the old tag text cannot be found, and
        the edit_tag process will be restarted. The user will also be alerted
        if the new tag text duplicates an existing tag, but no other
        action will be taken.

    Args:
        old_tag_text:
        new_tag_text:
    """
    try:
        tables.edit_tag(old_tag_text=old_tag_text, new_tag_text=new_tag_text)

    except tables.NoResultFound as exc:
        _exc_messagebox(exc)
        gui_select_all_tags()

    except tables.IntegrityError as exc:
        _exc_messagebox(exc)


def _exc_messagebox(exc):
    """This helper presents a GUI user alert with exception information.

    The message is the first item in exc.__notes__. Subsequent items are
    concatenated into the messagebox detail.

    Args:
        exc: The SQLAlchemy exception with a populated exc.__notes__
            attribute.

    Raises:
        Logs and reraises the original exception if the explanatory notes
        are missing.
    """
    if len(exc.__notes__) == 1:
        common.showinfo(message=exc.__notes__[0])

    elif len(exc.__notes__) > 1:
        common.showinfo(
            message=exc.__notes__[0], detail=", ".join(exc.__notes__[1:]) + "."
        )

    else:  # pragma nocover
        logging.error(MISSING_EXPLANATORY_NOTES)
        exc.add_note(MISSING_EXPLANATORY_NOTES)
        raise
