"""A module encapsulating the database and all SQLAlchemy based code.."""

#  Copyright© 2019. Stephen Rigden.
#  Last modified 9/10/19, 7:44 AM by stephen.
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

import datetime
import itertools
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any, Dict, Generator, Iterable, Optional

import sqlalchemy
import sqlalchemy.exc
import sqlalchemy.ext.declarative
import sqlalchemy.ext.hybrid
from sqlalchemy import (CheckConstraint, Column, ForeignKey, Integer, Sequence, String, Table, Text,
                        UniqueConstraint)
from sqlalchemy.ext.hybrid import hybrid_method
from sqlalchemy.orm import query, relationship
from sqlalchemy.orm.session import sessionmaker


Base = sqlalchemy.ext.declarative.declarative_base()
database_fn = 'movies.sqlite3'

movie_tag = Table('movie_tag', Base.metadata,
                  Column('movies_id', ForeignKey('movies.id'), primary_key=True),
                  Column('tags_id', ForeignKey('tags.id'), primary_key=True))
movie_review = Table('movie_review', Base.metadata,
                     Column('movies_id', ForeignKey('movies.id'), primary_key=True),
                     Column('reviews_id', ForeignKey('reviews.id'), primary_key=True))
engine: Optional[sqlalchemy.engine.base.Engine] = None
Session: Optional[sqlalchemy.orm.session.sessionmaker] = None


@dataclass
class TitleYear:
    """
    A data dataclass.

    This was created to clarify the typing of parameters
    """
    title: str
    year: int


def connect_to_database(filename: str = database_fn):
    """Make database available for use by this module."""

    # Create the database connection
    global engine, Session
    engine = sqlalchemy.create_engine(f"sqlite:///{filename}", echo=False)
    Session = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)

    # Update metadata
    with _session_scope() as session:
        timestamp = str(datetime.datetime.today())
        try:
            session.query(_MoviesMetaData).filter(_MoviesMetaData.name == 'date_created').one()

        # Code for a new database
        except sqlalchemy.orm.exc.NoResultFound:
            session.add_all([_MoviesMetaData(name='version', value='1'),
                             _MoviesMetaData(name='date_last_accessed', value=timestamp),
                             _MoviesMetaData(name='date_created', value=timestamp)])

        # Code for an existing database
        else:
            date_last_accessed = (session.query(_MoviesMetaData)
                                  .filter(_MoviesMetaData.name == 'date_last_accessed')
                                  .one())
            date_last_accessed.value = timestamp


def add_movie(movie: Dict):
    """Add a movie to the database

    Args:
        movie: A dictionary which must contain keys of title and year.
        It may contain keys of director, minutes, and notes.
    """
    _Movie(**movie).add()


def find_movies(criteria: Dict[str, Any]) -> Generator[dict, None, None]:
    """Search for a movie using any supplied_keys.

    Yield record fields which persist after the session has ended.
    This will produce one record for each movie, tag, and review combination. Therefore one movie may
    produce more than one yielded record.

    Args:
        criteria: A dictionary containing none or more of the following keys:
            title: str. A matching column will be a superstring of this value..
            director: str.A matching column will be a superstring of this value.
            minutes: list. A matching column will be between the minimum and maximum values in this
            iterable. A single value is permissible.
            year: list. A matching column will be between the minimum and maximum values in this
            iterable. A single value is permissible.
            notes: str. A matching column will be a superstring of this value.
            tag: list. Movies matching any tag in this list will be selected.

    Raises:
        ValueError: If a supplied_keys key is not a column name

    Generates:
        Yields:  Each compliant movie as a dictionary of title, director, minutes, year, notes, and tag.
        Sends: Not used.
        Returns: Not used.
    """
    _Movie.validate_columns(criteria.keys())

    # Execute searches
    with _session_scope() as session:
        movies = _build_movie_query(session, criteria)
        movies.order_by(_Movie.title)
        for movie, tag in movies:
            tag = tag.tag if tag else None
            yield dict(title=movie.title, director=movie.director, minutes=movie.minutes,
                       year=movie.year, notes=movie.notes, tag=tag)


