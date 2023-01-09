"""A module encapsulating the database and all SQLAlchemy based code.."""

#  Copyright (c) 2022-2023. Stephen Rigden.
#  Last modified 1/9/23, 8:37 AM by stephen.
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

import datetime
import logging
import sys
from contextlib import contextmanager
from typing import Generator, Iterable, List, Optional, Union

import sqlalchemy
import sqlalchemy.exc
import sqlalchemy.ext.declarative
import sqlalchemy.ext.hybrid
import sqlalchemy.orm
from sqlalchemy import (CheckConstraint, Column, Date, ForeignKey, Integer, String, Table, Text,
                        UniqueConstraint, )
from sqlalchemy.ext.hybrid import hybrid_method
from sqlalchemy.orm import relationship
from sqlalchemy.orm.session import sessionmaker

import exception
from config import FindMovieTypedDict, MovieKeyTypedDict, MovieTypedDict, MovieUpdateDef


class Base:
    """ See SQLAlchemy docs for why this is required.

    https://docs.sqlalchemy.org/en/20/changelog/migration_20.html#migration-to-2-0-step-six-add-allow-unmapped-to-explicitly-typed-orm-models
    """
    __allow_unmapped__ = True


Base = sqlalchemy.orm.declarative_base(cls=Base)
MUYBRIDGE = 1878
# Base = sqlalchemy.ext.declarative.declarative_base()   old sqlalchemy v1.4 code
database_fn = 'old movies.sqlite3'

movie_tag = Table('movie_tag', Base.metadata,
                  Column('movies_id', ForeignKey('movies.id'), primary_key=True),
                  Column('tags_id', ForeignKey('tags.id'), primary_key=True))
movie_review = Table('movie_review', Base.metadata,
                     Column('movies_id', ForeignKey('movies.id'), primary_key=True),
                     Column('reviews_id', ForeignKey('reviews.id'), primary_key=True))
engine: Optional[sqlalchemy.engine.base.Engine] = None
Session: Optional[sqlalchemy.orm.session.sessionmaker] = None


MovieSearch = Union[MovieKeyTypedDict, MovieTypedDict, FindMovieTypedDict]


def connect_to_database(filename: str = database_fn):
    """Make database available for use by this module."""
    
    # Create the database connection
    global engine, Session
    engine = sqlalchemy.create_engine(f"sqlite:///{filename}", echo=False, future=True)
    Session = sessionmaker(bind=engine, future=True)
    Base.metadata.create_all(engine)
    
    # Update metadata
    with _session_scope() as session:
        timestamp = str(datetime.datetime.today())
        try:
            session.query(MoviesMetaData).filter(MoviesMetaData.name == 'date_created').one()

        # Code for a new database
        except sqlalchemy.orm.exc.NoResultFound:
            session.add_all([MoviesMetaData(name='version', value='1'),
                             MoviesMetaData(name='date_last_accessed', value=timestamp),
                             MoviesMetaData(name='date_created', value=timestamp)])

        # Code for an existing database
        else:
            date_last_accessed = (session.query(MoviesMetaData)
                                  .filter(MoviesMetaData.name == 'date_last_accessed')
                                  .one())
            date_last_accessed.value = timestamp


def add_movie(movie: MovieTypedDict):
    """Add a movie to the database

    Args:
        movie: The movie to be added.
    """
    movie = Movie(**movie)
    try:
        with _session_scope() as session:
            session.add(movie)
            
    except sqlalchemy.exc.IntegrityError as exc:
        # The combination of title and year matches a record already in the database.
        if exc.orig.args[0] == 'UNIQUE constraint failed: movies.title, movies.year':
            msg = exc.orig.args[0]
            logging.error(msg)
            raise exception.MovieDBConstraintFailure(msg) from exc
        
        # The year is not in the valid range.
        if exc.orig.args[0] == 'CHECK constraint failed: movies':
            msg = f"Invalid year '{exc.params[3]}'."
            logging.error(msg)
            raise exception.MovieYearConstraintFailure(msg) from exc
        
        else:
            raise


