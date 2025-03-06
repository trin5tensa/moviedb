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

from pytest_check import check

from gui import select


# noinspection PyMissingOrEmptyDocstring
class TestSelectGUI:
    def test_post_init(self, tk, ttk, monkeypatch):
        # Arrange
        body_and_buttonbox = MagicMock(
            name="body_and_buttonbox",
            autospec=True,
        )
        outer_frame = MagicMock(name="outer_frame", autospec=True)
        body_frame = MagicMock(name="body_frame", autospec=True)
        buttonbox = MagicMock(name="buttonbox", autospec=True)
        body_and_buttonbox.return_value = (outer_frame, body_frame, buttonbox)
        monkeypatch.setattr(
            select.common, "create_body_and_buttonbox", body_and_buttonbox
        )
        name = select.SelectGUI.__name__.lower()
        destroy = MagicMock(name="destroy", autospec=True)
        monkeypatch.setattr(select.SelectGUI, "destroy", destroy)
        treeview = MagicMock(name="treeview", autospec=True)
        monkeypatch.setattr(select.SelectGUI, "treeview", treeview)
        columns = MagicMock(name="columns", autospec=True)
        monkeypatch.setattr(select.SelectGUI, "columns", columns)
        populate = MagicMock(name="populate", autospec=True)
        monkeypatch.setattr(select.SelectGUI, "populate", populate)
        create_button = MagicMock(name="create_button", autospec=True)
        monkeypatch.setattr(select.common, "create_button", create_button)
        text = select.common.CANCEL_TEXT
        column = 0
        default = "active"
        selection_callback = MagicMock(name="selection_callback", autospec=True)

        # Act
        select.SelectGUI(
            tk.Tk,
            selection_callback=selection_callback,
            titles=["title"],
            widths=[42],
            rows=["test tag 1"],
        )

        # Assert
        with check:
            body_and_buttonbox.assert_called_once_with(tk.Tk, name, destroy)
        with check:
            treeview.assert_called_once_with(body_frame)
        with check:
            columns.assert_called_once_with()
        with check:
            populate.assert_called_once_with()
        with check:
            create_button.assert_called_once_with(
                buttonbox,
                text=text,
                column=column,
                command=destroy,
                default=default,
            )

    def test__post_init_with_bad_widths(self, tk, ttk):
        # Act Assert
        with pytest.raises(ValueError, match=select.BAD_TITLES_AND_WIDTHS):
            select.SelectGUI(
                tk.Tk,
                selection_callback=lambda: None,
                titles=["title"],
                widths=[],
                rows=["test tag 1"],
            )

    def test__post_init_with_bad_titles(self, tk, ttk):
        # Act Assert
        with pytest.raises(ValueError, match=select.BAD_TITLES_AND_WIDTHS):
            select.SelectGUI(
                tk.Tk,
                selection_callback=lambda: None,
                titles=[],
                widths=[42],
                rows=["test tag 1"],
            )

    def test__post_init_with_bad_widths_and_titles(self, tk, ttk):
        # Act Assert
        with pytest.raises(ValueError, match=select.BAD_TITLES_AND_WIDTHS):
            select.SelectGUI(
                tk.Tk,
                selection_callback=lambda: None,
                titles=["title"],
                widths=[42, 43],
                rows=["test tag 1"],
            )
