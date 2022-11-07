"""Tests for movie database."""
#  Copyright (c) 2022-2022. Stephen Rigden.
#  Last modified 11/7/22, 8:01 AM by stephen.
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

import io
from contextlib import contextmanager, redirect_stdout
from dataclasses import dataclass
from functools import partial
from typing import Tuple

import pytest

import config
import moviedb


TEST_FN = 'test_filename.csv'


class TestMain:
    """
    Given: config.current has been initialized with a new instance of config.CurrentConfig
    When main() is called
    Then:
        start_up() is called.
        A successful start message is logged.
        The target of the SafePrinter() context manager is stored in config.current.safeprint.
        The target of the ThreadPoolExecutor() context manager is stored in config.current.executor.
        gui.run() is called.
        close_down() is called.
    """
    logging_calls = []
    func_calls = set()
    
    def func_call_helper(self, monkeypatch, func):
        monkeypatch.setattr(func, lambda: self.func_calls.add(func))
    
    @pytest.fixture()
    def main_patches(self, monkeypatch):
        """Monkeypatches and instruments all actions within main()."""
        monkeypatch.setattr('moviedb.config.current', moviedb.config.CurrentConfig())
        self.func_call_helper(monkeypatch, 'moviedb.start_up')
        monkeypatch.setattr(moviedb.logging, 'info', lambda msg: self.logging_calls.append(msg))
        monkeypatch.setattr(moviedb, 'SafePrinter', self.dummy_safe_printer)
        monkeypatch.setattr(moviedb.concurrent.futures, 'ThreadPoolExecutor', self.dummy_tp_executor)
        self.func_call_helper(monkeypatch, 'moviedb.gui.run')
        self.func_call_helper(monkeypatch, 'moviedb.close_down')
        
    @pytest.fixture()
    def main(self, main_patches, monkeypatch):
        moviedb.main()
        
    @contextmanager
    def dummy_safe_printer(self):
        yield 'dummy safe printer context manager called.'
        
    @contextmanager
    def dummy_tp_executor(self):
        yield 'dummy threadpool executor context manager called.'
        
    def test_start_up_is_called(self, main):
        assert {'moviedb.start_up'} & self.func_calls == {'moviedb.start_up'}
        
    def test_successful_start_message_is_logged(self, main):
        assert 'The program started successfully.' == self.logging_calls.pop()
        
    def test_safeprint_is_stored_in_config(self, main):
        assert moviedb.config.current.safeprint == 'dummy safe printer context manager called.'
        
    def test_tp_executor_is_stored_in_config(self, main):
        assert moviedb.config.current.threadpool_executor == 'dummy threadpool executor context manager called.'
        
    def test_gui_run_is_called(self, main):
        assert {'moviedb.gui.run'} & self.func_calls == {'moviedb.gui.run'}

    def test_close_down_is_called(self, main):
        assert {'moviedb.close_down'} & self.func_calls == {'moviedb.close_down'}


class TestStartUp:
    
    # noinspection PyMissingOrEmptyDocstring
    @pytest.fixture()
    def monkeypatch_startup(self, monkeypatch) -> Tuple[list, list, list]:
        logger_calls = []
        monkeypatch.setattr(moviedb, 'start_logger', lambda *args: logger_calls.append(args))
        load_config_calls = []
        monkeypatch.setattr(moviedb, 'load_config_file', lambda *args: load_config_calls.append(args))
        connect_calls = []
        monkeypatch.setattr(moviedb.database, 'connect_to_database', lambda: connect_calls.append(True))
        return logger_calls, load_config_calls, connect_calls
    
    def test_start_logger_called(self, monkeypatch_startup):
        program_path = moviedb.Path(moviedb.__file__)
        expected_path = program_path.cwd()
        expected_filename = program_path
        logger_calls, _, _ = monkeypatch_startup
        moviedb.start_up()
        path, filename = logger_calls[0]
        assert path == expected_path
        assert filename == expected_filename
    
    def test_load_config_file(self, monkeypatch_startup):
        program_path = moviedb.Path(moviedb.__file__)
        expected_filename = program_path.name
        
        _, load_config_calls, _ = monkeypatch_startup
        moviedb.start_up()
        filename = load_config_calls[0][0]
        assert filename == expected_filename
    
    def test_start_database_called(self, monkeypatch_startup):
        _, _, connect_calls = monkeypatch_startup
        moviedb.start_up()
        assert connect_calls == [True]


