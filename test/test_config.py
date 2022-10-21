"""Config test module."""

#  Copyright (c) 2022-2022. Stephen Rigden.
#  Last modified 10/15/22, 12:37 PM by stephen.
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

import pytest

import config


class TestConfig:
    test_tmdb_key = 'test_tmdb_key'

    def test_key_not_set_raises_exception(self):
        with pytest.raises(config.ConfigTMDBAPIKeyNeedsSetting):
            with self.config_context('', True) as configuration:
                _ = configuration.tmdb_api_key

    def test_key_returned(self):
        with self.config_context(self.test_tmdb_key, True) as configuration:
            assert configuration.tmdb_api_key == self.test_tmdb_key

    # noinspection PyPep8Naming
    def test_user_declined_TMDB_use_returns_empty_string(self):
        # with self.config_context(self.test_tmdb_key, False) as configuration:
        #     assert configuration.tmdb_api_key == ''
        with pytest.raises(config.ConfigTMDBDoNotUse):
            with self.config_context('Garbage', False) as configuration:
                _ = configuration.tmdb_api_key

    def test_setter_for_tmdb_api_key(self):
        with self.config_context(self.test_tmdb_key, False) as configuration:
            configuration.tmdb_api_key = 'new test key'
            assert configuration._tmdb_api_key == 'new test key'

    @contextmanager
    def config_context(self, key: str, use: bool):
        name = 'Test Config'
        version = 'Test.0.dev'
        configuration = config.PersistentConfig(name, version)
        configuration._tmdb_api_key = key
        configuration.use_tmdb = use
        yield configuration
