"""Prototype"""

#  Copyright (c) 2024. Stephen Rigden.
#  Last modified 5/29/24, 8:46 AM by stephen.
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

from collections.abc import Set, Iterator
from dataclasses import dataclass, field


@dataclass
class MovieInteger(Set):
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

    Raises:
        >> mint = MovieInteger('abc')
        >> int(mint)
        ValueError: invalid literal for int() with base 10: 'abc'

        >> mint = MovieInteger("2042-2044")
        >> int(mint)
        TypeError: Not a single integer value: {2042, 2043, 2044}

        >> mint = MovieInteger("2042-wxyz")
        >> int(mint)
        ValueError: invalid literal for int() with base 10: 'wxyz'
    """

    # todo
    #   Add to program phase documentation
    #   Create a formal issue
    #   Move into globalconstants.py
    #   Write formal tests
    #   Note: SQLAlchemy v2 replaces the v1 Query object with direct use of a select()
    #       construct notably dropping the deduplication and permitting the direct use of boolean
    #       search strings. See the ORM Querying Guide:
    #       https://docs.sqlalchemy.org/en/20/orm/queryguide/index.html
    _value: str | int
    _values: set = field(default_factory=set, init=False)

    element_delimiter = ","
    max_min_delimiter = "-"

    def __post_init__(self):
        elements = str(self._value).split(self.element_delimiter)

        for element in elements:
            element = element.strip(" ")

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
            raise TypeError(f"Not a single integer value: {self._values}")
