"""Test Module."""

#  Copyright© 2025. Stephen Rigden.
#  Last modified 3/7/25, 11:38 AM by stephen.
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

from gui import tviewselect as mut


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
        monkeypatch.setattr(mut.common, "create_body_and_buttonbox", body_and_buttonbox)
        name = mut.SelectGUI.__name__.lower()
        destroy = MagicMock(name="destroy", autospec=True)
        monkeypatch.setattr(mut.SelectGUI, "destroy", destroy)
        treeview = MagicMock(name="treeview", autospec=True)
        monkeypatch.setattr(mut.SelectGUI, "treeview", treeview)
        columns = MagicMock(name="columns", autospec=True)
        monkeypatch.setattr(mut.SelectGUI, "columns", columns)
        populate = MagicMock(name="populate", autospec=True)
        monkeypatch.setattr(mut.SelectGUI, "populate", populate)
        create_button = MagicMock(name="create_button", autospec=True)
        monkeypatch.setattr(mut.common, "create_button", create_button)
        text = mut.common.CANCEL_TEXT
        column = 0
        default = "active"
        selection_callback = MagicMock(name="selection_callback", autospec=True)

        # Act
        mut.SelectGUI(
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
        with pytest.raises(ValueError, match=mut.BAD_TITLES_AND_WIDTHS):
            mut.SelectGUI(
                tk.Tk,
                selection_callback=lambda x="": None,
                titles=["title"],
                widths=[],
                rows=["test tag 1"],
            )

    def test__post_init_with_bad_titles(self, tk, ttk):
        # Act Assert
        with pytest.raises(ValueError, match=mut.BAD_TITLES_AND_WIDTHS):
            mut.SelectGUI(
                tk.Tk,
                selection_callback=lambda x="": None,
                titles=[],
                widths=[42],
                rows=["test tag 1"],
            )

    def test__post_init_with_bad_widths_and_titles(self, tk, ttk):
        # Act Assert
        with pytest.raises(ValueError, match=mut.BAD_TITLES_AND_WIDTHS):
            mut.SelectGUI(
                tk.Tk,
                selection_callback=lambda x="": None,
                titles=["title"],
                widths=[42, 43],
                rows=["test tag 1"],
            )

    def test_treeview(self, select_gui, ttk, monkeypatch):
        # Arrange
        body_frame = MagicMock(name="body_frame", autospec=True)
        tree = MagicMock(name="tree", autospec=True)
        monkeypatch.setattr(mut.ttk, "Treeview", tree)
        tv_callback = MagicMock(name="tv_callback", autospec=True)
        monkeypatch.setattr(mut.SelectGUI, "treeview_callback", tv_callback)
        partial = MagicMock(name="partial", autospec=True)
        monkeypatch.setattr(mut, "partial", partial)

        # Act
        select_gui.treeview(body_frame)

        # Assert
        with check:
            tree.assert_called_once_with(body_frame, selectmode="browse")
        with check:
            tree().grid.assert_called_once_with(column=0, row=0, sticky="w")
        with check:
            tree().bind.assert_called_once_with(
                "<<TreeviewSelect>>",
                func=mut.partial(select_gui.treeview_callback, tree()),
            )

    def test_treeview_callback(self, select_gui, ttk, monkeypatch):
        # Arrange
        tree = MagicMock(name="tree", autospec=True)
        selected_row = 1
        tree.selection.return_value = [selected_row]
        monkeypatch.setattr(mut.ttk, "Treeview", tree)
        destroy = MagicMock(name="destroy", autospec=True)
        monkeypatch.setattr(mut.SelectGUI, "destroy", destroy)

        # Act
        select_gui.treeview_callback(tree)

        # Assert
        with check:
            # noinspection PyUnresolvedReferences
            select_gui.parent.after.assert_called_once_with(
                0, select_gui.selection_callback, select_gui.rows[selected_row]
            )
        with check:
            # noinspection PyUnresolvedReferences
            select_gui.destroy.assert_called_once_with()


@pytest.fixture(scope="function")
def select_gui(tk, monkeypatch):
    """Stops the SelectGUI.__post_init__ from running."""
    monkeypatch.setattr(
        mut.SelectGUI,
        "__post_init__",
        lambda *args, **kwargs: None,
    )

    # Create a skeleton SelectGUI object
    selection_callback = MagicMock(name="selection_callback", autospec=True)
    return mut.SelectGUI(
        tk.Tk,
        selection_callback=selection_callback,
        titles=["title"],
        widths=[42],
        rows=["test tag 1", "test tag 2", "test tag 3"],
    )
