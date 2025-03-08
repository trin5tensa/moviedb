"""Test Module."""

#  Copyright© 2025. Stephen Rigden.
#  Last modified 3/6/25, 8:18 AM by stephen.
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
from unittest.mock import MagicMock


@pytest.fixture(scope="function")
def tk(monkeypatch) -> MagicMock:
    """Stops Tk from starting."""
    tk = MagicMock(name="tk", autospec=True)
    return tk


@pytest.fixture(scope="function")
def ttk(monkeypatch) -> MagicMock:
    """Stops Tk.Ttk from starting."""
    ttk = MagicMock(name="ttk", autospec=True)
    return ttk
