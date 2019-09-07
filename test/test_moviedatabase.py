"""Tests for moviedatabase."""

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

import io
from contextlib import redirect_stdout
from dataclasses import dataclass

import pytest

import moviedatabase


TEST_FN = 'test_filename.csv'


@dataclass
class ArgParser:
    """Test dummy for Argument Parser"""
    verbosity: int = 0
    filename: str = TEST_FN
    database: str = None

    def __call__(self):
        return self


def test_missing_filename_raises_error(monkeypatch):
    expected = 'moviedb.py: the following arguments are required: filename'
    monkeypatch.setattr(moviedatabase, '_command_line_args', ArgParser(filename=''))
    monkeypatch.setattr(moviedatabase.database, 'connect_to_database', lambda: None)
    monkeypatch.setattr(moviedatabase.impexp, 'import_movies', lambda *args: None)
    with pytest.raises(ValueError) as exception:
        moviedatabase.main()
    assert exception.type is ValueError
    assert exception.value.args[0] == expected


def test_import_movies_called(monkeypatch):
    monkeypatch.setattr(moviedatabase, '_command_line_args', ArgParser())
    monkeypatch.setattr(moviedatabase.database, 'connect_to_database', lambda: None)
    calls = []
    monkeypatch.setattr(moviedatabase.impexp, 'import_movies', lambda db_fn: calls.append(db_fn))
    moviedatabase.main()
    assert calls == [TEST_FN]


def test_default_database_called(monkeypatch):
    monkeypatch.setattr(moviedatabase, '_command_line_args', ArgParser())
    calls = []
    monkeypatch.setattr(moviedatabase.database, 'connect_to_database', 
                        lambda *args, **kwargs: calls.append((args, kwargs)))
    monkeypatch.setattr(moviedatabase.impexp, 'import_movies', lambda *args: None)
    moviedatabase.main()
    assert calls == [((), {})]


def test_user_defined_database_called(monkeypatch):
    test_db = 'user_defined_filename'
    monkeypatch.setattr(moviedatabase, '_command_line_args', ArgParser(database=test_db))
    calls = []
    monkeypatch.setattr(moviedatabase.database, 'connect_to_database',
                        lambda *args, **kwargs: calls.append((args, kwargs)))
    monkeypatch.setattr(moviedatabase.impexp, 'import_movies', lambda *args: None)
    moviedatabase.main()
    assert calls == [((test_db, ), {})]


def test_verbosity_called_with_default_database(monkeypatch):
    expected_1 = "movies/moviedatabase.py"
    expected_2 = f"Loading movies from {TEST_FN}"
    expected_3 = "Adding movies to the default database."

    print_file = io.StringIO()
    with redirect_stdout(print_file):
        monkeypatch.setattr(moviedatabase, '_command_line_args', ArgParser(verbosity=42))
        monkeypatch.setattr(moviedatabase.database, 'connect_to_database', lambda: None)
        monkeypatch.setattr(moviedatabase.impexp, 'import_movies', lambda *args: None)
        moviedatabase.main()

    lines = [line for line in print_file.getvalue().split('\n')]
    assert lines[0][-23:] == expected_1
    assert lines[1] == expected_2
    assert lines[2] == expected_3


def test_verbosity_called_with_user_supplied_database(monkeypatch):
    test_database = 'user_defined_database'
    expected_1 = "movies/moviedatabase.py"
    expected_2 = f"Loading movies from {TEST_FN}"
    expected_3 = f"Adding movies to database '{test_database}'."

    print_file = io.StringIO()
    with redirect_stdout(print_file):
        monkeypatch.setattr(moviedatabase, '_command_line_args',
                            ArgParser(verbosity=42, database=test_database))
        monkeypatch.setattr(moviedatabase.database, 'connect_to_database', lambda *args: None)
        monkeypatch.setattr(moviedatabase.impexp, 'import_movies', lambda *args: None)
        moviedatabase.main()

    lines = [line for line in print_file.getvalue().split('\n')]
    assert lines[0][-23:] == expected_1
    assert lines[1] == expected_2
    assert lines[2] == expected_3


def test_command_line_arguments_called():
    namespace = moviedatabase._command_line_args()
    assert namespace.database is None
    assert namespace.filename[-11:] == 'movies/test'
    assert namespace.verbosity == 0
