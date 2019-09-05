"""Import and export data."""

#  Copyright© 2019. Stephen Rigden.
#  Last modified 9/5/19, 7:59 AM by stephen.
#
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
#
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
import csv
import sys
from typing import List, Tuple, Callable

import database
from error import MoviedbInvalidImportData
import utilities


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
        fn: Name of import file.

    Raises:
        ValueError if the header has invalid column names or if required column names are missing.

    """
    good_input = True

    # Create reject filename.
    root, _ = tuple(str(fn).split('.'))
    reject_fn = root + '_reject.csv'

    # Read import file.
    with open(fn, newline='', encoding='utf-8') as csvfile:
        movies_reader = csv.reader(csvfile)

        # Get headers and validate.
        header_row = next(movies_reader)
        header_row = list(map(str.lower, header_row))
        valid_len = len(header_row)

        for row in movies_reader:
            # Validate row length
            if len(row) != valid_len:
                # moviedatabase-#57 DRY reduction
                if good_input:
                    good_input = False
                    reject_coroutine = write_csv_file(reject_fn, header_row)
                reject_coroutine.send(("Row has too many or too few items.",))
                reject_coroutine.send(row)
                continue

            # Write movie to database
            movie = dict(zip(header_row, row))
            try:
                database.add_movie(movie)

            except database.sqlalchemy.exc.IntegrityError as exception:
                # moviedatabase-#57 DRY reduction
                if good_input:
                    good_input = False
                    reject_coroutine = write_csv_file(reject_fn, header_row)
                reject_coroutine.send((str(exception),))
                reject_coroutine.send(row)

            # ValueError is raised by invalid row values.
            except ValueError:
                # moviedatabase-#57 DRY reduction
                if good_input:
                    good_input = False
                    reject_coroutine = write_csv_file(reject_fn, header_row)
                reject_coroutine.send((f'{sys.exc_info()[0].__name__}: {sys.exc_info()[1]}',))
                reject_coroutine.send(row)

            # TypeError is raised by faulty headers so halt row processing.
            except TypeError:
                # moviedatabase-#57 DRY reduction
                if good_input:
                    good_input = False
                    reject_coroutine = write_csv_file(reject_fn, header_row)
                msg = (f"{sys.exc_info()[0].__name__}: The header row is bad.\n"
                       "It is missing a required column, has an invalid column, or has a "
                       "blank column.\n"
                       "Note that only the first error is reported.\n"
                       f"{sys.exc_info()[1]}")
                reject_coroutine.send((msg,))
                break

    if not good_input:
        msg = f"The import file '{fn}' has invalid data. See reject file for details."
        raise MoviedbInvalidImportData(msg)


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


# moviedatabase-#46 remove this function
def main():  # pragma: no cover
    database.connect_to_database()
    import_movies('movies.csv')


# moviedatabase-#46 remove this function
if __name__ == '__main__':  # pragma: no cover
    sys.exit(main())