class TestLoadConfigFile:
    program = 'test_program_name'
    version = 'test version'
    
    def test_existing_file_loaded_into_config_persistent(self, monkeypatch):
        expected = config.PersistentConfig(program=self.program, program_version=self.version)
        data = moviedb.asdict(expected)
        with self.fut_runner(self.program, data, monkeypatch):
            assert config.persistent == expected
    
    def test_absent_file_initializes_config_persistent(self, monkeypatch):
        expected = moviedb.VERSION = 'test first use'
        data = None
        with self.fut_runner(self.program, data, monkeypatch, file_not_found=True):
            assert config.persistent.program_version == expected
    
    @contextmanager
    def fut_runner(self, program, data, monkeypatch, file_not_found=False):
        if file_not_found:
            monkeypatch.setattr(moviedb, '_json_load', partial(self.dummy__json_load, program))
        else:
            monkeypatch.setattr(moviedb, '_json_load', lambda: data)

        yield moviedb.load_config_file(program)
    
    def dummy__json_load(self, *args):
        raise FileNotFoundError


def test_save_config_file(monkeypatch):
    persistent = moviedb.config.PersistentConfig(program='test_program', program_version='42')
    path = moviedb._json_path()
    calls = []
    monkeypatch.setattr(moviedb, '_json_dump', lambda *args: calls.append(args))
    moviedb._json_dump(persistent, path)
    
    assert calls == [(persistent, path)]


def test_save_config_file_called(monkeypatch):
    calls = []
    monkeypatch.setattr(moviedb, 'save_config_file', lambda *args: calls.append(True))
    monkeypatch.setattr(moviedb.logging, 'info', lambda *args: None)
    monkeypatch.setattr(moviedb.logging, 'shutdown', lambda: None)
    moviedb.close_down()
    assert calls == [True]


def test_ending_of_program_logged(monkeypatch):
    monkeypatch.setattr(moviedb, 'save_config_file', lambda *args: None)
    calls = []
    monkeypatch.setattr(moviedb.logging, 'info', lambda *args: calls.append(args))
    monkeypatch.setattr(moviedb.logging, 'shutdown', lambda: None)
    moviedb.close_down()
    assert calls == [('The program is ending.', )]


def test_start_logger_called(monkeypatch):
    monkeypatch.setattr(moviedb, 'save_config_file', lambda *args: None)
    monkeypatch.setattr(moviedb.logging, 'info', lambda *args: None)
    calls = []
    monkeypatch.setattr(moviedb.logging, 'shutdown',
                        lambda: calls.append(True))
    moviedb.close_down()
    assert calls == [True]


def test_start_logger(monkeypatch):
    log_root = moviedb.Path('log dir')
    log_fn = moviedb.Path('filename')
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


def test__json_load(monkeypatch, tmp_path):
    # Instrument the call to json_load
    expected_data = 'test json loads data'
    calls = []
    
    def dummy_json_load(*args):
        calls.append((args, expected_data))
        
    # Create a test dummy file in tmp_path
    fn = tmp_path / 'dummy_file.text'
    persistent = moviedb.config.PersistentConfig(program='test_program', program_version='42')
    moviedb._json_dump(moviedb.asdict(persistent), fn)

    # Call json_load
    monkeypatch.setattr(moviedb.json, 'load', partial(dummy_json_load))
    monkeypatch.setattr(moviedb, '_json_path', lambda: fn)
    moviedb._json_load()
    
    # Test the calling arguments
    fp = calls[0][0][0]
    assert isinstance(fp, io.TextIOWrapper)
    path = moviedb.Path(fp.name)
    assert path.name == 'dummy_file.text'
    
    # Test the return value
    data = calls[0][1]
    assert data is expected_data


def test__json_path():
    program_name = moviedb.Path(moviedb.__file__).stem
    suffix = config.CONFIG_JSON_SUFFIX
    assert moviedb._json_path().name == program_name + suffix
    
    
def test__json_dump(monkeypatch, tmp_path):
    persistent = moviedb.config.PersistentConfig(program='test_program', program_version='42')
    json_obj = moviedb.asdict(persistent)
    path = tmp_path / 'dummy_file.df'
    
    calls = []
    monkeypatch.setattr(moviedb.json, 'dump', lambda *args: calls.append(args))
    moviedb._json_dump(json_obj, path)
    
    assert calls[0][0] == json_obj
    fp = calls[0][1]
    assert isinstance(fp, io.TextIOWrapper)
    path = moviedb.Path(fp.name)
    assert path.name == 'dummy_file.df'

    
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
