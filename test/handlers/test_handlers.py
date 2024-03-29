"""Menu handlers test module."""

#  Copyright (c) 2022-2024. Stephen Rigden.
#  Last modified 3/20/24, 2:31 PM by stephen.
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

from collections import deque
from contextlib import contextmanager
from dataclasses import dataclass, field
from functools import partial
from typing import Callable, List, Literal, Sequence
from unittest.mock import MagicMock

import pytest

import config
import exception
import handlers
from test.dummytk import DummyTk


# noinspection PyMissingOrEmptyDocstring
class TestAboutDialog:
    messagebox_calls = []

    def test_about_dialog_called(self, monkeypatch):
        monkeypatch.setattr(
            handlers.guiwidgets_2, "gui_messagebox", self.gui_messagebox
        )
        with self.about_context():
            assert self.messagebox_calls == [
                (DummyParent(), "Test program name", "Test program version"),
            ]

    @contextmanager
    def about_context(self):
        hold_persistent = handlers.config.persistent
        hold_current = handlers.config.current

        handlers.config.persistent = handlers.config.PersistentConfig(
            program_name="Test program name", program_version="Test program version"
        )
        handlers.config.current = handlers.config.CurrentConfig(tk_root=DummyParent())
        try:
            handlers.about_dialog()
            yield
        finally:
            handlers.config.persistent = hold_persistent
            handlers.config.current = hold_current

    def gui_messagebox(self, *args):
        self.messagebox_calls.append(args)


# noinspection PyMissingOrEmptyDocstring
class TestGetTmdbGetApiKey:
    TEST_KEY = "dummy key"

    @contextmanager
    def get_tmdb_key(self, monkeypatch, api_key=TEST_KEY, use_tmdb=True):
        dummy_persistent_config = handlers.config.PersistentConfig(
            "test_prog", "test_vers"
        )
        dummy_persistent_config.use_tmdb = use_tmdb
        dummy_persistent_config.tmdb_api_key = api_key
        monkeypatch.setattr(handlers.config, "persistent", dummy_persistent_config)
        # noinspection PyProtectedMember
        yield handlers._get_tmdb_api_key()

    def test_key_returned(self, monkeypatch):
        with self.get_tmdb_key(monkeypatch) as ctx:
            assert ctx == self.TEST_KEY

    def test_do_not_use_tmdb_logged(self, monkeypatch, caplog):
        caplog.set_level("DEBUG")
        with self.get_tmdb_key(monkeypatch, use_tmdb=False):
            expected = f"User declined TMDB use."
            assert caplog.messages[0] == expected

    def test_key_needs_setting_calls_preferences_dialog(self, monkeypatch):
        calls = []
        monkeypatch.setattr(handlers, "settings_dialog", lambda: calls.append(True))
        with self.get_tmdb_key(monkeypatch, api_key=""):
            assert calls[0]