def find_movies(criteria: FindMovieTypedDict) -> List[MovieUpdateDef]:
    """Search for movies using any supplied_keys.
    
    Note:
        The benefits of lazy evaluation of the SQL search cannot be passed on to the caller as the
        query.count function returns the undeduplicated count which does not match the number of
        deduplicated records returned by the query.
        See https://docs.sqlalchemy.org/en/13/faq/sessions.html#faq-query-deduplicating

    Args:
        criteria: FindMovieDict. A dictionary containing none or more of the following keys:
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

    Returns:
        A list of movies compliant with the search criteria sorted by title and year.
    """
    Movie.validate_columns(criteria.keys())
    
    with _session_scope() as session:
        query = _build_movie_query(session, criteria)

    movies = [MovieUpdateDef(title=movie.title, director=movie.director, minutes=movie.minutes,
                             year=movie.year, notes=movie.notes, tags=[tag.tag for tag in movie.tags])
              for movie in query]
    movies.sort(key=lambda movie: movie['title'] + str(movie['year']))
    return movies


def replace_movie(old_movie: MovieKeyTypedDict, new_movie: MovieTypedDict):
    """Search for one movie and change one or more fields of that movie.

    Args:
        old_movie: Specifies the movie to be replaced.
        new_movie: Specifies the replacing movie.
        
    Raises:
        MovieDBMovieNotFound
            The old movie is no longer present so is no longer capable of being modified.  This
            function neither assumes nor checks that the new_movie information is sufficient to create a
            new valid record.
        MovieDBConstraintFailure
            The new movie has an edited title or year and the new combination matches that of an
            existing record.
    """
    try:
        with _session_scope() as session:
            # Locate the old movie
            try:
                movie = _build_movie_query(session, old_movie).one()
                
            # The old movie has gone and is no longer capable of being modified.
            except sqlalchemy.orm.exc.NoResultFound as exc:
                msg = (f'The movie was not found in the database. It may have been deleted by an '
                       f'external process.')
                logging.error(msg)
                raise exception.MovieDBMovieNotFound(msg) from exc
    
            for k, v in new_movie.items():
                setattr(movie, k, v)
            
    except sqlalchemy.exc.IntegrityError as exc:
        if exc.orig.args[0] == 'UNIQUE constraint failed: movies.title, movies.year':
            msg = exc.orig.args[0]
            logging.error(msg)
            raise exception.MovieDBConstraintFailure(msg) from exc
        else:
            raise


def del_movie(title_year: FindMovieTypedDict):
    """Change fields in records.

    Args:
        title_year: Specifies the movie to be deleted.
    """
    with _session_scope() as session:
        movie = _build_movie_query(session, title_year).one()
        session.delete(movie)


def all_tags() -> List[str]:
    """ List all tags in the database.
    
    Returns: A sorted list of tags
    """
    with _session_scope() as session:
        tags = session.query(Tag.tag)
    return sorted([tag[0] for tag in tags])


def movie_tags(title_year: MovieKeyTypedDict) -> List[str]:
    """ List the tags of a movie.
    
    Returns: A list of tags
    """
    with _session_scope() as session:
        tag_names = session.query(Tag.tag).join(Tag.movies).filter(Movie.title == title_year['title'])
        tag_names = tag_names.filter(Movie.year == title_year['year'])
    return [tag_name[0] for tag_name in tag_names]


def add_tag(new_tag: str):
    """Create the tag unless it already exists.

    Args:
        new_tag: Text of new tag.
    """

    # Add the tag unless it is already in the database.
    try:
        tag = Tag(new_tag)
        with _session_scope() as session:
            session.add(tag)
        pass
    except sqlalchemy.exc.IntegrityError:
        pass


def find_tags(criteria: str) -> List[str]:
    """Find tags which match the supplied pattern.
    
    Args:
        criteria: A match pattern.

    Returns:
        A list of matched tags.
    """
    with _session_scope() as session:
        tags = session.query(Tag).filter(Tag.tag.like(f"%{criteria}%"))
    return [tag.tag for tag in tags]