def edit_movie(title_year: TitleYear, updates: Dict[str, Any]):
    """Search for one movie and change one or more fields of that movie.

    Args:
        title_year: A TitleYear object
        updates: Dictionary of fields to be updated. See find_movies for detailed description.
            e.g. 'notes'-'Science Fiction'
    """
    criteria = dict(title=title_year.title, year=title_year.year)
    with _session_scope() as session:
        movie, tag = _build_movie_query(session, criteria).one()
        movie.edit(updates)


def del_movie(title_year: TitleYear):
    """Change fields in records.

    Args:
        title_year: A TitleYear object
    """
    criteria = dict(title=title_year.title, year=title_year.year)
    with _session_scope() as session:
        movie, tag = _build_movie_query(session, criteria).one()
        session.delete(movie)


def add_tag_and_links(new_tag: str, movies: Optional[Iterable[TitleYear]] = None):
    """Add links between a tag and one or more movies. Create the tag if it does not exist..

    Args:
        new_tag:
        movies: Tuples of TitleYear objects.
    """

    # Add the tag unless it is already in the database.
    try:
        _Tag(new_tag).add()
    except sqlalchemy.exc.IntegrityError:
        pass

    # Add links between movies and this tag.
    if movies:
        with _session_scope() as session:
            tag = session.query(_Tag).filter(_Tag.tag == new_tag).one()

            for title_year in movies:
                movie = (session.query(_Movie)
                         .filter(_Movie.title == title_year.title, _Movie.year == title_year.year)
                         .one())
                movie.tags.append(tag)


def edit_tag(old_tag: str, new_tag: str):
    """Edit the tag string.

    Args:
        old_tag:
        new_tag:
    """
    with _session_scope() as session:
        tag = session.query(_Tag).filter(_Tag.tag == old_tag).one()
        tag.tag = new_tag


def del_tag(tag: str):
    """Delete a tag.

    Args:
        tag:
    """
    with _session_scope() as session:
        tag_obj = session.query(_Tag).filter(_Tag.tag == tag).one()
        session.delete(tag_obj)


class _MoviesMetaData(Base):
    """Meta data table schema."""
    __tablename__ = 'meta_data'

    name = Column(String(80), primary_key=True)
    value = Column(String(80))

    def __repr__(self):  # pragma: no cover
        return (self.__class__.__qualname__ +
                f"(name={self.name!r}, value={self.value!r}")


class _Movie(Base):
    """Movies table schema."""
    __tablename__ = 'movies'

    id = Column(Integer, Sequence('movie_id_sequence'), primary_key=True)
    title = Column(String(80), nullable=False)
    director = Column(String(24))
    minutes = Column(Integer)
    year = Column(Integer, CheckConstraint('year>1877'), CheckConstraint('year<10000'), nullable=False)
    notes = Column(Text)
    UniqueConstraint(title, year)

    tags = relationship('_Tag', secondary='movie_tag', back_populates='movies', cascade='all')
    reviews = relationship('_Review', secondary='movie_review', back_populates='movies', cascade='all')

    def __init__(self, title: str, year: int, director: str = None,
                 minutes: int = None, notes: str = None):

        # Carry out validation which is not done by SQLAlchemy or sqlite3
        null_strings = set(itertools.filterfalse(lambda arg: arg != '', [title, year]))
        if null_strings == {''}:
            msg = 'Null values (empty strings) in row.'
            raise ValueError(msg)
        # noinspection PyStatementEffect
        {int(arg) for arg in [minutes, year]}

        self.title = title
        self.director = director
        self.minutes = minutes
        self.year = year
        self.notes = notes

    def __repr__(self):  # pragma: no cover
        return (self.__class__.__qualname__ +
                f"(title={self.title!r}, year={self.year!r}, "
                f"director={self.director!r}, minutes={self.minutes!r}, notes={self.notes!r})")

    def add(self):
        """Add self to database. """
        with _session_scope() as session:
            session.add(self)

    def edit(self, updates: Dict[str, Any]):
        """Edit any column of the table.

        Args:
            updates: Dictionary of fields to be updated. See find_movies for detailed description.
            e.g. {notes='Science Fiction}
        """
        self.validate_columns(updates.keys())
        for key, value in updates.items():
            setattr(self, key, value)

    @classmethod
    def validate_columns(cls, columns: Iterable[str]):
        """Raise ValueError if any column item is not a column of this class or the _Tag class.

        Args:
            columns: column names for validation

        Raises:
            Value Error: If any supplied keys are not valid column names.
        """
        # noinspection PyUnresolvedReferences
        valid_columns = set(cls.__table__.columns.keys()) | {'tags'}
        invalid_keys = set(columns) - valid_columns
        if invalid_keys:
            msg = f"Invalid attribute '{invalid_keys}'."
            # moviedatabase-#50 Add logging
            raise ValueError(msg)