# noinspection PyMissingOrEmptyDocstring
class TestTmdbIOExceptionHandler:
    askyesno_calls = None
    messagebox_calls = None
    preference_dialog_calls = None

    @contextmanager
    def tmdb_search_exception_callback(self, mock_fut, monkeypatch, askyesno=True):
        self.askyesno_calls = []
        self.messagebox_calls = []
        self.preference_dialog_calls = []

        # Patch config.current
        dummy_current_config = handlers.config.CurrentConfig()
        dummy_current_config.tk_root = DummyTk
        monkeypatch.setattr(handlers.config, "current", dummy_current_config)

        # Patch config.persistent
        dummy_persistent_config = handlers.config.PersistentConfig(
            "test_prog", "test_vers"
        )
        dummy_persistent_config.use_tmdb = True
        monkeypatch.setattr(handlers.config, "persistent", dummy_persistent_config)

        monkeypatch.setattr(
            handlers.guiwidgets_2,
            "gui_askyesno",
            partial(self.dummy_askyesno, askyesno=askyesno),
        )
        monkeypatch.setattr(
            handlers.guiwidgets_2, "gui_messagebox", partial(self.dummy_messagebox)
        )
        monkeypatch.setattr(
            handlers,
            "settings_dialog",
            lambda: self.preference_dialog_calls.append(True),
        )
        # noinspection PyProtectedMember
        handlers._tmdb_search_exception_callback(mock_fut)
        yield

    def dummy_askyesno(self, *args, askyesno=True):
        self.askyesno_calls.append(args)
        return askyesno

    def dummy_messagebox(self, *args):
        self.messagebox_calls.append(args)

    def test_future_result_called(self, mock_fut, monkeypatch):
        with self.tmdb_search_exception_callback(mock_fut, monkeypatch):
            assert mock_fut.result_called

    def test_invalid_tmdb_api_key_logs_exception(
        self, mock_fut_bad_key, monkeypatch, caplog
    ):
        caplog.set_level("DEBUG")
        with self.tmdb_search_exception_callback(mock_fut_bad_key, monkeypatch):
            expected = "Test bad key"
            assert caplog.messages[0] == expected

    def test_invalid_tmdb_api_key_calls_askyesno_dialog(
        self, mock_fut_bad_key, monkeypatch
    ):
        with self.tmdb_search_exception_callback(mock_fut_bad_key, monkeypatch):
            expected = (
                handlers.config.current.tk_root,
                "Invalid API key for TMDB.",
                "Do you want to set the key?",
            )
            assert self.askyesno_calls[0] == expected

    def test_invalid_tmdb_api_key_calls_preferences_dialog(
        self, mock_fut_bad_key, monkeypatch
    ):
        with self.tmdb_search_exception_callback(mock_fut_bad_key, monkeypatch):
            assert self.preference_dialog_calls[0]

    def test_tmdb_connection_timeout_calls_message_dialog(
        self, mock_fut_timeout, monkeypatch
    ):
        with self.tmdb_search_exception_callback(mock_fut_timeout, monkeypatch):
            expected = (
                handlers.config.current.tk_root,
                "TMDB database cannot be reached.",
            )
            assert self.messagebox_calls[0] == expected


# noinspection PyMissingOrEmptyDocstring
class TestTmdbIOHandler:
    search_string = "test search string"
    work_queue = handlers.queue.LifoQueue()

    @contextmanager
    def tmdb_io_handler(self, monkeypatch, mock_executor):
        # Patch config.current
        dummy_current_config = handlers.config.CurrentConfig()
        dummy_current_config.threadpool_executor = mock_executor
        monkeypatch.setattr(handlers.config, "current", dummy_current_config)

        # Patch config.persistent
        dummy_persistent_config = handlers.config.PersistentConfig(
            "test_prog", "test_vers"
        )
        dummy_persistent_config.use_tmdb = True
        dummy_persistent_config.tmdb_api_key = "test tmdb key"
        monkeypatch.setattr(handlers.config, "persistent", dummy_persistent_config)

        # noinspection PyProtectedMember
        handlers._tmdb_io_handler(self.search_string, self.work_queue)
        yield

    def test_submit_called(self, monkeypatch, mock_executor):
        with self.tmdb_io_handler(monkeypatch, mock_executor):
            func = handlers.tmdb.search_tmdb
            key = handlers.config.persistent._tmdb_api_key
            assert mock_executor.submit_calls == [
                (func, key, self.search_string, self.work_queue)
            ]

    def test_callback_set(self, monkeypatch, mock_executor):
        with self.tmdb_io_handler(monkeypatch, mock_executor):
            assert mock_executor.fut.add_done_callback_calls == [
                (handlers._tmdb_search_exception_callback,)
            ]


