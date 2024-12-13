"""Menu handlers.

This module is the glue between the user's selection of a menu item and the gui."""

#  Copyright© 2024. Stephen Rigden.
#  Last modified 12/13/24, 8:41 AM by stephen.
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
from config import MovieKeyTypedDict
from database_src import tables
from globalconstants import MovieTD, MovieBag, MovieInteger
from gui_handlers import moviebagfacade
from gui_handlers.handlers import _tmdb_io_handler, _select_tag_callback


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

    The optional movie_bag argument can be used to prepopulate the movie
    form. This is useful if the initial attempt to add a movie caused an
    exception. It gives the user the opportunity to fix input errors.

    Args:
        movie_bag
    """
    all_tags = tables.select_all_tags()
    guiwidgets_2.AddMovieGUI(
        config.current.tk_root,
        _tmdb_io_handler,
        list(all_tags),
        prepopulate_bag=movie_bag,
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
            _exc_messagebox(exc)
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
            # todo Raise issue to re-populate the search form with the
            #  faulty data. (SearchMovieGUI will be rewritten as part of a
            #  future GUI module update)
            search_for_movie()
        case 1:
            # Presents an Edit/View/Delete window to user
            movie_bag = movies_found[0]
            movie = moviebagfacade.convert_to_movie_update_def(movie_bag)

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
                config.current.tk_root, movies, select_movie_callback
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
        'edit movie' input screen populated with her previously entered data.

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
                _exc_messagebox(exc)
                _edit_movie(old_movie, prepopulate_bag=new_movie_bag)
            else:  # pragma nocover
                raise

    return func


def delete_movie_callback(movie: config.FindMovieTypedDict):
    """This callback function will delete a movie from the database.

    If the movie cannot be found then no action is taken.

    Args:
        movie: Specified by title and key.
    """
    movie_bag = MovieBag(
        title=movie["title"],
        year=MovieInteger(int(movie["year"][0])),
    )
    tables.delete_movie(movie_bag=movie_bag)


def select_movie_callback(movie: MovieKeyTypedDict):
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
        _edit_movie(old_movie, prepopulate_bag=movie_bag)


def add_tag():
    """Adds a new tag to the database."""
    guiwidgets_2.AddTagGUI(
        config.current.tk_root,
        add_tag_callback=add_tag_callback,
    )


def edit_tag():
    """Searches for tags with a user's match pattern."""
    guiwidgets_2.SearchTagGUI(
        config.current.tk_root,
        search_tag_callback=search_tag_callback,
    )


def add_tag_callback(tag_text: str):
    """Calls the database to add a new tag.

    Args:
        tag_text:
    """
    tables.add_tag(tag_text=tag_text)


def search_tag_callback(match: str):
    """Gets matching tag texts from the database.

    If no tags match the user is alerted and the tag editing process will
    be restarted. If a single match is found the 'edit tag' screen will
    be presented. If multiple tags match, a selectable list of the matches
    will be displayed.

    Args:
        match:
    """
    tags = tables.match_tags(match=match)

    if len(tags) == 0:
        guiwidgets_2.gui_messagebox(
            config.current.tk_root, message=tables.TAG_NOT_FOUND
        )
        edit_tag()

    elif len(tags) == 1:
        tag = tags.pop()
        delete_callback = delete_tag_callback(tag)
        edit_callback = edit_tag_callback(tag)
        guiwidgets_2.EditTagGUI(
            config.current.tk_root,
            delete_tag_callback=delete_callback,
            edit_tag_callback=edit_callback,
            tag=tag,
        )

    else:
        guiwidgets_2.SelectTagGUI(
            config.current.tk_root,
            select_tag_callback=_select_tag_callback,
            tags_to_show=list(tags),
        )


def delete_tag_callback(tag_text: str) -> Callable:
    """Creates a callback to delete a tag.

    Args:
        tag_text:

    Returns:
        The callback function.
    """

    def func():
        """Deletes a tag."""
        tables.delete_tag(tag_text=tag_text)

    return func


def edit_tag_callback(old_tag_text: str) -> Callable:
    """Creates a callback for editing a tag.

    Args:
        old_tag_text:

    Returns:
        The callback function.
    """

    def func(new_tag_text: str):
        """Changes a tag text from old_tag_text to new_tag_text.

        The user will be alerted if the old tag text cannot be found, and
        the edit_tag process will be restarted. The user will also be alerted
        if the new tag text duplicates an existing tag, but no other
        action will be taken.

        Args:
            new_tag_text:
        """
        try:
            tables.edit_tag(old_tag_text=old_tag_text, new_tag_text=new_tag_text)

        except tables.NoResultFound as exc:
            _exc_messagebox(exc)
            edit_tag()

        except tables.IntegrityError as exc:
            _exc_messagebox(exc)

    return func


def _edit_movie(
    old_movie: config.MovieKeyTypedDict, *, prepopulate_bag: MovieBag = None
):
    """A helper function which calls edit movie GUI.

    Args:
        old_movie:
        prepopulate_bag:

    Use Case:
        This supports exception cases handled by the edit_movie_callback.
        They need to redisplay the user edit which caused the exceptions.
    """
    guiwidgets_2.EditMovieGUI(
        config.current.tk_root,
        _tmdb_io_handler,
        list(tables.select_all_tags()),
        old_movie=config.MovieUpdateDef(**old_movie),
        prepopulate_bag=prepopulate_bag,
        edit_movie_callback=edit_movie_callback(old_movie),
        delete_movie_callback=delete_movie_callback,
    )


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
