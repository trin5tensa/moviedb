"""Main moviedatabase program"""

#  Copyright© 2019. Stephen Rigden.
#  Last modified 9/7/19, 8:58 AM by stephen.
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
import sys

import database
from error import MoviedbInvalidImportData
import impexp


def _command_line_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Import movies from a csv file.')
    parser.add_argument('filename',
                        help='a csv import file. See impexp.py for format requirements.')
    parser.add_argument('-d', '--database', help='database filename. Enter an empty '
                                                 'string to create an in-memory database')
    parser.add_argument('-v', '--verbosity', action='count', default=0, help='verbosity')
    return parser.parse_args()


def main():
    """Command line parse and dispatch."""
    args = _command_line_args()

    # Intercept empty string (which is accepted by argparse as a valid filename).
    if not args.filename:
        raise ValueError("moviedb.py: the following arguments are required: filename")

    non_default_database = args.database == '' or args.database

    if args.verbosity >= 1:
        print(f"Running {__file__}")
        print(f'Loading movies from {args.filename}')
        if non_default_database:
            print(f"Adding movies to database '{args.database}'.")
        else:
            print("Adding movies to the default database.")

    if non_default_database:
        database.connect_to_database(args.database)
    else:
        database.connect_to_database()

    try:
        impexp.import_movies(args.filename)
    except MoviedbInvalidImportData as exc:
        print(exc)


if __name__ == '__main__':  # pragma: no cover
    sys.exit(main())