class TestAddMovie:
    TAGS = ["Movie night candidate"]
    movie_gui_args = []

    def test_movie_gui_called(self, monkeypatch):
        monkeypatch.setattr(handlers.database, "all_tags", lambda *args: self.TAGS)
        mock_gui = MagicMock()
        monkeypatch.setattr(handlers.guiwidgets_2, "AddMovieGUI", mock_gui)

        with self.add_movie_context():
            mock_gui.assert_called_once_with(
                DummyParent(),
                handlers._tmdb_io_handler,
                self.TAGS,
                add_movie_callback=handlers.add_movie_callback,
            )

    # noinspection PyMissingOrEmptyDocstring
    @contextmanager
    def add_movie_context(self):
        hold_persistent = handlers.config.persistent
        hold_current = handlers.config.current

        handlers.config.persistent = handlers.config.PersistentConfig(
            "Test program name", "Test program version"
        )
        handlers.config.current = handlers.config.CurrentConfig(tk_root=DummyParent())
        try:
            yield handlers.add_movie()
        finally:
            handlers.config.persistent = hold_persistent
            handlers.config.current = hold_current


class TestDeleteMovie:
    def test_delete_movie_called(self, monkeypatch):
        calls = []
        # noinspection PyTypeChecker
        movie = handlers.config.FindMovieTypedDict(title="test title", year=[2042])
        monkeypatch.setattr(
            handlers.database, "del_movie", lambda *args: calls.append(args)
        )
        handlers.delete_movie_callback(movie)
        assert calls == [(movie,)]


class TestEditMovie:
    TAGS = ["Movie night candidate"]

    search_gui_args = []

    def test_edit_gui_called(self, monkeypatch):
        monkeypatch.setattr(handlers.database, "all_tags", lambda *args: self.TAGS)
        monkeypatch.setattr(
            handlers.guiwidgets,
            "SearchMovieGUI",
            lambda parent, callback, tags: self.search_gui_args.append(
                (parent, callback, tags)
            ),
        )
        with self.edit_movie_context():
            assert self.search_gui_args == [
                (DummyParent(), handlers._search_movie_callback, self.TAGS)
            ]

    # noinspection PyMissingOrEmptyDocstring
    @contextmanager
    def edit_movie_context(self):
        hold_app = handlers.config.current
        handlers.config.current = handlers.config.PersistentConfig(
            "Test program name", "Test program version"
        )
        handlers.config.current.tk_root = DummyParent()
        try:
            yield handlers.edit_movie()
        finally:
            handlers.config.current = hold_app


# noinspection PyMissingOrEmptyDocstring
class TestImportMovies:
    CSV_TEST_FN = "csv_test_fn"
    askopenfilename_calls = None
    import_movies_calls = None
    messagebox_calls = None

    def test_user_cancellation_of_askopenfilename_dialog(
        self, class_patches, monkeypatch
    ):
        monkeypatch.setattr(
            handlers.guiwidgets_2, "gui_askopenfilename", lambda **kwargs: ""
        )
        with self.import_movies_context():
            assert self.import_movies_calls == deque([])

    def test_get_filename_dialog_called(self, class_patches):
        with self.import_movies_context():
            assert self.askopenfilename_calls == [
                dict(
                    parent=handlers.config.current.tk_root,
                    filetypes=(("Movie import files", "*.csv"),),
                )
            ]

    def test_import_movies_called(self, class_patches):
        with self.import_movies_context():
            assert self.import_movies_calls.popleft() == self.CSV_TEST_FN

    def test_import_movies_raises_invalid_data_exception(
        self, class_patches, monkeypatch
    ):
        monkeypatch.setattr(
            handlers.impexp, "import_movies", self.dummy_import_movies_with_exception
        )
        with self.import_movies_context():
            assert self.messagebox_calls == [
                (
                    (handlers.config.current.tk_root,),
                    dict(
                        message="Errors were found in the input file.",
                        detail="Test exception message",
                        icon="warning",
                    ),
                )
            ]

    @pytest.fixture
    def class_patches(self, monkeypatch):
        monkeypatch.setattr(
            handlers.guiwidgets_2, "gui_askopenfilename", self.dummy_askopenfilename
        )
        monkeypatch.setattr(handlers.guiwidgets, "gui_messagebox", self.gui_messagebox)
        monkeypatch.setattr(handlers.impexp, "import_movies", self.dummy_import_movies)

    @contextmanager
    def import_movies_context(self):
        self.askopenfilename_calls = []
        self.import_movies_calls = deque()
        self.messagebox_calls = []
        hold_persistent = handlers.config.persistent
        hold_current = handlers.config.current

        handlers.config.persistent = handlers.config.PersistentConfig(
            program_name="test moviedb", program_version="test 1.0.0.dev"
        )
        handlers.config.current = handlers.config.CurrentConfig(tk_root="tk_root")
        try:
            yield handlers.import_movies()
        finally:
            handlers.config.persistent = hold_persistent
            handlers.config.current = hold_current

    def dummy_askopenfilename(self, **kwargs):
        self.askopenfilename_calls.append(kwargs)
        return self.CSV_TEST_FN

    def dummy_import_movies(self, csv_fn):
        self.import_movies_calls.append(csv_fn)

    def dummy_import_movies_with_exception(self, csv_fn):
        raise handlers.impexp.MoviedbInvalidImportData("Test exception message")

    def gui_messagebox(self, *args, **kwargs):
        self.messagebox_calls.append((args, kwargs))


