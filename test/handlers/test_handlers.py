"""Menu handlers for TMDB and dialogs."""

#  Copyright© 2025. Stephen Rigden.
#  Last modified 4/11/25, 8:12 AM by stephen.
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
from unittest.mock import MagicMock

from handlers import sundries


def test_about_dialog(monkeypatch):
    # Arrange
    persistent = MagicMock(name="persistent", autospec=True)
    persistent.program_name = "Dummy for test_about_dialog"
    persistent.program_version = "Dummy version"
    monkeypatch.setattr(sundries.config, "persistent", persistent)
    showinfo = MagicMock(name="showinfo", autospec=True)
    monkeypatch.setattr(sundries.common, "showinfo", showinfo)

    # Act
    sundries.about_dialog()

    # Assert
    showinfo.assert_called_once_with(
        persistent.program_name,
        detail=f"{sundries.VERSION} {persistent.program_version}",
    )


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
