"""Tests for movie database."""

#  Copyright ©2021. Stephen Rigden.
#  Last modified 3/5/21, 8:14 AM by stephen.
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
from contextlib import contextmanager, redirect_stdout
from dataclasses import dataclass
from typing import Tuple

import pytest

import moviedb


TEST_FN = 'test_filename.csv'


class TestMain:
    def test_start_up_called(self, class_patches, monkeypatch):
        calls = []
        monkeypatch.setattr(moviedb, 'start_up', lambda: calls.append(True))
        moviedb.main()
        assert calls == [True]

    def test_gui_called(self, class_patches, monkeypatch):
        calls = []
        monkeypatch.setattr(moviedb.gui, 'run', lambda: calls.append(True))
        moviedb.main()
        assert calls == [True]

    def test_close_down_called(self, class_patches, monkeypatch):
        calls = []
        monkeypatch.setattr(moviedb, 'close_down',
                            lambda: calls.append(True))
        moviedb.main()
        assert calls == [True]

    def test_logging_info_called(self, class_patches):
        self.info_calls = []
        moviedb.main()
        assert self.info_calls == ['The program started successfully.']

    info_calls = []

    # noinspection PyMissingOrEmptyDocstring
    @pytest.fixture()
    def class_patches(self, monkeypatch):
        monkeypatch.setattr(moviedb, 'start_up', lambda: None)
        monkeypatch.setattr(moviedb.gui, 'run', lambda: None)
        monkeypatch.setattr(moviedb, 'close_down', lambda: None)
        monkeypatch.setattr(moviedb.logging, 'info',
                            lambda msg: self.info_calls.append(msg))


class TestStartUp:
    
    # noinspection PyMissingOrEmptyDocstring
    @pytest.fixture()
    def monkeypatch_startup(self, monkeypatch) -> Tuple[list, list, list]:
        logger_calls = []
        monkeypatch.setattr(moviedb, 'start_logger',
                            lambda *args: logger_calls.append(args))
        load_config_calls = []
        monkeypatch.setattr(moviedb, 'load_config_file', lambda *args: load_config_calls.append(args))
        connect_calls = []
        monkeypatch.setattr(moviedb.database, 'connect_to_database',
                            lambda: connect_calls.append(True))
        return logger_calls, load_config_calls, connect_calls
    
    def test_start_logger_called(self, monkeypatch_startup):
        expected_path = 'movies'
        expected_filename = 'moviedb'
        logger_calls, _, _ = monkeypatch_startup
        moviedb.start_up()
        path, filename = logger_calls[0]
        assert path[-len(expected_path):] == expected_path
        assert filename == expected_filename
    
    def test_config_data_initialized(self, monkeypatch_startup):
        expected_path = 'movies'
        expected_filename = 'moviedb'
        _, load_config_calls, _ = monkeypatch_startup
        moviedb.start_up()
        path, filename = load_config_calls[0]
        assert path[-len(expected_path):] == expected_path
        assert filename == expected_filename
    
    def test_start_database_called(self, monkeypatch_startup):
        _, _, connect_calls = monkeypatch_startup
        moviedb.start_up()
        assert connect_calls == [True]


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
    
    
class TestLoadConfigFile:
    TEST_PARENT_DIR = 'Test Parent Dir'
    TEST_ROOT_DIR = 'Test Root Dir'
    TEST_PROGRAM_NAME = 'test_program_name'
    TEST_VERSION = '42.0.0001'
    
    def test_pickle_load_called(self, monkeypatch, tmpdir):
        pickle_load_calls = []
        monkeypatch.setattr(moviedb.pickle, 'load', lambda *args: pickle_load_calls.append(args))
        with self.class_context(tmpdir, create_config_file=True):
            assert isinstance(pickle_load_calls[0][0], io.BufferedReader)
            assert pickle_load_calls[0][0].name[-35:] == 'Parent Dir/test_program_name.pickle'
    
    def test_config_app_updated_with_read_data(self, tmpdir):
        with self.class_context(tmpdir, create_config_file=True):
            assert moviedb.config.app == moviedb.config.Config(self.TEST_PROGRAM_NAME,
                                                               self.TEST_VERSION)

    def test_file_not_found_logged(self, monkeypatch, tmpdir):
        logging_info_calls = []
        monkeypatch.setattr(moviedb.logging, 'info', lambda *args: logging_info_calls.append(args))
        info_text = "The config save file was not found. A new version will be initialized."
        path_string = (self.TEST_PARENT_DIR + '/' + self.TEST_PROGRAM_NAME +
                       moviedb.config.CONFIG_PICKLE_EXTENSION)
        with self.class_context(tmpdir, create_config_file=False):
            assert logging_info_calls[0][0][:70] == info_text
            assert logging_info_calls[0][0][-40:] == path_string
    
    def test_config_app_initialised_for_first_use(self, tmpdir):
        with self.class_context(tmpdir, create_config_file=False):
            assert moviedb.config.app == moviedb.config.Config(self.TEST_PROGRAM_NAME, moviedb.VERSION)
    
    @contextmanager
    def class_context(self, tmpdir, create_config_file):
        hold_config_app = moviedb.config.app
        config_pickle_dir = tmpdir.mkdir(self.TEST_PARENT_DIR)
        config_pickle_fn = self.TEST_PROGRAM_NAME + moviedb.config.CONFIG_PICKLE_EXTENSION
        config_pickle_path = moviedb.os.path.normpath(moviedb.os.path.join(
                config_pickle_dir, config_pickle_fn))
        root_dir = config_pickle_dir / self.TEST_ROOT_DIR
        
        if create_config_file:
            test_config_file = moviedb.config.Config(self.TEST_PROGRAM_NAME, self.TEST_VERSION)
            with open(config_pickle_path, 'wb') as f:
                moviedb.pickle.dump(test_config_file, f)
        
        yield moviedb.load_config_file(root_dir, self.TEST_PROGRAM_NAME)
        moviedb.config.app = hold_config_app

    
def test_save_config_file(monkeypatch):
    hold_config_app = moviedb.config.app
    moviedb.config.app = moviedb.config.Config('test moviedb', 'test version')

    calls = []
    monkeypatch.setattr(moviedb, '_save_config_file', lambda *args: calls.append(args))
    moviedb.save_config_file()
    
    assert calls[0][0][-34:] == 'Movies Project/test moviedb.pickle'
    moviedb.config.app = hold_config_app


def test__save_config_file(monkeypatch, tmpdir):
    test_parent_dir = 'Test Parent Dir'
    test_program_name = 'test_program_name'

    hold_config_app = moviedb.config.app
    moviedb.config.app = moviedb.config.Config('test moviedb', 'test version')

    pickle_fn = (tmpdir.mkdir(test_parent_dir) /
                 test_program_name + moviedb.config.CONFIG_PICKLE_EXTENSION)

    calls = []
    monkeypatch.setattr(moviedb.pickle, 'dump', lambda *args: calls.append(args))
    
    moviedb._save_config_file(pickle_fn)

    assert calls[0][0] == moviedb.config.app
    assert isinstance(calls[0][1], io.BufferedWriter)
    assert calls[0][1].name[-35:] == 'Parent Dir/test_program_name.pickle'
    moviedb.config.app = hold_config_app


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