# noinspection PyMissingOrEmptyDocstring
class TestSearchMovieCallback:
    search_title = "test tsmc"
    year = "4242"
    tags = ["tsmc 1", "tsmc 2"]
    movie_key = handlers.config.MovieKeyTypedDict(title=search_title, year=int(year))
    criteria = handlers.config.FindMovieTypedDict(title=search_title, year=[year])
    search_response: dict[str, list[handlers.database.MovieUpdateDef]] = dict(
        no_movies=[],
        one_movie=[handlers.config.MovieUpdateDef(title=search_title, year=int(year))],
        many_movies=[
            handlers.config.MovieUpdateDef(title=search_title + " 1", year=int(year)),
            handlers.config.MovieUpdateDef(title=search_title + " 2", year=int(year)),
        ],
    )
    find_movies_calls = []

    def dummy_find_movies_calls(
        self, found: Literal["no_movies", "one_movie", "many_movies"]
    ) -> Callable:
        """Mocks the handler's call to database.find_movies.

        Args:
            found:

        Returns:
            The mock function
        """
        self.find_movies_calls = []
        result = self.search_response[found]

        def func(*args) -> list[handlers.database.MovieUpdateDef]:
            self.find_movies_calls.append(args)
            return result

        return func

    @contextmanager
    def search_movie_callback(self, found, monkeypatch):
        global dummy_select_movie_gui_instance
        global dummy_edit_movie_gui_instance
        dummy_select_movie_gui_instance = []
        dummy_edit_movie_gui_instance = []

        monkeypatch.setattr(
            "handlers.database.find_movies", self.dummy_find_movies_calls(found)
        )
        monkeypatch.setattr(handlers.guiwidgets, "SelectMovieGUI", DummySelectMovieGUI)
        monkeypatch.setattr(handlers.guiwidgets_2, "EditMovieGUI", DummyMovieGUI)
        monkeypatch.setattr(handlers.database, "all_tags", lambda: self.tags)

        current = handlers.config.CurrentConfig()
        current.tk_root = DummyTk()
        monkeypatch.setattr("handlers.config.current", current)
        handlers._search_movie_callback(self.criteria, self.tags)
        yield

    def test_find_movies_called(self, monkeypatch):
        """Test the call to find_movies and suppress the generated error when none are found."""
        try:
            with self.search_movie_callback("no_movies", monkeypatch):
                pass
        except exception.DatabaseSearchFoundNothing:
            pass
        finally:
            assert self.find_movies_calls == [(self.criteria,)]

    def test_no_movies_found_raises_exception(self, monkeypatch):
        with pytest.raises(exception.DatabaseSearchFoundNothing):
            with self.search_movie_callback("no_movies", monkeypatch):
                pass

    def test_one_movie_found_calls_edit_movie(self, monkeypatch):
        with self.search_movie_callback("one_movie", monkeypatch):
            expected = [
                (
                    DummyTk(),
                    handlers._tmdb_io_handler,
                    self.tags,
                    None,
                    self.movie_key,
                    "edit_movie_callback.<locals>.func",
                    handlers.delete_movie_callback,
                )
            ]
            assert dummy_edit_movie_gui_instance == expected

    def test_multiple_movies_found_instantiates_edit_movie(self, monkeypatch):
        with self.search_movie_callback("many_movies", monkeypatch):
            expected = [
                (
                    DummyTk(),
                    self.search_response["many_movies"],
                    handlers._select_movie_callback,
                )
            ]
            assert dummy_select_movie_gui_instance == expected


