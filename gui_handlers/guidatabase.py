"""Menu handlers.

This module is the glue between the user's selection of a menu item and the gui."""

#  Copyright© 2024. Stephen Rigden.
#  Last modified 10/7/24, 2:13 PM by stephen.
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


import config

import guiwidgets
import guiwidgets_2
from database_src import tables
from globalconstants import MovieTD, MovieBag
from gui_handlers import moviebagfacade
from gui_handlers.handlers import (
    _tmdb_io_handler,
    _search_movie_callback,
)

TITLE_AND_YEAR_EXISTS_MSG = (
    "The title and release date clash with a movie already in the database"
)
IMPOSSIBLE_RELEASE_YEAR_MSG = "The release year is too early or too late."
TAG_NOT_FOUND_MSG = "One or more tags were not found in the database."


def add_movie(movie_bag: MovieBag = None):
    """Get new movie data from the user and add it to the database."""
    all_tags = tables.select_all_tags()
    guiwidgets_2.AddMovieGUI(
        config.current.tk_root,
        _tmdb_io_handler,
        list(all_tags),
        movie_bag=movie_bag,
        add_movie_callback=add_movie_callback,
    )


def add_movie_callback(gui_movie: MovieTD):
    """Add user supplied data to the database.

    Args:
        gui_movie:

    Logs and raises:
        MovieExists if title and year duplicate an existing movie.
        InvalidReleaseYear for year outside valid range.
        TagNotFound for tag not in database.
    """
    # noinspection PyUnresolvedReferences
    movie_bag = moviebagfacade.MovieBagFacade.from_movie_td(gui_movie)
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
    except tables.TagNotFound:
        guiwidgets_2.gui_messagebox(config.current.tk_root, message=TAG_NOT_FOUND_MSG)
        add_movie(movie_bag)


def edit_movie():
    """Get search movie data from the user and search for compliant records"""
    all_tags = tables.select_all_tags()
    guiwidgets.SearchMovieGUI(
        config.current.tk_root, _search_movie_callback, list(all_tags)
    )
