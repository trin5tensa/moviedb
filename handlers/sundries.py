"""Sundry Menu handlers."""

#  Copyright© 2025. Stephen Rigden.
#  Last modified 5/16/25, 1:30 PM by stephen.
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
from typing import Optional

import config
import tmdb
from gui import common, settings

TMDB_UNREACHABLE = "TMDB database cannot be reached."
INVALID_API_KEY = "Invalid API key for TMDB."
SET_API_KEY = "Do you want to set the TMDB API key?"
VERSION = "Version"


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
        common.tk_root,
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
        return None
    except config.ConfigTMDBAPIKeyNeedsSetting:
        settings_dialog()
        return None

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
