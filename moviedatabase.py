"""Main moviedatabase program"""
#  Copyright© 2019. Stephen Rigden.
import argparse
import sys

import database
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

    if args.verbosity >= 1:
        print(f"Running {__file__}")
        print(f'Loading movies from {args.filename}')
        if args.database:
            print(f"Adding movies to database '{args.database}'.")
        else:
            print("Adding movies to the default database.")

    if args.database:
        database.connect_to_database(args.database)
    else:
        database.connect_to_database()
    impexp.import_movies(args.filename)


if __name__ == '__main__':  # pragma: no cover
    sys.exit(main())