# noinspection PyMissingOrEmptyDocstring
class TestTags:
    def test_add_tag(self, monkeypatch):
        tag_gui_args = []
        monkeypatch.setattr(
            handlers.guiwidgets_2,
            "AddTagGUI",
            lambda *args, **kwargs: tag_gui_args.append((args, kwargs)),
        )

        tk_parent = DummyParent()
        add_tag_callback = handlers._add_tag_callback
        with self.tag_func_context(handlers.add_tag):
            assert tag_gui_args == [
                (
                    (tk_parent,),
                    {"add_tag_callback": add_tag_callback},
                )
            ]

    def test_edit_tag(self, monkeypatch):
        edit_tag_args = []
        monkeypatch.setattr(
            handlers.guiwidgets_2,
            "SearchTagGUI",
            lambda *args, **kwargs: edit_tag_args.append((args, kwargs)),
        )

        tk_parent = DummyParent()
        search_tag_callback = handlers._search_tag_callback
        with self.tag_func_context(handlers.edit_tag):
            assert edit_tag_args == [
                (
                    (tk_parent,),
                    {"search_tag_callback": search_tag_callback},
                ),
            ]

    @contextmanager
    def tag_func_context(self, tag_func):
        hold_persistent = handlers.config.persistent
        hold_current = handlers.config.current

        handlers.config.persistent = handlers.config.PersistentConfig(
            program_name="Test program name", program_version="Test program version"
        )
        handlers.config.current = handlers.config.CurrentConfig(tk_root=DummyParent())

        try:
            yield tag_func()

        finally:
            handlers.config.persistent = hold_persistent
            handlers.config.current = hold_current


class TestAddTagCallback:
    def test_(self, monkeypatch):
        calls = []
        monkeypatch.setattr(
            handlers.database, "add_tag", lambda *args: calls.append(args)
        )
        test_tag = "Test tag"
        handlers._add_tag_callback(test_tag)
        assert calls == [(test_tag,)]


