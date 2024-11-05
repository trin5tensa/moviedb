"""Database table functions."""

#  Copyright© 2024. Stephen Rigden.
#  Last modified 11/5/24, 10:41 AM by stephen.
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


session_factory: sessionmaker[Session] | None = None


def select_movie(*, movie_bag: MovieBag) -> MovieBag:
    """Selects and returns a single movie.

    This is not an identity function. See the detailed description of arguments and return
    value for a fuller explanation.

    Args:
        movie_bag:
            id: ignored
            created: ignored
            updated: ignored
            title: required
            year: required
            duration: ignored
            directors: ignored
            stars: ignored
            synopsis: ignored
            notes: ignored
            movie_tags: ignored

    Returns:
        A movie bag populated with every field that is present in the database.

    Raises:
        MovieNotFound if movie_bag is not in the database.
    """
    with session_factory() as session:
        try:
            movie = _select_movie(session, movie_bag=movie_bag)
        except NoResultFound:
            logging.error(MovieNotFound.__qualname__, MovieNotFound.__doc__, movie_bag)
            raise MovieNotFound(MovieNotFound.__doc__)

        movie_bag = _convert_to_movie_bag(movie)
    return movie_bag


def select_all_movies() -> list[MovieBag]:
    """Selects and returns all movies."""
    with session_factory() as session:
        movies = _select_all_movies(session)
        movie_bags = [_convert_to_movie_bag(movie) for movie in movies]
    return movie_bags


def match_movies(match: MovieBag) -> list[MovieBag]:
    """Selects and returns the intersection of matching movies.

    Match patterns are specified in a MovieBag object which can contain none, any,
    or all the fields of a MovieBag object. Each supplied field will be used to
    select compliant records.This function will return the intersection of the
    movie records selected by each field's name criteria. The internal
    database fields of 'id'. 'created', and 'updated' are ignored.

    Args:
        match:
            A movie bag object with the match fields specified below. The id, created,
            and updated fields are ignored.

            Match patterns are specified in a MovieBag object which can contain none,
            any, or all the following fields:
                title. Substring match.
                year. Contains match.
                duration. Contains match.
                directors. Substring set match.
                stars. Substring set match.
                synopsis. Substring match.
                notes. Substring match.
                movie_tags. Substring set match.

            Exact match. 4 will match `movie.id` = 4
            Substring match. The substring 'kwai' will match 'Bridge on the River Kwai'.
            Substring set match. Each item in the set will be matched as a substring
                match (defined above). The movie will only be selected if every item in
                the set matches.
                For a movie with stars {"Edgar Ethelred", "Fanny Fullworthy"}:
                    {'ethel'} will match
                    {'ethel', 'worth'} will match
                    {'ethel', 'bogart'} will not match.
            Contains match. A movie.year of `1955 in MovieInteger('1950-1960')` is a match.

    Returns:
        The intersection of the records selected by each field's search criteria.
    """
    with session_factory() as session:
        movies = _match_movies(session, match=match)
        movie_bags = [_convert_to_movie_bag(movie) for movie in movies]
    return movie_bags


def add_movie(*, movie_bag: MovieBag):
    """Adds a movie.

    Adds a movie, links it to tag table, links stars and directors to people
    table, and adds new people to person table.

    Args:
        movie_bag:
            id: ignored
            created: ignored
            updated: ignored
            title: required
            year: required
            duration: optional
            directors: optional
            stars: optional
            synopsis: optional
            notes: optional
            movie_tags: optional

    Logs and raises:
        MovieExists if title and year duplicate an existing movie.
        InvalidReleaseYear for year outside valid range.
        TagNotFound for tag not in database.
    """
    try:
        with session_factory() as session:
            movie = _add_movie(movie_bag=movie_bag)
            update_movie_relationships(movie, movie_bag, session)
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


