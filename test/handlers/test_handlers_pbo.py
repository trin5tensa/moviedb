"""test_handlers_pbo

This module contains new tests written after Brian Okken's course and book on
pytest in Fall 2022.
"""

#  Copyright© 2025. Stephen Rigden.
#  Last modified 4/19/25, 1:55 PM by stephen.
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
from handlers import sundries

from unittest.mock import MagicMock

import pytest


# noinspection PyMissingOrEmptyDocstring
class TestPreferencesDialog:
    """Test Strategy:

    The arguments for the preferences dialog are dependent on the state of
    the persistent config. All state configurations are tested. The
    Tkinter interface is mocked.
    """

    # Non-exceptional persistent state values
    TMDB_API_KEY = "TestKey"
    USE_TMDB = True

    @pytest.fixture()
    def settings(self, monkeypatch):
        settings = MagicMock(name="settings", autospec=True)
        monkeypatch.setattr(sundries.settings, "Settings", settings)
        return settings

    @contextmanager
    def persistent(self, tmdb_api_key, use_tmdb):
        hold_persistent = sundries.config.persistent
        sundries.config.persistent = sundries.config.PersistentConfig(
            "garbage", "garbage"
        )
        sundries.config.persistent.tmdb_api_key = tmdb_api_key
        sundries.config.persistent.use_tmdb = use_tmdb
        yield sundries.config.persistent
        sundries.config.persistent = hold_persistent

    def test_call_with_valid_display_key(self, settings, mock_config_current):
        with self.persistent(self.TMDB_API_KEY, self.USE_TMDB):
            sundries.settings_dialog()
            settings.assert_called_once_with(
                mock_config_current.tk_root,
                tmdb_api_key=self.TMDB_API_KEY,
                use_tmdb=self.USE_TMDB,
                save_callback=sundries._settings_callback,
            )

    def test_unset_key_call(self, settings, mock_config_current):
        no_key = ""
        with self.persistent(no_key, self.USE_TMDB):
            sundries.settings_dialog()
            settings.assert_called_once_with(
                mock_config_current.tk_root,
                tmdb_api_key=no_key,
                use_tmdb=self.USE_TMDB,
                save_callback=sundries._settings_callback,
            )

    def test_do_not_use_tmdb_call(self, settings, mock_config_current):
        no_key = ""
        use_tmdb = False
        with self.persistent(self.TMDB_API_KEY, use_tmdb):
            sundries.settings_dialog()
            settings.assert_called_once_with(
                mock_config_current.tk_root,
                tmdb_api_key=no_key,
                use_tmdb=use_tmdb,
                save_callback=sundries._settings_callback,
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
        hold_persistent = sundries.config.persistent
        sundries.config.persistent = sundries.config.PersistentConfig(
            "garbage", "garbage"
        )
        yield sundries.config.persistent
        sundries.config.persistent = hold_persistent

    def test_settings_updated(self, check):
        with self.persistent() as preferences:
            sundries._settings_callback(self.TMDB_API_KEY, self.USE_TMDB)
            check.equal(preferences.tmdb_api_key, self.TMDB_API_KEY)
            check.equal(preferences.use_tmdb, self.USE_TMDB)
