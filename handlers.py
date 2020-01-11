"""Menu handlers.

This module is the glue between the user's selection of a menu item and the gui."""

#  Copyright© 2020. Stephen Rigden.
#  Last modified 1/11/20, 2:08 PM by stephen.
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
import logging
from typing import Any, Sequence

import config
import database
import exception
import guiwidgets
import impexp


def about_dialog():
    """Display the about dialog."""
    guiwidgets.gui_messagebox(config.app.tk_root, config.app.name, config.app.version)


def add_movie():
    """ Get new movie data from the user and add it to the database. """
    tags = database.all_tags()
    guiwidgets.AddMovieGUI(config.app.tk_root, tags, add_movie_callback)


def add_movie_callback(movie: config.MovieDict, tags: Sequence[str]):
    """ Add user supplied data to the database.
    
    Args:
        movie:
        tags:
    """
    database.add_movie(movie)
    # TODO Remove note and 'noinspection' when fixed
    #   Pycharm reported bug:  https://youtrack.jetbrains.com/issue/PY-39404
    # noinspection PyTypedDict
    movies = (config.MovieKeyDict(title=movie['title'], year=movie['year']),)
    for tag in tags:
        database.add_tag_and_links(tag, movies)


def edit_movie():
    """ Get search movie data from the user and search for compliant records"""
    tags = database.all_tags()
    guiwidgets.SearchMovieGUI(config.app.tk_root, tags, search_movie_callback)


def search_movie_callback(criteria: config.FindMovieDict, tags: Sequence[str]):
    # moviedb-#109 Test this function
    
    # Find compliant movies.
    criteria['tags'] = tags
    # Remove empty items because SQL treats them as meaningful.
    criteria = {k: v
                for k, v in criteria.items()
                if v != '' and v != [] and v != ['', '']}
    movies = database.find_movies(criteria, yield_count=True)
    
    movies_found: Any = next(movies)
    if movies_found == 0:
        raise exception.MovieSearchFoundNothing
    elif movies_found == 1:
        movie = next(movies)
        tags = database.all_tags()
        guiwidgets.EditMovieGUI(config.app.tk_root, tags, edit_movie_callback, movie)
    elif movies_found > 1:
        guiwidgets.SelectMovieGUI(config.app.tk_root, movies, select_movie_callback)
    else:
        msg = f"The database search returned an unexpected value: {movies_found=}"
        logging.error(msg)
        guiwidgets.gui_messagebox(config.app.tk_root, 'Database Error', msg, icon='error')


def edit_movie_callback(movie: config.MovieUpdateDict):
    """ Add user supplied data to the database.

    Args:
        movie:
    """
    # moviedb-#109 Test this function
    
    # TODO Remove note and 'noinspection' when fixed
    #   Pycharm reported bug:  https://youtrack.jetbrains.com/issue/PY-39404
    # noinspection PyTypedDict
    title_year = dict(title=movie['title'], year=[movie['year']])
    # moviedb-#109
    #   The movie might have been deleted from the database
    #   So trap any 'not found' errors.
    #   Display helpful message.
    database.edit_movie(title_year, movie)


def select_movie_callback(title: str, year: int):
    # moviedb-#109 Test this function
    # Get record from database
    movies = database.find_movies(dict(title=title, year=year))
    movie = next(movies)
    tags = database.all_tags()
    guiwidgets.EditMovieGUI(config.app.tk_root, tags, edit_movie_callback, movie)


def import_movies():
    """Open a csv file and load the contents into the database."""
    csv_fn = guiwidgets.gui_askopenfilename(parent=config.app.tk_root,
                                            filetypes=(('Movie import files', '*.csv'),))
    try:
        impexp.import_movies(csv_fn)
    except impexp.MoviedbInvalidImportData as exc:
        guiwidgets.gui_messagebox(config.app.tk_root, message='Errors were found in the input file.',
                                  detail=exc.args[0], icon='warning')
