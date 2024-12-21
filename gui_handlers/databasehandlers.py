"""Menu handlers.

This module is the glue between the user's selection of a menu item and the gui."""

#  Copyright© 2024. Stephen Rigden.
#  Last modified 12/21/24, 1:31 PM by stephen.
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

from collections.abc import Sequence
from functools import partial

import config
import logging

import guiwidgets
import guiwidgets_2
from config import MovieKeyTypedDict
from database_src import tables
from globalconstants import MovieTD, MovieBag, MovieInteger
from gui_handlers import moviebagfacade
from gui_handlers.handlers import _tmdb_io_handler


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
    """
    all_tags = tables.select_all_tags()
    guiwidgets_2.AddMovieGUI(
        config.current.tk_root,
        _tmdb_io_handler,
        list(all_tags),
        prepopulate=prepopulate,
        add_movie_callback=db_add_movie,
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
    # moviedb-#459 Repopulate
    #  The class SearchMovieGUI is not currently able to support
    #  prepopulation, so the prepopulate parameter is ignored for now.
    all_tags = tables.select_all_tags()
    guiwidgets.SearchMovieGUI(config.current.tk_root, db_match_movies, list(all_tags))


def gui_edit_movie(
    old_movie: config.MovieKeyTypedDict, *, prepopulate: MovieBag = None
):
    """Presents a GUI form for editing movies from the database.

    Args:
        old_movie:
        prepopulate:
            This argument can be used to prepopulate the movie widget. This
            is useful if the initial attempt to edit a movie caused an
            exception. It gives the user the opportunity to fix
            input errors.
    """
    guiwidgets_2.EditMovieGUI(
        config.current.tk_root,
        _tmdb_io_handler,
        list(tables.select_all_tags()),
        old_movie=config.MovieUpdateDef(**old_movie),
        prepopulate=prepopulate,
        edit_movie_callback=partial(db_edit_movie, old_movie),
        delete_movie_callback=db_delete_movie,
    )


def db_add_movie(gui_movie: MovieTD):
    """Adds user supplied movie data to the database.

    A user alert is raised with diagnostic information if the database
    module rejects the addition. Then the user is presented with an
    'add movie' input screen populated with her previously entered data.

    Args:
        gui_movie:
    """
    movie_bag = moviebagfacade.convert_from_movie_td(gui_movie)
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


def db_match_movies(criteria: config.FindMovieTypedDict, tags: Sequence[str]):
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
        tags:
    """
    # Cleans up old style arguments
    criteria["tags"] = tags
    # Removes empty items because SQL treats them as meaningful.
    criteria = {
        k: v
        for k, v in criteria.items()
        if v != "" and v != [] and v != () and v != ["", ""]
    }  # pragma nocover

    # Converts old style arguments to new movie_bag argument
    movie_bag = moviebagfacade.convert_from_find_movie_typed_dict(criteria)

    movies_found = tables.match_movies(match=movie_bag)
    match len(movies_found):
        case 0:
            # Informs user and represent the search window.
            guiwidgets_2.gui_messagebox(
                config.current.tk_root,
                message=tables.MOVIE_NOT_FOUND,
            )
            gui_search_movie()

        case 1:
            # Presents an Edit/View/Delete window to user
            movie_bag = movies_found[0]
            movie = moviebagfacade.convert_to_movie_key_typed_dict(movie_bag)
            gui_edit_movie(movie)

        case _:
            # Presents a selection window showing the multiple compliant movies.
            movies = [
                moviebagfacade.convert_to_movie_update_def(movie_bag)
                for movie_bag in movies_found
            ]  # pragma nocover
            guiwidgets.SelectMovieGUI(config.current.tk_root, movies, db_select_movies)


def db_select_movies(movie: MovieKeyTypedDict):
    """Selects a single movie and presents a GUI edit form.

    If the movie is not found this function assumes the movie was deleted
    by another process. A user alert is given and the process aborts.

    Args:
        movie: The movie title and year are used to select a movie.
    """
    movie_key = MovieBag(title=movie["title"], year=MovieInteger(movie["year"]))
    try:
        movie_bag = tables.select_movie(movie_bag=movie_key)

    except tables.NoResultFound as exc:
        if exc.__notes__[0] == tables.MOVIE_NOT_FOUND:
            _exc_messagebox(exc)
        else:  # pragma nocover
            raise

    else:
        old_movie = moviebagfacade.convert_to_movie_update_def(movie_bag)
        gui_edit_movie(old_movie, prepopulate=movie_bag)


