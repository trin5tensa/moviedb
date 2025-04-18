"""Database update functions."""

#  Copyright© 2025. Stephen Rigden.
#  Last modified 4/17/25, 12:59 PM by stephen.
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

from moviebag import *

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
    invoked unless certain external environment changes are made before
    running the program. See the environment.start_engine for more
    information.

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
    metadata_obj = MetaData()
    with Session(engine) as session:
        tags, old_tags_check_count = _reflect_old_tags(
            session,
            metadata_obj,
        )
        movie_tags_sets, movie_id_keys_count = _reflect_old_movie_tag_links(
            tags,
            session,
            metadata_obj,
        )
        movie_bags, movie_bags_count = _reflect_old_movie(
            movie_tags_sets,
            session,
            metadata_obj,
        )

        # Check zero for tags
        if old_tags_check_count != len(tags):
            logging.error(DatabaseUpdateCheckZeroError, CHECK_ZERO_TAGS)
            raise DatabaseUpdateCheckZeroError(CHECK_ZERO_TAGS)

        # Check zero for movie tag links
        if len(movie_tags_sets) != movie_id_keys_count:
            logging.error(DatabaseUpdateCheckZeroError, CHECK_ZERO_MOVIE_TAG_LINKS)
            raise DatabaseUpdateCheckZeroError(CHECK_ZERO_MOVIE_TAG_LINKS)

        # Check zero for movies
        if movie_bags_count != len(movie_bags):
            logging.error(DatabaseUpdateCheckZeroError, CHECK_ZERO_MOVIES)
            raise DatabaseUpdateCheckZeroError(CHECK_ZERO_MOVIES)

    return movie_bags, set(tags.values())


def _reflect_old_tags(
    session: Session,
    metadata_obj: MetaData,
) -> tuple[dict[int, str], int]:
    """Returns tag texts indexed by tag object id.

    Args:
        session:
        metadata_obj:

    Returns
        Tag texts indexed by tag object id.
        A check count of tag objects.
    """
    old_tags_table = Table("tags", metadata_obj, autoload_with=engine)
    old_tags = session.execute(select(old_tags_table)).all()
    tags = {tag_id: tag_tag for tag_id, tag_tag in old_tags}  # pragma: no branch
    return tags, len(old_tags)


def _reflect_old_movie_tag_links(
    tags: dict[int, str],
    session: Session,
    metadata_obj: MetaData,
) -> tuple[dict[int, set[str]], int]:
    """Returns sets of tag texts indexed by Movie object id.

    Args:
        tags:
        session:
        metadata_obj:

    Returns:
        Sets of tag texts indexed by Movie object id.
        A check count of movie objects.
    """
    movie_tags_table = Table("movie_tag", metadata_obj, autoload_with=engine)
    old_movie_tags = session.execute(select(movie_tags_table)).all()
    movie_id_keys = {movie_tag[0] for movie_tag in old_movie_tags}  # pragma no branch
    movie_tags_sets = {movie_id: set() for movie_id in movie_id_keys}  # pragma nocover
    for movie_id, tag_id in old_movie_tags:
        try:
            tag = tags[tag_id]
        except KeyError:  # pragma nocover
            # The tag_id points to a nonexistent tag.
            pass
        else:
            movie_tags_sets[movie_id].add(tag)
    return movie_tags_sets, len(movie_id_keys)


def _reflect_old_movie(
    movie_tags: dict[int, set[str]],
    session: Session,
    metadata_obj: MetaData,
) -> tuple[list[MovieBag], int]:
    """Returns a list of movie_bags.

    Args:
        movie_tags: Lists of tag texts indexed by Movie object id.
        session:
        metadata_obj:

    Returns:
        A list of movie bags.
        A check count of movie records.
    """
    old_movies_table = Table("movies", metadata_obj, autoload_with=engine)
    old_movies = session.execute(select(old_movies_table)).all()

    movie_bags = []
    for movie in old_movies:

        new_movie = MovieBag(  # pragma no branch
            id=movie[0],
            title=movie[1],
            directors={s.strip() for s in movie[2].split(",")},
            duration=movie[3],
            year=movie[4],
            # Old movies put the synopsis in the 'notes' column.
            synopsis=movie[5],
            # Retain synopsis in 'notes' as the synopsis column is not yet handled in GUI.
            notes=movie[5],
        )

        # movie_tags = movie_tags[movie[0]]
        try:
            new_movie["movie_tags"] = movie_tags[movie[0]]
        except KeyError:
            pass

        movie_bags.append(new_movie)
    return movie_bags, len(old_movies)
