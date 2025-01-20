"""Main movie database program"""

#  Copyright© 2025. Stephen Rigden.
#  Last modified 1/8/25, 1:01 PM by stephen.
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

import concurrent.futures
import json
import logging
import os
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any

import config
import database
import mainwindow
from threadsafe_printer import SafePrinter


PROGRAM_VERSION = "1.0.0"


def main():
    """Initializes the program, runs it, and executes close down actions."""
    start_up()
    logging.info(f"The program started successfully. Version {PROGRAM_VERSION}")
    with SafePrinter() as safeprint:
        config.current.safeprint = safeprint
        with concurrent.futures.ThreadPoolExecutor() as executor:
            config.current.threadpool_executor = executor
            mainwindow.run_tktcl()
    close_down()


def start_up():
    """Initialize the program."""
    program_path = Path(__file__)
    start_logger(program_path.cwd(), program_path)
    config.current = config.CurrentConfig()
    load_config_file(program_path)
    database.environment.start_engine()


def close_down():
    """Execute close down activities."""
    # Check the database for orphans.
    database.tables.delete_all_orphans()

    # Save the config.Config pickle file
    save_config_file()

    logging.info("The program is ending.")
    logging.shutdown()


def start_logger(root_dir: Path, program: Path):
    """Start the logger."""
    q_name = os.path.normpath(os.path.join(root_dir, f"{program.stem}.log"))
    # noinspection PyArgumentList
    logging.basicConfig(
        format="{asctime} {levelname:8} {lineno:4d} {module:20} {message}",
        style="{",
        level="INFO",
        filename=q_name,
        filemode="w",
    )


def load_config_file(program: Path):
    """Create the persistent config object."""

    try:
        data = _json_load()

    except FileNotFoundError as exc:
        msg = (
            f"The config save file was not found. A new version will be initialized. "
            f"{exc.strerror}: {exc.filename}"
        )
        logging.info(msg)

        # Initialise persistent application data for first use
        _, name = os.path.split(program)
        name, _ = os.path.splitext(name)
        config.persistent = config.PersistentConfig(name.title(), PROGRAM_VERSION)

    else:
        config.persistent = config.PersistentConfig(**data)


def _json_load() -> dict:
    """Load JSON from file.

    Returns:
        A dictionary which will be used to create a PersistentConfig object.
    """
    with open(_json_path()) as fp:
        data = json.load(fp)
    return data


def save_config_file():
    """Save the persistent config object."""
    # noinspection PyTypeChecker
    _json_dump(asdict(config.persistent), _json_path())


def _json_path() -> Path:
    """Returns: A path name for the config file."""
    program_path = Path(__file__)
    json_dir = program_path.parent.parent
    json_fn = program_path.stem + config.CONFIG_JSON_SUFFIX
    return json_dir / json_fn


def _json_dump(obj: Any, path: Path):
    """
    Dump json to file.

    The separation of save_config_file and _save_config_file allows the test module to use a
    temporary in-memory file location during file operations.

    Args:
        obj: A json formatted string.
        path: Path of config file.
    """
    with open(path, "w") as fp:
        # noinspection PyTypeChecker
        json.dump(obj, fp)


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
