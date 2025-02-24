"""Test Module."""

#  Copyright© 2025. Stephen Rigden.
#  Last modified 2/24/25, 12:38 PM by stephen.
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
class TestInputZone:

    def test_input_zone_init(self, tk, ttk):
        # Arrange
        parent = ttk.Frame()
        col_0_width: int = 30
        col_1_width: int = 36

        # Act
        input_zone = common.InputZone(parent)

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
        label = MagicMock(name="label")
        monkeypatch.setattr(common.ttk, "Label", label)
        text = "test_create_label"
        row_ix = 42

        # Act
        input_zone = common.InputZone(parent)
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
        parent = ttk.Frame()
        input_zone = common.InputZone(parent)
        input_zone.col_1_width = 37
        create_label = MagicMock(name="create_label")
        monkeypatch.setattr(common.InputZone, "create_label", create_label)
        entry_field = MagicMock(name="entry_field")
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


def test_create_body_and_buttonbox(monkeypatch, tk):
    # Arrange
    frame = MagicMock(name="frame")
    monkeypatch.setattr(common.ttk, "Frame", frame)
    destroy = MagicMock(name="destroy")
    config = MagicMock(name="config")
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
    grid = MagicMock(name="grid")
    bind = MagicMock(name="bind")
    button = MagicMock(name="button")
    monkeypatch.setattr(common.ttk, "Button", button)
    button = button()
    button.grid = grid
    button.bind = bind
    buttonbox = common.ttk.Frame()
    text = "Dummy"
    column = 42
    partial = MagicMock(name="partial")
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
    with check:
        state.assert_called_once_with(["!disabled"])
    with check:
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
    notify = MagicMock(name="observer")
    entry = MagicMock(name="entry")
    monkeypatch.setattr(common.tk_facade, "Entry", entry)
    entry.observer.notify = notify
    entry_fields: common.tk_facade.EntryFieldItem = {"dummy key": entry}

    # Act
    common.init_button_enablements(entry_fields)

    # Assert
    notify.assert_called_once_with()


@pytest.fixture(scope="function")
def tk(monkeypatch):
    """Block tk from starting."""
    tk = MagicMock(name="tk")
    monkeypatch.setattr(common, "tk", tk)
    return tk


@pytest.fixture(scope="function")
def ttk(monkeypatch):
    """Block ttk from starting."""
    ttk = MagicMock(name="ttk")
    monkeypatch.setattr(common, "ttk", ttk)
    return ttk
