"""Menu handlers.

This module is the glue between the user's selection of a menu item and the gui."""

#  Copyright© 2020. Stephen Rigden.
#  Last modified 4/13/20, 6:51 AM by stephen.
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
    
    # Exit if the user clicked askopenfilename's cancel button
    if csv_fn == '':
        return
    
    try:
        impexp.import_movies(csv_fn)
    except impexp.MoviedbInvalidImportData as exc:
        guiwidgets.gui_messagebox(config.app.tk_root, message='Errors were found in the input file.',
                                  detail=exc.args[0], icon='warning')


def add_movie_callback(movie: config.MovieDef, selected_tags: Sequence[str]):
    """ Add user supplied data to the database.

    Args:
        movie:
        selected_tags:
    """
    
    database.add_movie(movie)
    movie = config.MovieKeyDef(title=movie['title'], year=movie['year'])
    for tag in selected_tags:
        database.add_movie_tag_link(tag, movie)


def search_movie_callback(criteria: config.FindMovieDef, tags: Sequence[str]):
    """Find movies which match the user entered criteria.
    Continue to the next appropriate stage of processing depending on whether no movies, one movie,
    or more than one movie is found.
    
    Args:
        criteria:
        tags:
    """
    
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
        movie = movies[0]
        guiwidgets.EditMovieGUI(config.app.tk_root, database.all_tags(), edit_movie_callback, movie)
    else:
        guiwidgets.SelectMovieGUI(config.app.tk_root, movies, select_movie_callback)


def edit_movie_callback(updates: config.MovieUpdateDef, selected_tags: Sequence[str]):
    """ Change movie and links in database in accordance with new user supplied data,

    Args:
        updates: Fields modified by the user or not.
        selected_tags: Tags selected by the user or previously selected for this record. Tags
            deselected by the user are not included.
    """
    # Edit the movie
    movie = config.FindMovieDef(title=updates['title'], year=[updates['year']])
    missing_movie_args = (config.app.tk_root, 'Missing movie',
                          f'The movie {movie} is not available. It may have been '
                          f'deleted by another process.')
    
    try:
        database.edit_movie(movie, updates)
    except exception.MovieSearchFoundNothing:
        guiwidgets.gui_messagebox(*missing_movie_args)
        return
    
    # Edit links
    movie = config.MovieKeyDef(title=updates['title'], year=updates['year'])
    old_tags = database.movie_tags(movie)
    try:
        database.edit_movies_tag(movie, old_tags, selected_tags)
    except exception.MovieSearchFoundNothing:
        guiwidgets.gui_messagebox(*missing_movie_args)


def select_movie_callback(title: str, year: int):
    """Edit a movie selected by the user from a list of movies.
    
    Args:
        title:
        year:
    """
    # Get record from database
    movie = database.find_movies(dict(title=title, year=year))[0]
    guiwidgets.EditMovieGUI(config.app.tk_root, database.all_tags(), edit_movie_callback, movie)
