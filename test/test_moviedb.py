"""Tests for moviedatabase."""

#  Copyright© 2019. Stephen Rigden.
#  Last modified 10/8/19, 6:57 AM by stephen.
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
from typing import Tuple

import pytest

import moviedb

TEST_FN = 'test_filename.csv'


@pytest.mark.usefixtures('monkeypatch')
class TestMain:
    def test_start_up_called(self, monkeypatch):
        calls = []
        monkeypatch.setattr(moviedb, 'start_up', lambda: calls.append(True))
        monkeypatch.setattr(moviedb.gui, 'run', lambda: None)
        monkeypatch.setattr(moviedb, 'close_down', lambda: None)
        moviedb.main()
        assert calls == [True]
    
    def test_gui_called(self, monkeypatch):
        monkeypatch.setattr(moviedb, 'start_up', lambda: None)
        calls = []
        monkeypatch.setattr(moviedb.gui, 'run', lambda: calls.append(True))
        monkeypatch.setattr(moviedb, 'close_down', lambda: None)
        moviedb.main()
        assert calls == [True]
    
    def test_close_down_called(self, monkeypatch):
        monkeypatch.setattr(moviedb, 'start_up', lambda: None)
        monkeypatch.setattr(moviedb.gui, 'run', lambda: None)
        calls = []
        monkeypatch.setattr(moviedb, 'close_down',
                            lambda: calls.append(True))
        moviedb.main()
        assert calls == [True]


@pytest.mark.usefixtures('monkeypatch')
class TestStartUp:
    @pytest.fixture()
    def monkeypatch_startup(self, monkeypatch) -> Tuple[list, list]:
        """Class patches.

        Args:
            monkeypatch: pytest fixture

        Returns:
            # moviedb-#82 Update docs
        """
        logger_calls = []
        monkeypatch.setattr(moviedb, 'start_logger',
                            lambda *args: logger_calls.append(args))
        connect_calls = []
        monkeypatch.setattr(moviedb.database, 'connect_to_database',
                            lambda: connect_calls.append(True))
        return logger_calls, connect_calls
    
    def test_start_logger_called(self, monkeypatch_startup):
        expected_path = 'movies'
        expected_filename = 'moviedb'
        logger_calls, _ = monkeypatch_startup
        moviedb.start_up()
        path, filename = logger_calls[0]
        assert path[-len(expected_path):] == expected_path
        assert filename == expected_filename
    
    def test_config_data_initialized(self):
        # moviedb-#82
        #  Why is the test run creating movies.sqlite3 in the test directory?
        #  Add monkeypatch_startup to patch call to database.connect_to_database()
        moviedb.start_up()
        assert isinstance(moviedb.config.app, moviedb.config.Config)
        assert moviedb.config.app.root_window is None
    
    def test_start_database_called(self, monkeypatch_startup):
        _, connect_calls = monkeypatch_startup
        moviedb.start_up()
        assert connect_calls == [True]


def test_start_logger_called(monkeypatch):
    calls = []
    monkeypatch.setattr(moviedb.logging, 'shutdown',
                        lambda: calls.append(True))
    moviedb.close_down()
    assert calls == [True]


def test_start_logger(monkeypatch):
    log_root = 'log dir'
    log_fn = 'filename'
    expected = dict(format='{asctime} {levelname:8} {lineno:4d} {module:20} {message}',
                    style='{',
                    level='INFO',
                    filename=f"{log_root}/{log_fn}.log",
                    filemode='w')
    calls = []
    monkeypatch.setattr(moviedb.logging, 'basicConfig',
                        lambda *args, **kwargs: calls.append(kwargs))
    moviedb.start_logger(log_root, log_fn)
    format_args = calls[0]
    assert format_args == expected


@dataclass
class ArgParser:
    """Test dummy for Argument Parser"""
    verbosity: int = 0
    import_csv: str = None
    database: str = None
    
    def __call__(self):
        return self


