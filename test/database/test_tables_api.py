"""Test module."""

#  Copyright© 2024. Stephen Rigden.
#  Last modified 7/11/24, 2:40 PM by stephen.
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
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session

from database_src import schema, tables

MATCH = "two"
PREFIX = "test tag "
SOUGHT_TAG = PREFIX + MATCH
TAG_TEXTS = {
    PREFIX + "one",
    PREFIX + MATCH,
    PREFIX + "three",
}


def test_select_all_tags(load_tags):
    tag_texts = tables.select_all_tags()
    assert tag_texts == TAG_TEXTS


@pytest.fixture(scope="session")
def session_engine():
    """Yields an engine."""
    engine: Engine = create_engine("sqlite+pysqlite:///:memory:")
    schema.Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture(scope="session")
def session_factory(session_engine: Engine) -> sessionmaker[Session]:
    """Returns a session factory.

    Args:
        session_engine:

    Returns:
        A session factory
    """
    tables.session_factory = sessionmaker(session_engine)
    return tables.session_factory


@pytest.fixture(scope="session")
def load_tags(session_factory):
    """Add TAG_TEXTS to the database.

    Args:
        session_factory:
    """
    with session_factory() as session:
        session.add_all([schema.Tag(text=text) for text in TAG_TEXTS])
        session.commit()
