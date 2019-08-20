# Python package imports
import csv
import sys

# Third party package imports


# Project Imports
from src.error import CoroutineCloseException
import src.database as database


# Constants


# Variables


# Pure data Dataclasses
# Named tuples


# API Classes


# API Functions
def import_movies(fn: str):
    """Import a csv file into the database.

    File format
    The first record will be a header row which must contain the column names 'title' and 'director'.
    It may contain column names 'minutes', 'year', and 'notes'.
    Subsequent records must match the first row in number  of items and their position in the row.

    Validation
    The entire file will be rejected if there are any invalid names in the first row.
    Individual records will be rejected if they are the wrong length.
    They will also be rejected if they violate database integrity rules.

    Output FIle
    Rejected records will be written to a file of the same name with a suffix of '.reject'.
    The header row will be written to that file as the first record.

    Args:
        fn:

    Raises:

    """
    # Create reject filename.
    root, _ = tuple(str(fn).split('.'))
    reject_fn = root + '.reject'

    # Set up reject coroutine.
    reject_coroutine = write_reject_coroutine(reject_fn)
    print('\nc50 reject_coroutine =', reject_coroutine)
    next(reject_coroutine)

    # Read import file.
    with open(fn, newline='', encoding='utf-8') as csvfile:
        movies_reader = csv.reader(csvfile)

        # Validate headers.
        headers = next(movies_reader)
        print('\nc100', headers)
        valid_len = len(headers)

        # Send bad header to reject file.
        reject_coroutine.send('Data Error: Bad header row.')
        reject_coroutine.send(headers)

        for row in movies_reader:
            movie = {k: v for (k, v) in zip(headers, row)}
            print()
            print(movie['Title'])
            print(movie)

            # Send bad record to reject file.
            reject_coroutine.send('Bad data row.')
            reject_coroutine.send(movie)

    print('\nc200 Calling reject_coroutine.close(). ')
    reject_coroutine.throw(CoroutineCloseException)

    # moviedatabase-#43 Are essential header fields preseent
    # moviedatabase-#43 Are any invalid header fields present
    # moviedatabase-#43 Save required record length
    # moviedatabase-#43 Derive reject file name
    # moviedatabase-#43 Loop through import file records
    # moviedatabase-#43 Validate record length
    # moviedatabase-#43 Call database.add_record
    # moviedatabase-#43 Write reject record to reject file


# Internal Module Classes


# Internal Module Functions
def write_reject_coroutine(reject_fn: str):
    print(f'mcr100 write_reject_coroutine has been called with {reject_fn}', )
    with open(reject_fn, 'w+', encoding='utf-8') as csvfile:
        print(f"mcr150: File '{reject_fn}' opened for writing.")
        while True:
            try:
                received = yield
            except CoroutineCloseException:
                print('mcr300 Ending write_reject_coroutine')
            else:
                print('mcr200 received =', received)


if __name__ == '__main__':
    # sys.exit(import_movies('moviedatabase.py'))
    sys.exit(import_movies('movies.csv'))