def db_edit_movie(old_movie: config.MovieKeyTypedDict, new_movie: MovieTD):
    """Changes a movie and its links in database with new user supplied data.

    A user alert is raised with diagnostic information if the database
    module rejects the addition. Then the user is presented with an
    'edit movie' input screen populated with previously entered data.

    Args:
        old_movie: The old movie key.
        new_movie: Fields with either original values or values modified by the user.
    """
    old_movie_bag = moviebagfacade.convert_from_movie_key_typed_dict(old_movie)
    new_movie_bag = moviebagfacade.convert_from_movie_td(new_movie)

    try:
        tables.edit_movie(old_movie_bag=old_movie_bag, replacement_fields=new_movie_bag)

    except (tables.NoResultFound, tables.IntegrityError) as exc:
        if exc.__notes__[0] in (
            tables.TAG_NOT_FOUND,
            tables.MOVIE_NOT_FOUND,
            tables.MOVIE_EXISTS,
            tables.INVALID_YEAR,
        ):
            _exc_messagebox(exc)
            gui_edit_movie(old_movie, prepopulate=new_movie_bag)
        else:  # pragma nocover
            raise


def db_delete_movie(movie: config.FindMovieTypedDict):
    """Deletes a movie from the database.

    No action will be taken if the movie does not exist.

    Args:
        movie: Specified by title and key.
    """
    movie_bag = MovieBag(
        title=movie["title"],
        year=MovieInteger(int(movie["year"][0])),
    )
    tables.delete_movie(movie_bag=movie_bag)


def gui_add_tag():
    """Presents a GUI form for adding a new movie."""
    guiwidgets_2.AddTagGUI(
        config.current.tk_root,
        add_tag_callback=db_add_tag,
    )


# noinspection PyUnusedLocal
def gui_search_tag(*, prepopulate: str = None):
    """Presents a GUI form for tag searches.

    Args:
        prepopulate:
            This argument can be used to prepopulate the tag widget. This
            is useful if the initial attempt to search for a tag caused
            an exception. It gives the user the opportunity to fix
            input errors.
    """
    # moviedb-#460 Repopulate
    #  The class SearchTagGUI is not currently able to support
    #  prepopulation, so the prepopulate parameter is ignored for now.
    guiwidgets_2.SearchTagGUI(
        config.current.tk_root,
        search_tag_callback=db_match_tags,
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
    # moviedb-#461 Repopulate
    #  The class EditTagGUI is not currently able to support
    #  prepopulation, so the prepopulate parameter is ignored for now.
    guiwidgets_2.EditTagGUI(
        config.current.tk_root,
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


def db_match_tags(match: str):
    """Selects movies from the database which match user-entered
    criteria and tags.

    If no tags match the user is alerted and the tag editing process will
    be restarted. If a single match is found the 'edit tag' screen will
    be presented. If multiple tags match, a selectable list of the matches
    will be displayed.

    Args:
        match: match pattern
    """
    tags = tables.match_tags(match=match)

    if len(tags) == 0:
        guiwidgets_2.gui_messagebox(
            config.current.tk_root, message=tables.TAG_NOT_FOUND
        )
        gui_search_tag(prepopulate=match)

    elif len(tags) == 1:
        tag = tags.pop()
        gui_edit_tag(tag, prepopulate=match)

    else:
        guiwidgets_2.SelectTagGUI(
            config.current.tk_root,
            select_tag_callback=gui_edit_tag,
            tags_to_show=list(tags),
        )


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
        gui_search_tag(prepopulate=old_tag_text)

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
        guiwidgets_2.gui_messagebox(
            config.current.tk_root,
            message=exc.__notes__[0],
        )

    elif len(exc.__notes__) > 1:
        guiwidgets_2.gui_messagebox(
            config.current.tk_root,
            message=exc.__notes__[0],
            detail=", ".join(exc.__notes__[1:]) + ".",
        )

    else:  # pragma nocover
        logging.error(MISSING_EXPLANATORY_NOTES)
        exc.add_note(MISSING_EXPLANATORY_NOTES)
        raise
