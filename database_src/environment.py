"""Database environment functions."""

#  Copyright© 2024. Stephen Rigden.
#  Last modified 9/19/24, 12:26 PM by stephen.
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
import logging
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_src import schema, tables, update

DATA_DIR_NAME = "Movie Data"
SAVED_VERSION = "saved_version"
DATABASE_STEM = "movie_database_"
NO_MOVIE_DATA_DIRECTORY_MSG = "Missing movie data directory."
NO_DATABASE_DIRECTORY_MSG = "Missing database directory."
UPDATE_SUCCESSFUL_MSG = "The database was successfully updated to "
DATABASE_REOPENED_MSG = "The database has been opened for use: Version "


def start_engine():
    """Creates the database environment.

    This will:
        Prepare a database for first use,
        or prepare an existing database for use,
        or update an older version ready for use.

    If the data directory 'Movie Data' does not exist in the expected location a new database
    will be created and readied for first use.

    If the data directory 'Movie Data' exists then the version number of the saved database
    will be retrieved from 'saved_version.json'. If it is the current version the SQL database
    will be started ready for use.

    Otherwise, a new current version database will be created. Data from the old database will
    be copied and transformed before loading into the new database.

    Naming conventions:
        data_dir_name = "Movie Data"
        database_dir_name = schema.VERSION (The current version from the schema module.)
        metadata_name = "saved_version"
        movie_database_name = "movie_database"

    Directory and file structure:
        Movie Data
        Movie Data / schema.VERSION
        Movie Data / schema.VERSION / movie_database_DBv1.sqlite3
        Movie Data / saved_version.json
            1 dict entry → {SAVED_VERSION: schema.VERSION}
    """
    data_dir_path, database_dir_path = _getcreate_directories(
        DATA_DIR_NAME, DATABASE_STEM + schema.VERSION
    )
    saved_version = _getcreate_metadata(data_dir_path)
    _register_session_factory(database_dir_path)

    if saved_version != schema.VERSION:
        _update_database(saved_version, data_dir_path)
    else:
        logging.info(DATABASE_REOPENED_MSG + schema.VERSION)


def _getcreate_directories(
    data_dir_name: str, database_dir_name: str
) -> tuple[Path, Path]:
    """Gets the data directory and database directory paths.

    It will log and create missing directories.

    Args:
        data_dir_name: This is located in the parent directory at the same
        level as the source files.
        database_dir_name: This directory contains the SQL database.

    Returns:
        A Path to the data directory.
        A Path to the database directory.
    """
    program_path = Path(__file__)

    movie_data_path = program_path.parents[2] / data_dir_name
    if not movie_data_path.is_dir():
        logging.info(NO_MOVIE_DATA_DIRECTORY_MSG)
    movie_data_path.mkdir(exist_ok=True)

    database_dir_path = movie_data_path / database_dir_name
    if not database_dir_path.is_dir():
        logging.info(NO_DATABASE_DIRECTORY_MSG)
    database_dir_path.mkdir(exist_ok=True)

    return movie_data_path, database_dir_path


def _getcreate_metadata(data_dir: Path) -> str:
    """Returns the version of the saved SQL database.

    This gets the database version from the metadata file. If it is not
    present the file will be created with a version_text equal to the
    current version.

    Args:
        data_dir: The directory containing the database data files.

    Returns:
        The version of the saved database.
    """
    saved_version_fn = data_dir / (SAVED_VERSION + ".json")
    try:
        with open(saved_version_fn) as fp:
            from_json = json.load(fp)
    except FileNotFoundError:
        data = {SAVED_VERSION: schema.VERSION}
        with open(saved_version_fn, "w") as fp:
            json.dump(data, fp)
        with open(saved_version_fn) as fp:
            from_json = json.load(fp)
    return from_json[SAVED_VERSION]


def _register_session_factory(database_dir: Path):
    """Registers a session factory for the database.

    This creates the SQL engine, creates all the tables from the schema, and
    registers a session factory.

    Args:
        database_dir:
    """
    database_name = DATABASE_STEM + schema.VERSION + ".sqlite3"
    database_fn = database_dir / database_name
    engine = create_engine(f"sqlite+pysqlite:///{database_fn}", echo=False)
    tables.session_factory = sessionmaker(engine)
    schema.Base.metadata.create_all(engine)


def _update_database(old_version: str, data_dir_path: Path):
    """Update the database with data from a previous version.

    This will call code which will extract data from the old version by
    schema reflection. The database is updated with data converted from old
    formats.

    Args:
        old_version: example 'DBv42'
        data_dir_path: example 'Movie Data'
    """
    old_database_name = DATABASE_STEM + old_version + ".sqlite3"
    old_database_fn = data_dir_path / old_version / old_database_name
    movies, tags = update.update_old_database(old_version, old_database_fn)
    for movie in movies:
        tables.add_movie(movie_bag=movie)
    tables.add_tags(tag_texts=tags)

    # Update saved version file with new version number.
    saved_version_fn = data_dir_path / (SAVED_VERSION + ".json")
    with open(saved_version_fn) as fp:
        data = json.load(fp)
    data[SAVED_VERSION] = schema.VERSION
    with open(saved_version_fn, "w") as fp:
        json.dump(data, fp)

    # Log the update as being successfully completed.
    logging.info(UPDATE_SUCCESSFUL_MSG + schema.VERSION)
