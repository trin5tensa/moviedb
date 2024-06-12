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


def add_movie_tags(engine, tags):
    """..."""
    with Session(engine) as session, session.begin():
        session.add_all([schema.Tag(text=tag) for tag in tags])


def add_full_movie(engine, movie_bag: MovieBag):
    """..."""

    with Session(engine) as session, session.begin():
        movie = schema.Movie(
            title=movie_bag.get("title"),
            year=int(movie_bag.get("year")),
        )

        # Identify existing people records.
        all_people = (stars := movie_bag.get("stars", set())) | (
            directors := movie_bag.get("directors", set())
        )
        stmt = select(schema.Person).where(schema.Person.name.in_(all_people))
        result = session.execute(stmt)
        present_objs = {person for person in result.scalars()}

        # Add new people objects
        new_people = all_people - {person.name for person in present_objs}
        new_objs = {
            schema.Person(name=new_person_name) for new_person_name in new_people
        }
        present_objs |= new_objs

        # Add directors and stars to movie
        movie.directors = {
            person for person in present_objs if person.name in directors
        }
        movie.stars = {person for person in present_objs if person.name in stars}

        # Tags
        # todo later: Handle invalid tag texts. Here they are silently dropped.
        if tags := movie_bag.get("movie_tags"):
            stmt = select(schema.Tag).where(schema.Tag.text.in_(tags))
            result = session.execute(stmt)
            movie.tags = {tag for tag in result.scalars()}

        session.add(movie)


def update_movie(engine: Engine, old_movie: MovieBag, new_movie_bag: MovieBag):
    """..."""
    # engine.echo = True
    with Session(engine) as session:
        with session.begin():
            # todo Tidy up the 'where' statement
            stmt = select(schema.Movie).where(
                schema.Movie.title == old_movie.get("title")
                and schema.Movie.year == old_movie.get("year")
            )
            existing_movie = session.scalar(stmt)

            existing_movie.title = new_movie_bag["title"]
            existing_movie.year = int(new_movie_bag["year"])

            # todo: Identify existing people records.
            # todo: Add new people objects
            # todo: Remove orphans
            # todo: Add directors and stars to movie

            # Tags
            # todo later: Handle invalid tag texts. Here they are silently dropped.
            if movies_tags := new_movie_bag.get("movie_tags"):
                stmt = select(schema.Tag).where(schema.Tag.text.in_(movies_tags))
                result = session.execute(stmt)
                existing_movie.tags = {tag for tag in result.scalars()}

    engine.echo = False


def print_movies(engine):
    """..."""
    print("\nMovies:")
    with Session(engine) as session, session.begin():
        result = session.execute(select(schema.Movie))
        for movie in result.scalars():
            print(
                f"{movie.id=}, {movie.title=}, {movie.year=}, "
                # f"{movie.directors=}, {movie.stars=}, "
                f"{movie.tags=}, "
                # f"{movie.created}, {movie.updated}"
                f""
            )


def print_movie_tags(engine):
    """..."""
    print("\nMovie Tags:")
    with Session(engine) as session, session.begin():
        result = session.execute(select(schema.Tag))
        for tag in result.scalars():
            print(f"{tag=}, {tag.created}, {tag.updated}")


def print_people(engine):
    """..."""
    print("\nPeople:")
    with Session(engine) as session, session.begin():
        result = session.execute(select(schema.Person))
        for person in result.scalars():
            print(
                f"{person.id}, {person.name}, "
                # f"{person.star_of_movies}, "
                # f"{person.director_of_movies}, "
                # f"{person.created}, {person.updated}"
                f""
            )


def start_engine() -> Engine:
    """..."""
    engine = create_engine("sqlite+pysqlite:///:memory:", echo=False)
    schema.Base.metadata.create_all(engine)
    return engine


def main():
    """Integration tests and usage examples."""
    engine = start_engine()
    add_full_movie(engine, title_year)
    add_movie_tags(engine, movie_tags)
    add_full_movie(engine, tagged_movie)
    update_movie(engine, old_movie=tagged_movie, new_movie_bag=new_movie)

    add_full_movie(engine, star_movie)
    add_full_movie(engine, star_movie_2)
    add_full_movie(engine, director_movie)
    add_full_movie(engine, ego_movie)

    print_movies(engine)
    print_movie_tags(engine)
    print_people(engine)


if __name__ == "__main__":
    sys.exit(main())