# noinspection PyMissingOrEmptyDocstring
class TestSearchTagCallback:
    def test_zero_tags_found_raises_exception(self, monkeypatch):
        tags_found = []
        monkeypatch.setattr(handlers.database, "find_tags", lambda *args: tags_found)
        tag_pattern = "42"
        with pytest.raises(exception.DatabaseSearchFoundNothing):
            with self.search_tag_context(tag_pattern):
                pass

    def test_one_tag_found_calls_edit_tag_gui(self, monkeypatch, class_patches):
        tags_found = ["42"]
        monkeypatch.setattr(handlers.database, "find_tags", lambda *args: tags_found)
        tag_pattern = "42"
        with self.search_tag_context(tag_pattern):
            args_ = dummy_edit_tag_gui_instance[0]
            assert args_[0] == DummyParent()
            assert args_[1] == "42"
            assert isinstance(args_[2], Callable)
            assert isinstance(args_[3], Callable)

    def test_multiple_tags_found_calls_select_tag_gui(self, monkeypatch, class_patches):
        tags_found = ["42", "43"]
        monkeypatch.setattr(handlers.database, "find_tags", lambda *args: tags_found)
        tag_pattern = "42"
        with self.search_tag_context(tag_pattern):
            args_ = dummy_select_tag_gui_instance[0]
            assert args_[0] == DummyParent()
            assert isinstance(args_[1], Callable)
            assert args_[2] == ["42", "43"]

    @pytest.fixture
    def class_patches(self, monkeypatch):
        monkeypatch.setattr(handlers.guiwidgets_2, "EditTagGUI", DummyEditTagGUI)
        monkeypatch.setattr(handlers.guiwidgets_2, "SelectTagGUI", DummySelectTagGUI)

    @contextmanager
    def search_tag_context(self, tag_pattern: str):
        hold_persistent = handlers.config.persistent
        hold_current = handlers.config.current

        handlers.config.persistent = handlers.config.PersistentConfig(
            program_name="Test program name", program_version="Test program version"
        )
        handlers.config.current = handlers.config.CurrentConfig(tk_root=DummyParent())

        try:
            yield handlers._search_tag_callback(tag_pattern)
        finally:
            handlers.config.persistent = hold_persistent
            handlers.config.current = hold_current


class TestEditTagCallback:
    old_tag = "test old tag"
    new_tag = "test new tag"

    def test_database_edit_tag_called(self, monkeypatch):
        edit_tags_args = []
        monkeypatch.setattr(
            handlers.database, "edit_tag", lambda *args: edit_tags_args.append(args)
        )
        with self.add_tag_callback_context():
            assert edit_tags_args == [(self.old_tag, self.new_tag)]

    def test_database_search_found_nothing_raised(self, monkeypatch):
        # noinspection PyMissingOrEmptyDocstring,PyUnusedLocal
        def raise_exception(*args):
            raise handlers.database.exception.DatabaseSearchFoundNothing

        message_args = []

        monkeypatch.setattr(handlers.database, "edit_tag", raise_exception)
        monkeypatch.setattr(
            handlers.guiwidgets,
            "gui_messagebox",
            lambda *args: message_args.append(args),
        )
        with self.add_tag_callback_context():
            assert message_args == [
                (
                    DummyParent(),
                    "Missing tag",
                    "The tag test old tag is no longer available. "
                    "It may have been deleted by another process.",
                )
            ]

    # noinspection PyMissingOrEmptyDocstring
    @contextmanager
    def add_tag_callback_context(self):
        hold_persistent = handlers.config.persistent
        hold_current = handlers.config.current

        handlers.config.persistent = handlers.config.PersistentConfig(
            program_name="Test program name", program_version="Test program version"
        )
        handlers.config.current = handlers.config.CurrentConfig(tk_root=DummyParent())
        callback = handlers._edit_tag_callback_wrapper(self.old_tag)

        try:
            yield callback(self.new_tag)
        finally:
            handlers.config.persistent = hold_persistent
            handlers.config.current = hold_current


# noinspection PyMissingOrEmptyDocstring
class TestDeleteTagCallback:
    tag = "test tag"

    def test_database_delete_tag_called(self, monkeypatch):
        del_tag_args = []
        monkeypatch.setattr(
            handlers.database, "del_tag", lambda *args: del_tag_args.append(args)
        )
        with self.delete_tag_callback_context():
            assert del_tag_args == [(self.tag,)]

    def test_database_search_found_nothing_ignored(self, monkeypatch):
        # noinspection PyUnusedLocal
        def raise_exception(*args):
            raise handlers.database.exception.DatabaseSearchFoundNothing

        monkeypatch.setattr(handlers.database, "del_tag", raise_exception)
        try:
            with self.delete_tag_callback_context():
                pass
        except handlers.database.exception.DatabaseSearchFoundNothing:
            assert False, (
                "Exception 'handlers.database.exception.DatabaseSearchFoundNothing'"
                " was not suppressed."
            )

    @contextmanager
    def delete_tag_callback_context(self):
        callback = handlers._delete_tag_callback_wrapper(self.tag)
        yield callback()


