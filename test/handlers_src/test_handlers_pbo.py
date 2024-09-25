"""test_handlers_pbo

This module contains new tests written after Brian Okken's course and book on pytest in Fall 2022.
"""

#  Copyright© 2024. Stephen Rigden.
#  Last modified 9/25/24, 8:35 AM by stephen.
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

import config
from contextlib import contextmanager
from handlers_src import handlers
from unittest.mock import MagicMock

import pytest


# noinspection PyMissingOrEmptyDocstring
class TestEscapeKeyDict:
    def test_dict_setitem_(self, check):
        test_func = MagicMock()
        ecd = handlers.EscapeKeyDict()
        ecd["one"] = test_func
        check.equal(ecd, {"one": test_func})
        ecd["two"] = test_func
        check.equal(ecd, {"one": test_func, "two": test_func})
        ecd["one"] = test_func
        check.equal(ecd, {"one": test_func, "two": test_func})

    # noinspection DuplicatedCode
    def test_escape(self, mock_config_current, monkeypatch, check):
        # Create an EscapeKeyDict object and get a window closure.
        ecd = handlers.EscapeKeyDict()
        parent = mock_config_current.tk_root
        accelerator = "<Escape>"
        closure = ecd.escape(parent, accelerator)

        # Create a mock keypress event, logging and gui_messagebox.
        keypress_event = MagicMock()
        mock_logging = MagicMock()
        monkeypatch.setattr(handlers, "logging", mock_logging)
        mock_messagebox = MagicMock()
        monkeypatch.setattr(handlers.guiwidgets_2, "gui_messagebox", mock_messagebox)

        # Test 'no valid name' error handling
        keypress_event.widget = ".!frame.!frame.!button"
        message = f"{ecd.accelerator_txt} {accelerator} {ecd.no_valid_name_txt}"
        closure(keypress_event)
        logging_msg = f"{message} {keypress_event.widget=}"
        with check:
            mock_logging.warning.assert_called_with(logging_msg)
        with check:
            mock_messagebox.assert_called_with(
                parent, ecd.internal_error_txt, message, icon="warning"
            )

        # Test 'more than one valid name' error handling
        keypress_event.widget = ".!frame.valid name.valid name"
        message = f"{ecd.accelerator_txt} {accelerator} {ecd.gt1_valid_name_txt}"
        closure(keypress_event)
        logging_msg = f"{message} {keypress_event.widget=}"
        with check:
            mock_logging.warning.assert_called_with(logging_msg)
        with check:
            mock_messagebox.assert_called_with(
                parent, ecd.internal_error_txt, message, icon="warning"
            )

        # Set up for call to method 'destroy'
        keypress_event.widget = ".!frame.valid name.!entry"
        mock_func = MagicMock()

        # Test destroy method called
        ecd.data = {"valid name": mock_func}
        closure(keypress_event)
        with check:
            mock_func.assert_called_once_with()

        # Test key error handling
        ecd.data = {"a different valid name": mock_func}
        closure(keypress_event)
        message = f"{ecd.accelerator_txt}  {accelerator} {ecd.key_error_text}"
        with check:
            mock_logging.warning.assert_called_with(f"{message} {ecd.data.keys()}")
        with check:
            mock_messagebox.assert_called_with(
                parent, ecd.internal_error_txt, message, icon="warning"
            )

        # Test type error handling
        bad_callback = None
        ecd.data = {"valid name": bad_callback}
        closure(keypress_event)
        message = f"{ecd.type_error_text} {ecd.accelerator_txt.lower()}  {accelerator}."
        with check:
            mock_logging.warning.assert_called_with(
                f"{message} {ecd.data['valid name']}"
            )
        with check:
            mock_messagebox.assert_called_with(
                parent, ecd.internal_error_txt, message, icon="warning"
            )


# noinspection PyMissingOrEmptyDocstring
class TestPreferencesDialog:
    """Test Strategy:

    The arguments for the preferences dialog are dependent on the state of the persistent config. All state
    configurations are tested. The Tkinter interface is mocked.
    """

    # Non-exceptional persistent state values
    TMDB_API_KEY = "TestKey"
    USE_TMDB = True

    @pytest.fixture()
    def widget(self, monkeypatch):
        widget = MagicMock()
        monkeypatch.setattr("handlers.guiwidgets_2.PreferencesGUI", widget)
        return widget

    @contextmanager
    def persistent(self, tmdb_api_key, use_tmdb):
        hold_persistent = handlers.config.persistent
        handlers.config.persistent = handlers.config.PersistentConfig(
            "garbage", "garbage"
        )
        handlers.config.persistent.tmdb_api_key = tmdb_api_key
        handlers.config.persistent.use_tmdb = use_tmdb
        yield handlers.config.persistent
        handlers.config.persistent = hold_persistent

    def test_call_with_valid_display_key(self, widget, mock_config_current):
        with self.persistent(self.TMDB_API_KEY, self.USE_TMDB):
            handlers.settings_dialog()
            widget.assert_called_once_with(
                mock_config_current.tk_root,
                self.TMDB_API_KEY,
                self.USE_TMDB,
                handlers._settings_callback,
            )

    def test_unset_key_call(self, widget, mock_config_current):
        no_key = ""
        with self.persistent(no_key, self.USE_TMDB):
            handlers.settings_dialog()
            widget.assert_called_once_with(
                mock_config_current.tk_root,
                no_key,
                self.USE_TMDB,
                handlers._settings_callback,
            )

    def test_do_not_use_tmdb_call(self, widget, mock_config_current):
        no_key = ""
        use_tmdb = False
        with self.persistent(self.TMDB_API_KEY, use_tmdb):
            handlers.settings_dialog()
            widget.assert_called_once_with(
                mock_config_current.tk_root,
                no_key,
                use_tmdb,
                handlers._settings_callback,
            )


