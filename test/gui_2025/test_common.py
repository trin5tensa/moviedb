"""Tests for the gui.common module.

This module contains tests for the common GUI components and utility functions
used throughout the application. It tests:

1. The LabelAndField class, which formats a parent frame with columns for labels,
   fields, and scrollbars, and provides methods to add different types of UI elements.

2. Utility functions for creating UI elements and handling button interactions:
   - create_body_and_buttonbox: Creates frames for an input form
   - create_button: Creates a button with Return key binding
   - enable_button: Enables or disables a button
   - invoke_button: Invokes a button's command
   - init_button_enablements: Sets initial button states
   - showinfo: Displays an info dialog
   - askyesno: Displays a yes/no dialog

Each test follows the Arrange-Act-Assert pattern, with comments marking each section.
"""

#  Copyright© 2025. Stephen Rigden.
#  Last modified 5/2/25, 3:11 PM by stephen.
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


# noinspection GrazieInspection
class TestLabelAndField:
    """Tests for the LabelAndField class in the common module.

    The LabelAndField class formats a parent frame with three columns for labels,
    fields, and scrollbars, and provides methods to add different types of UI elements.

    These tests verify:
    - Proper initialization of the LabelAndField instance
    - Creation of labels
    - Adding entry fields
    - Adding text fields with scrollbars
    - Adding checkboxes
    - Adding treeviews with scrollbars
    """

    def test_input_zone_init(self, tk, ttk):
        """Test the initialization of the LabelAndField class.

        This test verifies that:
        - The parent frame is correctly stored
        - The row iterator is properly initialized
        - Default column widths are set correctly
        - The parent frame's columns are configured properly

        Args:
            tk: Pytest fixture for tkinter
            ttk: Pytest fixture for tkinter.ttk
        """
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
        """Test the _create_label method of LabelAndField.

        This test verifies that:
        - A ttk.Label is created with the correct parent and text
        - The label is properly positioned in the grid with the correct parameters

        Args:
            tk: Pytest fixture for tkinter
            ttk: Pytest fixture for tkinter.ttk
            monkeypatch: Pytest fixture for patching objects
        """
        # Arrange
        parent = ttk.Frame()
        label = MagicMock(name="label", autospec=True)
        monkeypatch.setattr(common.ttk, "Label", label)
        text = "test_create_label"
        row_ix = 42

        # Act
        input_zone = common.LabelAndField(parent)
        input_zone._create_label(text, row_ix)

        # Assert
        with check:
            label.assert_called_once_with(parent, text=text)
        with check:
            label().grid.assert_called_once_with(
                column=0, row=row_ix, sticky="ne", padx=5
            )

    def test_add_entry_row(self, tk, ttk, monkeypatch):
        """Test the add_entry_row method of LabelAndField.

        This test verifies that:
        - The _create_label method is called with the correct parameters
        - The entry field widget is configured with the correct width
        - The entry field widget is properly positioned in the grid

        Args:
            tk: Pytest fixture for tkinter
            ttk: Pytest fixture for tkinter.ttk
            monkeypatch: Pytest fixture for patching objects
        """
        # Arrange
        # noinspection DuplicatedCode
        parent = ttk.Frame()
        input_zone = common.LabelAndField(parent)
        input_zone.col_1_width = 37
        create_label = MagicMock(name="create_label", autospec=True)
        monkeypatch.setattr(
            common.LabelAndField,
            "_create_label",
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
        """Test the add_text_row method of LabelAndField.

        This test verifies that:
        - The _create_label method is called with the correct parameters
        - The text field widget is properly positioned in the grid
        - A scrollbar is created with the correct parameters
        - The text field widget is configured with the correct parameters
        - The scrollbar is properly positioned in the grid

        Args:
            tk: Pytest fixture for tkinter
            ttk: Pytest fixture for tkinter.ttk
            monkeypatch: Pytest fixture for patching objects
        """
        # Arrange
        # noinspection DuplicatedCode
        parent = ttk.Frame()
        input_zone = common.LabelAndField(parent)
        input_zone.col_1_width = 38
        create_label = MagicMock(name="create_label", autospec=True)
        monkeypatch.setattr(
            common.LabelAndField,
            "_create_label",
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
        """Test the add_checkbox_row method of LabelAndField.

        This test verifies that:
        - The checkbox widget is configured with the correct text and width
        - The checkbox widget is properly positioned in the grid

        Args:
            tk: Pytest fixture for tkinter
            ttk: Pytest fixture for tkinter.ttk
            monkeypatch: Pytest fixture for patching objects
        """
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
        """Test the add_treeview_row method of LabelAndField.

        This test verifies that:
        - The _create_label method is called with the correct parameters
        - The treeview widget's column is configured correctly
        - Items are properly inserted into the treeview
        - The treeview widget is properly positioned in the grid
        - A scrollbar is created with the correct parameters
        - The treeview widget is configured with the correct parameters
        - The scrollbar is properly positioned in the grid

        Args:
            tk: Pytest fixture for tkinter
            ttk: Pytest fixture for tkinter.ttk
            monkeypatch: Pytest fixture for patching objects
        """
        # Arrange
        # noinspection DuplicatedCode
        parent = ttk.Frame()
        input_zone = common.LabelAndField(parent)
        input_zone.col_1_width = 38
        create_label = MagicMock(name="create_label", autospec=True)
        monkeypatch.setattr(
            common.LabelAndField,
            "_create_label",
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


def test_create_body_and_buttonbox(monkeypatch, tk, ttk):
    """Test the create_body_and_buttonbox function.

    This test verifies that:
    - The frames are created with the correct parameters
    - The frames are properly positioned in the grid
    - The frames are configured correctly
    - The function returns the correct frames

    Args:
        monkeypatch: Pytest fixture for patching objects
        tk: Pytest fixture for tkinter
        ttk: Pytest fixture for tkinter.ttk
    """
    # Arrange
    frame = MagicMock(name="frame", autospec=True)
    monkeypatch.setattr(common.ttk, "Frame", frame)
    name = "test frame name"

    # Act
    outer_frame, body_frame, buttonbox = common.create_body_and_buttonbox(tk, name)

    # Assert
    with check:
        frame.assert_has_calls(
            [
                call(tk, name=name),
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
    check.equal((outer_frame, body_frame, buttonbox), (frame(), frame(), frame()))


def test_create_button(tk, ttk, monkeypatch):
    """Test the create_button function.

    This test verifies that:
    - The button is created with the correct parameters
    - The button is properly positioned in the grid
    - The Return key is bound to invoke the button
    - The function returns the created button

    Args:
        tk: Pytest fixture for tkinter
        ttk: Pytest fixture for tkinter.ttk
        monkeypatch: Pytest fixture for patching objects
    """
    # Arrange
    grid = MagicMock(name="grid", autospec=True)
    button = MagicMock(name="button", autospec=True)
    monkeypatch.setattr(common.ttk, "Button", button)
    button = button()
    button.grid = grid
    buttonbox = ttk.Frame()
    text = "Dummy"
    column = 42

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
    check.equal(result, button)


def test_enable_button_with_true_state(monkeypatch):
    """Test the enable_button function with state=True.

    This test verifies that when enable_button is called with state=True:
    - The button's state is set to ["!disabled"]
    - The button's default is configured as "active"

    Args:
        monkeypatch: Pytest fixture for patching objects
    """
    # Arrange
    # noinspection DuplicatedCode
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
    """Test the enable_button function with state=False.

    This test verifies that when enable_button is called with state=False:
    - The button's state is set to ["disabled"]
    - The button's default is configured as "disabled"

    Args:
        monkeypatch: Pytest fixture for patching objects
    """
    # Arrange
    # noinspection DuplicatedCode
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
    """Test the invoke_button function.

    This test verifies that:
    - The button's invoke method is called

    Args:
        monkeypatch: Pytest fixture for patching objects
    """
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
    """Test the init_button_enablements function.

    This test verifies that:
    - The notify method of each entry field's observer is called

    Args:
        monkeypatch: Pytest fixture for patching objects
    """
    # Arrange
    notify = MagicMock(name="observer", autospec=True)
    entry = MagicMock(name="entry", autospec=True)
    monkeypatch.setattr(common.tk_facade, "Entry", entry)
    entry.observer.notify = notify
    entry_fields: common.tk_facade.EntryFields = {"dummy key": entry}

    # Act
    common.init_button_enablements(entry_fields)

    # Assert
    notify.assert_called_once_with()


# noinspection DuplicatedCode
def test_showinfo(monkeypatch):
    """Test the showinfo function.

    This test verifies that:
    - The messagebox.showinfo function is called with the correct parameters

    Args:
        monkeypatch: Pytest fixture for patching objects
    """
    # Arrange
    message = "Dummy showinfo"
    detail = "Dummy detail"
    parent = MagicMock(name="parent", autospec=True)
    monkeypatch.setattr(common.ttk, "Frame", parent)
    icon = common.messagebox.INFO
    default = common.messagebox.OK
    showinfo = MagicMock(name="showinfo", autospec=True)
    monkeypatch.setattr(common.messagebox, "showinfo", showinfo)
    kwargs = {
        "parent": parent,
        "detail": detail,
        "icon": icon,
        "default": default,
    }

    # Act
    common.showinfo(message, **kwargs)

    # Assert
    showinfo.assert_called_once_with(
        message=message, parent=parent, detail=detail, icon=icon, default=default
    )


# noinspection DuplicatedCode
def test_askyesno(monkeypatch):
    """Test the askyesno function.

    This test verifies that:
    - The messagebox.askyesno function is called with the correct parameters
    - The function returns the result from messagebox.askyesno

    Args:
        monkeypatch: Pytest fixture for patching objects
    """
    # Arrange
    message = "Dummy askyesno"
    detail = "Dummy detail"
    parent = MagicMock(name="parent", autospec=True)
    monkeypatch.setattr(common.ttk, "Frame", parent)
    icon = common.messagebox.QUESTION
    default = common.messagebox.NO
    askyesno = MagicMock(name="askyesno", autospec=True)
    askyesno.return_value = True
    monkeypatch.setattr(common.messagebox, "askyesno", askyesno)
    kwargs = {
        "parent": parent,
        "detail": detail,
        "icon": icon,
        "default": default,
    }

    # Act
    result = common.askyesno(message, **kwargs)

    # Assert
    with check:
        askyesno.assert_called_once_with(
            message=message, parent=parent, detail=detail, icon=icon, default=default
        )
    check.equal(result, askyesno.return_value)