# noinspection PyMissingOrEmptyDocstring
class TestSearchTagCallbackWrapper:
    tag = "Test tag"

    def test_select_tag_callback_calls_edit_tag_gui(self, monkeypatch):
        monkeypatch.setattr(handlers.guiwidgets_2, "EditTagGUI", DummyEditTagGUI)

        with self.callback_context():
            args = dummy_edit_tag_gui_instance[0]
            assert args[0] == DummyParent()
            assert args[1] == self.tag
            assert args[2].__code__.co_name == "delete_tag_callback"
            assert args[3].__code__.co_name == "edit_tag_callback"

    @contextmanager
    def callback_context(self):
        global dummy_edit_tag_gui_instance
        dummy_edit_tag_gui_instance = []
        hold_persistent = handlers.config.persistent
        hold_current = handlers.config.current

        handlers.config.persistent = handlers.config.PersistentConfig(
            program_name="Test program name", program_version="Test program version"
        )
        handlers.config.current = handlers.config.CurrentConfig(tk_root=DummyParent())
        try:
            yield handlers._select_tag_callback(self.tag)
        finally:
            handlers.config.persistent = hold_persistent
            handlers.config.current = hold_current
            dummy_edit_tag_gui_instance = []


@dataclass
class DummyParent:
    """Provide a dummy for Tk root."""

    pass


dummy_edit_movie_gui_instance = []


# noinspection PyMissingOrEmptyDocstring
@dataclass
class DummyMovieGUI:
    parent: DummyParent
    tmdb_search_callback: Callable
    all_tags: Sequence[str]
    add_movie_callback: Callable = field(default=None, kw_only=True)
    old_movie: config.MovieUpdateDef = field(default=None, kw_only=True)
    edit_movie_callback: Callable = field(default=None, kw_only=True)
    delete_movie_callback: Callable = field(default=None, kw_only=True)

    def __post_init__(self):
        dummy_edit_movie_gui_instance.append(
            (
                self.parent,
                self.tmdb_search_callback,
                self.all_tags,
                self.add_movie_callback,
                self.old_movie,
                self.edit_movie_callback.__qualname__,
                self.delete_movie_callback,
            )
        )


dummy_select_movie_gui_instance = []


# noinspection PyMissingOrEmptyDocstring
@dataclass
class DummySelectMovieGUI:
    parent: DummyParent
    movies: List[handlers.config.MovieUpdateDef]
    callback: Callable[[handlers.config.MovieUpdateDef, Sequence[str]], None]

    def __post_init__(self):
        dummy_select_movie_gui_instance.append(
            (self.parent, self.movies, self.callback)
        )


dummy_edit_tag_gui_instance = []


# noinspection PyMissingOrEmptyDocstring
@dataclass
class DummyEditTagGUI:
    parent: DummyParent
    tag: str
    delete_tag_callback: Callable[[str], None]
    edit_tag_callback: Callable[[str], None]

    def __post_init__(self):
        dummy_edit_tag_gui_instance.append(
            (self.parent, self.tag, self.delete_tag_callback, self.edit_tag_callback)
        )


dummy_select_tag_gui_instance = []


# noinspection PyMissingOrEmptyDocstring
@dataclass
class DummySelectTagGUI:
    parent: DummyParent
    select_tag_callback: Callable[[str], None]
    tags_to_show: Sequence[str]

    def __post_init__(self):
        dummy_select_tag_gui_instance.append(
            (self.parent, self.select_tag_callback, self.tags_to_show)
        )


dummy_gui_messagebox_calls = []


# noinspection PyMissingOrEmptyDocstring
def dummy_gui_messagebox(*args, **kwargs):
    dummy_gui_messagebox_calls.append((args, kwargs))
