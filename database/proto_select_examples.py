"""Prototype Database

Supports the prototyping of DBv1
"""

#  Copyright ©2024. Stephen Rigden.
#  Last modified 6/27/24, 6:48 AM by stephen.
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


from sqlalchemy import select
from sqlalchemy.orm import sessionmaker, Session

import schema

DATABASE_DIR = "DB" + schema.SCHEMA_VERSION
VERSION_FN = "schema_version"
MOVIE_DATABASE_FN = "movie_database.sqlite3"


def print_person_as_director(
    sessionmade: sessionmaker[Session],
    name: str = "Martin Scorsese",
):
    """Print a person and the films they've directed."""
    with sessionmade() as session:
        # noinspection PyTypeChecker
        stmt = select(schema.Person).where(schema.Person.name == name)
        for person in session.scalars(stmt):
            print("\n", person.id, person.name, person.director_of_movies)
            print("\tDirected:")
            for movie in person.director_of_movies:
                print(f"\t{movie}")


def print_bio(
    sessionmade: sessionmaker[Session],
    person: schema.Person,
):
    """Print a person and the films they've directed."""
    with sessionmade():
        print(person)
        print("\tDirected:")
        for movie in person.director_of_movies:
            print(f"\t{movie}")
        print("\tStarred:")
        for movie in person.star_of_movies:
            print(f"\t{movie}")