def add_movie_tag_link(tag: str, movie: MovieKeyTypedDict):
    """Add link between a tag and a movie.

    Args:
        tag: Name of tag.
        movie: Movie which will be linked to the new tag.
    """
    with _session_scope() as session:
        tag = session.query(Tag).filter(Tag.tag == tag).one()
        movie = (session.query(Movie)
                 .filter(Movie.title == movie['title'], Movie.year == movie['year'])
                 .one())
        movie.tags.append(tag)


def edit_tag(old_tag: str, new_tag: str):
    """Edit the tag string.

    Args:
        old_tag:
        new_tag:
    """
    try:
        with _session_scope() as session:
            tag = session.query(Tag).filter(Tag.tag == old_tag).one()
            tag.tag = new_tag
    
    # The specified tag is not available possibly because it was deleted by another process.
    except sqlalchemy.orm.exc.NoResultFound as exc:
        msg = f"The tag {old_tag} is not in the database."
        logging.info(msg)
        raise exception.DatabaseSearchFoundNothing(msg) from exc


def edit_movie_tag_links(movie: MovieKeyTypedDict, old_tags: Iterable[str], new_tags: Iterable[str]):
    """Replace the links to tags associated with a specified movie with links to a new set of tags.
    
    Args:
        movie:
        old_tags: The old set of tags which will be removed from the movie.
        new_tags: The new set of tags which will be linked to the movie.
        
    Any tags which appear in both sets will be ignored.
    This function relinks a movie and its tags. Neither the movie nor the tags are changed.
    """
    try:
        with _session_scope() as session:
            movie = (session.query(Movie)
                     .filter(Movie.title == movie['title'], Movie.year == movie['year'])
                     .one())
            for name in (set(old_tags) - set(new_tags)):
                tag = session.query(Tag).filter(Tag.tag == name).one()
                movie.tags.remove(tag)
            for name in (set(new_tags) - set(old_tags)):
                tag = session.query(Tag).filter(Tag.tag == name).one()
                movie.tags.append(tag)
    except sqlalchemy.orm.exc.NoResultFound as exc:
        msg = f"The movie {movie['title']}, {movie['year']} is not in the database."
        logging.info(msg)
        raise exception.DatabaseSearchFoundNothing(msg) from exc


def del_tag(tag: str):
    """Delete a tag.

    Args:
        tag:
    """
    with _session_scope() as session:
        tag_obj = session.query(Tag).filter(Tag.tag == tag).one()
        session.delete(tag_obj)


class MoviesMetaData(Base):
    """Meta data table schema."""
    __tablename__ = 'meta_data'

    name = Column(String(80), primary_key=True)
    value = Column(String(80))

    def __repr__(self):  # pragma: no cover
        return (self.__class__.__qualname__ +
                f"(name={self.name!r}, value={self.value!r}")


