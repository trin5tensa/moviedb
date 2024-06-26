"""Prototype Database

Supports the prototyping of DBv1
"""

#  Copyright ©2024. Stephen Rigden.
#  Last modified 6/26/24, 2:15 PM by stephen.
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
import os
from pathlib import Path

from sqlalchemy import create_engine, Table, MetaData, select, Engine
from sqlalchemy.orm import Session

from globalconstants import MovieBag

DATABASE_PREFIX = "DB"


class UnrecognizedOldVersion(Exception):
    """The old version number was not recognized."""


def update_old_database(
    version_of_record: str, movie_data_path: Path, old_database_fn: str
) -> tuple[int, dict[int, str], int, list[MovieBag]]:
    """..."""
    # Validate version of record.
    match version_of_record:
        case "v0":
            tag_count, new_tags, movie_count, new_movies = update_database_v0(
                version_of_record,
                movie_data_path,
                old_database_fn,
            )
        case _:
            msg = f'The old version number of "{version_of_record}" was not recognized'
            raise UnrecognizedOldVersion(msg)
    return tag_count, new_tags, movie_count, new_movies


def update_database_v0(
    version_of_record: str, movie_data_path: Path, old_database_fn: str
) -> tuple[int, dict[int, str], int, list[MovieBag]]:
    """..."""
    old_database_dir: Path = movie_data_path / f"{DATABASE_PREFIX}{version_of_record}"
    old_database_fn: Path = old_database_dir / old_database_fn
    old_engine = create_engine(f"sqlite+pysqlite:///{old_database_fn}", echo=False)
    metadata_obj = MetaData()

    with Session(old_engine) as session:
        tag_count, new_tags = get_old_tags(session, metadata_obj, old_engine)
        movie_tag_links = get_old_movie_tag_links(session, metadata_obj, old_engine)
        movie_count, new_movies = get_old_movie(
            session, metadata_obj, old_engine, new_tags, movie_tag_links
        )
        new_tags = new_tags.values()

    # Delete old database file and its directory
    os.remove(old_database_fn)
    os.rmdir(old_database_dir)

    # noinspection PyTypeChecker
    return tag_count, new_tags, movie_count, new_movies


def get_old_tags(
    session: Session, metadata_obj: MetaData, old_engine: Engine
) -> tuple[int, dict[int, str]]:
    """..."""
    old_tags = Table("tags", metadata_obj, autoload_with=old_engine)
    result = session.execute(select(old_tags))
    new_tags = {tag_id: tag_tag for tag_id, tag_tag in result.all()}
    return len(new_tags), new_tags


def get_old_movie_tag_links(
    session: Session, metadata_obj: MetaData, old_engine: Engine
) -> dict[int, list[int]]:
    """..."""
    old_movie_tags = Table("movie_tag", metadata_obj, autoload_with=old_engine)
    result = session.execute(select(old_movie_tags))
    movie_tag_links: dict[int, list[int]] = {}
    for movie_id, tag_id in result.all():
        tags = movie_tag_links.get(movie_id, [])
        tags.append(tag_id)
        movie_tag_links[movie_id] = tags
    return movie_tag_links


def get_old_movie(
    session: Session,
    metadata_obj: MetaData,
    old_engine: Engine,
    new_tags: dict[int, str],
    movie_tag_links: dict[int, list[int]],
) -> tuple[int, list[MovieBag]]:
    """..."""
    old_movies = Table("movies", metadata_obj, autoload_with=old_engine)
    result = session.execute(select(old_movies))

    new_movies = list()
    for movie in result.all():
        tags = movie_tag_links.get(movie[0], [])

        new_movie_tags = set()
        # Ignore invalid tag_id links in the movies table.
        for tag in tags:
            try:
                new_movie_tags.add(new_tags[tag])
            except KeyError:
                pass

        new_movie = MovieBag(
            id=movie[0],
            title=movie[1],
            directors={s.strip() for s in movie[2].split(",")},
            duration=movie[3],
            year=movie[4],
            # Old movies put the synopsis in the 'notes' column.
            synopsis=movie[5],
            # Retain synopsis in 'notes' as the synopsis column is not yet handled in GUI.
            notes=movie[5],
            movie_tags=new_movie_tags,
        )
        new_movies.append(new_movie)

    return len(new_movies), new_movies
