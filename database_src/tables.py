"""Database table functions."""

#  Copyright© 2024. Stephen Rigden.
#  Last modified 8/3/24, 6:09 AM by stephen.
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

from sqlalchemy import select, intersect
from sqlalchemy.exc import NoResultFound, IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from database_src import schema
from globalconstants import *

session_factory: sessionmaker[Session] | None = None


def select_movie(*, movie_bag: MovieBag) -> MovieBag:
    """Selects and returns a single movie.

    Args:
        A movie_bag containing the title and year of the movie.

    Returns:
        A movie
    """
    with session_factory() as session:
        movie = _select_movie(
            session, title=movie_bag["title"], year=int(movie_bag["year"])
        )
        return _convert_to_movie_bag(movie)


def select_all_movies() -> list[MovieBag]:
    """Selects and returns all movies."""
    with session_factory() as session:
        movies = _select_all_movies(session)
        movie_bags = [_convert_to_movie_bag(movie) for movie in movies]
    return movie_bags


def match_movies(match: MovieBag) -> list[MovieBag]:
    """Selects and returns matching movies.

    Match patterns are specified in a MovieBag object which can contain none, any,
    or all the fields of a MovieBag object. Each supplied field will be used to
    select compliant records.This function will return the intersection of the
    movie records selected by each field's match criteria. The internal
    database fields of 'id'. 'created', and 'updated' are ignored.

    Args:
        match:

        Match patterns are specified in a MovieBag object which can contain none,
        any, or all the following fields:
            title. Substring match
            year. Contains match
            duration. Contains match
            directors. Substring set match
            stars. Substring set match
            synopsis. Substring match
            notes. Substring match
            movie_tags. Substring set match

        Exact match. 4 will match movie.id = 4
        Substring match. The substring 'kwai' will match 'Bridge on the River Kwai'.
        Substring set match. Each item in the set will be matched as a substring
            match (defined above). The movie will only be selected if every item in
            the set matches.
            For a movie with stars {"Edgar Ethelred", "Fanny Fullworthy"}:
                {'ethel'} will match
                {'ethel', 'worth'} will match
                {'ethel', 'bogart'} will not match.
        Contains match. A movie.year of `1955 in MovieInteger('1950-1960')` is a match.
        Ignored. Will not be used for search.

    Returns:
        The intersection of the records selected by each field's search criteria.
    """
    with session_factory() as session:
        movies = _match_movies(session, match=match)
        movie_bags = [_convert_to_movie_bag(movie) for movie in movies]
    return movie_bags


def select_all_tags() -> set[str]:
    """Returns a list of all tag texts."""
    with session_factory() as session:
        tags = _select_all_tags(session)
    return {tag.text for tag in tags}


def add_tag(*, tag_text: str):
    """Add a tag.

    Args:
        tag_text:
    Raises:
        IntegrityError if the tag text is a duplicate.
    """
    try:
        with session_factory() as session, session.begin():
            _add_tag(session, tag_text=tag_text)
    except IntegrityError as exc:
        logging.error(exc.args[0])
        raise


