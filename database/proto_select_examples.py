"""Prototype Database

Supports the prototyping of DBv1
"""

#  Copyright ©2024. Stephen Rigden.
#  Last modified 6/22/24, 6:27 AM by stephen.
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
from pathlib import Path

from sqlalchemy import create_engine, select, Engine
from sqlalchemy.orm import Session

import schema

DATABASE_DIR = "DB" + schema.SCHEMA_VERSION
VERSION_FN = "schema_version"
MOVIE_DATABASE_FN = "movie_database.sqlite3"


def select_person_as_director(engine, name: str = "Martin Scorsese"):
    """Print a person and the films they've directed."""
    with Session(engine) as session:
        stmt = select(schema.Person).where(schema.Person.name == name)
        result = session.execute(stmt)
        for person in result.scalars().all():
            print("\n", person.id, person.name, person.director_of_movies)
            print("\tDirected:")
            for movie in person.director_of_movies:
                print(f"\t{movie}")


def start_engine() -> Engine:
    """..."""
    program_path = Path(__file__)
    movie_data_path = program_path.parents[2] / "Movies Data"
    movie_data_path.mkdir(exist_ok=True)
    database_dir_path = movie_data_path / DATABASE_DIR
    database_dir_path.mkdir(exist_ok=True)

    # Create engine
    database_fn = database_dir_path / MOVIE_DATABASE_FN
    engine = create_engine(f"sqlite+pysqlite:///{database_fn}", echo=False)
    schema.Base.metadata.create_all(engine)
    return engine


def main():
    """Integration tests and usage examples."""
    engine = start_engine()
    select_person_as_director(engine)


if __name__ == "__main__":
    sys.exit(main())
