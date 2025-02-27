"""Test Module."""

#  Copyright© 2025. Stephen Rigden.
#  Last modified 2/27/25, 6:57 AM by stephen.
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

import pytest
from pytest_check import check

from gui import common, tags


# noinspection PyMissingOrEmptyDocstring
class TestTagGUI:
    def test_tag_gui_init(self, tk, ttk, monkeypatch):
        # Arrange
        tag = "tag for test_tag_gui_init"
        name = tags.TagGUI.__name__.lower()
        destroy = MagicMock(name="destroy", autospec=True)
        monkeypatch.setattr(tags.TagGUI, "destroy", destroy)
        create_body_and_buttonbox = MagicMock(
            name="create_body_and_buttonbox",
            autospec=True,
        )
        outer_frame = MagicMock(name="outer_frame", autospec=True)
        body_frame = MagicMock(name="body_frame", autospec=True)
        buttonbox = MagicMock(name="buttonbox", autospec=True)
        create_body_and_buttonbox.return_value = (
            outer_frame,
            body_frame,
            buttonbox,
        )
        monkeypatch.setattr(
            common,
            "create_body_and_buttonbox",
            create_body_and_buttonbox,
        )
        user_input_frame = MagicMock(name="user_input_frame", autospec=True)
        monkeypatch.setattr(tags.TagGUI, "user_input_frame", user_input_frame)
        create_buttons = MagicMock(name="create_buttons", autospec=True)
        monkeypatch.setattr(tags.TagGUI, "create_buttons", create_buttons)
        init_button_enablements = MagicMock(
            name="init_button_enablements",
            autospec=True,
        )
        monkeypatch.setattr(common, "init_button_enablements", init_button_enablements)

        # Act
        tag_gui = tags.TagGUI(tk, tag)

        # Assert
        with check:
            create_body_and_buttonbox.assert_called_once_with(tk, name, destroy)
        check.equal(tag_gui.outer_frame, outer_frame)
        with check:
            user_input_frame.assert_called_once_with(body_frame)
        with check:
            create_buttons.assert_called_once_with(buttonbox)
        with check:
            init_button_enablements.assert_called_once_with(tag_gui.entry_fields)


@pytest.fixture(scope="function")
def tk(monkeypatch) -> MagicMock:
    """Stops Tk from starting."""
    tk = MagicMock(name="tk", autospec=True)
    monkeypatch.setattr(tags, "tk", tk)
    return tk


@pytest.fixture(scope="function")
def ttk(monkeypatch) -> MagicMock:
    """Stops Tk.Ttk from starting."""
    ttk = MagicMock(name="ttk", autospec=True)
    monkeypatch.setattr(tags, "ttk", ttk)
    return ttk
