"""Main moviedatabase program"""

#  Copyright© 2019. Stephen Rigden.
#  Last modified 9/14/19, 10:23 AM by stephen.
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

import argparse
import logging
import os
import sys

import database
from error import MoviedbInvalidImportData
import impexp


def main():
    """Initialize the program, run it, and execute close down activities."""
    # moviedb-#50 DayBreak
    #       Add logging calls throughout code
    start_up()
    print('Dummy call to GUI.')
    logging.info('THe program is running.')
    close_down()


def start_up():
    """Initialize the program."""
    root_dir, program_name = os.path.split(__file__)
    program, _ = program_name.split('.')
    start_logger(root_dir, program)


def close_down():
    """Execute close down activities."""
    logging.shutdown()


def start_logger(root_dir: str, program: str):
    """Start the logger."""
    q_name = os.path.normpath(os.path.join(root_dir, f"{program}.log"))
    print(q_name)
    logging.basicConfig(format='{asctime} {levelname:8} {lineno:4d} {module:20} {message}',
                        style='{',
                        level='INFO',
                        filename=q_name, filemode='w')


def command_line_args() -> argparse.Namespace:
    """Parse the command line arguments.

    Returns:
        Parsed arguments.
    """
    
    # moviedb-#50 Testme (monkeypatch argparse.ArgumentParser )
    description_msg = ("Invoke without arguments to run the gui. Invoke with the optional "
                       "'import_csv' argument to import a csv delimited text file.")
    parser = argparse.ArgumentParser(description=description_msg)
    parser.add_argument('-i', '--import_csv', default=None,
                        help='a csv import file. See impexp.py for format requirements.')
    parser.add_argument('-d', '--database', default=None,
                        help='database filename. Enter an empty string to create an in-memory database')
    parser.add_argument('-v', '--verbosity', action='count', default=0, help='verbosity')
    print(parser.parse_args())
    return parser.parse_args()


def command():
    """Command line parse and dispatch."""
    args = command_line_args()
    
    # Run GUI
    if not args.import_csv:
        return main()
    
    # An empty string is a valid SQLAlchemy non-default value for the database name.
    non_default_database = args.database == '' or args.database
    
    if args.verbosity >= 1:
        print(f"Running {__file__}")
        print(f'Loading movies from {args.import_csv}')
        if non_default_database:
            print(f"Adding movies to database '{args.database}'.")
        else:
            print("Adding movies to the default database.")
    
    if non_default_database:
        database.connect_to_database(args.database)
    else:
        database.connect_to_database()
    
    try:
        impexp.import_movies(args.import_csv)
    except MoviedbInvalidImportData as exc:
        print(exc)


if __name__ == '__main__':  # pragma: no cover
    sys.exit(command())
