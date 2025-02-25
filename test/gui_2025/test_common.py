"""Test Module."""

#  Copyright© 2025. Stephen Rigden.
#  Last modified 2/25/25, 1:42 PM by stephen.
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

from collections import UserDict

#  Copyright© 2025. Stephen Rigden.
#  Last modified 2/20/25, 6:36 AM by stephen.
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

from unittest.mock import MagicMock, call

import pytest
from pytest_check import check

from gui import common


# noinspection PyMissingOrEmptyDocstring
class TestLabelAndField:

    def test_input_zone_init(self, tk, ttk):
        # Arrange
        parent = ttk.Frame()
        col_0_width: int = 30
        col_1_width: int = 36

        # Act
        input_zone = common.LabelAndField(parent)

        # Assert
        check.equal(input_zone.parent, parent)
        check.is_instance(input_zone.row, common.Iterator)
        check.equal(input_zone.col_0_width, col_0_width)
        check.equal(input_zone.col_1_width, col_1_width)
        with check:
            # noinspection PyUnresolvedReferences
            input_zone.parent.assert_has_calls(
                [
                    call.columnconfigure(0, weight=1, minsize=col_0_width),
                    call.columnconfigure(1, weight=1),
                    call.columnconfigure(2, weight=1),
                ]
            )

    def test_create_label(self, tk, ttk, monkeypatch):
        # Arrange
        parent = ttk.Frame()
        label = MagicMock(name="label", autospec=True)
        monkeypatch.setattr(common.ttk, "Label", label)
        text = "test_create_label"
        row_ix = 42

        # Act
        input_zone = common.LabelAndField(parent)
        input_zone.create_label(text, row_ix)

        # Assert
        with check:
            label.assert_called_once_with(parent, text=text)
        with check:
            label().grid.assert_called_once_with(
                column=0, row=row_ix, sticky="ne", padx=5
            )

    def test_add_entry_row(self, tk, ttk, monkeypatch):
        # Arrange
        # noinspection DuplicatedCode
        parent = ttk.Frame()
        input_zone = common.LabelAndField(parent)
        input_zone.col_1_width = 37
        create_label = MagicMock(name="create_label", autospec=True)
        monkeypatch.setattr(
            common.LabelAndField,
            "create_label",
            create_label,
        )
        entry_field = MagicMock(name="entry_field", autospec=True)
        entry_field.label_text = "test of add_entry_row"
        row_ix = 0

        # Act
        input_zone.add_entry_row(entry_field)

        # Assert
        with check:
            create_label.assert_called_once_with(entry_field.label_text, row_ix)
        with check:
            entry_field.widget.configure.assert_called_once_with(
                width=input_zone.col_1_width
            )
        with check:
            entry_field.widget.grid.assert_called_once_with(column=1, row=row_ix)

    def test_add_text_row(self, tk, ttk, monkeypatch):
        # Arrange
        # noinspection DuplicatedCode
        parent = ttk.Frame()
        input_zone = common.LabelAndField(parent)
        input_zone.col_1_width = 38
        create_label = MagicMock(name="create_label", autospec=True)
        monkeypatch.setattr(
            common.LabelAndField,
            "create_label",
            create_label,
        )
        entry_field = MagicMock(name="entry_field", autospec=True)
        entry_field.label_text = "test of add_text_row"
        entry_field.widget.yview = MagicMock(name="yview", autospec=True)
        row_ix = 0
        scrollbar = MagicMock(name="scrollbar", autospec=True)
        monkeypatch.setattr(common.ttk, "Scrollbar", scrollbar)

        # Act
        input_zone.add_text_row(entry_field)

        # Assert
        with check:
            create_label.assert_called_once_with(entry_field.label_text, row_ix)
        with check:
            entry_field.widget.grid.assert_called_once_with(
                column=1, row=row_ix, sticky="e"
            )
        with check:
            scrollbar.assert_called_once_with(
                parent,
                orient="vertical",
                command=entry_field.widget.yview,
            )
        with check:
            entry_field.widget.configure.assert_has_calls(
                [
                    call(
                        width=input_zone.col_1_width - 2,
                        height=8,
                        wrap="word",
                        font="TkTextFont",
                        padx=15,
                        pady=10,
                    ),
                    call(yscrollcommand=scrollbar().set),
                ]
            )
        with check:
            scrollbar().grid.assert_called_once_with(
                column=2,
                row=row_ix,
                sticky="ns",
            )

    def test_add_checkbox_row(self, tk, ttk, monkeypatch):
        # Arrange
        parent = ttk.Frame()
        input_zone = common.LabelAndField(parent)
        input_zone.col_1_width = 37
        entry_field = MagicMock(name="entry_field", autospec=True)
        entry_field.label_text = "test of add_entry_row"
        row_ix = 0

        # Act
        input_zone.add_checkbox_row(entry_field)

        # Assert
        with check:
            entry_field.widget.configure.assert_called_once_with(
                text=entry_field.label_text, width=input_zone.col_1_width
            )
        with check:
            entry_field.widget.grid.assert_called_with(column=1, row=row_ix)

    def test_add_treeview_row(self, tk, ttk, monkeypatch):
        # Arrange
        parent = ttk.Frame()
        input_zone = common.LabelAndField(parent)
        input_zone.col_1_width = 38
        create_label = MagicMock(name="create_label", autospec=True)
        monkeypatch.setattr(
            common.LabelAndField,
            "create_label",
            create_label,
        )
        entry_field = MagicMock(name="entry_field", autospec=True)
        entry_field.label_text = "test of test_add_treeview_row"
        entry_field.widget.yview = MagicMock(name="yview", autospec=True)
        row_ix = 0
        scrollbar = MagicMock(name="scrollbar", autospec=True)
        monkeypatch.setattr(common.ttk, "Scrollbar", scrollbar)
        tag_item = "test of test_add_treeview_row"
        all_tags = ["tag_item", ""]

        # Act
        input_zone.add_treeview_row(entry_field, all_tags)

        # Assert
        with check:
            create_label.assert_called_once_with(
                entry_field.label_text,
                row_ix,
            )
        with check:
            entry_field.widget.column.assert_called_once_with(
                "tags",
                width=127,
            )
        with check:
            entry_field.widget.insert(
                "",
                "end",
                tag_item,
                text=tag_item,
                tags="tags",
            )
        with check:
            entry_field.widget.grid.assert_called_once_with(
                column=1,
                row=row_ix,
                sticky="e",
            )
        with check:
            scrollbar.assert_called_once_with(
                parent,
                orient="vertical",
                command=entry_field.widget.yview,
            )
        with check:
            entry_field.widget.configure.assert_has_calls(
                [
                    call(
                        columns=("tags",),
                        height=7,
                        selectmode="extended",
                        show="tree",
                        padding=5,
                    ),
                    call(yscrollcommand=scrollbar().set),
                ]
            )
        with check:
            scrollbar().grid.assert_called_once_with(
                column=2,
                row=row_ix,
                sticky="ns",
            )


