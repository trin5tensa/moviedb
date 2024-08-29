"""Database environment functions."""

#  Copyright© 2024. Stephen Rigden.
#  Last modified 8/29/24, 8:27 AM by stephen.
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

from pathlib import Path

from sqlalchemy.orm import Session, sessionmaker

from database_src import schema

session_factory: sessionmaker[Session] | None = None


def start_engine():
    """Creates the database environment.

    This will:
        Prepare a database for first use,
        or prepare an existing database for use,
        and update an older version.

    Pseudocode:
        Call _getcreate_directories
        Call _getcreate_metadata
        Call _register_session_factory
        Save the session factory to tables.session_factory
        If current version is different to saved version
            call _update_database(old_version: str, old_version_fn: Path)
            which will update the database with data from the previous version.
        Log successful start of database
    """
    data_directory = "Movie Data"
    version_text = "version"
    database_dir_prefix = "DB"
    # todo NB: Version number format is "DBv0" or "DBv1"
    current_version = database_dir_prefix + schema.VERSION
    metadata_fn = "schema_version.json"
    movie_database_fn = "movie_database.sqlite3"


def _getcreate_directories(
    data_directory: str, current_version: str
) -> tuple[Path, Path]:
    """Gets the data directory and database directory paths.

    If either directory is not present it will be created.

    Args:
        data_directory: This is located in the parent directory of the source
            data files directory.
        current_version: This directory contains the SQL database.

    Returns:
        A Path to the data directory.
        A Path to the database directory.
    """
    pass


def _getcreate_metadata(
    data_directory: Path, metadata_fn: str, current_version: dict
) -> str:
    """Returns the version of the saved SQL database.

    This gets the database version from the metadata file. If it is not
    present the file will be created with a version_text equal to the
    current version.

    Args:
        data_directory: The directory containing the database data files.
        metadata_fn: The name of the metadata file.
        current_version: A dict with the single entry of
            <version text>: <saved version>

    Returns:
        The version of the saved database.
    """
    pass


def _register_session_factory(database_directory: Path):
    """Registers a session factory for the database.

    This creates the SQL engine, creates all the tables from the schema, and
    registers a session factory.

    Args:
        database_directory:
    """
    pass


def _update_database(old_version: str, old_version_fn: Path):
    """Update the database with data from a previous version.

    This will call code which will extract data from the old version by
    schema reflection. Movie data is returned in movie bag format allowing
    use of standard table module functions for updating.

    Raises:
        UnrecognizedOldVersion if the old version number is not recognized.
        DatabaseUpdateCheckZeroError if old and new record counts don't match.

    Pseudocode:
        Call update.update_old_database(old_version: str, old_version_fn: Path)
            returning tags: set[str], movies: list[MovieBag]
        Call tables.add_tags
        Call tables.add_movie for each movie in list.
        Update metafile with new version number
        Log the update as being successfully completed
    """
    pass