def add_tags(*, tag_texts: set[str]):
    """Add a list of tags.

    Args:
        tag_texts:
    Raises:
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

    The exception NoResultFound is ignored if the record is not present.

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


def _convert_to_movie_bag(movie: schema.Movie) -> MovieBag:
    """Converts a Movie object into a movie_bag.

    Args:
        movie:

    Returns:
        A movie bag.
    """
    movie_bag = MovieBag(
        id=movie.id,
        created=movie.created,
        updated=movie.updated,
        title=movie.title,
        year=MovieInteger(movie.year),
    )

    if movie.notes:
        movie_bag["notes"] = movie.notes
    if movie.duration:
        movie_bag["duration"] = MovieInteger(movie.duration)
    if movie.synopsis:
        movie_bag["synopsis"] = movie.synopsis
    if movie.stars:
        movie_bag["stars"] = {person.name for person in movie.stars}
    if movie.directors:
        movie_bag["directors"] = {person.name for person in movie.directors}
    if movie.tags:
        movie_bag["movie_tags"] = {tag.text for tag in movie.tags}

    return movie_bag


def _select_movie(session: Session, *, title: str, year: int) -> schema.Movie:
    """Selects and returns a single movie.

    Args:
        session:
        title:
        year:

    Returns:
        A movie.
    """
    # noinspection PyTypeChecker
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
            case "notes":
                statements.append(
                    select(schema.Movie).where(schema.Movie.notes.like(f"%{criteria}%"))
                )
            case "title":
                statements.append(
                    select(schema.Movie).where(schema.Movie.title.like(f"%{criteria}%"))
                )
            case "year":
                statements.append(
                    select(schema.Movie).where(schema.Movie.year.in_(list(criteria)))
                )
            case "duration":
                statements.append(
                    select(schema.Movie).where(
                        schema.Movie.duration.in_(list(criteria))
                    )
                )
            case "synopsis":
                statements.append(
                    select(schema.Movie).where(
                        schema.Movie.synopsis.like(f"%{criteria}%")
                    )
                )
            case "stars":
                for star in criteria:
                    statements.append(
                        (
                            select(schema.Movie)
                            .select_from(schema.Movie)
                            .join(schema.Movie.stars)
                            .where(schema.Person.name.like(f"%{star}%"))
                        )
                    )
            case "directors":
                for director in criteria:
                    statements.append(
                        (
                            select(schema.Movie)
                            .select_from(schema.Movie)
                            .join(schema.Movie.directors)
                            .where(schema.Person.name.like(f"%{director}%"))
                        )
                    )
            case "movie_tags":
                for movie_tag in criteria:
                    statements.append(
                        (
                            select(schema.Movie)
                            .select_from(schema.Movie)
                            .join(schema.Movie.tags)
                            .where(schema.Tag.text.like(f"%{movie_tag}%"))
                        )
                    )

    if statements:
        intersection = intersect(*statements)
        statement = select(schema.Movie).from_statement(intersection)
        matches = session.scalars(statement).all()
        return set(matches)


def _select_all_movies(session: Session) -> set[schema.Movie]:
    """Selects all movies.

    Args:
        session:

    Returns:
        All movies.
    """
    statement = select(schema.Movie)
    return set(session.scalars(statement).all())


def _add_movie(session: Session, *, movie_bag: MovieBag):
    """Add a new movie to the Movie table.

    Neither the related tables nor the relationship columns are changed by
    this function. If that is needed use the high level function add_movie.

    Args:
        session:
        movie_bag:
    """
    movie = schema.Movie(
        title=movie_bag["title"],
        year=int(movie_bag["year"]),
        duration=int(movie_bag["duration"]),
        synopsis=movie_bag["synopsis"],
        notes=movie_bag["notes"],
    )
    session.add(movie)


def _delete_movie(session: Session, *, movie: schema.Movie):
    """Delete a movie from the Movie table.

    Related records which have a relationship with the movie will have the relationship
    deleted. The related record will be otherwise unaffected.

    Args:
        session:
        movie:
    """
    session.delete(movie)


def _edit_movie(*, movie: schema.Movie, edit_fields: MovieBag):
    """Edit movie with edit_fields.

    Neither the related tables nor the relationship columns are changed by
    this function.  If that is needed use the high level function edit_movie.

    Args:
        movie:
        edit_fields:
    """
    for column, value in edit_fields.items():
        match column:
            case "title":
                movie.title = value
            case "year":
                movie.year = int(value)
            case "duration":  # pragma nocover
                movie.duration = int(value)
            case "synopsis":  # pragma nocover
                movie.synopsis = value
            case "notes":  # pragma nocover
                movie.notes = value


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


def _match_people(session: Session, *, match: str) -> set[schema.Person]:
    """Selects a people with a name that contains the match substring.

    Args:
        session: The current session.
        match: Name substring
    Returns:
        None or more people.
    """
    statement = select(schema.Person).where(schema.Person.name.like(f"%{match}%"))
    return set(session.scalars(statement).all())


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


def _delete_orphans(session: Session, candidates: set[schema.Person]):
    for person in candidates:
        if person.star_of_movies != set():
            continue
        if person.director_of_movies != set():
            continue
        session.delete(person)


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


def _select_all_tags(session: Session) -> set[schema.Tag]:
    """Returns a list of every tag.

    Args:
        session:
    Returns:
        A set of tags.
    """
    statement = select(schema.Tag)
    return set(session.scalars(statement).all())


def _add_tag(session: Session, *, tag_text: str):
    """Adds new tags from a tag text.

    Args:
        session:
        tag_text:
    """
    session.add(schema.Tag(text=tag_text))


def _add_tags(session: Session, *, tag_texts: set[str]):
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
