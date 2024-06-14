"""Prototype Database

Supports the prototyping of DBv1
"""

#  Copyright ©2024. Stephen Rigden.
#  Last modified 6/12/24, 6:53 AM by stephen.
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

import sys

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

import schema
from data import title_year, movie_tags, tagged_movie
from globalconstants import *


def add_basic_movie(engine, movie_in: MovieBag):
    """..."""
    # print(f"{new_movie=}")
    with Session(engine) as session:
        movie = schema.Movie(
            title=movie_in.get("title"),
            year=int(movie_in.get("year")),
        )
        session.add(movie)
        session.commit()
        movie_in.update(
            MovieBag(
                id=movie.id,
                created=movie.created,
                updated=movie.updated,
            )
        )


def add_tagged_movie(engine, movie_in: MovieBag):
    """..."""
    # engine.echo = True
    with Session(engine) as session:
        match_tags = session.execute(
            select(schema.Tag).where(schema.Tag.text.in_(movie_in["movie_tags"]))
        )
        found_tags = {tag for tag in match_tags.scalars()}

        movie = schema.Movie(
            title=movie_in.get("title"), year=int(movie_in.get("year")), tags=found_tags
        )
        session.add(movie)
        session.commit()

        movie_in.update(
            MovieBag(
                id=movie.id,
                created=movie.created,
                updated=movie.updated,
            )
        )
    engine.echo = False


def print_movies(engine):
    """..."""
    with Session(engine) as session:
        result = session.execute(select(schema.Movie))
        for movie in result.scalars():
            print(f"{movie=}")


def add_movie_tags(engine, tags):
    """..."""
    with Session(engine) as session:
        session.add_all([schema.Tag(text=tag) for tag in tags])
        session.commit()


def print_movie_tags(engine):
    """..."""
    with Session(engine) as session:
        result = session.execute(select(schema.Tag))
        for tag in result.scalars():
            print(f"{tag=}")


def main():
    """Integration tests and usage examples."""
    engine = create_engine("sqlite+pysqlite:///:memory:", echo=False)
    schema.Base.metadata.create_all(engine)

    # Create simple movies
    add_basic_movie(engine, title_year)
    print(f"\n{title_year=}")
    # try:
    #     add_basic_movie(engine, title_year)
    # except IntegrityError:
    #     print("IntegrityError - non unique title and year")
    # try:
    #     add_basic_movie(engine, title_low_year)
    # except IntegrityError:
    #     print("IntegrityError - year < min")
    # try:
    #     add_basic_movie(engine, title_high_year)
    # except IntegrityError:
    #     print("IntegrityError - year >= max")

    # Create Movie Tags
    add_movie_tags(engine, movie_tags[:])

    # Add movie with tag
    add_tagged_movie(engine, tagged_movie)

    print("\n\n")
    print_movies(engine)
    print("\n\n")
    print_movie_tags(engine)


if __name__ == "__main__":
    sys.exit(main())
