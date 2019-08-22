# Python package imports
# TODO Remove layout reminder comments.
import csv
import sys

# Third party package imports


# Project Imports
from src.error import CoroutineCloseException
import src.database as database
import src.utilities as utilities


# Constants
REQUIRED_HEADERS = {'title', 'year'}


# Pure data Dataclasses
# Named tuples


# API Classes


# API Functions
def import_movies(fn: str):
    """Import a csv file into the database.

    File format
    The first record will be a header row which must contain the column names 'title' and 'year'.
    It may contain column names 'minutes', 'director', and 'notes'.
    Subsequent records must match the first row in number  of items and their position in the row.

    Validation
    The entire file will be rejected if there are any invalid names in the first row.
    Individual records will be rejected if they are the wrong length.
    They will also be rejected if they violate database integrity rules.

    Output FIle
    Rejected records will be written to a file of the same name with a suffix of '.reject'.
    The valid header row will be written to that file as the first record as a convenience.

    Args:
        fn:

    Raises:
        ValueError if the header has invalid column names or if required column names are missing.

    """
    # Create reject filename.
    root, _ = tuple(str(fn).split('.'))
    reject_fn = root + '_reject.csv'

    # Set up reject file writer.
    reject_coroutine = write_csv_file(reject_fn)

    # Read import file.
    with open(fn, newline='', encoding='utf-8') as csvfile:
        movies_reader = csv.reader(csvfile)

        # Get headers and validate.
        headers = next(movies_reader)
        headers = list(map(str.lower, headers))
        # moviedatabase-#43 Replace with new API function valid_movie_columns.
        valid_columns = database._Movie.valid_import_columns()

        # Are 'title' and 'year' present?
        # moviedatabase-#43 Try removing this title validation and using a 'try' around
        #  database.add_movie.
        missing_header = REQUIRED_HEADERS - set(headers)
        if missing_header:
            missing_header = ', '.join(missing_header)
            msg = f"Required column(s) '{missing_header}' is or are missing from the header record."
            # moviedatabase-#50 Add logging
            raise ValueError(msg)

        # Are there any fields which should not be present?
        # moviedatabase-#43 Try removing this title validation and using a 'try' around
        #  database.add_movie.
        wrong_headers = set(headers) - valid_columns
        if wrong_headers:
            wrong_headers = ', '.join(wrong_headers)
            msg = f"Invalid column name(s) '{wrong_headers}'."
            # moviedatabase-#50 Add logging
            raise ValueError(msg)

        # Write valid headers to reject file.
        reject_coroutine.send(headers)
        valid_len = len(headers)

        for row in movies_reader:
            # Validate row length
            if len(row) != valid_len:
                # moviedatabase-#50 Add logging
                reject_coroutine.send(row)
                continue

            # Write movie to database
            movie = dict(zip(headers, row))
            try:
                database.add_movie(movie)
            except database.sqlalchemy.exc.IntegrityError:
                # moviedatabase-#50 Add logging
                reject_coroutine.send(row)

    # moviedatabase-#43 CoroutineCloseException not necessary - remove
    reject_coroutine.throw(CoroutineCloseException)


# Internal Module Classes


@utilities.coroutine_primer
def write_csv_file(fn: str):
    """Coroutine: Write a csv file.

    received = yield:
        A csv row formatted as a list of strings. Each item will become part of a column in the csv
        table.
    """
    with open(fn, 'w+', encoding='utf-8') as csvfile:
        csv_writer = csv.writer(csvfile)
        while True:
            try:
                received = yield
            # moviedatabase-#43 CoroutineCloseException not necessary - remove
            except CoroutineCloseException:
                pass
            else:
                csv_writer.writerow(received)


def main():
    database.connect_to_database()
    import_movies('movies.csv')


if __name__ == '__main__':
    sys.exit(main())
