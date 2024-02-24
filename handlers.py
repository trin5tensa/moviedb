"""Menu handlers.

This module is the glue between the user's selection of a menu item and the gui."""
#  Copyright (c) 2022-2024. Stephen Rigden.
#  Last modified 2/24/24, 1:51 PM by stephen.
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

import concurrent.futures
import logging
import queue
from collections import UserDict
from typing import Callable, Optional, Literal

import config
import database
import exception
import guiwidgets
import guiwidgets_2
import impexp
import tmdb
from globalconstants import *


class EscapeKeyDict(UserDict):
    """Support for Apple's <Escape> amd <Command-.> key presses.

    Use Case:
        Apple GUI docs state the <Escape> and <Command-.> accelerator keys should end the current
         activity.

    Application of the Apple requirements to moviedb is accomplished by calling the destroy
    method of the moviedb object. The precise nature of what happens when a specific destroy
    method is called can vary so this approach can accommodate any tkinter widget which is
    managed by a moviedb class. This excludes 'convenience' windows such as messageboxes.

    The two escape accelerators have been attached to Tk/Tcl's root with the bind_all function.
    When either accelerator is pressed the closure within the escape method will be called.

    The complicated design of this class has been dictated by the inadequacy of information
    provided by the keypress event callback from tkinter. A moviedb object will be destroyed
    by the closure and this object is identified by naming the outer frame widget. This outer
    frame name can be extracted from the keypress event supplied by tkinter. This is used to
    match an entry in the 'data' attribute of this class. This entry should be registered when
    the moviedb object is initialized. Extensive validation is necessary to ensure that all of
    these elements are in place.

    The matching is accomplished by:
    1) Uniquely naming the outer frame widget with the name of the moviedb class.
    2) Registering in this class the mapping of the outer frame name and its destroy method.
    """

    internal_error_txt = "Internal Error"
    accelerator_txt = "Accelerator"
    no_valid_name_txt = (
        "detected but no valid name was found in the topmost Tk/Tcl window."
    )
    gt1_valid_name_txt = (
        "detected but more than one valid name was found in the topmost Tk/Tcl window."
    )
    key_error_text = "detected but not found in lookup dictionary."
    type_error_text = "Invalid callback for"

    def __setitem__(self, outer_frame: str, destroy: Callable):
        """Register a destroy method for a particular outer frame."""
        if outer_frame not in self:
            self.data[outer_frame] = destroy

    def escape(
        self,
        parent: guiwidgets_2.TkParentType,
        accelerator: Literal["<Escape>", "<Command-.>"],
    ):
        """Sets up the callback which will destroy a moviedb logical window.


        Args:
            parent: Used to call tkinter messageboxes
            accelerator: User readable text used for reporting exceptions.
        """

        def closure(keypress_event):
            """Destroys a moviedb logical window.

            Args:
                keypress_event:
            """
            outer_frame_names = [
                widget_name
                for widget_name in str(keypress_event.widget).split(".")
                if widget_name and widget_name[:1] != "!"
            ]

            # Validate the Tk/Tcl name
            match len(outer_frame_names):
                case 1:
                    pass
                case 0:
                    message = (
                        f"{self.accelerator_txt} {accelerator} {self.no_valid_name_txt}"
                    )
                    logging.warning(f"{message} {keypress_event.widget=}")
                    guiwidgets_2.gui_messagebox(
                        parent, self.internal_error_txt, message, icon="warning"
                    )
                    return
                case _:
                    message = f"{self.accelerator_txt} {accelerator} {self.gt1_valid_name_txt}"
                    logging.warning(f"{message} {keypress_event.widget=}")
                    guiwidgets_2.gui_messagebox(
                        parent, self.internal_error_txt, message, icon="warning"
                    )
                    return

            # Try to call the widget's destroy method.
            outer_frame_name = outer_frame_names[0]
            try:
                self.data[outer_frame_name]()
            except KeyError:
                message = f"{self.accelerator_txt}  {accelerator} {self.key_error_text}"
                logging.warning(f"{message} {self.data.keys()}")
                guiwidgets_2.gui_messagebox(
                    parent, self.internal_error_txt, message, icon="warning"
                )
            except TypeError:
                message = f"{self.type_error_text} {self.accelerator_txt.lower()}  {accelerator}."
                logging.warning(f"{message} {self.data[outer_frame_name]}")
                guiwidgets_2.gui_messagebox(
                    parent, self.internal_error_txt, message, icon="warning"
                )

        return closure


def about_dialog():
    """Display the 'about' dialog."""
    guiwidgets_2.gui_messagebox(
        config.current.tk_root,
        config.persistent.program_name,
        config.persistent.program_version,
    )


def settings_dialog():
    """Display the 'preferences' dialog."""
    try:
        display_key = config.persistent.tmdb_api_key
    except (config.ConfigTMDBAPIKeyNeedsSetting, config.ConfigTMDBDoNotUse):
        display_key = ""
    guiwidgets_2.PreferencesGUI(
        config.current.tk_root,
        display_key,
        config.persistent.use_tmdb,
        _settings_callback,
    )


