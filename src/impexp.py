# Python package imports


# Third party package imports


# Project Imports
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
    Subsequent records must match the first row in number of items and their position in the row.

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
    pass


# Internal Module Classes


# Internal Module Functions