class Movie(Base):
    """Movies table schema."""
    __tablename__ = 'movies'

    id = Column(Integer, sqlalchemy.Sequence('movie_id_sequence'), primary_key=True)
    title = Column(String(80), nullable=False)
    director = Column(String(24))
    minutes = Column(Integer)
    year = Column(Integer, CheckConstraint(f'year>={MUYBRIDGE}'), CheckConstraint('year<10000'),
                  nullable=False)
    notes = Column(Text)
    tmdb_id = Column(Integer)
    original_title = Column(String(80))
    release_date = Column(Date)
    synopsis = Column(Text)
    UniqueConstraint(title, year)

    tags = relationship('Tag', secondary='movie_tag', back_populates='movies')
    reviews = relationship('Review', secondary='movie_review', back_populates='movies')

    def __init__(self, title: str, year: str, director: str = '', minutes: str = '', notes: str = '',
                 tmdb_id: str = '', original_title: str = '', release_date: datetime.date = None,
                 synopsis: str = ''):
    
        # Carry out validation which is not done by SQLAlchemy or sqlite3
        if year == '':
            msg = f"Year string expected but got empty string."
            logging.error(msg)
            raise ValueError(msg)
        
        if minutes == '':
            minutes = 0
        try:
            {int(arg) for arg in [minutes, year]}
        except ValueError as exc:
            msg = (f"{exc}\nA non-integer value has been supplied for either the year "
                   f"or the minute column.")
            logging.error(msg)
            raise

        self.title = title
        self.director = director
        self.minutes = minutes
        self.year = year
        self.notes = notes
        self.tmdb_id = tmdb_id
        self.original_title = original_title
        self.release_date = release_date
        self.synopsis = synopsis

    def __repr__(self):  # pragma: no cover
        return (self.__class__.__qualname__ +
                f"(title={self.title!r}, year={self.year!r}, "
                f"director={self.director!r}, minutes={self.minutes!r}, notes={self.notes!r})")

    @classmethod
    def validate_columns(cls, columns: Iterable[str]):
        """Raise ValueError if any column item is not a column of this class or the Tag class.

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
            logging.error(msg)
            raise ValueError(msg)


class Tag(Base):
    """Table schema for tags."""
    __tablename__ = 'tags'

    id = Column(sqlalchemy.Integer, sqlalchemy.Sequence('tag_id_sequence'), primary_key=True)
    tag = Column(String(24), nullable=False, unique=True)

    movies = relationship('Movie', secondary='movie_tag', back_populates='tags')

    def __init__(self, tag: str):
        self.tag = tag

    def __repr__(self):  # pragma: no cover
        return (self.__class__.__qualname__ +
                f"(tag={self.tag!r})")


class Review(Base):
    """Reviews tables schema.

    This table has been designed to provide a single row for a reviewer and rating value.
    So a 3.5/4 star rating from Ebert will be linked to none or more movies.
    The reviewer can ba an individual like 'Ebert' or an aggregator like 'Rotten Tomatoes.
    max_rating is part of the secondary key. This allows for a particular reviewer changing
    his/her/its rating system.
    """
    __tablename__ = 'reviews'

    id = Column(sqlalchemy.Integer, sqlalchemy.Sequence('review_id_sequence'), primary_key=True)
    reviewer = Column(String(24), nullable=False)
    rating = Column(Integer, nullable=False)
    max_rating = Column(Integer, nullable=False)
    UniqueConstraint(reviewer, rating, max_rating)

    movies = relationship('Movie', secondary='movie_review',
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
def _session_scope() -> Generator[Session, None, None]:
    """Provide a session scope around a series of operations."""
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        msg = (f'An incomplete database session has been rolled back because of exception:\n'
               f'{sys.exc_info()[0].__name__}')
        logging.info(msg)
        raise
    finally:
        session.close()


def _build_movie_query(session: Session, criteria: MovieSearch) -> sqlalchemy.orm.query.Query:
    """Build a query.

    Args:
        session: This function must be run inside a caller supplied Session object.
        criteria: Record selection criteria. See find_movies for detailed description.
            e.g. 'title'-'Solaris'

    Returns:
        An SQL Query object
    """

    # noinspection PyUnresolvedReferences
    movies = session.query(Movie).outerjoin(Movie.tags)
    if 'title' in criteria:
        movies = movies.filter(Movie.title.like(f"%{criteria['title']}%"))
    if 'director' in criteria:
        movies = movies.filter(Movie.director.like(f"%{criteria['director']}%"))
    if 'minutes' in criteria:
        minutes = criteria['minutes']
        try:
            low, high = min(minutes), max(minutes)
        except TypeError:
            low = high = minutes
        if not low:
            low = high
        movies = movies.filter(Movie.minutes.between(low, high))
    if 'year' in criteria:
        year = criteria['year']
        try:
            low, high = min(year), max(year)
        except TypeError:
            low = high = year
        if not low:
            low = high
        movies = movies.filter(Movie.year.between(low, high))
    if 'notes' in criteria:
        movies = movies.filter(Movie.notes.like(f"%{criteria['notes']}%"))
    if 'tags' in criteria:
        tags = criteria['tags']
        if isinstance(tags, str):
            tags = [tags, ]
        movies = (movies.filter(Tag.tag.in_(tags)))
    return movies
