"""Database update functions."""

#  Copyright© 2024. Stephen Rigden.
#  Last modified 9/9/24, 2:44 PM by stephen.
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

import logging
from pathlib import Path

from sqlalchemy import MetaData, Engine, Table, select, create_engine
from sqlalchemy.orm import Session

from globalconstants import *

DIALECT = "sqlite+pysqlite:///"
INFO_UPDATE_V0_STARTING = "The update from the v0 database is starting."
CHECK_ZERO_TAGS = "Record count mismatch on tags table."
CHECK_ZERO_MOVIE_TAG_LINKS = "Record count mismatch on movie tag links table."
CHECK_ZERO_MOVIES = "Record count mismatch on movie table."

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
    """
    match old_version:
        case "DBv0":
            return _reflect_database_v0(old_version_fn)
        case _:
            logging.error(UnrecognizedOldVersion)
            raise UnrecognizedOldVersion


class UnrecognizedOldVersion(Exception):
    """The old version number was not recognized."""


class DatabaseUpdateCheckZeroError(Exception):
    """Record counts in the old database are compared with the counts after
    processing."""


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
        2) The database named 'movie_database.sqlite3' located within the 'DBv0' directory.
        ( ../Movies Data/DBv0/movie_database.sqlite3)

    Returns:
        A list of movie bags
        A list of tag texts.
    """
    logging.info(INFO_UPDATE_V0_STARTING)
    _register_engine(old_database_fn)
    return _reflect_data()


def _register_engine(old_database_fn: Path):
    """Registers an engine in this module for reflective use with the old database.

    Args:
        old_database_fn:
    """
    global engine
    engine = create_engine(f"{DIALECT}{old_database_fn}", echo=False)


def _reflect_data() -> tuple[list[MovieBag], set[str]]:
    """
    Collect data from the old database and return a list of movie bags.

    A list of tag texts is returned. The same texts are included in the movie
    bags. Both are in the format expected by the functions of the
    database.tables module.

    Raises:
        DatabaseUpdateCheckZeroError if any of the following checks fail:
            Tag list length not equal to the number of old tag records.
            Movie tag links not equal to number of old movie_tag records.
            Movie bag list length not equal to number of old movie records.

    Returns:
        A list of movie bags.
        A set of tag texts.
    """
    with Session(engine) as session:
        old_tags, old_tags_check_count = _reflect_old_tags(session)
        old_movie_tag_links, old_movie_tag_links_count = _reflect_old_movie_tag_links(
            old_tags, session
        )
        movie_bags, movie_bags_count = _reflect_old_movie(old_movie_tag_links, session)

        # Check zero for tags
        if old_tags_check_count != len(old_tags):
            logging.error(DatabaseUpdateCheckZeroError, CHECK_ZERO_TAGS)
            raise DatabaseUpdateCheckZeroError(CHECK_ZERO_TAGS)

        # Check zero for movie tag links
        links_count = 0
        for movie_bag in movie_bags:
            movie_tag_count = len(movie_bag.get("movie_tags", set()))
            links_count += movie_tag_count
        if old_movie_tag_links_count != links_count:
            logging.error(DatabaseUpdateCheckZeroError, CHECK_ZERO_MOVIE_TAG_LINKS)
            raise DatabaseUpdateCheckZeroError(CHECK_ZERO_MOVIE_TAG_LINKS)

        # Check zero for movies
        if movie_bags_count != len(movie_bags):
            logging.error(DatabaseUpdateCheckZeroError, CHECK_ZERO_MOVIES)
            raise DatabaseUpdateCheckZeroError(CHECK_ZERO_MOVIES)

    return movie_bags, set(old_tags.values())


def _reflect_old_tags(session: Session) -> tuple[dict[int, str], int]:
    """Returns tag texts indexed by tag object id.

    Args:
        session:

    Returns
        Tag texts indexed by tag object id.
        A check count of tag objects.
    """
    metadata_obj = MetaData()
    old_tags_table = Table("tags", metadata_obj, autoload_with=engine)
    old_tags = session.execute(select(old_tags_table)).all()
    new_tags = {tag_id: tag_tag for tag_id, tag_tag in old_tags}
    return new_tags, len(old_tags)


def _reflect_old_movie_tag_links(
    tags: dict[int, str], session: Session
) -> tuple[dict[int, set[str]], int]:
    """Returns lists of tag texts indexed by Movie object id.

    Args:
        tags:
        session:

    Returns:
        Lists of tag texts indexed by Movie object id.
        A check count of movie tag objects.
    """
    metadata_obj = MetaData()
    old_movie_tags = Table("movie_tag", metadata_obj, autoload_with=engine)
    links = session.execute(select(old_movie_tags)).all()
    movie_id_keys = {movie_tag[0] for movie_tag in links}
    movie_tag_links = {movie_id: set() for movie_id in movie_id_keys}
    for movie_id, tag_id in links:
        movie_tag_links[movie_id].add(tags[tag_id])
    return movie_tag_links, len(links)


def _reflect_old_movie(
    movie_tags: dict[int, set[str]], session: Session
) -> tuple[list[MovieBag], int]:
    """Returns a list of movie_bags.

    Args:
        movie_tags: Lists of tag texts indexed by Movie object id.
        session:

    Returns:
        A list of movie bags.
        A check count of movie records.
    """
    metadata_obj = MetaData()
    old_movies_table = Table("movies", metadata_obj, autoload_with=engine)
    old_movies = session.execute(select(old_movies_table)).all()

    movie_bags = []
    for movie in old_movies:
        m_id, m_title, m_year, m_directors, m_notes = movie
        movie_bag = MovieBag(
            title=m_title,
            year=MovieInteger(m_year),
        )
        if m_directors:
            movie_bag["directors"] = m_directors
        if m_notes:
            movie_bag["notes"] = m_notes
            movie_bag["synopsis"] = m_notes
        if tags := movie_tags.get(m_id):
            movie_bag["movie_tags"] = tags
        movie_bags.append(movie_bag)

    return movie_bags, len(old_movies)