def _get_tmdb_api_key() -> Optional[str]:
    """
    Retrieve the TMDB API key from preference storage.

    Handles:
        config.ConfigTMDBDoNotUse:
            The exception is logged and None is returned.
        config.ConfigTMDBAPIKeyNeedsSetting:
            A call to the preferences dialog is scheduled and None is returned.

    Returns:
        The TMDB API key or None if handled exceptions were encountered.
    """
    try:
        tmdb_api_key = config.persistent.tmdb_api_key
    except config.ConfigTMDBDoNotUse:
        logging.info(f"User declined TMDB use.")
    except config.ConfigTMDBAPIKeyNeedsSetting:
        settings_dialog()
    else:
        return tmdb_api_key


def add_movie():
    """Get new movie data from the user and add it to the database."""
    all_tags = database.all_tags()
    guiwidgets_2.AddMovieGUI(
        config.current.tk_root,
        _tmdb_io_handler,
        all_tags,
        add_movie_callback=_add_movie_callback,
    )


def edit_movie():
    """Get search movie data from the user and search for compliant records"""
    all_tags = database.all_tags()
    guiwidgets.SearchMovieGUI(config.current.tk_root, _search_movie_callback, all_tags)


def add_tag():
    """Add a new tag to the database."""
    guiwidgets_2.AddTagGUI(config.current.tk_root, _add_tag_callback)


# noinspection PyMissingOrEmptyDocstring
def edit_tag():
    """Get tag string pattern from the user and search for compliant records."""
    guiwidgets_2.SearchTagGUI(config.current.tk_root, _search_tag_callback)


def import_movies():
    """Open a csv file and load the contents into the database."""
    csv_fn = guiwidgets_2.gui_askopenfilename(
        parent=config.current.tk_root, filetypes=(("Movie import files", "*.csv"),)
    )

    # Exit if the user clicked askopenfilename cancel button
    if csv_fn == "":
        return

    try:
        impexp.import_movies(csv_fn)
    except impexp.MoviedbInvalidImportData as exc:
        guiwidgets.gui_messagebox(
            config.current.tk_root,
            message="Errors were found in the input file.",
            detail=exc.args[0],
            icon="warning",
        )


def _settings_callback(tmdb_api_key: str, use_tmdb: bool):
    """
    Update the config file with the user's changes.

    Args:
        tmdb_api_key:
        use_tmdb:
    """
    config.persistent.tmdb_api_key = tmdb_api_key
    config.persistent.use_tmdb = use_tmdb


# PyCharm typing bug suppressed
# noinspection PyTypedDict
def _add_movie_callback(movie: MovieTD):
    """Add user supplied data to the database.

    Args:
        movie:
    """

    selected_tags = movie[MOVIE_TAGS]
    del movie[MOVIE_TAGS]

    database.add_movie(movie)
    movie = config.MovieKeyTypedDict(title=movie["title"], year=movie["year"])
    for tag in selected_tags:
        database.add_movie_tag_link(tag, movie)


def _delete_movie_callback(movie: config.FindMovieTypedDict):
    """Delete a movie.

    Args:
        movie:
    """
    try:
        database.del_movie(movie)

    except database.NoResultFound:
        # This can happen if the movie was deleted by another process between the user retrieving
        # a record for deletion and the call to actually delete it.
        pass


def _search_movie_callback(criteria: config.FindMovieTypedDict, tags: Sequence[str]):
    """Finds movies in the database which match the user entered criteria.
    Continue to the next appropriate stage of processing depending on whether no movies, one
    movie, or more than one movie is found.

    Args:
        criteria:
        tags:
    """

    # Find compliant movies.
    criteria["tags"] = tags
    # Remove empty items because SQL treats them as meaningful.
    criteria = {
        k: v
        for k, v in criteria.items()
        if v != "" and v != [] and v != () and v != ["", ""]
    }
    movies = database.find_movies(criteria)

    if (movies_found := len(movies)) <= 0:
        raise exception.DatabaseSearchFoundNothing
    elif movies_found == 1:
        movie = movies[0]
        movie_key = config.MovieKeyTypedDict(title=movie["title"], year=movie["year"])

        guiwidgets_2.EditMovieGUI(
            config.current.tk_root,
            _tmdb_io_handler,
            database.all_tags(),
            old_movie=movie,
            edit_movie_callback=_edit_movie_callback(movie_key),
            delete_movie_callback=_delete_movie_callback,
        )

    else:
        # noinspection PyTypeChecker
        guiwidgets.SelectMovieGUI(
            config.current.tk_root, movies, _select_movie_callback
        )


