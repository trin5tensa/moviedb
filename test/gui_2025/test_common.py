"""Test Module."""

#  Copyright© 2025. Stephen Rigden.
#  Last modified 2/22/25, 8:52 AM by stephen.
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

from pytest_check import check

from gui import common


def test_create_two_frame_form(monkeypatch):
    # Arrange
    tk = MagicMock(name="tk")
    monkeypatch.setattr(common, "tk", tk)
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


def test_create_button(monkeypatch):
    # Arrange
    ttk = MagicMock(name="ttk")
    monkeypatch.setattr(common, "ttk", ttk)
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
