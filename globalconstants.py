"""Global constants and type definitions."""

#  Copyright© 2025. Stephen Rigden.
#  Last modified 4/17/25, 9:54 AM by stephen.
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
from collections.abc import Iterator
from dataclasses import dataclass, field
from datetime import datetime
from typing import TypedDict

# todo move these imports to gui.common
# This tkinter import method supports accurate test mocking of tk and ttk.
import tkinter as tk
import tkinter.ttk as ttk

# todo Clean up
#  Rename module to moviebag.py


NO_INTEGER_VALUE = "This object cannot provide an integer value"


class MovieBag(TypedDict, total=False):
    """A structured bag for movie data.

    Whilst the individual fields are defined in detail there is no
    requirement or guarantee that any particular field is present. That is
    the responsibility of the data producer and data consumer.
    There is also no guarantee that any present item will have a truthful
    value.

    See function setstr_to_str for a display conversion of directors, stars,
    and tags.
    """

    title: str
    year: "MovieInteger"
    duration: "MovieInteger"
    directors: set[str]
    stars: set[str]
    synopsis: str
    notes: str
    tags: set[str]

    # Database fields
    id: int
    created: datetime
    updated: datetime


@dataclass
class MovieInteger(set):
    """A hybrid set class which can hold a unary integer or a search _pattern.

    Use for adding, displaying, or updating records:
        >> mint = MovieInteger('2042')
        >> int(mint)
        2042

        >> mint = MovieInteger(2042)
        >> int(mint)
        2042

    Use as a search _pattern:
        >> mint = MovieInteger('2020-2022')
        >> 2021 in mint
        True
        >> 2042 in mint
        False

        >> mint = MovieInteger('2020-2022, 2021, 2029, 2025-2027')
        >> list(mint)
        [2020, 2021, 2022, 2025, 2026, 2027, 2029]
        >> 2021 in mint
        True

    Raises:
        >> mint = MovieInteger('abc')
        ValueError: invalid literal for int() with base 10: 'abc'

        >> mint = MovieInteger("2042-2044")
        >> int(mint)
        TypeError: Not a single integer value: {2042, 2043, 2044}

        >> mint = MovieInteger("2042-wxyz")
        ValueError: invalid literal for int() with base 10: 'wxyz'

    Use case:
        This simplifies the layout of the GUI, otherwise movie search and
        movie display movies require separate layouts and support code.
    """

    _value: str | int
    _values: set = field(default_factory=set, init=False)

    element_delimiter = ","
    max_min_delimiter = "-"

    def __post_init__(self):
        elements = str(self._value).split(self.element_delimiter)

        for element in elements:
            element = element.strip(" -")

            if self.max_min_delimiter in element:
                min_max = element.split(self.max_min_delimiter)
                if len(min_max) != 2:
                    raise ValueError(
                        f"Expected a range in the format '<low int>-<high int>'. Got:"
                        f" {element}"
                    )
                self._values |= set(
                    i for i in range(int(min(min_max)), int(max(min_max)) + 1)
                )

            else:
                self._values.add(int(element))

    def __str__(self):
        return str(self._value)

    def __len__(self) -> int:
        return len(self._values)

    def __iter__(self) -> Iterator:
        return iter(self._values)

    def __contains__(self, item: int) -> bool:
        return item in self._values

    def __int__(self) -> int:
        if len(self._values) == 1:
            return list(self._values)[0]
        else:
            raise TypeError(f"{NO_INTEGER_VALUE}: {self._values}")


def setstr_to_str(setstr: set[str] | None) -> str:
    """Converts a MovieBag set of strings into a single comma-delimited
    string for display. The strings are sorted alphabetically for ease
    of testing.

    Examples:
        In each case the setstr argument is the expected result of
        movie_bag.get('key', None).

        {"ts"} → "ts"
        {"ts1", "ts2"} → "ts1, ts2"
        {""} → ""
        None → ""

    Args:
        setstr: Either a set of strings or None

    Returns:
        A single comma-delimited string.
    """
    setstr = setstr if setstr else ""
    return ", ".join(sorted(setstr))
