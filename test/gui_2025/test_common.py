"""Test Module."""

#  Copyright© 2025. Stephen Rigden.
#  Last modified 2/18/25, 6:56 AM by stephen.
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


from gui import common


def test_enable_button_with_true_state(monkeypatch):
    # Arrange
    state = MagicMock(name="state")
    configure = MagicMock(name="configure")
    button = MagicMock(name="button")
    monkeypatch.setattr(common.ttk, "Button", button)
    button.state = state
    button.configure = configure
    enable = True

    # Act
    common.enable_button(button, state=enable)

    # Assert
    state.assert_called_once_with(["!disabled"])
    configure.assert_called_once_with(default="active")


def test_enable_button_with_false_state(monkeypatch):
    # Arrange
    state = MagicMock(name="state")
    configure = MagicMock(name="configure")
    button = MagicMock(name="button")
    monkeypatch.setattr(common.ttk, "Button", button)
    button.state = state
    button.configure = configure
    enable = False

    # Act
    common.enable_button(button, state=enable)

    # Assert
    state.assert_called_once_with(["disabled"])
    configure.assert_called_once_with(default="disabled")


def test_test_init_button_enablements(monkeypatch):
    # Arrange
    notify = MagicMock(name="observer")
    entry = MagicMock(name="entry")
    monkeypatch.setattr(common.tk_facade, "Entry", entry)
    entry.observer.notify = notify
    entry_fields: common.tk_facade.EntryFieldItem = {"dummy key": entry}

    # Act
    common.init_button_enablements(entry_fields)

    # Assert
    notify.assert_called_once_with()
