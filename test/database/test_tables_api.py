"""Test module."""

#  Copyright© 2024. Stephen Rigden.
#  Last modified 7/13/24, 8:53 AM by stephen.
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
from sqlalchemy import create_engine, Engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker, Session

from database_src import schema, tables

MATCH = "two"
THIRD = "three"
PREFIX = "test tag "
SOUGHT_TAG = PREFIX + MATCH
THIRD_TAG = PREFIX + THIRD
TAG_TEXTS = {
    PREFIX + "one",
    SOUGHT_TAG,
    THIRD_TAG,
}


def test_select_all_tags(load_tags):
    tag_texts = tables.select_all_tags()
    assert tag_texts == TAG_TEXTS


def test_add_tag(load_tags):
    new_tag = "test new tag"

    tables.add_tag(tag_text=new_tag)

    tags = tables.select_all_tags()
    assert tags & {new_tag} == {new_tag}


def test_add_tags(load_tags):
    new_tag = "test new tag"
    tables.add_tags(tag_texts=[new_tag])

    tags = tables.select_all_tags()
    assert tags & {new_tag} == {new_tag}


def test_add_duplicate_tag_text_raises_exception(load_tags):
    new_tag = "test new tag"
    tables.add_tag(tag_text=new_tag)

    with pytest.raises(
        IntegrityError,
        match="UNIQUE constraint failed: tag.text",
    ):
        tables.add_tag(tag_text=new_tag)


def test_edit_tag(load_tags):
    old_tag_text = SOUGHT_TAG
    new_tag_text = "test new tag"

    tables.edit_tag(old_tag_text=old_tag_text, new_tag_text=new_tag_text)

    tags_remaining = tables.select_all_tags()
    check.equal(tags_remaining & {SOUGHT_TAG}, set())
    check.equal(tags_remaining & {new_tag_text}, {new_tag_text})


def test_edit_duplicate_tag_text_raises_exception(load_tags):
    old_tag_text = SOUGHT_TAG
    # Already present in another Tag object.
    new_tag_text = THIRD_TAG

    with pytest.raises(
        IntegrityError,
        match="UNIQUE constraint failed: tag.text",
    ):
        tables.edit_tag(old_tag_text=old_tag_text, new_tag_text=new_tag_text)


def test_delete_tag(load_tags):
    tables.delete_tag(tag_text=SOUGHT_TAG)

    tags_remaining = tables.select_all_tags()
    assert tags_remaining & set(SOUGHT_TAG) == set()


def test_delete_missing_tag_suppresses_exception(load_tags):
    tables.delete_tag(tag_text=SOUGHT_TAG)
    tables.delete_tag(tag_text=SOUGHT_TAG)


@pytest.fixture(scope="function")
def session_engine():
    """Yields an engine."""
    engine: Engine = create_engine("sqlite+pysqlite:///:memory:")
    schema.Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture(scope="function")
def session_factory(session_engine: Engine) -> sessionmaker[Session]:
    """Returns a session factory.

    Args:
        session_engine:

    Returns:
        A session factory
    """
    tables.session_factory = sessionmaker(session_engine)
    return tables.session_factory


@pytest.fixture(scope="function")
def load_tags(session_factory):
    """Add TAG_TEXTS to the database.

    Args:
        session_factory:
    """
    with session_factory() as session:
        session.add_all([schema.Tag(text=text) for text in TAG_TEXTS])
        session.commit()
