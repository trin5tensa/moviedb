"""Application configuration data """

#  Copyright© 2020. Stephen Rigden.
#  Last modified 4/13/20, 8:06 AM by stephen.
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

from dataclasses import dataclass
from typing import Optional, Sequence, TypedDict


tk: 'tk'
mainwindow: 'mainwindow'


# moviedb-#173 Clean Up
#   Change TypedDict names from …Def to …TypedDict
#   Move all TypedDicts to database.py


class MovieKeyDef(TypedDict):
    """Mandatory field for a movie."""
    title: str
    year: int


class MovieDef(MovieKeyDef, total=False):
    """Optional fields for a movie."""
    director: str
    minutes: int
    notes: str


class MovieUpdateDef(TypedDict, total=False):
    """A dictionary of fields for updating.
    
    WARNING: Only use this definition for updating existing records."""
    title: str
    director: str
    year: int
    minutes: int
    notes: str
    tags: Sequence[str]


class FindMovieDef(TypedDict, total=False):
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
    year: Sequence[int]
    director: str
    minutes: Sequence[int]
    notes: str
    tags: Sequence[str]


@dataclass
class Config:
    """The applications configuration data.
    
    A single object of this class is created in the application's start_up() function.
    """
    # Program
    name: str
    version: str
    # tk.Tk screen geometry
    geometry: str = None

    # Save the root window for easy access for testing.
    tk_root: 'tk.Tk' = None
    gui_environment: 'mainwindow.MainWindow' = None


app: Optional[Config] = None