def edit_movie(*, old_movie_bag: MovieBag, new_movie_bag: MovieBag):
    """Edits a movie.

    Edits an existing movie, updates links to tag table, updates person table
    links for stars and directors, adds new people to person table, and deletes
    orphans from person table.

    Args:
        old_movie_bag:
            id: ignored
            created: ignored
            updated: ignored
            title: required
            year: required
            duration: ignored
            directors: ignored
            stars: ignored
            synopsis: ignored
            notes: ignored
            movie_tags: ignored
        new_movie_bag:
            id: ignored
            created: ignored
            updated: ignored
            title: required
            year: required
            duration: optional
            directors: optional
            stars: optional
            synopsis: optional
            notes: optional
            movie_tags: optional

    Raises:
        MovieNotFound if old_movie_bag is not in the database.
        MovieExists if new title and year duplicate an existing movie.
        InvalidReleaseYear for new year outside valid range.
        TagNotFound for new tag not in database.
    """
    try:
        with session_factory() as session:
            try:
                movie = _select_movie(session, movie_bag=old_movie_bag)
            except NoResultFound:
                logging.error(
                    MovieNotFound.__qualname__, MovieNotFound.__doc__, old_movie_bag
                )
                raise MovieNotFound

            candidate_orphans = movie.directors | movie.stars
            _edit_movie(movie=movie, edit_fields=new_movie_bag)
            update_movie_relationships(movie, new_movie_bag, session)
            _delete_orphans(session, candidates=candidate_orphans)
            session.commit()

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


def update_movie_relationships(
    movie: schema.Movie, movie_bag: MovieBag, session: Session
):
    """Updates the directors, stars, and tags relationships of the movie.

    This is a support function with contains common code.

    Args:
        movie:
        movie_bag:
        session:

    Raises:
        TagNotFound
    """
    if movie_tags := movie_bag.get("movie_tags"):
        try:
            movie.tags = {
                _select_tag(session, text=tag_text) for tag_text in movie_tags
            }
        except NoResultFound as exc:
            logging.error(TagNotFound.__qualname__, TagNotFound.__doc__, movie_tags)
            raise TagNotFound from exc

    if directors := movie_bag.get("directors"):
        movie.directors = _getadd_people(session, names=directors)
    if stars := movie_bag.get("stars"):
        movie.stars = _getadd_people(session, names=stars)


def delete_movie(*, movie_bag: MovieBag):
    """Deletes a movie.

    Deletes an existing movie, deletes links to tag table, deletes person
    table links for stars and directors, and deletes orphans from person
    table.

    No exception will be raised if the movie has already been deleted. If the movie_bag
    contains orphan stars or directors they will be deleted.

        Args:
            movie_bag:
                id: ignored
                created: ignored
                updated: ignored
                title: required
                year: required
                duration: ignored
                directors: ignored
                stars: ignored
                synopsis: ignored
                notes: ignored
                movie_tags: ignored
    """
    with session_factory() as session:
        try:
            movie = _select_movie(session, movie_bag=movie_bag)
        except NoResultFound:
            directors = movie_bag.get("directors", set())
            stars = movie_bag.get("stars", set())
            candidate_orphans = set(_select_people(session, names=stars | directors))
        else:
            candidate_orphans = movie.directors | movie.stars
            _delete_movie(session, movie=movie)

        _delete_orphans(session, candidates=candidate_orphans)
        session.commit()


def delete_all_orphans():
    """Deletes all orphans.

    Use Case:
        It is possible for a movie to be deleted by another process without handling orphan
        people. THis function should be run at program termination to delete any orphans
        created in ths manner.
    """
    with session_factory() as session:
        all_people = _select_all_people(session)
        count = _delete_orphans(session, candidates=all_people)
        if count:
            logging.info(
                f"{count} Orphan(s) were removed. "
                f"They should have been removed before now."
            )
        session.commit()


def select_all_tags() -> set[str]:
    """Returns a list of all tag texts."""
    with session_factory() as session:
        tags = _select_all_tags(session)
    return {tag.text for tag in tags}


def match_tags(*, match: str) -> set[str]:
    """Returns tag texts which contain a substring.

    Args:
        match:

    Returns:
        A set of complaint tag texts.
    """
    with session_factory() as session:
        tags = _match_tags(session, match=match)
    return {tag.text for tag in tags}


def add_tag(*, tag_text: str):
    """Adds a tag.

    Args:
        tag_text:
    """
    try:
        with session_factory() as session, session.begin():
            _add_tag(session, text=tag_text)
    except IntegrityError:
        # Identical tags are silently suppressed.
        pass


