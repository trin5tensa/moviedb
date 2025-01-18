"""Menu handlers test module."""

#  Copyright© 2025. Stephen Rigden.
#  Last modified 1/18/25, 6:41 AM by stephen.
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

from contextlib import contextmanager
from dataclasses import dataclass
from functools import partial

from handlers import sundries
from test.dummytk import DummyTk


# noinspection PyMissingOrEmptyDocstring
class TestAboutDialog:
    messagebox_calls = []

    def test_about_dialog_called(self, monkeypatch):
        monkeypatch.setattr(
            sundries.guiwidgets_2, "gui_messagebox", self.gui_messagebox
        )
        with self.about_context():
            assert self.messagebox_calls == [
                (DummyParent(), "Test program name", "Test program version"),
            ]

    @contextmanager
    def about_context(self):
        hold_persistent = sundries.config.persistent
        hold_current = sundries.config.current

        sundries.config.persistent = sundries.config.PersistentConfig(
            program_name="Test program name", program_version="Test program version"
        )
        sundries.config.current = sundries.config.CurrentConfig(tk_root=DummyParent())
        try:
            sundries.about_dialog()
            yield
        finally:
            sundries.config.persistent = hold_persistent
            sundries.config.current = hold_current

    def gui_messagebox(self, *args):
        self.messagebox_calls.append(args)


# noinspection PyMissingOrEmptyDocstring
class TestGetTmdbGetApiKey:
    TEST_KEY = "dummy key"

    @contextmanager
    def get_tmdb_key(self, monkeypatch, api_key=TEST_KEY, use_tmdb=True):
        dummy_persistent_config = sundries.config.PersistentConfig(
            "test_prog", "test_vers"
        )
        dummy_persistent_config.use_tmdb = use_tmdb
        dummy_persistent_config.tmdb_api_key = api_key
        monkeypatch.setattr(sundries.config, "persistent", dummy_persistent_config)
        # noinspection PyProtectedMember
        yield sundries._get_tmdb_api_key()

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
        monkeypatch.setattr(sundries, "settings_dialog", lambda: calls.append(True))
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
        dummy_current_config = sundries.config.CurrentConfig()
        dummy_current_config.tk_root = DummyTk
        monkeypatch.setattr(sundries.config, "current", dummy_current_config)

        # Patch config.persistent
        dummy_persistent_config = sundries.config.PersistentConfig(
            "test_prog", "test_vers"
        )
        dummy_persistent_config.use_tmdb = True
        monkeypatch.setattr(sundries.config, "persistent", dummy_persistent_config)

        monkeypatch.setattr(
            sundries.guiwidgets_2,
            "gui_askyesno",
            partial(self.dummy_askyesno, askyesno=askyesno),
        )
        monkeypatch.setattr(
            sundries.guiwidgets_2, "gui_messagebox", partial(self.dummy_messagebox)
        )
        monkeypatch.setattr(
            sundries,
            "settings_dialog",
            lambda: self.preference_dialog_calls.append(True),
        )
        # noinspection PyProtectedMember
        sundries._tmdb_search_exception_callback(mock_fut)
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
                sundries.config.current.tk_root,
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
                sundries.config.current.tk_root,
                "TMDB database cannot be reached.",
            )
            assert self.messagebox_calls[0] == expected


# noinspection PyMissingOrEmptyDocstring
class TestTmdbIOHandler:
    search_string = "test search string"
    work_queue = sundries.queue.LifoQueue()

    @contextmanager
    def tmdb_io_handler(self, monkeypatch, mock_executor):
        # Patch config.current
        dummy_current_config = sundries.config.CurrentConfig()
        dummy_current_config.threadpool_executor = mock_executor
        monkeypatch.setattr(sundries.config, "current", dummy_current_config)

        # Patch config.persistent
        dummy_persistent_config = sundries.config.PersistentConfig(
            "test_prog", "test_vers"
        )
        dummy_persistent_config.use_tmdb = True
        dummy_persistent_config.tmdb_api_key = "test tmdb key"
        monkeypatch.setattr(sundries.config, "persistent", dummy_persistent_config)

        # noinspection PyProtectedMember
        sundries._tmdb_io_handler(self.search_string, self.work_queue)
        yield

    def test_submit_called(self, monkeypatch, mock_executor):
        with self.tmdb_io_handler(monkeypatch, mock_executor):
            func = sundries.tmdb.search_tmdb
            key = sundries.config.persistent._tmdb_api_key
            assert mock_executor.submit_calls == [
                (func, key, self.search_string, self.work_queue)
            ]

    def test_callback_set(self, monkeypatch, mock_executor):
        with self.tmdb_io_handler(monkeypatch, mock_executor):
            assert mock_executor.fut.add_done_callback_calls == [
                (sundries._tmdb_search_exception_callback,)
            ]


@dataclass
class DummyParent:
    """Provide a dummy for Tk root."""

    pass


dummy_gui_messagebox_calls = []


# noinspection PyMissingOrEmptyDocstring
def dummy_gui_messagebox(*args, **kwargs):
    dummy_gui_messagebox_calls.append((args, kwargs))