def test_create_body_and_buttonbox(monkeypatch, tk):
    # Arrange
    frame = MagicMock(name="frame", autospec=True)
    monkeypatch.setattr(common.ttk, "Frame", frame)
    destroy = MagicMock(name="destroy", autospec=True)
    config = MagicMock(name="config", autospec=True)
    monkeypatch.setattr(common, "config", config)
    name = "test frame name"
    monkeypatch.setitem(common.config.current.escape_key_dict, name, destroy)
    common.config.current.escape_key_dict = UserDict()
    common.config.current.escape_key_dict[name] = None

    # Act
    outer_frame, body_frame, buttonbox = common.create_body_and_buttonbox(
        tk, name, destroy
    )

    # Assert
    with check:
        frame.assert_has_calls(
            [
                call(common.tk, name=name),
                call().grid(column=0, row=0, sticky="nsew"),
                call().columnconfigure(0, weight=1),
                call().rowconfigure(0, weight=1),
                call().rowconfigure(1, minsize=35),
                call(outer_frame, padding=(10, 25, 10, 0)),
                call().grid(column=0, row=0, sticky="n"),
                call(outer_frame, padding=(5, 5, 10, 10)),
                call().grid(column=0, row=1, sticky="e"),
            ]
        )
    check.equal(common.config.current.escape_key_dict[name], destroy)
    check.equal((outer_frame, body_frame, buttonbox), (frame(), frame(), frame()))


