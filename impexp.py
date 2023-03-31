"""Import and export data."""

#  Copyright (c) 2022-2022. Stephen Rigden.
#  Last modified 10/15/22, 12:37 PM by stephen.
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

import csv
import sys
from typing import Callable, List, Tuple

import database
import utilities


# noinspection GrazieInspection
def import_movies(fn: str):
    """Import a csv file into the database.

    File format
    The first record will be a header row which must contain the column names 'title' and 'year'.
    It may contain column names 'minutes', 'director', and 'notes'.
    The fields of each row must comply with the columns defined by the headed row.

    Validation
    The entire file will be rejected if there are any invalid names in the first row.
    Individual records will be rejected if they are the wrong length or if they violate
    the database's integrity rules.

    Output FIle
    Rejected records will be written to a file of the same name with a suffix of '_reject.csv'.
    The valid header row will be written to that file as the first record as a convenience to the user.

    Args:
        fn: Name of import file.
    """
    reject_file_created = False

    with open(fn, newline='', encoding='utf-8') as csvfile:
        movies_reader = csv.reader(csvfile)

        # Get headers and validate.
        header_row = next(movies_reader)
        header_row = list(map(str.lower, header_row))
        valid_len = len(header_row)
        write_reject_file = create_reject_file(fn, header_row)

        for row in movies_reader:
            # Validate row length
            if len(row) != valid_len:
                msg = ("Row has too many or too few items.",)
                write_reject_file(msg, row)
                reject_file_created = True
                continue

            # Write movie to database
            movie = dict(zip(header_row, row))
            try:
                database.add_movie(movie)

            except database.sqlalchemy.exc.IntegrityError as exception:
                msg = (str(exception),)
                write_reject_file(msg, row)
                reject_file_created = True

            # ValueError is raised by invalid row values.
            except ValueError:
                msg = (f'{sys.exc_info()[0].__name__}: {sys.exc_info()[1]}',)
                write_reject_file(msg, row)
                reject_file_created = True

            # TypeError is raised by faulty headers so halt row processing.
            except TypeError:
                msg = (f"{sys.exc_info()[0].__name__}: The header row is bad.\n"
                       "It is missing a required column, has an invalid column, or has a "
                       "blank column.\n"
                       "Note that only the first error is reported.\n"
                       f"{sys.exc_info()[1]}"),
                row = ('',)
                write_reject_file(msg, row)
                reject_file_created = True
                break

    # Let the user know there if there are input data problems which need fixing.
    if reject_file_created:
        msg = (f"The import file '{fn}' has invalid data. "
               f"See '{fn}_reject.csv' file for details.")
        raise MoviedbInvalidImportData(msg)


class MoviedbInvalidImportData(Exception):
    """Exception raised for bad import file data."""


# noinspection GrazieInspection
def create_reject_file(fn: str, header_row: List[str]) -> Callable:
    """Return a reject file writer.
    
    On first call this write will create the reject file and write the column headers as the first row.
    ON this and all subsequent calls the error and the line causing the error will be written.

    Args:
        fn:
        header_row:

    Returns:
        A writer routine that will write an error to the reject file. The write will usually consist of:
        1) THe headers if they have not already been written
        2) The error message
        3) The line at fault.
    """
    root, _ = tuple(str(fn).split('.'))
    reject_fn = root + '_reject.csv'
    good_input = True
    reject_coroutine = None

    def wrapped(msg: Tuple[str], row: Tuple[str]):
        """Write an error message and the tuple to the reject file.

        Args:
            msg: The error message
            row: The tuple read from the input csv file.
        """
        nonlocal good_input, reject_coroutine
        if good_input:
            good_input = False
            reject_coroutine = write_csv_file(reject_fn, header_row)
        reject_coroutine.send(msg)
        reject_coroutine.send(row)

    return wrapped


@utilities.coroutine_primer
def write_csv_file(fn: str, header_row: List[str]):
    """Coroutine: Write a csv file.

    received = yield:
        A csv row formatted as a list of strings. Each item will become part of a column in the csv
        table.
    """
    with open(fn, 'w+', encoding='utf-8') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(header_row)
        while True:
            received = yield
            csv_writer.writerow(received)
