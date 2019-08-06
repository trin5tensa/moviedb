"""A module encapsulating the database and all SQLAlchemy based code.."""
import datetime
from contextlib import contextmanager
from typing import Any, Dict, Generator, Iterable, Optional, Tuple

import sqlalchemy
import sqlalchemy.exc
import sqlalchemy.ext.declarative
import sqlalchemy.ext.hybrid
from sqlalchemy import (CheckConstraint, Column, ForeignKey, Integer, Sequence,
                        String, Text, UniqueConstraint)
from sqlalchemy.ext.hybrid import hybrid_method
from sqlalchemy.orm import query, relationship
from sqlalchemy.orm.session import sessionmaker

# Third party package imports


# Constants
Base = sqlalchemy.ext.declarative.declarative_base()
database_fn = 'movies.db'

# Variables
engine: Optional[sqlalchemy.engine.base.Engine] = None
Session: Optional[sqlalchemy.orm.session.sessionmaker] = None


# Pure data Dataclasses
# Named tuples


# API Classes


# API Functions
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
        movie: A dictionary which must contain title, director, minutes, and year.
        It may contain notes.
    """
    _Movie(**movie).add()


def find_movies(criteria: Dict[str, Any]) -> Generator[dict, None, None]:
    """Search for a movie using any supplied_keys.

    Yield record fields which persist after the session has ended.
    This will produce one record for each movie, tag, and review combination. Therefore one movie may
    produce more than one return record.

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
        Yields: A dictionary of attributes and values copied from each combination of movie and tag.
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


def edit_movie(title: str, year: int, updates: Dict[str, Any]):
    """Search for one movie and change one or more fields of that movie.

    Use edit_tag and edit_review to edit those fields.

    Args:
        title: Movie title
        year: Movie year
        updates: Dictionary of fields to be updated. See find_movies for detailed description.
            e.g. 'notes'-'Science Fiction'
    """
    criteria = dict(title=title, year=year)
    with _session_scope() as session:
        # _build_movie_query(session, criteria).one().edit(updates)
        movie, tag = _build_movie_query(session, criteria).one()
        movie.edit(updates)


def del_movie(title: str, year: int):
    """Change fields in records.

    Args:
        title: Movie title
        year: Movie year
    """
    criteria = dict(title=title, year=year)
    with _session_scope() as session:
        movie, tag = _build_movie_query(session, criteria).one()
        session.delete(movie)


def add_tag_and_links(new_tag: str, movies: Optional[Iterable[Tuple[str, int]]] = None):
    """Add links between a tag and one or more movies. Create the tag if it does not exist..

    Args:
        new_tag:
        movies: Tuples of a movie'a title and its year of release.
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
    """Delete a tag.

    Args:
        tag:
    """
    with _session_scope() as session:
        tag_obj = session.query(_Tag).filter(_Tag.tag == tag).one()
        session.delete(tag_obj)


# Internal Module Classes
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
    director = Column(String(24), nullable=False)
    minutes = Column(Integer, nullable=False)
    year = Column(Integer, CheckConstraint('year>1877'), CheckConstraint('year<10000'), nullable=False)
    notes = Column(Text, default=None)
    UniqueConstraint(title, year)

    tags = relationship('_Tag', secondary='movie_tag', back_populates='movies', cascade='all')
    reviews = relationship('_Review', secondary='movie_review', back_populates='movies', cascade='all')

    def __init__(self, title: str, director: str, minutes: int, year: int, notes: str = None):
        self.title = title
        self.director = director
        self.minutes = minutes
        self.year = year
        self.notes = notes

    def __repr__(self):  # pragma: no cover
        return (self.__class__.__qualname__ +
                f"(title={self.title!r}, director={self.director!r}, minutes={self.minutes!r}, "
                f"year={self.year!r}, notes={self.notes!r})")

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
        """Raise ValueError if any column item is not a column of this class.

        Args:
            columns: column names for validation

        Raises:
            Value Error: If any supplied keys are not valid column names.
        """
        valid_columns = set(cls.__table__.columns.keys()) | {'tags'}
        invalid_keys = set(columns) - valid_columns
        if invalid_keys:
            # moviedatabase-#37
            #  Change the message to read:
            #   f"Invalid attibute '{invalid_keys}'."
            msg = f"Key(s) '{invalid_keys}' is not a valid search key."
            raise ValueError(msg)


class _Tag(Base):
    """Table schema for entities who have seen a movie."""
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


class _MovieTag(Base):
    """Many to many link table for _Movie and _Tag."""
    __tablename__ = 'movie_tag'

    movies_id = Column(Integer, ForeignKey('movies.id'), primary_key=True)
    tags_id = Column(Integer, ForeignKey('tags.id'), primary_key=True)


class _MovieReview(Base):
    """Many to many link table for _Movie and _Review."""
    __tablename__ = 'movie_review'

    movies_id = Column(Integer, ForeignKey('movies.id'), primary_key=True)
    review_id = Column(Integer, ForeignKey('reviews.id'), primary_key=True)


class _Review(Base):
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


# Internal Module Functions
@contextmanager
def _session_scope():
    """Provide a session scope around a series of operations."""
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
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
    # movies = (session.query(_Movie))
    if 'id' in criteria:
        movies = movies.filter(_Movie.id == criteria['id'])
    if 'title' in criteria:
        movies = movies.filter(_Movie.title.like(f"%{criteria['title']}%"))
    if 'director' in criteria:
        movies = movies.filter(_Movie.director.like(f"%{criteria['director']}%"))
    if 'minutes' in criteria:
        if not isinstance(criteria['minutes'], list):
            criteria['minutes'] = [criteria['minutes'], ]
        movies = movies.filter(_Movie.minutes.between(min(criteria['minutes']),
                                                      max(criteria['minutes'])))
    if 'year' in criteria:
        if not isinstance(criteria['year'], list):
            criteria['year'] = [criteria['year'], ]
        movies = movies.filter(_Movie.year.between(min(criteria['year']),
                                                   max(criteria['year'])))
    if 'notes' in criteria:
        movies = movies.filter(_Movie.notes.like(f"%{criteria['notes']}%"))
    if 'tags' in criteria:
        if not isinstance(criteria['tags'], list):
            criteria['tags'] = [criteria['tags'], ]
        # moviedatabase-#37
        #   Is there any way of not using _MovieTag directly?
        movies = (movies
                  .filter(_Tag.tag.in_(criteria['tags']))
                  .filter(_Tag.id == _MovieTag.tags_id)
                  .filter(_Movie.id == _MovieTag.movies_id))

    # print()
    # for movie, tag in movies.all():
    #     if tag:
    #         print(movie.id, movie.title, movie.minutes, movie.tags, tag.id, tag.tag)
    #     else:
    #         print(movie.id, movie.title, movie.minutes, movie.tags)

    return movies
