"""Test module."""

#  Copyright© 2024. Stephen Rigden.
#  Last modified 9/3/24, 11:51 AM by stephen.
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

import pytest
from pytest_check import check
from sqlalchemy import (
    create_engine,
    Engine,
    Table,
    MetaData,
    Column,
    Integer,
    String,
    insert,
    select,
)
from sqlalchemy.orm import Session

from database_src import update
from globalconstants import MovieInteger, MovieBag


def test__reflect_old_tags(create_test_database, db_session):
    tag_table, _, _ = create_test_database
    expected_tags = _get_old_tags(tag_table, db_session)

    tags, check_count = update._reflect_old_tags(db_session)

    check.equal(tags, expected_tags)
    check.equal(check_count, len(expected_tags))


def test__reflect_old_movie_tag_links(create_test_database, db_session):
    tag_table, movie_tag_table, _ = create_test_database
    old_tags = _get_old_tags(tag_table, db_session)
    expected_links, old_movie_links = _get_old_movie_tag_links(
        old_tags, movie_tag_table, db_session
    )

    expanded_links, check_count = update._reflect_old_movie_tag_links(
        old_tags, db_session
    )

    check.equal(expanded_links, expected_links)
    check.equal(check_count, len(old_movie_links))


def test__reflect_old_movie(create_test_database, db_session):
    tag_table, movie_tag_table, movies_table = create_test_database
    old_tags = _get_old_tags(tag_table, db_session)
    tag_links, old_movie_links = _get_old_movie_tag_links(
        old_tags, movie_tag_table, db_session
    )
    expected_bags, expected_count = _get_old_movies(movies_table, tag_links, db_session)

    movie_bags, check_count = update._reflect_old_movie(tag_links, db_session)

    check.equal(movie_bags, expected_bags)
    check.equal(check_count, expected_count)


def _get_old_tags(tag_table: Table, db_session) -> dict[int, str]:
    statement = select(tag_table)
    result = db_session.execute(statement).all()
    return {tag_id: tag_text for tag_id, tag_text in result}


def _get_old_movie_tag_links(
    old_tags: dict[int, str], movie_tag_table: Table, db_session
) -> tuple[dict[int, set[str]], list[tuple[int, int]]]:
    statement = select(movie_tag_table)
    old_movie_links = db_session.execute(statement).all()

    # Integrate tags into tag links
    movie_id_keys = {movie_tag[0] for movie_tag in old_movie_links}
    expected_links = {movie_id: set() for movie_id in movie_id_keys}
    for movie_id, tag_id in old_movie_links:
        expected_links[movie_id].add(old_tags[tag_id])

    return expected_links, old_movie_links


def _get_old_movies(
    movies_table: Table, tag_links: dict[int, set[str]], db_session
) -> tuple[list[MovieBag], int]:
    statement = select(movies_table)
    old_movies = db_session.execute(statement).all()

    expected_bags = []
    for movie in old_movies:
        m_id, m_title, m_year, m_directors, m_notes = movie
        movie_bag = update.MovieBag(
            title=m_title,
            year=MovieInteger(m_year),
        )
        if m_directors:
            movie_bag["directors"] = m_directors
        if m_notes:
            movie_bag["notes"] = m_notes
            movie_bag["synopsis"] = m_notes
        if tags := tag_links.get(m_id):
            movie_bag["movie_tags"] = tags

        expected_bags.append(movie_bag)

    return expected_bags, len(old_movies)


@pytest.fixture(scope="module")
def session_engine():
    """Yields an engine."""
    update.engine = create_engine("sqlite+pysqlite:///:memory:")
    yield update.engine


@pytest.fixture(scope="module")
def db_session(session_engine: Engine):
    """Yields a database connection.

    Args:
        session_engine:
    """
    with Session(session_engine) as session:
        # with Session(update.engine) as session:
        yield session
        session.rollback()
        session.close()


@pytest.fixture(scope="module")
def create_test_database(session_engine: Engine):
    """Creates a test database."""
    metadata_obj = MetaData()

    # Create tables
    tag_table = Table(
        "tags",
        metadata_obj,
        Column("id", Integer, primary_key=True),
        Column("tag", String),
    )
    movies_table = Table(
        "movies",
        metadata_obj,
        Column("id", Integer, primary_key=True),
        Column("title", String),
        Column("year", Integer),
        Column("director", String),
        Column("notes", String),
    )
    movie_tag_table = Table(
        "movie_tag",
        metadata_obj,
        Column("movies_id", Integer),
        Column("tag_id", Integer),
    )

    # Emit tables
    metadata_obj.create_all(session_engine)

    # Insert data
    with Session(session_engine) as session:
        statement = insert(tag_table).values(tag="Tag 1")
        session.execute(statement)
        statement = insert(tag_table).values(tag="Tag 2")
        session.execute(statement)
        statement = insert(tag_table).values(tag="Tag 3")
        session.execute(statement)

        statement = insert(movies_table).values(title="Movie 1", year="4241")
        session.execute(statement)
        statement = insert(movies_table).values(
            title="Movie 2",
            year="4242",
            director="Derek Director, Edgar Ethelbert",
            notes="notes or synopsis",
        )
        session.execute(statement)
        statement = insert(movies_table).values(title="Movie 3", year="4243")
        session.execute(statement)

        statement = insert(movie_tag_table).values(movies_id=1, tag_id=3)
        session.execute(statement)
        statement = insert(movie_tag_table).values(movies_id=2, tag_id=1)
        session.execute(statement)
        statement = insert(movie_tag_table).values(movies_id=2, tag_id=2)
        session.execute(statement)
        statement = insert(movie_tag_table).values(movies_id=2, tag_id=3)
        session.execute(statement)

        # todo delete the following print suite
        statement = select(tag_table)
        result = session.execute(statement).all()
        print(f"f {result=}")
        statement = select(movies_table)
        result = session.execute(statement).all()
        print(f"f {result=}")
        statement = select(movie_tag_table)
        result = session.execute(statement).all()
        print(f"f {result=}")

        session.commit()

    return tag_table, movie_tag_table, movies_table
