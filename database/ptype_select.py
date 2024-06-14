"""Prototype Database

Supports the prototyping of DBv1:
Experiments with the select statement
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

from sqlalchemy import create_engine, select, Engine
from sqlalchemy.orm import Session

import schema
from data import *
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


def start_engine() -> Engine:
    """..."""
    engine = create_engine("sqlite+pysqlite:///:memory:", echo=False)
    schema.Base.metadata.create_all(engine)
    return engine


def select_tags(engine):
    """..."""
    print()
    with Session(engine) as session:
        stmt = select(schema.Tag).where(schema.Tag.text == "4 Star")
        result = session.execute(stmt)
        # for tag in result.scalars():
        #     print(f"{tag=}")

    print()
    new_tags = ["5 Star", "4 Star", "No Star"]

    # engine.echo = True
    with Session(engine) as session:
        stmt = select(schema.Tag).where(schema.Tag.text.in_(new_tags))
        result = session.execute(stmt)
        in_ids = [tag.id for tag in result.scalars()]
        for id_ in in_ids:
            print(f"{session.get(schema.Tag, id_)=}")
    print(f"{in_ids=}")
    engine.echo = False

    print()
    # engine.echo = True
    with Session(engine) as session:
        stmt = select(schema.Tag).where(schema.Tag.text.not_in(new_tags))
        result = session.execute(stmt)
        in_ids = [tag.id for tag in result.scalars()]
        for id_ in in_ids:
            print(f"{session.get(schema.Tag, id_)=}")
    print(f"{in_ids=}")
    engine.echo = False

    print()
    # engine.echo = True
    with Session(engine) as session:
        match_tags = session.execute(
            select(schema.Tag).where(schema.Tag.text.in_(new_tags))
        )
        found_tags = {tag.id for tag in match_tags.scalars()}
    print(f"{found_tags=}")
    engine.echo = False


def main():
    """Integration tests and usage examples."""
    engine = start_engine()
    add_basic_movie(engine, title_year)
    add_movie_tags(engine, movie_tags[:])
    print_movies(engine)
    print_movie_tags(engine)

    select_tags(engine)


if __name__ == "__main__":
    sys.exit(main())
