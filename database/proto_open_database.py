"""Prototype Database

Supports the prototyping of DBv1
"""

#  Copyright ©2024. Stephen Rigden.
#  Last modified 6/26/24, 8:34 AM by stephen.
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

from sqlalchemy import create_engine, select, Engine, func, intersect
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.orm import sessionmaker, Session

import schema
from data import tagged_movie, new_movie, movie_tags, star_movie
from proto_select_examples import select_person_as_director, print_bio
from proto_update_database import update_old_database
from globalconstants import *

MOVIES_DATA_DIR = "Movies Data"
DATABASE_DIR = "DB" + schema.SCHEMA_VERSION
VERSION_FN = "schema_version"
MOVIE_DATABASE_FN = "movie_database.sqlite3"


class DatabaseUpdateCheckZeroError(Exception):
    """A database update cross-check has failed."""


def start_engine() -> sessionmaker[Session]:
    """..."""
    movie_data_path, database_dir_path = create_database_directories()
    schema_version_fp = movie_data_path / f"{VERSION_FN}.json"
    database_file_version = create_metadata_file(schema_version_fp)
    sessionmade = build_engine(database_dir_path)

    # Does database need to be updated to a schema version?
    if schema.SCHEMA_VERSION != database_file_version:
        update_database(
            sessionmade,
            database_file_version,
            movie_data_path,
            schema_version_fp,
        )

    return sessionmade


def create_database_directories() -> tuple[Path, Path]:
    """..."""
    # Create data directory structure if not already present
    program_path = Path(__file__)
    # todo in production version:  Request user permission for creation of new 'Movies Data' as
    #  this may be caused by an external environmental problem.
    #  This is fragile - What happens if the location of this source file changes from
    #  being 'Coding/M2-Movies-2024/database'?
    movie_data_path = program_path.parents[2] / MOVIES_DATA_DIR
    # todo in production version: Log missing movie_data_path
    movie_data_path.mkdir(exist_ok=True)
    database_dir_path = movie_data_path / DATABASE_DIR
    # todo in production version: Log missing database_path
    database_dir_path.mkdir(exist_ok=True)
    return movie_data_path, database_dir_path


def create_metadata_file(schema_version_fp: Path) -> str:
    """..."""
    # Get or create metadata file
    # todo in production version: Add schema metadata datetime stamps
    try:
        with open(schema_version_fp) as fp:
            from_json = json.load(fp)
    except FileNotFoundError:
        # todo in production version:  Log missing metafile
        database_file_version = schema.SCHEMA_VERSION

        data = {
            VERSION_FN: database_file_version,
        }
        with open(schema_version_fp, "w") as fp:
            json.dump(data, fp)
    else:
        database_file_version = from_json[VERSION_FN]
    return database_file_version


def build_engine(database_dir_path: Path) -> sessionmaker[Session]:
    """..."""
    # Create engine
    database_fn = database_dir_path / MOVIE_DATABASE_FN
    # Make a new clean empty database for prototyping
    # clean_the_database(database_fn)
    # engine = create_engine(f"sqlite+pysqlite:///{database_fn}", echo=True)
    engine = create_engine(f"sqlite+pysqlite:///{database_fn}", echo=False)
    # engine = create_engine(f"sqlite+pysqlite:///{database_fn}", echo=True)
    sessionmade = sessionmaker(engine)
    schema.Base.metadata.create_all(engine)
    return sessionmade


def update_database(
    engine: Engine,
    database_file_version: str,
    movie_data_path: Path,
    schema_version_fp: Path,
):
    """..."""
    # Todo Update for use of sessionmaker and integration test
    # todo in production version:  Log update requirement.
    old_tag_count, old_tags, old_movie_count, old_movies = update_old_database(
        database_file_version, movie_data_path, MOVIE_DATABASE_FN
    )

    # Add old tags to new tags table.
    add_movie_tags(engine, old_tags)
    with Session(engine) as session:
        stmt = select(func.count()).select_from(schema.Tag)
        new_tag_count: int = session.execute(stmt).scalar()
    if old_tag_count != new_tag_count:
        # todo in production version: Log exception
        msg = (
            f"Old and new tag record counts do not agree."
            f" {old_tag_count} != {new_tag_count}"
        )
        raise DatabaseUpdateCheckZeroError(msg)

    # Add old movies to new movies table
    for movie in old_movies:
        add_full_movie(engine, movie)
    with Session(engine) as session:
        stmt = select(func.count()).select_from(schema.Movie)
        new_movie_count: int = session.execute(stmt).scalar()
    if old_movie_count != new_movie_count:
        # todo in production version: Log exception
        msg = (
            f"Old and new movie record counts do not agree."
            f" {old_movie_count} != {new_movie_count}"
        )
        raise DatabaseUpdateCheckZeroError(msg)

    # Update metadata file with new version number.
    with open(schema_version_fp) as fp:
        from_json = json.load(fp)
    from_json[VERSION_FN] = schema.SCHEMA_VERSION
    with open(schema_version_fp, "w") as fp:
        json.dump(from_json, fp)


