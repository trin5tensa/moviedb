"""Database table functions."""

#  Copyright© 2024. Stephen Rigden.
#  Last modified 7/20/24, 1:31 PM by stephen.
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

from collections.abc import Sequence

from sqlalchemy import select, intersect
from sqlalchemy.exc import NoResultFound, IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from database_src import schema
import logging

session_factory: sessionmaker[Session] | None = None


def select_all_tags() -> set[str]:
    """Returns a list of all tags.

    Returns:
        A list of all tags.
    """
    with session_factory() as session:
        tags = _select_all_tags(session)
    return {tag.text for tag in tags}


def add_tag(*, tag_text: str):
    """Add a tag.

    Args:
        tag_text:
    Raises:
        Exceptions are logged.
        IntegrityError if the tag text is a duplicate.
    """
    try:
        with session_factory() as session, session.begin():
            _add_tag(session, tag_text=tag_text)
    except IntegrityError as exc:
        logging.error(exc.args[0])
        raise


def add_tags(*, tag_texts: list[str]):
    """Add a list of tags.

    Args:
        tag_texts:
    Raises:
        Exceptions are logged.
        IntegrityError if any tag text is a duplicate.
    """
    try:
        with session_factory() as session, session.begin():
            _add_tags(session, tag_texts=tag_texts)
    except IntegrityError as exc:
        logging.error(exc.args[0])
        raise


def edit_tag(*, old_tag_text: str, new_tag_text: str):
    """

    Args:
        old_tag_text:
        new_tag_text:
    Raises:
        Exceptions are logged.
        NoRecordFound if the old tag text cannot be found.
        IntegrityError if the new tag text is a duplicate.
    """
    try:
        with session_factory() as session, session.begin():
            try:
                tag = _match_tag(session, match=old_tag_text)
            except NoResultFound as exc:
                logging.error(exc.args[0])
                raise
            else:
                _edit_tag(tag=tag, replacement_text=new_tag_text)
    except IntegrityError as exc:
        logging.error(exc.args[0])
        raise


def delete_tag(*, tag_text: str):
    """Delete a tag.

    The exception NoResultFound is ignored if record is not present.

    Args:
        tag_text:
    """
    with session_factory() as session, session.begin():
        try:
            tag = _match_tag(session, match=tag_text)
        except NoResultFound:
            pass
        else:
            _delete_tag(session, tag=tag)


def _select_person(session: Session, *, match: str) -> schema.Person:
    """Returns a single person.

    Args:
        session: The current session.
        match: Search text
    Returns:
        A person.
    """
    statement = select(schema.Person).where(schema.Person.name.like(f"%{match}%"))
    return session.scalars(statement).one()


def _match_people(session: Session, *, match: str) -> Sequence[schema.Person]:
    """Selects a single person.

    Args:
        session: The current session.
        match: Search text
    Returns:
        A person.
    """
    statement = select(schema.Person).where(schema.Person.name.like(f"%{match}%"))
    return session.scalars(statement).all()


def _add_person(session: Session, *, name: str):
    """Add a person to the Person table.

    Args:
        session:
        name: Name of person.
    """
    session.add(schema.Person(name=name))


def _delete_person(session: Session, *, person: schema.Person):
    """Deletes a tag.

    Args:
        session:
        person:
    """
    session.delete(person)


def _delete_orphans(session: Session, candidate_names: Sequence[str]):
    pass


def _match_tag(session: Session, *, match: str) -> schema.Tag:
    """Selects a single tag.

    Args:
        session: The current session.
        match: Search text
    Returns:
        A tag.
    """
    statement = select(schema.Tag).where(schema.Tag.text.like(f"%{match}%"))
    return session.scalars(statement).one()


def _select_all_tags(session: Session) -> Sequence[schema.Tag]:
    """Returns a list of every tag.

    Args:
        session:
    Returns:
        A set of tags.
    """
    statement = select(schema.Tag)
    return session.scalars(statement).all()


def _add_tag(session: Session, *, tag_text: str):
    """Adds new tags from a tag text.

    Args:
        session:
        tag_text:
    """
    session.add(schema.Tag(text=tag_text))


def _add_tags(session: Session, *, tag_texts: list[str]):
    """Adds new tags from a list of tag texts.

    Args:
        session:
        tag_texts:
    """
    session.add_all([schema.Tag(text=tag) for tag in tag_texts])


def _edit_tag(*, tag: schema.Tag, replacement_text: str):
    """

    Args:
        tag:
        replacement_text:
    """
    tag.text = replacement_text


def _delete_tag(session: Session, *, tag: schema.Tag):
    """Deletes a tag.

    Args:
        session:
        tag:
    """
    session.delete(tag)
