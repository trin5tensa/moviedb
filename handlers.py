"""Menu handlers.

This module is the glue between the user's selection of a menu item and the gui."""

#  Copyright© 2020. Stephen Rigden.
#  Last modified 1/24/20, 7:14 AM by stephen.
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
from typing import List, Sequence

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
    all_tags = database.all_tags()
    guiwidgets.AddMovieGUI(config.app.tk_root, all_tags, add_movie_callback)


def add_movie_callback(movie: config.MovieDict, selected_tags: Sequence[str]):
    """ Add user supplied data to the database.
    
    Args:
        movie:
        selected_tags:
    """
    database.add_movie(movie)
    # TODO Remove note and 'noinspection' when fixed
    #   Pycharm reported bug:  https://youtrack.jetbrains.com/issue/PY-39404
    # noinspection PyTypedDict
    movie = config.MovieKeyDict(title=movie['title'], year=movie['year'])
    for tag in selected_tags:
        database.add_movie_tag_link(tag, movie)


def edit_movie():
    """ Get search movie data from the user and search for compliant records"""
    all_tags = database.all_tags()
    guiwidgets.SearchMovieGUI(config.app.tk_root, all_tags, search_movie_callback)


def search_movie_callback(criteria: config.FindMovieDict, tags: Sequence[str]):
    # moviedb-#109 Test this function
    
    # Find compliant movies.
    criteria['tags'] = tags
    # Remove empty items because SQL treats them as meaningful.
    criteria = {k: v
                for k, v in criteria.items()
                if v != '' and v != [] and v != () and v != ['', '']}
    movies = database.find_movies(criteria)
    
    if (movies_found := len(movies)) == 0:
        raise exception.MovieSearchFoundNothing
    elif movies_found == 1:
        _instantiate_edit_movie_gui(movies)
    elif movies_found > 1:
        guiwidgets.SelectMovieGUI(config.app.tk_root, movies, select_movie_callback)
    else:
        msg = f"The database search returned an unexpected value: {movies_found=}"
        logging.error(msg)
        guiwidgets.gui_messagebox(config.app.tk_root, 'Database Error', msg, icon='error')


def edit_movie_callback(movie: config.MovieUpdateDict, selected_tags: Sequence[str]):
    """ Add user supplied data to the database.

    Args:
        movie:
    """
    # moviedb-#109 Test this function
    
    # Edit the movie
    # TODO Remove this note and 'noinspection' when fixed
    #   Pycharm reported bug:  https://youtrack.jetbrains.com/issue/PY-39404
    # noinspection PyTypedDict
    title_year = config.FindMovieDict(title=movie['title'], year=[movie['year']])
    # moviedb-#109
    #   The movie might have been deleted from the database
    #   So trap any 'not found' errors.
    #   Display helpful message.
    database.edit_movie(title_year, movie)
    
    # Edit links
    old_tags = {tag.tag for tag in database.movies_tags(title_year)}
    new_tags = set(selected_tags)
    delete_tag_links = old_tags - new_tags
    add_tag_links = new_tags - old_tags
    
    print(f"{delete_tag_links=}")
    print(f"{add_tag_links=}")
    # moviedb-#109
    #   Remove tags deleted from the treeview selection by the user.
    #   Adding: Use add_tag_and_links
    
    raise exception.DatabaseException


def select_movie_callback(title: str, year: int):
    # moviedb-#109 Test this function
    # Get record from database
    movies = database.find_movies(dict(title=title, year=year))
    _instantiate_edit_movie_gui(movies)


def import_movies():
    """Open a csv file and load the contents into the database."""
    csv_fn = guiwidgets.gui_askopenfilename(parent=config.app.tk_root,
                                            filetypes=(('Movie import files', '*.csv'),))
    try:
        impexp.import_movies(csv_fn)
    except impexp.MoviedbInvalidImportData as exc:
        guiwidgets.gui_messagebox(config.app.tk_root, message='Errors were found in the input file.',
                                  detail=exc.args[0], icon='warning')


def _instantiate_edit_movie_gui(movies: List[config.FindMovieDict]):
    # moviedb-#109 Test this function
    all_tags = database.all_tags()
    for movie in movies:
        guiwidgets.EditMovieGUI(config.app.tk_root, all_tags, edit_movie_callback, movie)
