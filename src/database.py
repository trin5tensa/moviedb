"""Exclusive database connections."""
import datetime
from contextlib import contextmanager
from typing import Any, Dict, Iterable, Optional, Generator, Tuple

import sqlalchemy
import sqlalchemy.exc
import sqlalchemy.ext.hybrid
from sqlalchemy import (CheckConstraint, Column, ForeignKey, Integer, Sequence,
                        String, Table, Text, UniqueConstraint)
from sqlalchemy.ext import declarative
from sqlalchemy.ext.hybrid import hybrid_method
from sqlalchemy.orm import query, relationship
from sqlalchemy.orm.session import sessionmaker, Session

# Third party package imports


# Constants
_SQLAlchemyBase = sqlalchemy.ext.declarative.declarative_base()
_movie_tag = Table('_movie_tag', _SQLAlchemyBase.metadata,
                   Column('movies_id', ForeignKey('movies.id'), primary_key=True),
                   Column('tags_id', ForeignKey('tags.id'), primary_key=True))
_movie_review = Table('_movie_review', _SQLAlchemyBase.metadata,
                      Column('movies_id', ForeignKey('movies.id'), primary_key=True),
                      Column('reviews_id', ForeignKey('reviews.id'), primary_key=True))
database_fn = 'movies.db'

# Variables
_engine: Optional[sqlalchemy.engine.base.Engine] = None
_Session: Optional[sqlalchemy.orm.session.sessionmaker] = None


# Pure data Dataclasses
# Named tuples


# API Classes


# API Functions


# Internal Module Classes
class _MoviesMetaData(_SQLAlchemyBase):
    """Meta data table schema."""
    __tablename__ = 'meta_data'

    name = Column(String(80), primary_key=True)
    value = Column(String(80))

    def __repr__(self):  # pragma: no cover
        return (self.__class__.__qualname__ +
                f"(name={self.name!r}, value={self.value!r}")


class _Movie(_SQLAlchemyBase):
    """Movies table schema."""
    __tablename__ = 'movies'

    id = Column(Integer, Sequence('movie_id_sequence'), primary_key=True)
    title = Column(String(80), nullable=False)
    director = Column(String(24), nullable=False)
    minutes = Column(Integer, nullable=False)
    year = Column(Integer, CheckConstraint('year>1877'), CheckConstraint('year<10000'), nullable=False)
    notes = Column(Text, default=None)
    UniqueConstraint(title, year)

    tags = relationship('_Tag', secondary=_movie_tag,
                        back_populates='movies', cascade='all')
    reviews = relationship('_Review', secondary=_movie_review,
                           back_populates='movies', cascade='all')

    def __repr__(self):  # pragma: no cover
        return (self.__class__.__qualname__ +
                f"(title={self.title!r}, director={self.director!r}, minutes={self.minutes!r}, "
                f"year={self.year!r}, notes={self.notes!r})")


class _Tag(_SQLAlchemyBase):
    """Table schema for entities who have seen a movie."""
    __tablename__ = 'tags'

    id = Column(sqlalchemy.Integer, Sequence('tag_id_sequence'), primary_key=True)
    tag = Column(String(24), nullable=False, unique=True)

    movies = relationship('_Movie', secondary=_movie_tag, back_populates='tags', cascade='all')

    def __repr__(self):  # pragma: no cover
        return (self.__class__.__qualname__ +
                f"(tag={self.tag!r})")