def add_movie_tags(sessionmade: sessionmaker[Session], tags: Sequence[str]):
    """..."""
    with sessionmade() as session, session.begin():
        session.add_all([schema.Tag(text=tag) for tag in tags])


def select_all_tags(sessionmade: sessionmaker[Session]) -> set[str]:
    """..."""
    with sessionmade() as session:
        stmt = select(schema.Tag)
        texts = {tag.text for tag in (session.scalars(stmt))}
    return texts


def select_tag(sessionmade: sessionmaker[Session], match: str) -> set[str]:
    """..."""
    with sessionmade() as session:
        stmt = select(schema.Tag).where(schema.Tag.text.like(f"%{match}%"))
        texts = {tag.text for tag in (session.scalars(stmt))}
    return texts


def delete_tag(sessionmade: sessionmaker[Session], text: str):
    """..."""
    with sessionmade() as session, session.begin():
        # noinspection PyTypeChecker
        stmt = select(schema.Tag).where(schema.Tag.text == text)
        session.delete(session.scalars(stmt).one())


def select_movie(sessionmade: sessionmaker[Session], movie_bag: MovieBag) -> MovieBag:
    """..."""
    # print(f"{movie_bag=}")
    with sessionmade() as session:
        # noinspection PyTypeChecker
        title_year_intersect = intersect(
            select(schema.Movie).where(schema.Movie.title == movie_bag.get("title")),
            select(schema.Movie).where(schema.Movie.year == int(movie_bag.get("year"))),
        )
        stmt = select(schema.Movie).from_statement(title_year_intersect)
        movie = session.scalars(stmt).one()
        # print(f"sm {movie=}")

        movie_bag = MovieBag(
            id=movie.id,
            title=movie.title,
            year=MovieInteger(movie.year),
            notes=movie.notes,
            synopsis=movie.synopsis,
            created=movie.created,
            updated=movie.updated,
            directors=movie.directors,
            stars=movie.stars,
            movie_tags=movie.tags,
        )
        if movie.duration:
            movie_bag["duration"] = MovieInteger(movie.duration)
        return movie_bag


def add_full_movie(sessionmade: sessionmaker[Session], movie_bag: MovieBag):
    """..."""
    try:
        with sessionmade() as session, session.begin():

            movie = schema.Movie(
                title=movie_bag.get("title"),
                year=int(movie_bag.get("year")),
                # duration=int(movie_bag.get("duration")),
                synopsis=movie_bag.get("synopsis"),
                notes=movie_bag.get("notes"),
            )
            if duration := movie_bag.get("duration"):
                movie.duration = duration

            session.add(movie)

            # Identify existing people records.
            all_people_names = (stars_names := movie_bag.get("stars", set())) | (
                directors_names := movie_bag.get("directors", set())
            )
            stmt = select(schema.Person).where(schema.Person.name.in_(all_people_names))
            with session.no_autoflush:
                result = session.execute(stmt)
            xtg_people = set(result.scalars().all())

            # Add new people records
            new_people_names = all_people_names - {person.name for person in xtg_people}
            new_people = {
                schema.Person(name=new_person_name)
                for new_person_name in new_people_names
                if new_person_name != ""
            }

            all_people = xtg_people | new_people

            # Add directors and stars to movie
            movie.directors = {
                person for person in all_people if person.name in directors_names
            }
            movie.stars = {
                person for person in all_people if person.name in stars_names
            }

            # Add tags to movie.
            # todo later: Handle invalid tag texts. Here they are silently dropped.
            if tags := movie_bag.get("movie_tags", set()):
                stmt = select(schema.Tag).where(schema.Tag.text.in_(tags))
                result = session.execute(stmt)
                movie.tags = set(result.scalars().all())

    except IntegrityError:
        # todo in production code: Log exception
        raise


def update_movie(
    sessionmade: sessionmaker[Session], old_movie: MovieBag, update: MovieBag
):
    """..."""
    with sessionmade() as session, session.begin():
        # Find 'old' movie
        # noinspection PyTypeChecker
        # session.bind.echo = True
        title_year_intersect = intersect(
            select(schema.Movie).where(schema.Movie.title == old_movie.get("title")),
            select(schema.Movie).where(schema.Movie.year == int(old_movie.get("year"))),
        )
        stmt = select(schema.Movie).from_statement(title_year_intersect)
        movie = session.scalars(stmt).one()

        # Update simple fields (not those with relationships)
        movie.title = update["title"]
        movie.year = int(update["year"])
        movie.duration = update.get("duration")
        movie.synopsis = update.get("synopsis")
        movie.notes = update.get("notes")

        # # Tags
        # # todo later: Handle invalid tag texts. Here they are silently dropped.
        if movies_tags := update.get("movie_tags"):
            stmt = select(schema.Tag).where(schema.Tag.text.in_(movies_tags))
            movie.tags = set(session.scalars(stmt).all())

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
        for person in {person for person in session.scalars(stmt)}:
            if not person.star_of_movies and not person.director_of_movies:
                session.delete(person)

        # session.bind.echo = False