@pytest.mark.usefixtures('monkeypatch')
class TestCommand:
    def test_missing_filename_calls_main(self, monkeypatch):
        calls = []
        monkeypatch.setattr(moviedb, 'main', lambda: calls.append(True))
        monkeypatch.setattr(moviedb, 'command_line_args', ArgParser())
        moviedb.command()
        assert calls == [True]
    
    def test_import_movies_called(self, monkeypatch):
        monkeypatch.setattr(moviedb, 'command_line_args', ArgParser(import_csv=TEST_FN))
        monkeypatch.setattr(moviedb.database, 'connect_to_database', lambda: None)
        calls = []
        monkeypatch.setattr(moviedb.impexp, 'import_movies', lambda db_fn: calls.append(db_fn))
        moviedb.command()
        assert calls == [TEST_FN]
    
    def test_import_movies_raises_invalid_data_error(self, monkeypatch):
        test_exc = 'Test Exception'
        
        def dummy_import_movies(_):
            """Error raising dummy.

            Args:
                _: Unused
            """
            raise moviedb.impexp.MoviedbInvalidImportData(test_exc)
        
        print_file = io.StringIO()
        with redirect_stdout(print_file):
            monkeypatch.setattr(moviedb, 'command_line_args', ArgParser(import_csv=TEST_FN))
            monkeypatch.setattr(moviedb.database, 'connect_to_database', lambda: None)
            monkeypatch.setattr(moviedb.impexp, 'import_movies', dummy_import_movies)
            moviedb.command()
        
        lines = [line for line in print_file.getvalue().split('\n')]
        assert lines[0] == test_exc
    
    def test_default_database_called(self, monkeypatch):
        monkeypatch.setattr(moviedb, 'command_line_args', ArgParser(import_csv=TEST_FN))
        calls = []
        monkeypatch.setattr(moviedb.database, 'connect_to_database', lambda: calls.append(True))
        monkeypatch.setattr(moviedb.impexp, 'import_movies', lambda *args: None)
        moviedb.command()
        assert calls == [True]
    
    def test_user_defined_database_called(self, monkeypatch):
        test_db = 'user_defined_filename'
        monkeypatch.setattr(moviedb, 'command_line_args', ArgParser(import_csv=TEST_FN,
                                                                    database=test_db))
        calls = []
        monkeypatch.setattr(moviedb.database, 'connect_to_database',
                            lambda database: calls.append(database))
        monkeypatch.setattr(moviedb.impexp, 'import_movies', lambda *args: None)
        moviedb.command()
        assert calls[0] == test_db
    
    def test_verbosity_called_with_default_database(self, monkeypatch):
        expected_1 = "movies/moviedb.py"
        expected_2 = f"Loading movies from {TEST_FN}"
        expected_3 = "Adding movies to the default database."
        
        print_file = io.StringIO()
        with redirect_stdout(print_file):
            monkeypatch.setattr(moviedb, 'command_line_args', ArgParser(import_csv=TEST_FN,
                                                                        verbosity=42))
            monkeypatch.setattr(moviedb.database, 'connect_to_database', lambda: None)
            monkeypatch.setattr(moviedb.impexp, 'import_movies', lambda database: None)
            moviedb.command()
        
        lines = [line for line in print_file.getvalue().split('\n')]
        assert lines[0][-len(expected_1):] == expected_1
        assert lines[1] == expected_2
        assert lines[2] == expected_3
    
    def test_verbosity_called_with_user_supplied_database(self, monkeypatch):
        test_database = 'user_defined_database'
        expected_1 = "movies/moviedb.py"
        expected_2 = f"Loading movies from {TEST_FN}"
        expected_3 = f"Adding movies to database '{test_database}'."
        
        print_file = io.StringIO()
        with redirect_stdout(print_file):
            monkeypatch.setattr(moviedb, 'command_line_args',
                                ArgParser(import_csv=TEST_FN, verbosity=42, database=test_database))
            monkeypatch.setattr(moviedb.database, 'connect_to_database', lambda *args: None)
            monkeypatch.setattr(moviedb.impexp, 'import_movies', lambda *args: None)
            moviedb.command()
        
        lines = [line for line in print_file.getvalue().split('\n')]
        assert lines[0][-len(expected_1):] == expected_1
        assert lines[1] == expected_2
        assert lines[2] == expected_3
