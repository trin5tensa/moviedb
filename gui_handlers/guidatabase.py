"""Menu handlers.

This module is the glue between the user's selection of a menu item and the gui."""

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

from collections.abc import Sequence, Callable
import config

import guiwidgets
import guiwidgets_2
from database_src import tables
from database_src.tables import MOVIE_NOT_FOUND
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


# todo 11/21/2024 Exception review
def add_movie_callback(gui_movie: MovieTD):
    """Add user supplied data to the database.

    Args:
        gui_movie:

    Logs and raises:
        MovieExists if title and year duplicate an existing movie.
        InvalidReleaseYear for year outside valid range.
        NoResultFound_OLD for tag not in database.
    """
    # noinspection PyUnresolvedReferences
    movie_bag = moviebagfacade.convert_from_movie_td(gui_movie)
    try:
        tables.add_movie(movie_bag=movie_bag)
        return

    except tables.IntegrityError as exc:
        match exc.__notes__[0]:
            case tables.MOVIE_EXISTS:
                guiwidgets_2.gui_messagebox(
                    config.current.tk_root,
                    message=exc.__notes__[0],
                    detail=f"{exc.__notes__[1]}, {exc.__notes__[2]}.",
                )

            case tables.INVALID_YEAR:
                guiwidgets_2.gui_messagebox(
                    config.current.tk_root,
                    message=exc.__notes__[0],
                    detail=exc.__notes__[1],
                )

    except tables.NoResultFound as exc:
        guiwidgets_2.gui_messagebox(
            config.current.tk_root, message=exc.__notes__[0], detail=exc.__notes__[1]
        )

    add_movie(movie_bag)


# todo 11/21/2024 Exception review
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
                message=MOVIE_NOT_FOUND,
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


# todo 11/21/2024 Exception review
def edit_movie_callback(old_movie: config.MovieKeyTypedDict) -> Callable:
    """Create the edit movie callback


    Args:
        old_movie: The movie that is to be edited.
            The record's key values may be altered by the user. This function will delete the old
            record and add a new record.

    Returns:
        A callback function which GUI edit can call with edits entered by the user.
    """

    def func(new_movie: MovieTD):
        """Change movie and links in database with new user supplied data,

        NoResultFound
        MovieExists
        InvalidReleaseYear

        Args:
            new_movie: Fields with either original values or values modified by the user.



        Raises exception.DatabaseSearchFoundNothing
        """
        old_movie_bag = moviebagfacade.convert_from_movie_key_typed_dict(old_movie)
        new_movie_bag = moviebagfacade.convert_from_movie_td(new_movie)

        try:
            tables.edit_movie(
                old_movie_bag=old_movie_bag, replacement_fields=new_movie_bag
            )

        except tables.MovieNotFound:
            # The old movie has been deleted by another process. The edit was rolled back.
            # Since the movie selected by the user for editing is no longer available no
            # further help can be provided beyond informing the user.
            # todo fix
            guiwidgets_2.gui_messagebox(
                config.current.tk_root,
                message=f"{MOVIE_NO_LONGER_PRESENT} {old_movie_bag['title']}, "
                f"{old_movie_bag['year']}",
            )

        except tables.NoResultFound as exc:
            # A tag was deleted by another process. The edit was rolled back. Represent the
            # edit screen with the values which were entered by the user.
            guiwidgets_2.gui_messagebox(
                config.current.tk_root,
                message=exc.__notes__[0],
                detail=exc.__notes__[1],
            )
            _edit_movie(old_movie, new_movie_bag)

        except tables.MovieExists:
            # An attempt to change the key was rejected as the new key was not unique.
            # The edit was rolled back.
            # todo fix
            guiwidgets_2.gui_messagebox(
                config.current.tk_root,
                message=f"{TITLE_AND_YEAR_EXISTS_MSG}. {new_movie_bag['title']}, "
                f"{new_movie_bag['year']}",
            )
            _edit_movie(old_movie, new_movie_bag)

        except tables.InvalidReleaseYear:
            # An attempt to change the year was rejected as impossibly early
            # or late. The edit was rolled back.
            # todo fix
            guiwidgets_2.gui_messagebox(
                config.current.tk_root,
                message=f"{INVALID_RELEASE_YEAR_MSG}. {new_movie_bag['title']}, "
                f"{new_movie_bag['year']}",
            )
            _edit_movie(old_movie, new_movie_bag)

    return func


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