def delete_movie(sessionmade: sessionmaker[Session], movie: MovieBag):
    """..."""
    with sessionmade() as session, session.begin():
        # noinspection PyTypeChecker
        title_year_intersect = intersect(
            select(schema.Movie).where(schema.Movie.title == movie.get("title")),
            select(schema.Movie).where(schema.Movie.year == int(movie.get("year"))),
        )
        stmt = select(schema.Movie).from_statement(title_year_intersect)
        movie = session.scalars(stmt).one()

        # Identify potential orphans
        star_orphan_names = {star.name for star in movie.stars}
        director_orphan_names = {director.name for director in movie.directors}
        orphan_names = star_orphan_names | director_orphan_names

        session.delete(movie)

        # Remove orphans
        stmt = select(schema.Person).where(schema.Person.name.in_(orphan_names))
        for person in {person for person in session.scalars(stmt)}:
            if not person.star_of_movies and not person.director_of_movies:
                session.delete(person)


def select_all_people(sessionmade: sessionmaker[Session]) -> set[str]:
    """..."""
    with sessionmade() as session:
        stmt = select(schema.Person)
        names = {person.name for person in session.scalars(stmt)}
    return names


def select_people(sessionmade: sessionmaker[Session], match: str) -> set[str]:
    """..."""
    with sessionmade() as session:
        stmt = select(schema.Person).where(schema.Person.name.like(f"%{match}%"))
        names = {person.name for person in session.scalars(stmt)}
    return names


def print_all_movies(sessionmade: sessionmaker[Session]):
    """..."""
    print()
    with sessionmade() as session:
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


def clean_the_database(database_fn: Path):
    """..."""
    # todo Not for production: Use for prototyping only.
    # Delete the database file
    database_fn.unlink(missing_ok=True)


def igr_test_tags(session_config: sessionmaker[Session]):
    """..."""
    texts = select_all_tags(session_config)
    for text in texts:
        print(f"{text=}")

    print()
    texts = select_tag(session_config, "again")
    for text in texts:
        print(f"{text=}")

    print()
    new_tags = ["new tag 1", "new tag 2", "new tag 3"]
    add_movie_tags(session_config, new_tags)
    texts = select_all_tags(session_config)
    for text in texts:
        print(f"{text=}")

    print()
    for new_tag in new_tags:
        delete_tag(session_config, new_tag)
    texts = select_all_tags(session_config)
    for text in texts:
        print(f"{text=}")


def igr_test_people(sessionmade: sessionmaker[Session]):
    """..."""
    print()
    for name in select_all_people(sessionmade):
        print(name)

    print()
    for name in select_people(sessionmade, "sidney"):
        print(name)


def igr_test_movies(sessionmade: sessionmaker[Session]):
    """..."""
    print("\nSelecting 'Killers of the Flower Moon'")
    movie = MovieBag(title="Killers of the Flower Moon", year=MovieInteger(2023))
    print(select_movie(sessionmade, movie))

    print("\nAdding 'Tagged Movie'")
    try:
        add_full_movie(sessionmade, tagged_movie)
    except IntegrityError:
        print(
            "Tagged Movie: (sqlite3.IntegrityError) UNIQUE constraint failed: "
            "movie.title, movie.year"
        )
    print(select_movie(sessionmade, tagged_movie))

    print("\nDeleting 'Tagged Movie'")
    delete_movie(sessionmade, tagged_movie)

    try:
        print(select_movie(sessionmade, tagged_movie))
    except NoResultFound:
        print(f"{tagged_movie['title']}, {tagged_movie['year']} successfully deleted.")

    print("\nUpdating 'Tagged Movie' with 'Updated Movie'")
    try:
        delete_movie(sessionmade, tagged_movie)
    except NoResultFound:
        pass
    try:
        delete_movie(sessionmade, new_movie)
    except NoResultFound:
        pass
    add_movie_tags(sessionmade, movie_tags)

    add_full_movie(sessionmade, tagged_movie)
    update_movie(sessionmade, tagged_movie, new_movie)
    try:
        print(select_movie(sessionmade, tagged_movie))
    except NoResultFound:
        print("Tagged Movie was not found in database and that was expected.")
    try:
        print(select_movie(sessionmade, new_movie))
    except NoResultFound:
        print("New Movie was not found in database and this was unexpected.")

    for tag in movie_tags:
        delete_tag(sessionmade, tag)

    print()
    # delete_movie(sessionmade, tagged_movie)
    delete_movie(sessionmade, new_movie)

    with sessionmade() as session:
        stmt = select(schema.Person)
        for person in [person for person in session.scalars(stmt) if person.id >= 595]:
            print_bio(sessionmade, person)


def main():
    """Integration tests and usage examples."""
    sessionmade = start_engine()

    # igr_test_tags(sessionmade)
    # igr_test_people(sessionmade)
    igr_test_movies(sessionmade)
    # select_person_as_director(sessionmade)


if __name__ == "__main__":
    sys.exit(main())
