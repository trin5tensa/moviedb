"""Tests for import module."""

#  Copyright (c) 2020-2022. Stephen Rigden.
#  Last modified 11/26/22, 12:59 PM by stephen.
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
BAD_ROW_DATA = """title,year,notes
Hamlet,1996,1"""


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
    with pytest.raises(impexp.MoviedbInvalidImportData):
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
                'test error message"\n""\n')

    # noinspection PyUnusedLocal
    def mock_add_movie(movie: dict):
        """Test dummy: Raise error"""
        raise TypeError("test error message")

    monkeypatch.setattr(impexp.database, 'add_movie', mock_add_movie, raising=True)
    bad_column_fn = path / 'bad_column.csv'
    bad_column_fn.write(BAD_COLUMN)
    with pytest.raises(impexp.MoviedbInvalidImportData):
        impexp.import_movies(bad_column_fn)
    reject_fn = path / 'bad_column_reject.csv'
    assert reject_fn.read() == expected


# noinspection DuplicatedCode
def test_database_integrity_violation(path, monkeypatch):
    """Test database integrity violation causes record rejection."""
    expected_left = ('title,year,notes\n"(builtins.int) 3\n[SQL: 1]\n[parameters: 2]\n'
                     '(Background on this error at: ')
    expected_right = 'Hamlet,1996,2\n'
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
    with pytest.raises(impexp.MoviedbInvalidImportData):
        impexp.import_movies(violation_data_fn)
        
    assert reject_fn.read()[:90] == expected_left
    assert reject_fn.read()[-14:] == expected_right


# noinspection DuplicatedCode
def test_invalid_row_values(path, monkeypatch):
    """Test database integrity violation causes record rejection."""
    error_msg = 'Hid behind tapestry.'
    expected = ('title,year,notes\n'
                f'ValueError: {error_msg}\n'
                'Hamlet,1996,1\n')

    # noinspection PyUnusedLocal, DuplicatedCode
    def mock_add_movie(movie: dict):
        """Force add_movie call to raise ValueError."""
        raise ValueError(error_msg)

    monkeypatch.setattr(impexp.database, 'add_movie', mock_add_movie, raising=True)
    violation_data_fn = path / 'violation_data.csv'
    violation_data_fn.write(BAD_ROW_DATA)
    reject_fn = path / 'violation_data_reject.csv'
    with pytest.raises(impexp.MoviedbInvalidImportData):
        impexp.import_movies(violation_data_fn)
    assert reject_fn.read() == expected


def test_create_reject_file(path, monkeypatch):
    error_msg = 'Unsuccessful bank robbery'
    expected = ("title,year,minutes,notes\n"
                f"ValueError: {error_msg}\n"
                "Hamlet,1996,242,\n"
                f"ValueError: {error_msg}\n"
                "Revanche,2008,122,Oscar nominated\n")

    # noinspection PyUnusedLocal, DuplicatedCode
    def mock_add_movie(movie: dict):
        """Force add_movie call to raise ValueError."""
        raise ValueError(error_msg)

    monkeypatch.setattr(impexp.database, 'add_movie', mock_add_movie, raising=True)
    data_fn = path / 'data.csv'
    data_fn.write(GOOD_DATA)
    reject_fn = path / 'data_reject.csv'

    with pytest.raises(impexp.MoviedbInvalidImportData):
        impexp.import_movies(data_fn)
    
    assert reject_fn.read() == expected
