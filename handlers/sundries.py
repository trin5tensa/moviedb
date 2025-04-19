"""Sundry Menu handlers."""

#  Copyright© 2025. Stephen Rigden.
#  Last modified 4/19/25, 11:48 AM by stephen.
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
from gui import common, settings
import tmdb

TMDB_UNREACHABLE = "TMDB database cannot be reached."
INVALID_API_KEY = "Invalid API key for TMDB."
SET_API_KEY = "Do you want to set the TMDB API key?"
VERSION = "Version"


# noinspection DuplicatedCode
class EscapeKeyDict(UserDict):
    """Support for Apple's <Escape> amd <Command-.> key presses.

    Use Case:
        Apple GUI docs state the <Escape> and <Command-.> accelerator keys
        should end the current activity.

    Application of the Apple requirements to moviedb is accomplished by calling
    the destroy method of the moviedb object. The precise nature of what
    happens when a specific destroy method is called can vary so this
    approach can accommodate any tkinter widget managed by a moviedb class.
    This excludes 'convenience' windows such as messageboxes.

    The two escape accelerators have been attached to Tk/Tcl's root with the
    bind_all function. When either accelerator is pressed the closure within
    the escape method will be called.

    # todo Isn't this what 'partials' are for?
    The complicated design of this class has been dictated by the inadequacy
    of information provided by the keypress event callback from tkinter. A
    moviedb object will be destroyed by the closure and this object is
    identified by naming the outer frame widget. This outer frame name
    can be extracted from the keypress event supplied by tkinter. This is
    used to match an entry in the 'data' attribute of this class. This
    entry should be registered when the moviedb object is initialized.
    Extensive validation is necessary to ensure that each element is in place.

    The matching is accomplished by:
    1) Uniquely naming the outer frame widget with the name of the moviedb
    class.
    2) Registering in this class the mapping of the outer frame name and its
    destroy method.
    """

    # todo Move this class to gui.sundries module.
    #  Move globalconstants.TkParentType and TkSequence to tk_facade.

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
        # todo Why is it necessary to avoid overwriting an existing value for a key?
        if outer_frame not in self:
            self.data[outer_frame] = destroy

    def escape(
        self,
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
            outer_frame_names = [  # pragma no branch
                widget_name
                for widget_name in str(keypress_event.widget).split(".")
                if widget_name and widget_name[:1] != "!"
            ]

            # Validate the Tk/Tcl name
            match len(outer_frame_names):
                case 1:
                    pass
                case 0:
                    detail = (
                        f"{self.accelerator_txt} {accelerator} {self.no_valid_name_txt}"
                    )
                    logging.warning(f"{detail} {keypress_event.widget=}")
                    common.showinfo(
                        self.internal_error_txt,
                        detail=detail,
                        icon="warning",
                    )
                    return
                case _:
                    detail = (
                        f"{self.accelerator_txt} {accelerator}"
                        f" {self.gt1_valid_name_txt}"
                    )
                    logging.warning(f"{detail} {keypress_event.widget=}")
                    common.showinfo(
                        self.internal_error_txt,
                        detail=detail,
                        icon="warning",
                    )
                    return

            # Try to call the widget's destroy method.
            outer_frame_name = outer_frame_names[0]
            try:
                self.data[outer_frame_name]()
            except KeyError:
                detail = f"{self.accelerator_txt}  {accelerator} {self.key_error_text}"
                logging.warning(f"{detail} {self.data.keys()}")
                common.showinfo(
                    self.internal_error_txt,
                    detail=detail,
                    icon="warning",
                )
            except TypeError:
                detail = (
                    f"{self.type_error_text} {self.accelerator_txt.lower()}"
                    f"  {accelerator}."
                )
                logging.warning(f"{detail} {self.data[outer_frame_name]}")
                common.showinfo(
                    self.internal_error_txt,
                    detail=detail,
                    icon="warning",
                )

        return closure


def about_dialog():
    """Display the 'about' dialog."""
    common.showinfo(
        config.persistent.program_name,
        detail=f"{VERSION} {config.persistent.program_version}",
    )


def settings_dialog():
    """Display the 'preferences' dialog."""
    try:
        display_key = config.persistent.tmdb_api_key
    except (config.ConfigTMDBAPIKeyNeedsSetting, config.ConfigTMDBDoNotUse):
        display_key = ""
    # noinspection PyArgumentList
    settings.Settings(
        config.current.tk_root,
        tmdb_api_key=display_key,
        use_tmdb=config.persistent.use_tmdb,
        save_callback=_settings_callback,
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
        The TMDB API key if it has been set and the user has not switched off TMDB.
    """
    try:
        tmdb_api_key = config.persistent.tmdb_api_key
    except config.ConfigTMDBDoNotUse:
        logging.info(f"User declined TMDB use.")
    except config.ConfigTMDBAPIKeyNeedsSetting:
        settings_dialog()
    else:
        return tmdb_api_key


def _settings_callback(tmdb_api_key: str, use_tmdb: bool):
    """
    Update the config file with the user's changes.

    Args:
        tmdb_api_key:
        use_tmdb:
    """
    config.persistent.tmdb_api_key = tmdb_api_key
    config.persistent.use_tmdb = use_tmdb


# noinspection DuplicatedCode
def _tmdb_search_exception_callback(fut: concurrent.futures.Future):
    """
    This handles exceptions encountered while running tmdb.search_tmdb and
    which need user interaction.

    Args:
        fut:
    """
    try:
        fut.result()

    except tmdb.exception.TMDBAPIKeyException as exc:
        logging.error(exc)
        if common.askyesno(  # pragma no branch
            INVALID_API_KEY,
            detail=SET_API_KEY,
        ):
            settings_dialog()

    except tmdb.exception.TMDBConnectionTimeout:
        common.showinfo(TMDB_UNREACHABLE)


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
