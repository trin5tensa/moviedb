"""Menu handlers.

This module is the glue between the user's selection of a menu item and the gui."""

#  Copyright© 2020. Stephen Rigden.
#  Last modified 6/20/20, 2:51 PM by stephen.
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

from typing import Callable, Sequence

import sqlalchemy.orm

import config
import database
import exception
import guiwidgets
import guiwidgets_2
import impexp


def about_dialog():
    """Display the about dialog."""
    guiwidgets.gui_messagebox(config.app.tk_root, config.app.name, config.app.version)


def add_movie():
    """ Get new movie data from the user and add it to the database. """
    all_tags = database.all_tags()
    # PyCharm https://youtrack.jetbrains.com/issue/PY-41268
    # noinspection PyTypeChecker
    guiwidgets.AddMovieGUI(config.app.tk_root, add_movie_callback, delete_movie_callback, ['commit'],
                           all_tags)


def edit_movie():
    """ Get search movie data from the user and search for compliant records"""
    all_tags = database.all_tags()
    guiwidgets.SearchMovieGUI(config.app.tk_root, search_movie_callback, all_tags)


def add_tag():
    """Add a new tag to the database."""
    # PyCharm https://youtrack.jetbrains.com/issue/PY-41268
    # noinspection PyTypeChecker
    guiwidgets_2.AddTagGUI(config.app.tk_root, add_tag_callback)


# noinspection PyMissingOrEmptyDocstring
def edit_tag():
    """ Get tag string pattern from the user and search for compliant records."""
    guiwidgets_2.SearchTagGUI(config.app.tk_root, search_tag_callback)


def import_movies():
    """Open a csv file and load the contents into the database."""
    csv_fn = guiwidgets_2.gui_askopenfilename(parent=config.app.tk_root,
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


def delete_movie_callback(movie: config.FindMovieDef):
    """Delete a movie.
    
    Args:
        movie:
        
    Raises:
        sqlalchemy.orm.exc.NoResultFound
            This exception is raised if the record cannot be found. This can happen if the movie was
            deleted by another process in between the user retrieving a record for deletion and the
            call to actually delete it.
            The exception is silently ignored.
    """
    try:
        database.del_movie(movie)
    
    except sqlalchemy.orm.exc.NoResultFound:
        pass


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
        raise exception.DatabaseSearchFoundNothing
    elif movies_found == 1:
        movie = movies[0]
        # PyCharm bug https://youtrack.jetbrains.com/issue/PY-41268
        # noinspection PyTypeChecker
        guiwidgets.EditMovieGUI(config.app.tk_root, edit_movie_callback, delete_movie_callback,
                                ['commit', 'delete'], database.all_tags(), movie)
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
                          f'The movie {movie} is no longer available. It may have been '
                          f'deleted by another process.')
    
    try:
        database.edit_movie(movie, updates)
    except exception.DatabaseSearchFoundNothing:
        guiwidgets.gui_messagebox(*missing_movie_args)
        return
    
    # Edit links
    movie = config.MovieKeyDef(title=updates['title'], year=updates['year'])
    old_tags = database.movie_tags(movie)
    try:
        database.edit_movies_tag(movie, old_tags, selected_tags)
    except exception.DatabaseSearchFoundNothing:
        guiwidgets.gui_messagebox(*missing_movie_args)


def select_movie_callback(title: str, year: int):
    """Edit a movie selected by the user from a list of movies.
    
    Args:
        title:
        year:
    """
    # Get record from database
    movie = database.find_movies(dict(title=title, year=year))[0]
    # PyCharm bug https://youtrack.jetbrains.com/issue/PY-41268
    # noinspection PyTypeChecker
    guiwidgets.EditMovieGUI(config.app.tk_root, edit_movie_callback, delete_movie_callback,
                            ['commit', 'delete'], database.all_tags(), movie)


def add_tag_callback(tag: str):
    """Add a new user supplied tag to the database.
    
    Args:
        tag:

    """
    database.add_tag(tag)


def search_tag_callback(tag_pattern: str):
    """Search for tags matching a supplied substring pattern.
    
    Args:
        tag_pattern:
        
    Raises:
        DatabaseSearchFoundNothing if no matching tags are found.
    """
    # moviedb-#169
    #   Check 0, 1, and many handling
    tags = database.find_tags(tag_pattern)
    tags_found = len(tags)
    if tags_found <= 0:
        raise exception.DatabaseSearchFoundNothing
    elif tags_found == 1:
        tag = tags[0]
        delete_callback = delete_tag_callback_wrapper(tag)
        edit_callback = edit_tag_callback_wrapper(tag)
        # moviedb-#193  Pass tag To EditTagGUI
        #   Test
        guiwidgets_2.EditTagGUI(config.app.tk_root, tag, delete_callback, edit_callback)
    else:
        guiwidgets_2.SelectTagGUI(config.app.tk_root, select_tag_callback, tags)


def edit_tag_callback_wrapper(old_tag: str) -> Callable:
    """Create the edit tag callback.
    
    Args:
        old_tag:

    Returns:
        The callback function edit_tag_callback.
    """
    
    def edit_tag_callback(new_tag: str):
        """Change the tag column of a record of the Tag table.
        
        If the tag is no longer in the database this function assumes that it has been deleted by
        another process. A user alert is raised.
        
        Args:
            new_tag:
        """
        # moviedb-#169
        #   Integration Tests:
        #       Edit a tag with no links to any movie records
        #       Edit a tag with a link to a single movie record. Ensure movies remain correctly linked.
        #       Edit a tag with links to more than one movie record. Ensure movies remain
        #       correctly linked.
        #       Edit a tag that has been removed from the database during the edit process.

        missing_tag_args = (config.app.tk_root, 'Missing tag',
                            f'The tag {old_tag} is no longer available. It may have been '
                            f'deleted by another process.')

        try:
            database.edit_tag(old_tag, new_tag)
        except exception.DatabaseSearchFoundNothing:
            guiwidgets.gui_messagebox(*missing_tag_args)

    return edit_tag_callback


def delete_tag_callback_wrapper(tag: str) -> Callable:
    """Create the edit tag callback.
    
    Args:
        tag:

    Returns:
        The callback function delete_tag_callback.
    """
    
    def delete_tag_callback():
        """Change the tag column of a record of the Tag table.
        
        If the tag is no longer in the database this function assumes that it has been deleted by
        another process. The database error is silently suppressed.
        """
        # moviedb-#170
        #   Integration Tests:
        #       Delete a tag with no links to any movie records
        #       Delete a tag with a link to a single movie record. Ensure movies remain correctly linked.
        #       Delete a tag with links to more than one movie record. Ensure movies remain
        #       correctly linked.
        #       Delete a tag that has been removed from the database during the edit process.
        
        try:
            database.del_tag(tag)
        
        # The record has already been deleted by another process:
        except exception.DatabaseSearchFoundNothing:
            pass
    
    return delete_tag_callback


def select_tag_callback(old_tag: str):
    """Change the tag column of a record of the Tag table.

    If the tag is no longer in the database this function assumes that it has been deleted by
    another process. A user alert is raised .
    """
    delete_callback = delete_tag_callback_wrapper(old_tag)
    edit_callback = edit_tag_callback_wrapper(old_tag)
    guiwidgets_2.EditTagGUI(config.app.tk_root, old_tag, delete_callback, edit_callback)