def test_create_button(monkeypatch, ttk):
    # Arrange
    grid = MagicMock(name="grid", autospec=True)
    bind = MagicMock(name="bind", autospec=True)
    button = MagicMock(name="button", autospec=True)
    monkeypatch.setattr(common.ttk, "Button", button)
    button = button()
    button.grid = grid
    button.bind = bind
    buttonbox = common.ttk.Frame()
    text = "Dummy"
    column = 42
    partial = MagicMock(name="partial", autospec=True)
    monkeypatch.setattr(common, "partial", partial)

    # Act
    result = common.create_button(
        buttonbox,
        text,
        column,
        lambda: None,
        "active",
    )

    # Assert
    with check:
        grid.assert_called_once_with(column=column, row=0)
    with check:
        bind.assert_called_once_with(
            "<Return>", common.partial(common.invoke_button, button)
        )
    check.equal(result, button)


def test_enable_button_with_true_state(monkeypatch):
    # Arrange
    state = MagicMock(name="state", autospec=True)
    configure = MagicMock(name="configure", autospec=True)
    button = MagicMock(name="button", autospec=True)
    monkeypatch.setattr(common.ttk, "Button", button)
    button.state = state
    button.configure = configure
    enable = True

    # Act
    common.enable_button(button, state=enable)

    # Assert
    with check:
        state.assert_called_once_with(["!disabled"])
    with check:
        configure.assert_called_once_with(default="active")


def test_enable_button_with_false_state(monkeypatch):
    # Arrange
    state = MagicMock(name="state", autospec=True)
    configure = MagicMock(name="configure", autospec=True)
    button = MagicMock(name="button", autospec=True)
    monkeypatch.setattr(common.ttk, "Button", button)
    button.state = state
    button.configure = configure
    enable = False

    # Act
    common.enable_button(button, state=enable)

    # Assert
    with check:
        state.assert_called_once_with(["disabled"])
    with check:
        configure.assert_called_once_with(default="disabled")


def test_invoke_button(monkeypatch):
    # Arrange
    invoke = MagicMock(name="invoke")
    button = MagicMock(name="button")
    monkeypatch.setattr(common.ttk, "Button", button)
    button.invoke = invoke

    # Act
    common.invoke_button(button)

    # Assert
    with check:
        invoke.assert_called_once_with()


def test_test_init_button_enablements(monkeypatch):
    # Arrange
    notify = MagicMock(name="observer", autospec=True)
    entry = MagicMock(name="entry", autospec=True)
    monkeypatch.setattr(common.tk_facade, "Entry", entry)
    entry.observer.notify = notify
    entry_fields: common.tk_facade.EntryFieldItem = {"dummy key": entry}

    # Act
    common.init_button_enablements(entry_fields)

    # Assert
    notify.assert_called_once_with()


@pytest.fixture(scope="function")
def tk(monkeypatch) -> MagicMock:
    """Stops Tk from starting."""
    tk = MagicMock(name="tk", autospec=True)
    monkeypatch.setattr(common, "tk", tk)
    return tk


@pytest.fixture(scope="function")
def ttk(monkeypatch) -> MagicMock:
    """Stops Tk.Ttk from starting."""
    ttk = MagicMock(name="ttk", autospec=True)
    monkeypatch.setattr(common, "ttk", ttk)
    return ttk