class _Review(_SQLAlchemyBase):
    """Reviews tables schema.

    This table has been designed to provide a single row for a reviewer and rating value. So a 3.5/4 star
    rating from Ebert will be linked to none or more movies.
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

    movies = relationship('_Movie', secondary=_movie_review,
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


# Internal Module Functions
@contextmanager
def _session_scope():
    """Provide a session scope around a series of operations."""
    session = _Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


def _search_movies(criteria: Dict[str, Any]) -> Generator[_Movie, None, None]:
    """Search for a movie using any supplied_keys

    Args:
        criteria: A dictionary containing none or more of the following keys:
            title: str. A matching column will be a superstring of this value..
            director: str.A matching column will be a superstring of this value.
            minutes: list. A matching column will be between the minimum and maximum values in this
            iterable. A single value is permissible.
            year:  list. A matching column will be between the minimum and maximum values in this
            iterable. A single value is permissible.
            notes: str. A matching column will be a superstring of this value.

    Raises:
        ValueError: If a supplied_keys key is not a column name

    Generates:
        Yields: Compliant _Movie objects.
        Sends: Not used.
        Returns: Not used.
    """
    _validate_column_names(criteria.keys())

    # Execute searches
    with _session_scope() as session:
        movies = _query_movie(session, criteria)

        movies.order_by(_Movie.title)
        for movie in movies:
            yield movie


def _validate_column_names(supplied_keys: Iterable[str]):
    """Check the list

    Args:
        supplied_keys:

    Raises:
        Value Error:

    """
    valid_keys = set(_Movie.__table__.columns.keys())
    invalid_keys = set(supplied_keys) - valid_keys
    if invalid_keys:
        msg = f"Key(s) '{invalid_keys}' not in valid set '{valid_keys}'."
        raise ValueError(msg)


def _query_movie(session: Session, criteria: Dict[str, Any]) -> sqlalchemy.orm.query.Query:
    """Build a query.

    Args:
        session: This function must be run inside a caller supplied Session object.
        criteria: Record selection criteria. See _search_movies for detailed description.
            e.g. 'title'-'Solaris'

    Returns:
        An SQL Query object
    """
    movies = (session.query(_Movie))
    if 'id' in criteria:
        movies = movies.filter(_Movie.id == criteria['id'])
    if 'title' in criteria:
        movies = movies.filter(_Movie.title.like(f"%{criteria['title']}%"))
    if 'director' in criteria:
        movies = movies.filter(_Movie.director.like(f"%{criteria['director']}%"))
    if 'minutes' in criteria:
        movies = movies.filter(_Movie.minutes.between(min(criteria['minutes']),
                                                      max(criteria['minutes'])))
    if 'year' in criteria:
        movies = movies.filter(_Movie.year.between(min(criteria['year']),
                                                   max(criteria['year'])))
    if 'notes' in criteria:
        movies = movies.filter(_Movie.title.like(f"%{criteria['notes']}%"))
    return movies


def connect_to_database(filename: str = database_fn):
    """Make database available for use by this module."""
    # Create the database connection
    global _engine, _Session
    _engine = sqlalchemy.create_engine(f"sqlite:///{filename}", echo=False)
    _Session = sessionmaker(bind=_engine)
    _SQLAlchemyBase.metadata.create_all(_engine)

    # Update metadata
    with _session_scope() as session:
        timestamp = str(datetime.datetime.today())
        try:
            session.query(_MoviesMetaData).filter(_MoviesMetaData.name == 'date_created').one()

        # Code for a new database
        except sqlalchemy.orm.exc.NoResultFound:
            session.add_all([_MoviesMetaData(name='date_last_accessed', value=timestamp),
                             _MoviesMetaData(name='date_created', value=timestamp)])

        # Code for an existing database
        else:
            date_last_accessed = (session.query(_MoviesMetaData)
                                  .filter(_MoviesMetaData.name == 'date_last_accessed')
                                  .one())
            date_last_accessed.value = timestamp


def add_movie(movie: Dict):
    """Add a movie.

    Args:
        movie: A dictionary which must contain title, director, minutes, and year.
        It may contain notes.
    """
    movie = _Movie(**movie)
    with _session_scope() as session:
        session.add(movie)


def add_movies(movies_args: Iterable[Dict]):
    """Add one or more movies.

    Args:
        movies_args: An iterable of dictionaries which must contain title, director, minutes,
        and year. It may contain 'notes'.
    """
    movies = [_Movie(**movie) for movie in movies_args]
    with _session_scope() as session:
        session.add_all(movies)


def edit_movie(criteria: Dict[str, Any], updates: Dict[str, Any]):
    """Change fields in records.

    Args:
        criteria: Record selection criteria. See _search_movies for detailed description.
            e.g. 'title'-'Solaris'
        updates: Dictionary of fields to be updated. See _search_movies for detailed description.
            e.g. 'notes'-'Science Fiction'
    """
    _validate_column_names(criteria.keys())
    _validate_column_names(updates.keys())
    with _session_scope() as session:
        movie = _query_movie(session, criteria).one()
        for key, value in updates.items():
            setattr(movie, key, value)


def del_movie(criteria: Dict[str, Any]):
    """Change fields in records.

    Args:
        criteria: Record selection criteria. See _search_movies for detailed description.
            e.g. 'title'-'Solaris'
    """
    _validate_column_names(criteria.keys())

    with _session_scope() as session:
        movie = _query_movie(session, criteria).one()
        session.delete(movie)


def add_tag_and_links(new_tag: str, movies: Optional[Iterable[Tuple[str, int]]] = None):
    """Add links between a tag and one or more movies. Create the tag if it does not exist..

    Args:
        new_tag:
        movies: Tuples of a movie'a title and its year of release.
    """
    tag = _Tag(tag=new_tag)
    with _session_scope() as session:
        tags = session.query(_Tag).filter(_Tag.tag == new_tag)
        if tags.count() is 0:
            session.add(tag)

        if movies:
            tag = tags.one()
            for title, year in movies:
                movie = (session.query(_Movie)
                         .filter(_Movie.title == title, _Movie.year == year)
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
    with _session_scope() as session:
        tag_obj = session.query(_Tag).filter(_Tag.tag == tag).one()
        session.delete(tag_obj)
