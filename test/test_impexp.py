"""Tests for import module."""
#  Copyright© 2019. Stephen Rigden.
import pytest

import impexp


GOOD_DATA = """title,year,minutes,notes
Hamlet,1996,242,
Revanche,2008,122,Oscar nominated"""
NO_TITLE = """year,minutes,notes
Hamlet,1996,242
"""
NO_YEAR = 'title,director,minutes,notes,'
BAD_COLUMN = """title,year,garbage
Hamlet,1996,242
"""
BAD_FIELD = """title,year
Hamlet,1996,Branagh,242,this always will be,garbage,
"""
VIOLATION_DATA = """title,year,notes
Hamlet,1996,1
Hamlet,1996,2"""


@pytest.fixture(scope='session')
def path(tmpdir_factory):
    """Create a temporary directory."""
    path = tmpdir_factory.mktemp('tempdir')
    return path


def test_row_length_validation(path):
    """Test validation of correct number of fields in data row."""
    expected = ("title,year\n"
                "Row has too many or too few items.\n"
                "Hamlet,1996,Branagh,242,this always will be,garbage,\n")
    bad_field_fn = path / 'bad_field.csv'
    bad_field_fn.write(BAD_FIELD)
    reject_fn = path / 'bad_field_reject.csv'
    impexp.import_movies(bad_field_fn)
    assert reject_fn.read() == expected


def test_add_movie_called(path, monkeypatch):
    """Test database.add_movie called."""
    expected = [dict(title='Hamlet', year='1996', minutes='242', notes=''),
                dict(title='Revanche', year='2008', minutes='122', notes='Oscar nominated')]
    calls = []

    def mock_add_movie(movie: dict):
        """Accumulate the arguments of each call in an external list. """
        calls.append(movie)

    monkeypatch.setattr(impexp.database, 'add_movie', mock_add_movie, raising=True)
    good_data_fn = path / 'good_data.csv'
    good_data_fn.write(GOOD_DATA)

    impexp.import_movies(good_data_fn)
    assert calls == expected


def test_column_heading_validation(path, monkeypatch):
    """Test validation of invalid field."""
    expected = ('title,year,garbage\n'
                '"TypeError: The header row is bad.\n'
                'It is missing a required column, has an invalid column, '
                'or has a blank column.\n'
                'Note that only the first error is reported.\n'
                'test error message"\n')

    # noinspection PyUnusedLocal
    def mock_add_movie(movie: dict):
        """Test dummy: Raise error"""
        raise TypeError("test error message")

    monkeypatch.setattr(impexp.database, 'add_movie', mock_add_movie, raising=True)
    bad_column_fn = path / 'bad_column.csv'
    bad_column_fn.write(BAD_COLUMN)
    impexp.import_movies(bad_column_fn)
    reject_fn = path / 'bad_column_reject.csv'
    assert reject_fn.read() == expected


def test_database_integrity_violation(path, monkeypatch):
    """Test database integrity violation causes record rejection."""
    expected = ('title,year,notes\n'
                '"(builtins.int) 3\n'
                '[SQL: 1]\n'
                '[parameters: 2]\n'
                '(Background on this error at: http://sqlalche.me/e/gkpj)"\n'
                'Hamlet,1996,2\n')
    calls = []

    def mock_add_movie(movie: dict):
        """Accumulate the arguments of each call in an external list. """
        calls.append(movie)
        if len(calls) > 1:
            raise impexp.database.sqlalchemy.exc.IntegrityError(1, 2, 3)

    monkeypatch.setattr(impexp.database, 'add_movie', mock_add_movie, raising=True)
    violation_data_fn = path / 'violation_data.csv'
    violation_data_fn.write(VIOLATION_DATA)
    reject_fn = path / 'violation_data_reject.csv'
    impexp.import_movies(violation_data_fn)
    assert reject_fn.read() == expected
