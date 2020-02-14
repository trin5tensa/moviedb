"""Menu handlers.

This module is the glue between the user's selection of a menu item and the gui."""

#  Copyright© 2020. Stephen Rigden.
#  Last modified 2/12/20, 2:13 PM by stephen.
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


from typing import Sequence

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


def edit_movie():
    """ Get search movie data from the user and search for compliant records"""
    all_tags = database.all_tags()
    guiwidgets.SearchMovieGUI(config.app.tk_root, all_tags, search_movie_callback)


def import_movies():
    """Open a csv file and load the contents into the database."""
    csv_fn = guiwidgets.gui_askopenfilename(parent=config.app.tk_root,
                                            filetypes=(('Movie import files', '*.csv'),))
    try:
        impexp.import_movies(csv_fn)
    except impexp.MoviedbInvalidImportData as exc:
        guiwidgets.gui_messagebox(config.app.tk_root, message='Errors were found in the input file.',
                                  detail=exc.args[0], icon='warning')


def add_movie_callback(movie: config.MovieDict, selected_tags: Sequence[str]):
    """ Add user supplied data to the database.

    Args:
        movie:
        selected_tags:
    """
    database.add_movie(movie)
    movie = config.MovieKeyDict(title=movie['title'], year=movie['year'])
    for tag in selected_tags:
        database.add_movie_tag_link(tag, movie)


def search_movie_callback(criteria: config.FindMovieDict, tags: Sequence[str]):
    # Find compliant movies.
    criteria['tags'] = tags
    # Remove empty items because SQL treats them as meaningful.
    criteria = {k: v
                for k, v in criteria.items()
                if v != '' and v != [] and v != () and v != ['', '']}
    movies = database.find_movies(criteria)

    if (movies_found := len(movies)) <= 0:
        raise exception.MovieSearchFoundNothing
    elif movies_found == 1:
        _instantiate_edit_movie_gui(movies[0])
    else:
        guiwidgets.SelectMovieGUI(config.app.tk_root, movies, select_movie_callback)


def edit_movie_callback(updates: config.MovieUpdateDict, selected_tags: Sequence[str]):
    """ Add user supplied data to the database.

    Args:
        updates: Fields modified by the user or not.
        selected_tags: Tags selected by the user or previously selected for this record. Tags
            deselected by the user are not included.
    """
    # Edit the movie
    movie = config.FindMovieDict(title=updates['title'], year=[updates['year']])
    
    # moviedb-#109
    #   The movie might have been deleted from the database
    #   So trap any 'not found' errors.
    #   Display helpful message.
    database.edit_movie(movie, updates)
    
    # Edit links
    movie = config.MovieKeyDict(title=updates['title'], year=updates['year'])
    old_tags = database.movie_tags(movie)
    database.edit_movies_tag(movie, old_tags, selected_tags)


def select_movie_callback(title: str, year: int):
    # Get record from database
    movie = database.find_movies(dict(title=title, year=year))[0]
    _instantiate_edit_movie_gui(movie)


def _instantiate_edit_movie_gui(movie: config.MovieUpdateDict):
    all_tag_names = database.all_tags()
    guiwidgets.EditMovieGUI(config.app.tk_root, all_tag_names, edit_movie_callback, movie)
