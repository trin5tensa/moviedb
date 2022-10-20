"""Application configuration data """

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

from dataclasses import dataclass
from typing import Optional, Sequence, TypedDict

#TODO Delete CONFIG_PICKLE_EXTENSION
CONFIG_PICKLE_EXTENSION = '.pickle'
CONFIG_JSON_SUFFIX = '_config.json'
SECURE_JSON_SUFFIX = '_cfgs.json'


tk: 'tk'


class MovieKeyTypedDict(TypedDict):
    """Mandatory field for a movie."""
    title: str
    year: int


class MovieTypedDict(MovieKeyTypedDict, total=False):
    """Optional fields for a movie."""
    director: str
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
class Config:
    """The applications configuration data.
    
    A single object of this class is loaded in the application's start_up() function and pickled
    on exit.
    """
    # TODO Delete this class
    # Program
    name: str
    version: str
    
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


@dataclass
class CurrentConfig:
    """The application's configuration data.

    This transient configuration data is created during a single program run and is discarded when the program
    terminates.
    """
    # TODO Test Class
    tk_root: 'tk.Tk' = None


@dataclass
class PersistentConfig:
    """The application's configuration data.

    This persistent configuration data is loaded in the application's start_up() function and saved on exit.
    """
    # TODO Save and reload this class
    # Program
    program: str
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
        

# TODO Delete app
app: Optional[Config] = None
current: Optional[CurrentConfig] = None
persistent: Optional[PersistentConfig] = None


class ConfigException(Exception):
    """Base exception for config module."""


class ConfigTMDBAPIKeyNeedsSetting(ConfigException):
    """The TMDB key is missing."""


class ConfigTMDBDoNotUse(ConfigException):
    """The user has set use_tmdb to false."""
