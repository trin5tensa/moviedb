"""Test module."""

#  Copyright© 2024. Stephen Rigden.
#  Last modified 7/9/24, 2:00 PM by stephen.
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

from pytest_check import check

#  Copyright© 2024. Stephen Rigden.
#  Last modified 7/9/24, 1:13 PM by stephen.
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

from sqlalchemy import create_engine, Engine
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import sessionmaker, Session, scoped_session

import pytest

from database_src import schema, tables

MATCH = "two"
PREFIX = "test tag "
SOUGHT_TAG = PREFIX + MATCH
TAG_TEXTS = {
    PREFIX + "one",
    PREFIX + MATCH,
    PREFIX + "three",
}


def test__select_tag(
    load_tags: None,
    db_session: Session,
    session_factory: sessionmaker[Session],
    session_engine: Engine,
):
    tag = tables._select_tag(db_session, MATCH)

    assert tag.text == SOUGHT_TAG


def test__select_all_tags(
    load_tags: None,
    db_session: Session,
    session_factory: sessionmaker[Session],
    session_engine: Engine,
):
    tags = tables._select_all_tags(db_session)
    texts = {tag.text for tag in tags}

    assert texts == TAG_TEXTS


def test__add_tags(
    db_session: Session,
    session_factory: sessionmaker[Session],
    session_engine: Engine,
):
    test_text = "test add tag"
    tables._add_tags(db_session, [test_text])

    tag = tables._select_tag(db_session, test_text)
    assert tag.text == test_text


def test__edit_tag(
    load_tags: None,
    db_session: Session,
    session_factory: sessionmaker[Session],
    session_engine: Engine,
):
    test_new_text = "test edited tag"
    tables._edit_tag(db_session, SOUGHT_TAG, test_new_text)

    tag = tables._select_tag(db_session, test_new_text)
    assert tag.text == test_new_text


def test__delete_tag(
    load_tags: None,
    db_session: Session,
    session_factory: sessionmaker[Session],
    session_engine: Engine,
):
    tables._delete_tag(db_session, SOUGHT_TAG)

    with check.raises(NoResultFound):
        tables._select_tag(db_session, SOUGHT_TAG)


@pytest.fixture(scope="function")
def load_tags(db_session: Session):
    """Add test tags to the database.

    Args:
        db_session:
    """
    db_session.add_all([schema.Tag(text=text) for text in TAG_TEXTS])


@pytest.fixture(scope="session")
def session_engine():
    """Yields an engine."""
    engine: Engine = create_engine("sqlite+pysqlite:///:memory:")
    schema.Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture(scope="session")
def session_factory(session_engine: Engine) -> sessionmaker[Session]:
    """Returns a scoped session factory.

    Args:
        session_engine:

    Returns:
        A scoped session
    """
    return sessionmaker(session_engine)


@pytest.fixture(scope="function")
def db_session(session_factory: scoped_session):
    """Yields a database connection.

    Args:
        session_factory:
    """
    session: Session = session_factory()
    yield session
    session.rollback()
    session.close()