def add_tags(*, tag_texts: set[str]):
    """Adds a list of tags.

    Args:
        tag_texts:
    """
    try:
        with session_factory() as session, session.begin():
            _add_tags(session, texts=tag_texts)
    except IntegrityError:
        # Identical tags are silently suppressed.
        pass


def edit_tag(*, old_tag_text: str, new_tag_text: str):
    """Edits the text of an existing tag.

    Args:
        old_tag_text:
        new_tag_text:
    Raises:
        Logs and raises a TagNotFound exception.
        Logs and raises a TagExists exception.
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
    """This unique movie key is already present in the database."""


class InvalidReleaseYear(IntegrityError):
    """The release year is impossibly early or late."""


class MovieNotFound(NoResultFound):
    """A key search for a movie failed."""


class TagNotFound(NoResultFound):
    """A key search for a tag failed."""


class TagExists(IntegrityError):
    """This unique tag key is already present in the database."""


def _select_movie(session: Session, *, movie_bag: MovieBag) -> schema.Movie:
    """Selects and returns a single ORM movie.

    Args:
        session:
        movie_bag:
            id: ignored
            created: ignored
            updated: ignored
            title: required
            year: required
            duration: ignored
            directors: ignored
            stars: ignored
            synopsis: ignored
            notes: ignored
            movie_tags: ignored
    """
    # noinspection PyTypeChecker
    statement = (
        select(schema.Movie)
        .where(schema.Movie.title == movie_bag["title"])
        .where(schema.Movie.year == int(movie_bag["year"]))
    )
    movie = session.scalars(statement).one()
    return movie


def _select_all_movies(session: Session) -> set[schema.Movie]:
    """Selects and returns all ORM movies.

    Args:
        session:
    """
    statement = select(schema.Movie)
    return set(session.scalars(statement).all())


def _match_movies(session: Session, *, match: MovieBag) -> set[schema.Movie] | None:
    """Selects and returns matching ORM movies.

    Args:
        session:
        match:
            A movie bag object with the match fields specified below. The id, created,
            and updated fields are ignored.

            Match patterns are specified in a MovieBag object which can contain none,
            any, or all the following fields:
                title. Substring match.
                year. Contains match.
                duration. Contains match.
                directors. Substring set match.
                stars. Substring set match.
                synopsis. Substring match.
                notes. Substring match.
                movie_tags. Substring set match.

            Exact match. 4 will match `movie.id` = 4
            Substring match. The substring 'kwai' will match 'Bridge on the River Kwai'.
            Substring set match. Each item in the set will be matched as a substring
                match (defined above). The movie will only be selected if every item in
                the set matches.
                For a movie with stars {"Edgar Ethelred", "Fanny Fullworthy"}:
                    {'ethel'} will match
                    {'ethel', 'worth'} will match
                    {'ethel', 'bogart'} will not match.
            Contains match. A movie.year of `1955 in MovieInteger('1950-1960')` is a match.

    Returns:
        The intersection of the ORM movies selected by each field's search criteria.
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
        # https://docs.sqlalchemy.org/en/20/orm/queryguide
        # /select.html#selecting-entities-from-subqueries
        intersection = intersect(*statements)
        statement = select(schema.Movie).from_statement(intersection)
        matches = session.scalars(statement).all()
        return set(matches)


def _add_movie(*, movie_bag: MovieBag) -> schema.Movie:
    """Add a new movie to the Movie table.

    Neither the related tables nor the relationship columns are changed by
    this function. If that is needed use the high level function add_movie.

    Args:
        movie_bag:
            id: ignored
            created: ignored
            updated: ignored
            title: required
            year: required
            duration: optional
            directors: ignored
            stars: ignored
            synopsis: optional
            notes: optional
            movie_tags: ignored

    Returns:
        The new ORM movie.
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


def _edit_movie(*, movie: schema.Movie, edit_fields: MovieBag):
    """Edits a movie.

    Neither the related tables nor the relationship columns are changed by
    this function.  If that is needed use the high level function edit_movie.

    Args:
        movie: ORM Movie.
        edit_fields: movie bag
            id: ignored
            created: ignored
            updated: ignored
            title: optional
            year: optional
            duration: optional
            directors: ignored
            stars: ignored
            synopsis: optional
            notes: optional
            movie_tags: ignored
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


