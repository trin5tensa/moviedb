"""Prototype Database

Supports the prototyping of DBv1:
Experiments with the select statement
"""

#  Copyright ©2024. Stephen Rigden.
#  Last modified 6/17/24, 8:49 AM by stephen.
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

import json
import sys
from pathlib import Path

from sqlalchemy import create_engine, select, Engine, union_all
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

import schema
from data import *
from globalconstants import *

DATABASE_DIR = "DB" + schema.SCHEMA_VERSION
VERSION_FN = "schema_version"
MOVIE_DATABASE_FN = "movie_database.sqlite"


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
        all_people_names = (stars_names := movie_bag.get("stars", set())) | (
            directors_names := movie_bag.get("directors", set())
        )
        stmt = select(schema.Person).where(schema.Person.name.in_(all_people_names))
        result = session.execute(stmt)
        xtg_people = set(result.scalars().all())

        # Add new people records
        new_people_names = all_people_names - {person.name for person in xtg_people}
        new_people = {
            schema.Person(name=new_person_name) for new_person_name in new_people_names
        }
        all_people = xtg_people | new_people

        # Add directors and stars to movie
        movie.directors = {
            person for person in all_people if person.name in directors_names
        }
        movie.stars = {person for person in all_people if person.name in stars_names}

        # Tags
        # todo later: Handle invalid tag texts. Here they are silently dropped.
        if tags := movie_bag.get("movie_tags"):
            stmt = select(schema.Tag).where(schema.Tag.text.in_(tags))
            result = session.execute(stmt)
            movie.tags = set(result.scalars().all())

        session.add(movie)


def update_movie(engine: Engine, old_movie: MovieBag, update: MovieBag):
    """..."""
    with Session(engine) as session, session.begin():
        # Find 'old' movie
        # noinspection PyTypeChecker
        title_year_union = union_all(
            select(schema.Movie).where(schema.Movie.title == old_movie.get("title")),
            select(schema.Movie).where(schema.Movie.year == int(old_movie.get("year"))),
        )
        stmt = select(schema.Movie).from_statement(title_year_union)
        movie = session.scalar(stmt)

        # Update simple fields (not those with relationships)
        movie.title = update["title"]
        movie.year = int(update["year"])

        # Tags
        # todo later: Handle invalid tag texts. Here they are silently dropped.
        if movies_tags := update.get("movie_tags"):
            stmt = select(schema.Tag).where(schema.Tag.text.in_(movies_tags))
            result = session.execute(stmt)
            movie.tags = set(result.scalars().all())

        # Identify existing people records.
        all_people_names = (new_stars_names := update.get("stars", set())) | (
            new_directors_names := update.get("directors", set())
        )
        stmt = select(schema.Person).where(schema.Person.name.in_(all_people_names))
        result = session.execute(stmt)
        xtg_people = set(result.scalars().all())

        # Add new people records
        new_people_names = all_people_names - {person.name for person in xtg_people}
        new_people = {
            schema.Person(name=new_person_name) for new_person_name in new_people_names
        }
        all_people = xtg_people | new_people

        # Identify potential orphans
        star_orphan_names = {star.name for star in movie.stars} - new_stars_names
        director_orphan_names = {
            director.name for director in movie.directors
        } - new_directors_names
        orphan_names = star_orphan_names | director_orphan_names

        # Add directors and stars to movie
        movie.directors = {
            person for person in all_people if person.name in new_directors_names
        }
        movie.stars = {
            person for person in all_people if person.name in new_stars_names
        }

        # Remove orphans
        stmt = select(schema.Person).where(schema.Person.name.in_(orphan_names))
        result = session.execute(stmt)
        orphans = {person for person in result.scalars()}
        for person in orphans:
            if not person.star_of_movies and not person.director_of_movies:
                session.delete(person)


def print_movies(engine):
    """..."""
    print("\nMovies:")
    with Session(engine) as session, session.begin():
        result = session.execute(select(schema.Movie))
        for movie in result.scalars():
            print(
                f"{movie.id=}, {movie.title=}, {movie.year=}, "
                # f"{movie.created}, {movie.updated}, "
                # f"{movie.updated.second}, {movie.updated.microsecond}, ",
                f"",
                end="",
            )
            if movie.stars:
                print("stars = ", end="")
                for star in movie.stars:
                    print(star.name, end=", ")
            if movie.directors:
                print("directors = ", end="")
                for director in movie.directors:
                    print(director.name, end=", ")
            if movie.tags:
                print("tags = ", end="")
                for tag in movie.tags:
                    print(tag.text, end=", ")
            print()


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
    # Create data directory structure if not already present
    program_path = Path(__file__)
    movie_data_path = program_path.parents[2] / "Movies Data"
    # todo in production version: Log missing movie_data_path
    movie_data_path.mkdir(exist_ok=True)
    database_dir_path = movie_data_path / DATABASE_DIR
    # todo in production version:  Log missing database_path
    database_dir_path.mkdir(exist_ok=True)

    # Get or create metadata file
    schema_version_fp = movie_data_path / f"{VERSION_FN}.json"
    try:
        with open(schema_version_fp) as fp:
            from_json = json.load(fp)
    except FileNotFoundError as exc:
        # todo in production version:  Log missing metafile
        database_file_version = schema.SCHEMA_VERSION

        data = {
            VERSION_FN: database_file_version,
        }
        with open(schema_version_fp, "w") as fp:
            json.dump(data, fp)
    else:
        database_file_version = from_json[VERSION_FN]

    # Does database need to be updated to new schema version?
    if schema.SCHEMA_VERSION != database_file_version:
        # todo in production version:  Log update requirement.
        # todo in production version:  Request user user permission for update.
        print("Version mismatch: Database update required.")

    # Create engine
    database_fn = database_dir_path / MOVIE_DATABASE_FN
    engine = create_engine(f"sqlite+pysqlite:///{database_fn}", echo=False)
    schema.Base.metadata.create_all(engine)

    return engine


def main():
    """Integration tests and usage examples."""
    # todo implement a way of dropping the data from the tables so each run can start with an
    #  empty database.
    engine = start_engine()

    add_full_movie(engine, title_year)
    add_movie_tags(engine, movie_tags)
    add_full_movie(engine, tagged_movie)

    print_movies(engine)
    print_movies(engine)
    print_movie_tags(engine)
    print_people(engine)


if __name__ == "__main__":
    sys.exit(main())
