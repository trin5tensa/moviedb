"""Database update functions."""

#  Copyright© 2024. Stephen Rigden.
#  Last modified 8/29/24, 8:27 AM by stephen.
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

from pathlib import Path

from sqlalchemy import MetaData, Engine, create_engine
from sqlalchemy.orm import Session

from globalconstants import MovieBag

engine: Engine | None = None


def update_old_database(
    old_version: str, old_version_fn: Path
) -> tuple[list[MovieBag], set[str]]:
    """
    Calls update code dependent on the old_version.

    Args:
        old_version:
        old_version_fn:

    Raises:
        UnrecognizedOldVersion

    Returns:
        A tuple of:
            A list of MovieBags
            A set of tag texts.

    Pseudocode:
        match case old_version == DBv0:
            Call _reflect_database_v0(old_database_fn)
            Return movies, tags
        match case _: Log and raise UnrecognizedOldVersion
    """
    pass


class UnrecognizedOldVersion(Exception):
    """The old version number was not recognized."""


class DatabaseUpdateCheckZeroError(Exception):
    """Old and new record counts are unequal."""


def _reflect_database_v0(
    old_database_fn: Path,
) -> tuple[list[MovieBag], set[str]]:
    """Updates v0 database to v1.

    Version v0 is not automatically recognizable. This update will not be
    invoked unless certain external environment changes are made before running the program.
        1) The 'Movies Data' directory which holds the database files must be
        present in its expected location. This is currently in the parent of
        the source code directory (../Movies Data)
        2) A file 'schema_version.json' located within the 'Movies Data'
        directory and containing the dictionary entry {"schema_version": "v0"}.
        (../Movies Data/schema_version.json)

    The v0 database and its enclosing folder are required to be in the following locations:
        1) The database directory 'DBv0' located within the 'Movies Data' directory.
        (../Movies Data/DBv0)
        2) The database named 'movie_database.sqlite3' located within the 'DBv0' directory. (
        ../Movies
        Data/DBv0/movie_database.sqlite3)

    Returns:
        A list of movie bags
        A list of tag texts.

    Raises:
        MissingDatabaseDirectory
        MissingDatabase

    Pseudocode:
        Log the update from v0 is starting
        Call _register_engine(old_database_fn: Path)
        Call _reflect_data() -> movies, tags.
    """
    pass


def _register_engine(old_database_fn: Path):
    """Registers an engine in this module for reflective use with the old database.

    Args:
        old_database_fn:
    """
    # global engine
    # engine = create_engine(f"sqlite+pysqlite:///{old_database_fn}", echo=False)
    pass


def _reflect_data() -> tuple[list[MovieBag], set[str]]:
    """
    Collect data from the old database and return a list of movie bags.

    A list of tag texts is returned. The same texts are included in the movie bags. This
    duplication is intended to enable the use of existing update functions.

    Pseudocode:
        DO NOT delete v0 data. (Will happen when DBv1 is updated to new schema).
        With Session(old_engine) as session:
            Call _reflect_old_tags(session) ->
                dict of tags (tag key), count.
            Call _reflect_movie_tag_links(dict of tags (tag key), session) ->
                dict of tags (movie key).
            Call _reflect_movies(dict of tags (movie key), session) ->
                list of movie bags, count.
        Check lists match record counts and
            log and raise DatabaseUpdateCheckZeroError.
        Return movies and tags.
    """
    pass


def _reflect_old_tags(session: Session) -> tuple[dict[int, str], int]:
    """Returns Tag tag indexed by Tag id.

    Args:
        session:

    Returns
        Dict k: tag id  v: tag.tag
        Count of tags

    Pseudocode:
        Reflect old tags table.
        Select all tag records.
        Get length of result.all().
        Return dict and original tag count.
    """
    pass


def _reflect_old_movie_tag_links(
    tags: dict[int, str], session: Session
) -> dict[int, str]:
    """Returns Tag tag indexed by Movie id.

    Args:
        tags:
        session:

    Pseudocode:
        Reflect old movie_tag table.
        Select all movie_tag records.
        Return a dict of movie.id: tag.tag.
    """
    pass


def _reflect_old_movie(
    movie_tags: dict[int, str], session: Session
) -> tuple[list[MovieBag], int]:
    """Returns a list of movie_bags with movie_tags item.

    Args:
        movie_tags:
        session:

    Returns:
        A list of movie bags.
        A count of movie records.

    Pseudocode:
        Reflect movies table.
        Select all movie records.
        Get length of result.all().
        Loop though movies:
            Create a dictionary of movie bags keyed on movies.id.
        Loop through movie_tags:.
            Add tag text to movie bag.
        Return a list of movie_bags.values() and the count of movie records.
    """
    pass
