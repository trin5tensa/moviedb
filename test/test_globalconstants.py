"""Test module."""

#  Copyright© 2025. Stephen Rigden.
#  Last modified 3/10/25, 12:52 PM by stephen.
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

import pytest
from pytest_check import check

from globalconstants import MovieInteger, setstr_to_str


class TestMovieInteger:

    def test_integer(self):
        mint = MovieInteger(42)
        check.equal(int(mint), 42)

        mint = MovieInteger("42")
        check.equal(int(mint), 42)

        mint = MovieInteger("2023-2024")
        with check.raises(TypeError):
            int(mint)

        with check.raises(ValueError):
            MovieInteger("garbage")

    def test_search_pattern(self):
        mint = MovieInteger("2020-2022, 2021, 2029, 2025-2027")
        check.equal(str(mint), "2020-2022, 2021, 2029, 2025-2027")
        check.equal(list(mint), [2020, 2021, 2022, 2025, 2026, 2027, 2029])
        check.is_true(2021 in mint)
        check.is_false(2042 in mint)

        with check.raises(ValueError):
            MovieInteger("2022-2024-2026")

    def test_bad_range(self):
        with check.raises(ValueError):
            MovieInteger("2020-garbage")


@pytest.mark.parametrize(
    "it, ot",
    [
        ({"ts"}, "ts"),
        ({"ts2", "ts1"}, "ts1, ts2"),
        ({""}, ""),
        (None, ""),
    ],
)
def test_setstr_to_str(it, ot):
    # Act and assert
    assert setstr_to_str(it) == ot
