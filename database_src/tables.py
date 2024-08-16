"""Database table functions."""

#  Copyright© 2024. Stephen Rigden.
#  Last modified 8/16/24, 8:03 AM by stephen.
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
from database_src.schema import Person
from globalconstants import *

# todo Clean up
#   Where 'movie_bag' is a parameter specify the required and optional contents.

session_factory: sessionmaker[Session] | None = None


def add_movie(*, movie_bag: MovieBag):
    """Adds a movie.

    Adds a movie, links it to tag table, links stars and directors to people
    table, and adds new people to person table.

    Args:
        movie_bag:

    Logs and raises:
        MovieExists if title and year duplicate an existing movie.
        InvalidReleaseYear for year outside valid range.
        TagNotFound for tag not in database.
    """
    try:
        with session_factory() as session:
            movie = _add_movie(movie_bag=movie_bag)
            if movie_tags := movie_bag.get("movie_tags"):
                movie.tags = {
                    _select_tag(session, text=tag_text) for tag_text in movie_tags
                }
            if directors := movie_bag.get("directors"):
                movie.directors = _getadd_people(session, names=directors)
            if stars := movie_bag.get("stars"):
                movie.stars = _getadd_people(session, names=stars)

            session.add(movie)
            session.commit()

    except IntegrityError as exc:
        if "UNIQUE constraint failed: movie.title, movie.year" in exc.args[0]:
            msg = f"Duplicate title and year: {movie.title=}, {movie.year=}."
            logging.error(str(exc.orig), msg)
            raise MovieExists(exc.statement, exc.params, exc.orig) from exc
        elif "CHECK constraint failed: year" in exc.args[0]:
            logging.error(str(exc.orig), exc.args)
            raise InvalidReleaseYear(exc.statement, exc.params, exc.orig) from exc
        else:  # pragma nocover
            logging.error(exc.orig)
            raise

    except NoResultFound as exc:
        msg = movie_bag["movie_tags"]
        logging.error(exc.args[0], f"Bad tag: {msg}")
        raise TagNotFound(msg) from exc


def edit_movie(*, old_movie_bag: MovieBag, new_movie_bag: MovieBag):
    """Edits a movie.

    Edits an existing movie, updates links to tag table, updates person table
    links for stars and directors, adds new people to person table, and deletes
    orphans from person table.

    Args:
        old_movie_bag:
        new_movie_bag:

    Logs and raises:
        MovieExists if new title and year duplicate an existing movie.
        InvalidReleaseYear for new year outside valid range.
        TagNotFound for new tag not in database.
    """
    try:
        with session_factory() as session:
            movie = _select_movie(
                session, title=old_movie_bag["title"], year=int(old_movie_bag["year"])
            )
            _edit_movie(movie=movie, edit_fields=new_movie_bag)
            if movie_tags := new_movie_bag.get("movie_tags"):
                movie.tags = {
                    _select_tag(session, text=tag_text) for tag_text in movie_tags
                }
            if directors := new_movie_bag.get("directors"):
                movie.directors = _getadd_people(session, names=directors)
            if stars := new_movie_bag.get("stars"):
                movie.stars = _getadd_people(session, names=stars)

            # Orphan removal
            old_directors = old_movie_bag.get("directors", set())
            old_stars = old_movie_bag.get("stars", set())
            candidates = _select_people(
                session,
                names=(old_directors | old_stars),
            )
            _delete_orphans(session, candidates=set(candidates))

            session.commit()

    except NoResultFound as exc:
        msg = new_movie_bag["movie_tags"]
        logging.error(exc.args[0], f"Bad tag: {msg}")
        raise TagNotFound(msg) from exc

    except IntegrityError as exc:
        if "UNIQUE constraint failed: movie.title, movie.year" in exc.args[0]:
            msg = f"Duplicate title and year."
            logging.error(str(exc.orig), msg)
            raise MovieExists(exc.statement, exc.params, exc.orig) from exc
        elif "CHECK constraint failed: year" in exc.args[0]:
            logging.error(str(exc.orig), exc.args)
            raise InvalidReleaseYear(exc.statement, exc.params, exc.orig) from exc
        else:  # pragma nocover
            logging.error(exc.orig)
            raise


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
    movie records selected by each field's name criteria. The internal
    database fields of 'id'. 'created', and 'updated' are ignored.

    Args:
        match:

        Match patterns are specified in a MovieBag object which can contain none,
        any, or all the following fields:
            title. Substring name
            year. Contains name
            duration. Contains name
            directors. Substring set name
            stars. Substring set name
            synopsis. Substring name
            notes. Substring name
            movie_tags. Substring set name

        Exact name. 4 will name `movie.id` = 4
        Substring name. The substring 'kwai' will name 'Bridge on the River Kwai'.
        Substring set name. Each item in the set will be matched as a substring
            match (defined above). The movie will only be selected if every item in
            the set matches.
            For a movie with stars {"Edgar Ethelred", "Fanny Fullworthy"}:
                {'ethel'} will name
                {'ethel', 'worth'} will name
                {'ethel', 'bogart'} will not name.
        Contains name. A movie.year of `1955 in MovieInteger('1950-1960')` is a name.
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
        IntegrityError if the tag match is a duplicate.
    """
    try:
        with session_factory() as session, session.begin():
            _add_tag(session, tag_text=tag_text)
    except IntegrityError as exc:
        logging.error(exc.args[0])
        raise TagExists(exc.statement, exc.params, exc.orig) from exc


def add_tags(*, tag_texts: set[str]):
    """Add a list of tags.

    Args:
        tag_texts:
    Raises:
        IntegrityError if any tag match is a duplicate.
    """
    try:
        with session_factory() as session, session.begin():
            _add_tags(session, tag_texts=tag_texts)
    except IntegrityError as exc:
        logging.error(exc.args[0])
        raise TagExists(exc.statement, exc.params, exc.orig) from exc


def edit_tag(*, old_tag_text: str, new_tag_text: str):
    """

    Args:
        old_tag_text:
        new_tag_text:
    Raises:
        NoRecordFound if the old tag match cannot be found.
        IntegrityError if the new tag match is a duplicate.
    """
    try:
        with session_factory() as session, session.begin():
            try:
                tag = _select_tag(session, text=old_tag_text)
            except NoResultFound as exc:
                logging.error(exc.args[0])
                raise TagNotFound from exc
            else:
                _edit_tag(tag=tag, replacement_text=new_tag_text)
    except IntegrityError as exc:
        logging.error(exc.args[0])
        raise TagExists(exc.statement, exc.params, exc.orig) from exc


def delete_tag(*, tag_text: str):
    """Delete a tag.

    The exception NoResultFound is ignored if the record is not present.

    Args:
        tag_text:
    """
    with session_factory() as session, session.begin():
        try:
            tag = _select_tag(session, text=tag_text)
        except NoResultFound:
            pass
        else:
            _delete_tag(session, tag=tag)


class MovieExists(IntegrityError):
    pass


class InvalidReleaseYear(IntegrityError):
    pass


class TagNotFound(NoResultFound):
    pass


class TagExists(IntegrityError):
    pass


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
    # todo Change signature to use incoming movie bag.
    # noinspection PyTypeChecker
    statement = (
        select(schema.Movie)
        .where(schema.Movie.title == title)
        .where(schema.Movie.year == year)
    )
    movie = session.scalars(statement).one()
    # print(f"_select_movie: {movie=}")
    return movie


def _match_movies(session: Session, *, match: MovieBag) -> set[schema.Movie] | None:
    """Selects matching movies.

    Args:
        session:
        match: A MovieBag object containing any items to be used as search criteria.

    Returns:
        Matching movies.
        Returns None if name argument is an empty dict.
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


