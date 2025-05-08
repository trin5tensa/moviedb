"""Test Module."""

#  Copyright© 2025. Stephen Rigden.
#  Last modified 5/8/25, 9:37 AM by stephen.
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
from unittest.mock import MagicMock, call

from pytest_check import check

from moviebag import MovieBag, MovieInteger
from gui import tviewselect as mut


# noinspection PyMissingOrEmptyDocstring,DuplicatedCode
class TestSelectGUI:
    def test_post_init(self, tk, ttk, monkeypatch):
        """Test SelectGUI.__post_init__ correctly initializes the GUI.

        This test verifies that the __post_init__ method:
        1. Creates the body and buttonbox using create_body_and_buttonbox
        2. Creates a treeview using the treeview method
        3. Sets up columns for the treeview using the columns method
        4. Populates the treeview with data using the populate method
        5. Creates a cancel button using create_button
        6. Updates idle tasks using update_idletasks

        Args:
            tk: Mock for tkinter module
            ttk: Mock for tkinter.ttk module
            monkeypatch: Pytest fixture for patching dependencies
        """
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
        # noinspection DuplicatedCode
        monkeypatch.setattr(mut.SelectGUI, "treeview", treeview)
        columns = MagicMock(name="columns", autospec=True)
        monkeypatch.setattr(mut.SelectGUI, "columns", columns)
        populate = MagicMock(name="populate", autospec=True)
        monkeypatch.setattr(mut.SelectGUI, "populate", populate)
        create_button = MagicMock(name="create_button", autospec=True)
        monkeypatch.setattr(mut.common, "create_button", create_button)
        text = mut.CANCEL_TEXT
        column = 0
        default = "active"
        selection_callback = MagicMock(name="selection_callback", autospec=True)
        bind_key = MagicMock(name="bind_key", autospec=True)
        monkeypatch.setattr(mut.common, "bind_key", bind_key)

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
            body_and_buttonbox.assert_called_once_with(tk.Tk, name)
        with check:
            treeview.assert_called_once_with(body_frame)
        with check:
            columns.assert_called_once_with(treeview())
        with check:
            populate.assert_called_once_with(treeview())
        with check:
            create_button.assert_called_once_with(
                buttonbox,
                text=text,
                column=column,
                command=destroy,
                default=default,
            )
        check.equal(
            bind_key.call_args_list,
            [
                call(tk.Tk, "<Escape>", create_button()),
                call(tk.Tk, "<Command-.>", create_button()),
            ],
        )
        with check:
            tk.Tk.update_idletasks.assert_called_once_with()

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
        tree_obj = select_gui.treeview(body_frame)

        # Assert
        with check:
            tree.assert_called_once_with(body_frame, selectmode="browse")
        with check:
            tree_obj.grid.assert_called_once_with(column=0, row=0, sticky="w")
        with check:
            tree_obj.bind.assert_called_once_with(
                "<<TreeviewSelect>>",
                func=mut.partial(select_gui.treeview_callback, tree_obj),
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

    def test_columns(self, select_gui, ttk, monkeypatch):
        # Act and assert
        with check.raises(NotImplementedError):
            select_gui.columns(MagicMock(name="treeview", autospec=True))

    def test_populate(self, select_gui, ttk, monkeypatch):
        # Act and assert
        with check.raises(NotImplementedError):
            select_gui.populate(MagicMock(name="treeview", autospec=True))

    def test_destroy(self, select_gui, ttk, monkeypatch):
        # Arrange
        outer_frame = MagicMock(name="outer_frame", autospec=True)
        select_gui.outer_frame = outer_frame
        unbind = MagicMock(name="unbind", autospec=True)
        monkeypatch.setattr(select_gui.parent, "unbind", unbind)
        outer_frame = MagicMock(name="outer_frame", autospec=True)
        monkeypatch.setattr(select_gui, "outer_frame", outer_frame)

        # Act
        select_gui.destroy()

        # Assert
        check.equal(
            unbind.call_args_list,
            [
                call("<Escape>"),
                call("<Command-.>"),
            ],
        )
        outer_frame.destroy.assert_called_once_with()


# noinspection PyMissingOrEmptyDocstring
class TestSelectTagGUI:
    def test_columns(self, select_tag_gui, ttk, monkeypatch):
        # Arrange
        width = 500
        tree = MagicMock(name="tree", autospec=True)
        monkeypatch.setattr(mut.ttk, "Treeview", tree)

        # Act
        select_tag_gui.columns(tree)

        # Assert
        with check:
            tree.column.assert_called_once_with("#0", width=width)
        with check:
            tree.heading.assert_called_once_with("#0", text=mut.MOVIE_TAGS_TEXT)
        with check:
            tree.configure.assert_called_once_with(height=15)

    def test_populate(self, select_tag_gui, ttk, monkeypatch):
        # Arrange
        tree = MagicMock(name="tree", autospec=True)
        monkeypatch.setattr(mut.ttk, "Treeview", tree)

        # Act
        select_tag_gui.populate(tree)

        # Assert
        check.equal(select_tag_gui.rows, ["test tag 1", "test tag 2", "test tag 3"])
        with check:
            tree.insert.assert_has_calls(
                [
                    call("", "end", iid="0", text=select_tag_gui.rows[0], values=[]),
                    call("", "end", iid="1", text=select_tag_gui.rows[1], values=[]),
                    call("", "end", iid="2", text=select_tag_gui.rows[2], values=[]),
                ],
            )


class TestSelectMovieGUI:

    def test_columns(self, select_movie_gui, ttk, monkeypatch):
        # Arrange
        tree = MagicMock(name="tree", autospec=True)
        monkeypatch.setattr(mut.ttk, "Treeview", tree)

        # Act
        select_movie_gui.columns(tree)

        # Assert
        with check:
            tree.heading.assert_has_calls(
                [
                    call("#0", text=mut.TITLE.title()),
                    call("#1", text=mut.YEAR.title()),
                    call("#2", text=mut.DIRECTORS.title()),
                    call("#3", text=mut.DURATION.title()),
                    call("#4", text=mut.SYNOPSIS.title()),
                ]
            )
        with check:
            tree.column.assert_has_calls(
                [
                    call("#0", width=225),
                    call("#1", width=40),
                    call("#2", width=200),
                    call("#3", width=50),
                    call("#4", width=550),
                ]
            )
        with check:
            tree.configure.assert_called_once_with(
                height=25, columns=select_movie_gui.titles[1:]
            )

    def test_populate(self, select_movie_gui, ttk, monkeypatch):
        # Arrange
        tree = MagicMock(name="tree", autospec=True)
        monkeypatch.setattr(mut.ttk, "Treeview", tree)

        # Act
        select_movie_gui.populate(tree)

        # Assert
        check.equal(
            select_movie_gui.rows,
            [
                MovieBag(title="Test Movie 1", year=MovieInteger(4041)),
                MovieBag(
                    title="Test Movie 2",
                    year=MovieInteger(4042),
                    directors={"Dick Dir", "Edgar Ebo"},
                    duration=MovieInteger(42),
                    synopsis="A synopsis",
                ),
                MovieBag(title="Test Movie 3", year=MovieInteger(4043)),
            ],
        )
        with check:
            tree.insert.assert_has_calls(
                [
                    call(
                        "", "end", iid=0, text="Test Movie 1", values=(4041, "", "", "")
                    ),
                    call(
                        "",
                        "end",
                        iid=1,
                        text="Test Movie 2",
                        values=(4042, "Dick Dir, Edgar Ebo", 42, "A synopsis"),
                    ),
                    call(
                        "", "end", iid=2, text="Test Movie 3", values=(4043, "", "", "")
                    ),
                ]
            )


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


@pytest.fixture(scope="function")
def select_tag_gui(tk, monkeypatch):
    """Stops the SelectGUI.__post_init__ from running."""
    monkeypatch.setattr(
        mut.SelectGUI,
        "__post_init__",
        lambda *args, **kwargs: None,
    )

    # Create a skeleton SelectTagGUI object
    selection_callback = MagicMock(name="selection_callback", autospec=True)
    return mut.SelectTagGUI(
        tk.Tk,
        selection_callback=selection_callback,
        rows=["test tag 3", "test tag 2", "test tag 1"],
    )


@pytest.fixture(scope="function")
def select_movie_gui(tk, monkeypatch):
    """Stops the SelectGUI.__post_init__ from running."""
    monkeypatch.setattr(
        mut.SelectGUI,
        "__post_init__",
        lambda *args, **kwargs: None,
    )

    # Create a skeleton SelectMovieGUI object
    selection_callback = MagicMock(name="selection_callback", autospec=True)
    return mut.SelectMovieGUI(
        tk.Tk,
        selection_callback=selection_callback,
        rows=[
            MovieBag(title="Test Movie 3", year=MovieInteger(4043)),
            MovieBag(
                title="Test Movie 2",
                year=MovieInteger(4042),
                directors={"Dick Dir", "Edgar Ebo"},
                duration=MovieInteger(42),
                synopsis="A synopsis",
            ),
            MovieBag(title="Test Movie 1", year=MovieInteger(4041)),
        ],
    )