# noinspection PyMissingOrEmptyDocstring
class TestPreferencesCallback:
    """Test Strategy:

    Check that the persistent configuration os correctly updated.
    """

    TMDB_API_KEY = "TestKey"
    USE_TMDB = True

    @contextmanager
    def persistent(self):
        hold_persistent = handlers.config.persistent
        handlers.config.persistent = handlers.config.PersistentConfig(
            "garbage", "garbage"
        )
        yield handlers.config.persistent
        handlers.config.persistent = hold_persistent

    def test_settings_updated(self, check):
        with self.persistent() as preferences:
            handlers._settings_callback(self.TMDB_API_KEY, self.USE_TMDB)
            check.equal(preferences.tmdb_api_key, self.TMDB_API_KEY)
            check.equal(preferences.use_tmdb, self.USE_TMDB)


# noinspection PyMissingOrEmptyDocstring
class TestDeleteMovieCallback:
    """Test Strategy:

    CHeck that database delete movie function is called.
    """

    MOVIE = config.FindMovieTypedDict(title="Test Movie Title", year=["4242"])

    @pytest.fixture()
    def del_movie(self, monkeypatch):
        del_movie = MagicMock()
        monkeypatch.setattr("handlers.database.del_movie", del_movie)
        return del_movie

    def test_delete_movie_call(self, del_movie):
        handlers.delete_movie_callback(self.MOVIE)
        del_movie.assert_called_once_with(self.MOVIE)

    def test_no_result_exception(self, del_movie):
        del_movie.side_effect = handlers.database.NoResultFound
        handlers.delete_movie_callback(self.MOVIE)
        del_movie.assert_called_once_with(self.MOVIE)


# noinspection PyMissingOrEmptyDocstring
class TestSelectMovieCallback:
    """Strategy
    Calls to database and GUI modules are mocked.
    """

    TITLE = "Mock Title"
    YEAR = 2042
    MOVIE = handlers.config.MovieUpdateDef(title=TITLE, year=YEAR)
    MOVIES = [MOVIE]
    TAGS = ["tag 1", "tag 2"]

    @pytest.fixture()
    def find_movies(self, monkeypatch):
        find_movies = MagicMock(return_value=self.MOVIES)
        monkeypatch.setattr("handlers.database.find_movies", find_movies)
        return find_movies

    @pytest.fixture()
    def movie_gui(self, monkeypatch):
        movie_gui = MagicMock()
        monkeypatch.setattr("handlers.guiwidgets_2.EditMovieGUI", movie_gui)
        return movie_gui

    @pytest.fixture()
    def all_tags(self, monkeypatch):
        all_tags = MagicMock(return_value=self.TAGS)
        monkeypatch.setattr("handlers.database.all_tags", all_tags)
        return all_tags

    def test_database_find_movies_called(
        self, find_movies, movie_gui, all_tags, mock_config_current
    ):
        handlers._select_movie_callback(self.MOVIE)
        find_movies.assert_called_once_with(
            dict(title=self.TITLE, year=[str(self.YEAR)])
        )

    def test_movie_gui_called(
        self, find_movies, movie_gui, all_tags, mock_config_current, check
    ):
        handlers._select_movie_callback(self.MOVIE)
        call_args = movie_gui.call_args
        tk_root, tmdb, all_tags = call_args.args
        movie, edit_movie, delete_movie = call_args.kwargs.items()

        msg = "Incorrect argument for guiwidgets_2.MovieGUI."
        check.equal(tk_root, mock_config_current.tk_root, msg)
        check.equal(tmdb, handlers._tmdb_io_handler, msg)
        check.equal(all_tags, self.TAGS, msg)
        check.equal(movie, ("old_movie", self.MOVIE), msg)
        k, v = edit_movie
        check.equal(k, "edit_movie_callback", msg)
        check.is_in("edit_movie_callback", str(v), msg)
        check.equal(
            delete_movie, ("delete_movie_callback", handlers.delete_movie_callback), msg
        )