class _Tag(Base):
    """Table schema for tags."""
    __tablename__ = 'tags'

    id = Column(sqlalchemy.Integer, Sequence('tag_id_sequence'), primary_key=True)
    tag = Column(String(24), nullable=False, unique=True)

    movies = relationship('_Movie', secondary='movie_tag', back_populates='tags', cascade='all')

    def __init__(self, tag: str):
        self.tag = tag

    def __repr__(self):  # pragma: no cover
        return (self.__class__.__qualname__ +
                f"(tag={self.tag!r})")

    def add(self):
        """Add self to database. """
        with _session_scope() as session:
            session.add(self)


class _Review(Base):
    """Reviews tables schema.

    This table has been designed to provide a single row for a reviewer and rating value.
    So a 3.5/4 star rating from Ebert will be linked to none or more movies.
    The reviewer can ba an individual like 'Ebert' for an aggregator like 'Rotten Tomatoes.
    max_rating is part of the secondary key. This allows for a particular reviewer changing
    his/her/its rating system.
    """
    __tablename__ = 'reviews'

    id = Column(sqlalchemy.Integer, Sequence('review_id_sequence'), primary_key=True)
    reviewer = Column(String(24), nullable=False)
    rating = Column(Integer, nullable=False)
    max_rating = Column(Integer, nullable=False)
    UniqueConstraint(reviewer, rating, max_rating)

    movies = relationship('_Movie', secondary='movie_review',
                          back_populates='reviews', cascade='all')

    _percentage: int = None

    # noinspection PyMissingOrEmptyDocstring
    @hybrid_method
    def percentage(self) -> int:
        if self._percentage is None:
            self._percentage = int(100 * self.rating / self.max_rating)
        return self._percentage

    def __repr__(self):  # pragma: no cover
        return (self.__class__.__qualname__ +
                f"(reviewer={self.reviewer!r}, rating={self.rating!r}),"
                f" max_rating={self.max_rating!r}), ")


@contextmanager
def _session_scope():
    """Provide a session scope around a series of operations."""
    session = Session()
    # noinspection PyPep8
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        # moviedatabase-#50 Add logging
        raise
    finally:
        session.close()


def _build_movie_query(session: Session, criteria: Dict[str, Any]) -> sqlalchemy.orm.query.Query:
    """Build a query.

    Args:
        session: This function must be run inside a caller supplied Session object.
        criteria: Record selection criteria. See find_movies for detailed description.
            e.g. 'title'-'Solaris'

    Returns:
        An SQL Query object
    """
    movies = (session.query(_Movie, _Tag).outerjoin(_Movie.tags))
    if 'id' in criteria:
        movies = movies.filter(_Movie.id == criteria['id'])
    if 'title' in criteria:
        movies = movies.filter(_Movie.title.like(f"%{criteria['title']}%"))
    if 'director' in criteria:
        movies = movies.filter(_Movie.director.like(f"%{criteria['director']}%"))
    if 'minutes' in criteria:
        minutes = criteria['minutes']
        try:
            low, high = min(minutes), max(minutes)
        except TypeError:
            low = high = minutes
        movies = movies.filter(_Movie.minutes.between(low, high))
    if 'year' in criteria:
        year = criteria['year']
        try:
            low, high = min(year), max(year)
        except TypeError:
            low = high = year
        movies = movies.filter(_Movie.year.between(low, high))
    if 'notes' in criteria:
        movies = movies.filter(_Movie.notes.like(f"%{criteria['notes']}%"))
    if 'tags' in criteria:
        tags = criteria['tags']
        if isinstance(tags, str):
            tags = [tags, ]
        movies = (movies.filter(_Tag.tag.in_(tags)))

    return movies