def _add_movie(*, movie_bag: MovieBag) -> schema.Movie:
    """Add a new movie to the Movie table.

    Neither the related tables nor the relationship columns are changed by
    this function. If that is needed use the high level function add_movie.

    Args:
        movie_bag:
    """
    movie = schema.Movie(
        title=movie_bag["title"],
        year=int(movie_bag["year"]),
    )
    if duration := movie_bag.get("duration"):
        movie.duration = int(duration)
    if synopsis := movie_bag.get("synopsis"):
        movie.synopsis = synopsis
    if notes := movie_bag.get("notes"):
        movie.notes = notes
    return movie


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


def _select_person(session: Session, *, name: str) -> schema.Person:
    """Returns a single person.

    Args:
        session: The current session.
        name: Name of person
    Returns:
        A person object
    """
    # noinspection PyTypeChecker
    statement = select(schema.Person).where(schema.Person.name == name)
    return session.scalars(statement).one()


def _select_people(session: Session, *, names: set[str]) -> Sequence[Person]:
    """Returns a sequence of people.

    Args:
        session: The current session.
        names: Names of people.
    Returns:
        A sequence of people.
    """
    # todo Consider converting return value to a set
    statement = select(schema.Person).where(schema.Person.name.in_(list(names)))
    return session.scalars(statement).all()


def _match_people(session: Session, *, match: str) -> set[schema.Person]:
    """Selects people with names that contains the name substring.

    Args:
        session: The current session.
        match: Name substring
    Returns:
        None or more people.
    """
    statement = select(schema.Person).where(schema.Person.name.like(f"%{match}%"))
    return set(session.scalars(statement).all())


def _add_person(session: Session, *, name: str) -> schema.Person:
    """Add a person to the Person table.

    Args:
        session:
        name: Name of person.

    Returns:
        Person
    """
    person = schema.Person(name=name)
    session.add(person)
    return person


def _getadd_people(session: Session, *, names: set[str]) -> set[schema.Person]:
    """Get and add people.

    Args:
        session:
        names:

    Returns:
        A set of Persons
    """
    people = set()
    for name in names:
        try:
            person = _select_person(session, name=name)
        except NoResultFound:
            person = _add_person(session, name=name)
        people.add(person)
    return people


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


def _select_tag(session: Session, *, text: str) -> schema.Tag:
    """Selects a single tag.

    Args:
        session: The current session.
        text: Search match
    Returns:
        A tag.
    """
    # noinspection PyTypeChecker
    statement = select(schema.Tag).where(schema.Tag.text == text)
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
    """Adds new tags from a tag match.

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
    """Edits a tag.

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
