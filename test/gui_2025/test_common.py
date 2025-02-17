"""Test Module."""

#  Copyright© 2025. Stephen Rigden.
#  Last modified 2/17/25, 1:36 PM by stephen.
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

from unittest.mock import MagicMock

from pytest_check import check

from gui import common


def test_test_init_button_enablements(monkeypatch):
    # Arrange
    notify = MagicMock(name="observer")
    entry = MagicMock(name="entry")
    monkeypatch.setattr(common.tk_facade, "Entry", entry)
    entry.observer.notify = notify
    entry_fields: common.tk_facade.EntryFieldItem = {"mock key": entry}

    # Act
    common.init_button_enablements(entry_fields)

    # Assert
    for v in entry_fields.values():
        # noinspection PyUnresolvedReferences
        notify.assert_called_once_with()
