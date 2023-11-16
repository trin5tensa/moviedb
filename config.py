"""Application configuration data """

#  Copyright (c) 2022-2023. Stephen Rigden.
#  Last modified 1/28/23, 8:30 AM by stephen.
#  This program_name is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#  This program_name is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License
#  along with this program_name.  If not, see <https://www.gnu.org/licenses/>.

from collections import UserDict
from collections.abc import Callable, Sequence
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Optional, TypedDict

CONFIG_JSON_SUFFIX = '_config.json'


tk: 'tk'
current: Optional['CurrentConfig'] = None
persistent: Optional['PersistentConfig'] = None


class MovieKeyTypedDict(TypedDict):
    """Mandatory field for a movie."""
    title: str
    year: int


class MovieTypedDict(MovieKeyTypedDict, total=False):
    """Optional fields for a movie."""
    director: str | list[str]
    minutes: int
    notes: str


class MovieUpdateDef(MovieTypedDict, total=False):
    """A dictionary of fields for updating.
    
    WARNING: Only use this definition for updating existing records."""
    tags: Sequence[str]


class FindMovieTypedDict(TypedDict, total=False):
    """A dictionary containing none or more of the following keys:
            title: A matching column will be a superstring of this value.
            director: A matching column will be a superstring of this value.
            minutes: A matching column will be between the minimum and maximum values in this
            iterable. A single value is permissible.
            year: A matching column will be between the minimum and maximum values in this
            iterable. A single value is permissible.
            notes: A matching column will be a superstring of this value.
            tag: Movies matching any tag in this list will be selected.
    """
    title: str
    year: Sequence[str]
    director: str
    minutes: Sequence[str]
    notes: str
    tags: Sequence[str]


@dataclass
class CurrentConfig:
    """The application's configuration data.

    This transient configuration data is created during a single program_name run and is discarded when the program_name
    terminates.
    """
    tk_root: 'tk.Tk' = None
    safeprint: Callable = None
    threadpool_executor: ThreadPoolExecutor = None
    escape_key_dict: UserDict = None


@dataclass
class PersistentConfig:
    """The application's configuration data.

    This persistent configuration data is loaded in the application's start_up() function and saved on exit.
    """
    # Program
    program_name: str
    program_version: str

    # tk.Tk screen geometry
    geometry: str = None

    # TMDB
    _tmdb_api_key: str = ''
    use_tmdb: bool = True

    @property
    def tmdb_api_key(self):
        """ Return the tmdb_api_key but raise exceptions for missing key and user suppressed access."""
        # User wants to use TMDB
        if self.use_tmdb:
            # …but the key has not been set so raise exception
            if self._tmdb_api_key == '':
                raise ConfigTMDBAPIKeyNeedsSetting
            # otherwise return the possibly valid key.
            else:
                return self._tmdb_api_key
    
        # Otherwise the user has declined to use TMDB
        else:
            raise ConfigTMDBDoNotUse

    @tmdb_api_key.setter
    def tmdb_api_key(self, value: str):
        self._tmdb_api_key = value
        

class ConfigException(Exception):
    """Base exception for config module."""


class ConfigTMDBAPIKeyNeedsSetting(ConfigException):
    """The TMDB key is missing."""


class ConfigTMDBDoNotUse(ConfigException):
    """The user has set use_tmdb to false."""
