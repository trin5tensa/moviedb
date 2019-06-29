"""Exclusive database connections."""
import datetime
import sys
from typing import Optional

# Third party package imports

import sqlalchemy.ext.hybrid
from sqlalchemy import CheckConstraint, Column, ForeignKey, Integer, Sequence, String, Table, Text, UniqueConstraint
from sqlalchemy.ext import declarative
from sqlalchemy.ext.hybrid import hybrid_method
from sqlalchemy.orm import relationship, session, sessionmaker

# Project Imports


# Constants
engine: Optional[sqlalchemy.engine.base.Engine] = None
Session: Optional[session.sessionmaker] = None
SQLAlchemyBase = sqlalchemy.ext.declarative.declarative_base()
movies_tags = Table('movies_seers', SQLAlchemyBase.metadata,
                    Column('movies_id', ForeignKey('movies.id'), primary_key=True),
                    Column('tags_id', ForeignKey('tags.id'), primary_key=True))
movies_reviews = Table('movies_reviews', SQLAlchemyBase.metadata,
                       Column('movies_id', ForeignKey('movies.id'), primary_key=True),
                       Column('reviews_id', ForeignKey('reviews.id'), primary_key=True))


# Variables


# Pure data Dataclasses
# Named tuples


# API Classes


# API Functions
def create_database(filename: str):
    """Create the database in an external file."""
    global engine, Session
    engine = sqlalchemy.create_engine(f"sqlite:///{filename}", echo=False)
    Session = sessionmaker(bind=engine)
    update_metadata(date=str(datetime.datetime.now()))


# Internal Module Classes
class _MetaData(SQLAlchemyBase):
    """Meta data table schema."""
    __tablename__ = 'meta_data'

    name = Column(String(80), primary_key=True)
    value = Column(String(80))

    def __repr__(self):
        return (self.__class__.__qualname__ +
                f"(name={self.name!r}, value={self.value!r}")


class _Movie(SQLAlchemyBase):
    """Movies table schema."""
    __tablename__ = 'movies'

    id = Column(Integer, Sequence('movie_id_sequence'), primary_key=True)
    title = Column(String(80), nullable=False)
    director = Column(String(24), nullable=False)
    minutes = Column(Integer, nullable=False)
    year = Column(Integer, CheckConstraint('year>1877'), CheckConstraint('year<10000'), nullable=False, )
    notes = Column(Text)
    UniqueConstraint(title, year)

    seers = relationship('_Tag', secondary=movies_tags, back_populates='movies')
    reviews = relationship('Review', secondary=movies_reviews, back_populates='movies')

    def __repr__(self):
        return (self.__class__.__qualname__ +
                f"(title={self.title!r}, director={self.director!r}, minutes={self.minutes!r}, "
                f"year={self.year!r}, notes={self.notes!r})")


class _Tag(SQLAlchemyBase):
    """Table schema for entities who have seen a movie."""
    __tablename__ = 'tags'

    id = Column(sqlalchemy.Integer, Sequence('tag_id_sequence'), primary_key=True)
    tag = Column(String(24), nullable=False, unique=True)

    movies = relationship('_Movie', secondary=movies_tags, back_populates='tags')

    def __repr__(self):
        return (self.__class__.__qualname__ +
                f"(tag={self.tag!r})")


class Review(SQLAlchemyBase):
    """Reviews tables schema.

    This table has been designed to provide a single row for a reviewer and rating value. So a 3.5/4 star
    rating from Ebert will be linked to none or more movies.
    The reviewer can ba an individual like 'Ebert' ®or an aggregator like 'Rotten Tomatoes.
    max_rating is part of the secondary key. THis allows for a particular reviewer changing
    his/her/its rating system.
    """
    __tablename__ = 'reviews'

    id = Column(sqlalchemy.Integer, Sequence('review_id_sequence'), primary_key=True)
    reviewer = Column(String(24), nullable=False)
    rating = Column(Integer, nullable=False)
    max_rating = Column(Integer, nullable=False)
    UniqueConstraint(reviewer, rating, max_rating)

    movies = relationship('_Movie', secondary=movies_reviews, back_populates='reviews')

    _percentage: int = None

    # noinspection PyMissingOrEmptyDocstring
    @hybrid_method
    def percentage(self) -> int:
        if self._percentage is None:
            self._percentage = int(100 * self.rating / self.max_rating)
        return self._percentage

    def __repr__(self):
        return (self.__class__.__qualname__ +
                f"(reviewer={self.reviewer!r}, rating={self.rating!r}), max_rating={self.max_rating!r}), ")


# Internal Module Functions
def update_metadata(**kwargs):
    # TODO 8
    pass


# noinspection PyMissingOrEmptyDocstring
def main():
    pass


if __name__ == '__main__':
    sys.exit(main())
