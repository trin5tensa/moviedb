"""Database table functions."""

#  Copyright© 2024. Stephen Rigden.
#  Last modified 7/23/24, 3:51 AM by stephen.
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
import logging

from sqlalchemy import select, intersect
from sqlalchemy.exc import NoResultFound, IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from database_src import schema
from globalconstants import *

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


def _select_movie(session: Session, *, title: str, year: int) -> schema.Movie:
    """Selects a single movie.

    Args:
        session:
        title:
        year:

    Returns:
        A movie.
    """
    statement = (
        select(schema.Movie)
        .where(schema.Movie.title == title)
        .where(schema.Movie.year == year)
    )
    return session.scalars(statement).one()


def _match_movies(session: Session, *, match: MovieBag) -> set[schema.Movie] | None:
    """Selects matching movies.

    Args:
        session:
        match: A MovieBag object containing any items to be used as search criteria.

    Returns:
        Matching movies.
        Returns None if match argument is an empty dict.
    """
    statements = []
    for column, criteria in match.items():
        match column:
            case "id":
                statements.append(
                    select(schema.Movie.id).where(schema.Movie.id == criteria)
                )
            case "notes":
                statements.append(
                    select(schema.Movie.id).where(
                        schema.Movie.notes.like(f"%{criteria}%")
                    )
                )
            case "title":
                statements.append(
                    select(schema.Movie.id).where(
                        schema.Movie.title.like(f"%{criteria}%")
                    )
                )
            case "year":
                statements.append(
                    select(schema.Movie.id).where(schema.Movie.year.in_(list(criteria)))
                )
            case "duration":
                statements.append(
                    select(schema.Movie.id).where(
                        schema.Movie.duration.in_(list(criteria))
                    )
                )
            case "synopsis":
                statements.append(
                    select(schema.Movie.id).where(
                        schema.Movie.synopsis.like(f"%{criteria}%")
                    )
                )
            case "stars":
                for star in criteria:
                    statements.append(
                        (
                            select(schema.Movie.id)
                            .select_from(schema.Movie)
                            .join(schema.Movie.stars)
                            .where(schema.Person.name.like(f"%{star}%"))
                        )
                    )
            case "directors":
                for director in criteria:
                    statements.append(
                        (
                            select(schema.Movie.id)
                            .select_from(schema.Movie)
                            .join(schema.Movie.directors)
                            .where(schema.Person.name.like(f"%{director}%"))
                        )
                    )
            case "movie_tags":
                for movie_tag in criteria:
                    statements.append(
                        (
                            select(schema.Movie.id)
                            .select_from(schema.Movie)
                            .join(schema.Movie.tags)
                            .where(schema.Tag.text.like(f"%{movie_tag}%"))
                        )
                    )

    if statements:
        # DayBreak
        #   1 Read manual on intersect
        #           Common Table Expression
        #   2 SO/SQLALcforum
        #       Why does intersect(*statements) only return ids
        statement = intersect(*statements)
        ids = session.scalars(statement).all()
        statement = select(schema.Movie).where(schema.Movie.id.in_(ids))
        matches = session.scalars(statement).all()
        return set(matches)


def _select_all_movies(session: Session) -> Sequence[schema.Movie]:
    """Selects all movies.

    Args:
        session:

    Returns:
        All movies.
    """
    statement = select(schema.Movie)
    return session.scalars(statement).all()


def _translate_to_moviebag(session: Session, movie: schema.Movie) -> MovieBag:
    # Todo: Suspended until #391 and #392 have been completed.
    # Ensures that id and datestamps are populated.
    session.add(movie)
    session.flush()

    movie_bag = MovieBag(
        title=movie.title,
        year=MovieInteger(movie.year),
        duration=MovieInteger(movie.duration),
        directors={person.name for person in movie.directors},
        stars={person.name for person in movie.stars},
        synopsis=movie.synopsis,
        notes=movie.notes,
        movie_tags={tag.text for tag in movie.tags},
        id=movie.id,
        created=movie.created,
        updated=movie.updated,
    )

    return movie_bag


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
