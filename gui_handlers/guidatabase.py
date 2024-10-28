"""Menu handlers.

This module is the glue between the user's selection of a menu item and the gui."""

#  Copyright© 2024. Stephen Rigden.
#  Last modified 10/28/24, 4:01 PM by stephen.
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
IMPOSSIBLE_RELEASE_YEAR_MSG = "The release year is too early or too late."
TAG_NOT_FOUND_MSG = "One or more tags were not found in the database."
NO_COMPLIANT_MOVIES_FOUND_MSG = "No compliant movies were found"


def add_movie(movie_bag: MovieBag = None):
    """Get new movie data from the user and add it to the database.

    Args:
        movie_bag: If the user's data causes a database exception then this function
        will be called again with movie_bag populated with the data fields originally
        entered by the user.
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

    Args:
        gui_movie:

    Logs and raises:
        MovieExists if title and year duplicate an existing movie.
        InvalidReleaseYear for year outside valid range.
        TagNotFound_OLD for tag not in database.
    """
    # noinspection PyUnresolvedReferences
    movie_bag = moviebagfacade.convert_from_movie_td(gui_movie)
    try:
        tables.add_movie(movie_bag=movie_bag)
    except tables.MovieExists:
        guiwidgets_2.gui_messagebox(
            config.current.tk_root, message=TITLE_AND_YEAR_EXISTS_MSG
        )
        add_movie(movie_bag)
    except tables.InvalidReleaseYear:
        guiwidgets_2.gui_messagebox(
            config.current.tk_root, message=IMPOSSIBLE_RELEASE_YEAR_MSG
        )
        add_movie(movie_bag)
    except tables.TagNotFound_OLD:
        guiwidgets_2.gui_messagebox(config.current.tk_root, message=TAG_NOT_FOUND_MSG)
        add_movie(movie_bag)


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
                config.current.tk_root, message=NO_COMPLIANT_MOVIES_FOUND_MSG
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
            tables.edit_movie(old_movie_bag=old_movie_bag, new_movie_bag=new_movie_bag)

        except tables.TagNotFound_OLD:
            # todo Remove this message when the tables.py design problem is fixed.
            #   Due to an as yet unexplored design problem* in tables.py we got here because
            #   either an expected movie record or an expected tag record was not found.
            #   For the time being, the user will be notified and the process will end.
            #   *
            #   When a tuple is not found by a select statement it seems likely that the
            #   exception is not raised immediately but when the session is committed. If an
            #   exception can be raised by more than one operation within a a session then it
            #   becomes difficult to determine which statement is at fault.
            guiwidgets_2.gui_messagebox(
                config.current.tk_root, message=TAG_NOT_FOUND_MSG
            )

        except tables.MovieExists:
            guiwidgets_2.gui_messagebox(
                config.current.tk_root, message=TITLE_AND_YEAR_EXISTS_MSG
            )
            full_movie_bag = tables.select_movie(movie_bag=new_movie_bag)
            guiwidgets_2.EditMovieGUI(
                config.current.tk_root,
                _tmdb_io_handler,
                list(tables.select_all_tags()),
                old_movie=config.MovieUpdateDef(**old_movie),
                edited_movie_bag=full_movie_bag,
                edit_movie_callback=edit_movie_callback(old_movie),
                delete_movie_callback=delete_movie_callback,
            )

    return func
