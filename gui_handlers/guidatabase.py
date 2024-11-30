"""Menu handlers.

This module is the glue between the user's selection of a menu item and the gui."""

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

from collections.abc import Sequence, Callable
import config
import logging

import guiwidgets
import guiwidgets_2
from database_src import tables
from globalconstants import MovieTD, MovieBag
from gui_handlers import moviebagfacade
from gui_handlers.handlers import (
    _tmdb_io_handler,
    delete_movie_callback,
    _select_movie_callback,
)
from gui_handlers.moviebagfacade import convert_to_movie_update_def

TITLE_AND_YEAR_EXISTS_MSG = (
    "The title and release date clash with a movie already in the database"
)
INVALID_RELEASE_YEAR_MSG = "The release year is too early or too late."
MOVIE_NO_LONGER_PRESENT = "The original movie is no longer present in the database."
MISSING_EXPLANATORY_NOTES = (
    "Exception raised without explanatory notes needed for user alert."
)


def add_movie(movie_bag: MovieBag = None):
    """Gets new movie data from the user and adds it to the database.

    The optional movie_bag argument can be used to prepopulate the movie form. This is useful
    if the initial attempt to add a movie caused an exception. It gives the user the opportunity

    Args:
        movie_bag
    """
    all_tags = tables.select_all_tags()
    guiwidgets_2.AddMovieGUI(
        config.current.tk_root,
        _tmdb_io_handler,
        list(all_tags),
        movie_bag=movie_bag,
        add_movie_callback=add_movie_callback,
    )


def search_for_movie():
    """Get search movie data from the user and search for compliant records"""
    all_tags = tables.select_all_tags()
    guiwidgets.SearchMovieGUI(
        config.current.tk_root, search_for_movie_callback, list(all_tags)
    )


def add_movie_callback(gui_movie: MovieTD):
    """Add user supplied data to the database.

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
            exc_messagebox(exc)
            # todo What happens to the tag selection if the edit is represented?
            add_movie(movie_bag)
        else:  # pragma nocover
            raise


def search_for_movie_callback(criteria: config.FindMovieTypedDict, tags: Sequence[str]):
    """Finds movies in the database which match the user entered criteria.
    Continue to the next appropriate stage of processing depending on whether no movies, one
    movie, or more than one movie is found.

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
    }

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
            search_for_movie()
        case 1:
            # Presents an Edit/View/Delete window to user
            movie_bag = movies_found[0]
            movie = convert_to_movie_update_def(movie_bag)

            guiwidgets_2.EditMovieGUI(
                config.current.tk_root,
                _tmdb_io_handler,
                list(tables.select_all_tags()),
                old_movie=movie,
                edit_movie_callback=edit_movie_callback(movie),
                delete_movie_callback=delete_movie_callback,
            )
        case _:
            # Presents a selection window showing the multiple compliant movies.
            movies = [
                moviebagfacade.convert_to_movie_update_def(movie_bag)
                for movie_bag in movies_found
            ]
            guiwidgets.SelectMovieGUI(
                config.current.tk_root, movies, _select_movie_callback
            )


def edit_movie_callback(old_movie: config.MovieKeyTypedDict) -> Callable:
    """Create the edit movie callback

    Args:
        old_movie: The movie that is to be edited.
            The record's key values may be altered by the user. This function
            will delete the old record and add a new record.

    Returns:
        A callback function which GUI edit can call with edits entered by the user.
    """

    def func(new_movie: MovieTD):
        """Change movie and links in database with new user supplied data,

        A user alert is raised with diagnostic information if the database
        module rejects the addition. Then the user is presented with an
        'add movie' input screen populated with her previously entered data.

        Args:
            new_movie: Fields with either original values or values modified by the user.
        """
        old_movie_bag = moviebagfacade.convert_from_movie_key_typed_dict(old_movie)
        new_movie_bag = moviebagfacade.convert_from_movie_td(new_movie)

        try:
            tables.edit_movie(
                old_movie_bag=old_movie_bag, replacement_fields=new_movie_bag
            )

        except (tables.NoResultFound, tables.IntegrityError) as exc:
            if exc.__notes__[0] in (
                tables.TAG_NOT_FOUND,
                tables.MOVIE_NOT_FOUND,
                tables.MOVIE_EXISTS,
                tables.INVALID_YEAR,
            ):
                exc_messagebox(exc)
                # todo What happens to the tag selection if the edit is represented?
                _edit_movie(old_movie, new_movie_bag)
            else:  # pragma nocover
                raise

    return func


# todo Test this function
def _edit_movie(old_movie: config.MovieKeyTypedDict, new_movie_bag: MovieBag):
    """A helper function which calls edit movie GUI.

    Args:
        old_movie:
        new_movie_bag:

    Use Case:
        This supports exception cases handled by the edit_movie_callback.
        They need to redisplay the user edit which caused the exceptions.
    """
    guiwidgets_2.EditMovieGUI(
        config.current.tk_root,
        _tmdb_io_handler,
        list(tables.select_all_tags()),
        old_movie=config.MovieUpdateDef(**old_movie),
        edited_movie_bag=new_movie_bag,
        edit_movie_callback=edit_movie_callback(old_movie),
        delete_movie_callback=delete_movie_callback,
    )


def exc_messagebox(exc):
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