def _delete_movie(session: Session, *, movie: schema.Movie):
    """Delete a movie from the Movie table.

    Related records which have a relationship with the movie will have the relationship
    deleted. The related record will be otherwise unaffected.

    Args:
        session:
        movie: ORM movie.
    """
    session.delete(movie)


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


def _select_person(session: Session, *, name: str) -> schema.Person:
    """Returns an ORM person.

    Args:
        session: The current session.
        name: Name of person
    """
    # noinspection PyTypeChecker
    statement = select(schema.Person).where(schema.Person.name == name)
    return session.scalars(statement).one()


def _select_people(session: Session, *, names: set[str]) -> set[Person]:
    """Returns a set of ORM persons matching the names.

    The names argument must contain full names and not substrings. See the
    _match_people function for substring matching.

    Args:
        session: The current session.
        names: Names of people.
    """
    statement = select(schema.Person).where(schema.Person.name.in_(list(names)))
    return set(session.scalars(statement).all())


def _select_all_people(session: Session) -> set[Person]:
    """Returns a set of all ORM persons.

    Args:
        session: The current session.
    """
    statement = select(schema.Person)
    return set(session.scalars(statement).all())


def _match_people(session: Session, *, match: str) -> set[schema.Person]:
    """Selects people with names that contain the substring.

    Args:
        session: The current session.
        match: Substring
    Returns:
        A set of ORM persons which may be empty.
    """
    statement = select(schema.Person).where(schema.Person.name.like(f"%{match}%"))
    return set(session.scalars(statement).all())


def _add_person(session: Session, *, name: str) -> schema.Person:
    """Adds a person to the ORM Person table.

    Args:
        session:
        name: Name of person.

    Returns:
        An ORM Person.
    """
    person = schema.Person(name=name)
    session.add(person)
    return person


def _getadd_people(session: Session, *, names: set[str]) -> set[schema.Person]:
    """Returns ORM Persons adding them to the table if they are not already present.

    Args:
        session:
        names:

    Returns:
        A set of ORM Persons
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
    """Deletes an ORM Person.

    Args:
        session:
        person:
    """
    session.delete(person)


def _delete_orphans(session: Session, candidates: set[schema.Person]) -> int:
    """Deletes ORM Persons with no relationship to any ORM Movie.

    Args:
        session:
        candidates:

    Returns:
        A count of orphans deleted.
    """
    count = 0
    for person in candidates:
        if person.star_of_movies != set():
            continue
        if person.director_of_movies != set():
            continue
        count = +1
        session.delete(person)
    return count


def _select_tag(session: Session, *, text: str) -> schema.Tag:
    """Selects and returns a single ORM Tag.

    Args:
        session: The current session.
        text:
    """
    # noinspection PyTypeChecker
    statement = select(schema.Tag).where(schema.Tag.text == text)
    return session.scalars(statement).one()


def _match_tags(session: Session, *, match: str) -> set[schema.Tag]:
    """Selects and returns a set of ORM Tags.

    Args:
        session: The current session.
        match: A substring of sought tag.texts
    """
    statement = select(schema.Tag).where(schema.Tag.text.like(f"%{match}%"))
    return set(session.scalars(statement).all())


def _select_all_tags(session: Session) -> set[schema.Tag]:
    """Returns a set of all ORM Tags.

    Args:
        session:
    """
    statement = select(schema.Tag)
    return set(session.scalars(statement).all())


def _add_tag(session: Session, *, text: str):
    """Adds a new ORM Tag.

    Args:
        session:
        text:
    """
    session.add(schema.Tag(text=text))


def _add_tags(session: Session, *, texts: set[str]):
    """Adds new ORM Tags.

    Args:
        session:
        texts:
    """
    session.add_all([schema.Tag(text=tag) for tag in texts])


def _edit_tag(*, tag: schema.Tag, replacement_text: str):
    """Edits an ORM Tag.

    Args:
        tag:
        replacement_text:
    """
    tag.text = replacement_text


def _delete_tag(session: Session, *, tag: schema.Tag):
    """Deletes an ORM Tag.

    Args:
        session:
        tag:
    """
    session.delete(tag)