def _edit_movie_callback(old_movie: config.MovieKeyTypedDict) -> Callable:
    """Create the edit movie callback

    Args:
        old_movie: The movie that is to be edited.
            The record's key values may be altered by the user. This function will delete the old
            record and add a new record.

    Returns:
        edit_movie_callback
    """

    def func(new_movie: MovieTD):
        """Change movie and links in database with new user supplied data,

        Args:
            new_movie: Fields with either original values or values modified by the user.

        Raises exception.DatabaseSearchFoundNothing
        """
        selected_tags = new_movie[MOVIE_TAGS]
        del new_movie[MOVIE_TAGS]

        # Edit the movie
        database.replace_movie(old_movie, new_movie)

        # Edit links
        old_tags = database.movie_tags(old_movie)
        new_movie = MovieTD(title=new_movie[TITLE], year=new_movie[YEAR])

        try:
            database.edit_movie_tag_links(new_movie, old_tags, selected_tags)

        # Can't add tags because new movie has been deleted.
        except exception.DatabaseSearchFoundNothing:
            missing_movie_args = (
                config.current.tk_root,
                "Missing movie",
                f"The movie {new_movie} is no longer in the database. It may have "
                f"been deleted by another process. ",
            )
            guiwidgets.gui_messagebox(*missing_movie_args)

    return func


def _select_movie_callback(movie_id: config.MovieKeyTypedDict):
    """Edit a movie selected by the user from a list of movies.

    Args:
        movie_id:
    """
    # Get one movie from the database
    criteria = config.FindMovieTypedDict(
        title=movie_id["title"], year=[str(movie_id["year"])]
    )
    movie = database.find_movies(criteria)[0]

    # Display the movie in the edit movie form.
    movie_key = config.MovieKeyTypedDict(title=movie["title"], year=movie["year"])
    guiwidgets_2.EditMovieGUI(
        config.current.tk_root,
        _tmdb_io_handler,
        database.all_tags(),
        old_movie=movie,
        edit_movie_callback=_edit_movie_callback(movie_key),
        delete_movie_callback=_delete_movie_callback,
    )


def _add_tag_callback(tag: str):
    """Add a new user supplied tag to the database.

    Args:
        tag:

    """
    database.add_tag(tag)


def _search_tag_callback(tag_pattern: str):
    """Search for tags matching a supplied substring pattern.

    Args:
        tag_pattern:

    Raises:
        DatabaseSearchFoundNothing if no matching tags are found.
    """
    tags = database.find_tags(tag_pattern)
    tags_found = len(tags)
    if tags_found <= 0:
        raise exception.DatabaseSearchFoundNothing
    elif tags_found == 1:
        tag = tags[0]
        delete_callback = _delete_tag_callback_wrapper(tag)
        edit_callback = _edit_tag_callback_wrapper(tag)
        guiwidgets_2.EditTagGUI(
            config.current.tk_root, tag, delete_callback, edit_callback
        )
    else:
        guiwidgets_2.SelectTagGUI(config.current.tk_root, _select_tag_callback, tags)


def _edit_tag_callback_wrapper(old_tag: str) -> Callable:
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

        missing_tag_args = (
            config.current.tk_root,
            "Missing tag",
            f"The tag {old_tag} is no longer available. It may have been "
            f"deleted by another process.",
        )

        try:
            database.edit_tag(old_tag, new_tag)
        except exception.DatabaseSearchFoundNothing:
            guiwidgets.gui_messagebox(*missing_tag_args)

    return edit_tag_callback


def _delete_tag_callback_wrapper(tag: str) -> Callable:
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
        try:
            database.del_tag(tag)

        # The record has already been deleted by another process:
        except exception.DatabaseSearchFoundNothing:
            pass

    return delete_tag_callback


def _select_tag_callback(old_tag: str):
    """Change the tag column of a record of the Tag table.

    If the tag is no longer in the database this function assumes that it has been deleted by
    another process. A user alert is raised.
    """
    delete_callback = _delete_tag_callback_wrapper(old_tag)
    edit_callback = _edit_tag_callback_wrapper(old_tag)
    guiwidgets_2.EditTagGUI(
        config.current.tk_root, old_tag, delete_callback, edit_callback
    )


def _tmdb_search_exception_callback(fut: concurrent.futures.Future):
    """
    This handles exceptions encountered while running tmdb.search_tmdb and which need user
    interaction.

    Args:
        fut:
    """
    try:
        fut.result()

    except exception.TMDBAPIKeyException as exc:
        logging.error(exc)
        msg = "Invalid API key for TMDB."
        detail = "Do you want to set the key?"
        if guiwidgets_2.gui_askyesno(
            config.current.tk_root, msg, detail
        ):  # pragma no branch
            settings_dialog()

    except exception.TMDBConnectionTimeout:
        msg = "TMDB database cannot be reached."
        guiwidgets_2.gui_messagebox(config.current.tk_root, msg)


def _tmdb_io_handler(search_string: str, work_queue: queue.Queue):
    """
    Runs the movie search in a thread from the pool.

    Args:
        search_string: The title search string
        work_queue: A queue where compliant movies can be placed.
    """
    if tmdb_api_key := _get_tmdb_api_key():  # pragma no branch
        executor = config.current.threadpool_executor
        fut = executor.submit(tmdb.search_tmdb, tmdb_api_key, search_string, work_queue)
        fut.add_done_callback(_tmdb_search_exception_callback)
