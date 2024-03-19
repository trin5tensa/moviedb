""" Test module. """

#  Copyright (c) 2023-2024. Stephen Rigden.
#  Last modified 3/19/24, 1:19 PM by stephen.
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

import guiwidgets_2


# noinspection PyMissingOrEmptyDocstring
class TestInputZone:
    test_label_text = "test label text"

    def test_post_init(self, mock_tk, ttk):
        cut = guiwidgets_2.InputZone(mock_tk)

        with check:
            mock_tk.columnconfigure.assert_has_calls(
                [
                    call(0, weight=1, minsize=cut.col_0_width),
                    call(1, weight=1),
                    call(2, weight=1),
                ]
            )

    def test_add_entry_row(self, mock_tk, ttk, facade_entry, monkeypatch):
        cut = guiwidgets_2.InputZone(mock_tk)
        monkeypatch.setattr(cut, "create_label", mock_create_label := MagicMock())

        cut.add_entry_row(facade_entry)
        with check:
            mock_create_label.assert_called_once_with(facade_entry.label_text, 0)
        with check:
            facade_entry.widget.configure.assert_called_once_with(width=cut.col_1_width)
        with check:
            facade_entry.widget.grid.assert_called_once_with(column=1, row=0)

    def test_add_text_row(self, mock_tk, ttk, facade_text, scrollbar, monkeypatch):
        cut = guiwidgets_2.InputZone(mock_tk)
        monkeypatch.setattr(cut, "create_label", mock_create_label := MagicMock())

        cut.add_text_row(facade_text)
        with check:
            mock_create_label.assert_called_once_with(facade_text.label_text, 0)
        with check:
            scrollbar.assert_called_once_with(
                cut.parent, orient="vertical", command=facade_text.widget.yview
            )
        with check:
            facade_text.widget.configure.assert_has_calls(
                [
                    call(
                        width=cut.col_1_width - 2,
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
            facade_text.widget.grid.assert_called_once_with(column=1, row=0, sticky="e")
        with check:
            scrollbar().grid.assert_called_once_with(column=2, row=0, sticky="ns")

    def test_add_checkbox_row(self, mock_tk, ttk, facade_checkbox, monkeypatch):
        cut = guiwidgets_2.InputZone(mock_tk)

        cut.add_entry_row(facade_checkbox)
        with check:
            facade_checkbox.widget.configure.assert_called_once_with(
                width=cut.col_1_width
            )
        with check:
            facade_checkbox.widget.grid.assert_called_once_with(column=1, row=0)

    def test_add_treeview_row(
        self, mock_tk, ttk, facade_treeview, scrollbar, monkeypatch
    ):
        test_tag_1 = "test tag 1"
        test_tag_2 = "test tag 2"
        test_tag_3 = "test tag 3"
        test_all_tags = [test_tag_1, test_tag_2, test_tag_3]

        cut = guiwidgets_2.InputZone(mock_tk)
        monkeypatch.setattr(cut, "create_label", mock_create_label := MagicMock())

        cut.add_treeview_row(facade_treeview, test_all_tags)
        with check:
            mock_create_label.assert_called_once_with(facade_treeview.label_text, 0)
        with check:
            scrollbar.assert_called_once_with(
                cut.parent, orient="vertical", command=facade_treeview.widget.yview
            )
        with check:
            facade_treeview.widget.configure.assert_has_calls(
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
            facade_treeview.widget.column.assert_called_once_with("tags", width=127)
        with check:
            facade_treeview.widget.insert.assert_has_calls(
                [
                    call("", "end", test_tag_1, text=test_tag_1, tags="tags"),
                    call("", "end", test_tag_2, text=test_tag_2, tags="tags"),
                    call("", "end", test_tag_3, text=test_tag_3, tags="tags"),
                ]
            )
        with check:
            facade_treeview.widget.grid.assert_called_once_with(
                column=1, row=0, sticky="e"
            )
        with check:
            scrollbar().grid.assert_called_once_with(column=2, row=0, sticky="ns")

    def test_create_label(self, mock_tk, ttk, label):
        test_text = "test text"

        cut = guiwidgets_2.InputZone(mock_tk)

        cut.create_label(test_text, 42)
        with check:
            label.assert_called_once_with(mock_tk, text=test_text)
        with check:
            label().grid.assert_called_once_with(column=0, row=42, sticky="ne", padx=5)


# noinspection PyMissingOrEmptyDocstring
class TestCreateInputFormFraming:
    def test_create_input_form_framing(self, mock_tk, ttk, monkeypatch):
        test_name = "test widget"
        test_destroy = MagicMock()
        monkeypatch.setattr(
            guiwidgets_2,
            "create_body_and_button_frames",
            mock_create_body_and_button_frames := MagicMock(),
        )
        outer_frame = MagicMock()
        body_frame = MagicMock()
        buttonbox = MagicMock()
        mock_create_body_and_button_frames.return_value = (
            outer_frame,
            body_frame,
            buttonbox,
        )

        result = guiwidgets_2.create_input_form_framing(
            mock_tk, test_name, test_destroy
        )
        with check:
            mock_create_body_and_button_frames.assert_called_once_with(
                mock_tk, test_name, test_destroy
            )
        check.equal(result, (outer_frame, body_frame, buttonbox))
        with check:
            outer_frame.rowconfigure.assert_has_calls(
                [call(0, weight=1), call(1, minsize=35)]
            )


# noinspection PyMissingOrEmptyDocstring
@pytest.fixture
def mock_tk(monkeypatch):
    monkeypatch.setattr(guiwidgets_2, "tk", mock := MagicMock())
    return mock


# noinspection PyMissingOrEmptyDocstring
@pytest.fixture
def ttk(monkeypatch):
    monkeypatch.setattr(guiwidgets_2, "ttk", mock := MagicMock())
    return mock


# noinspection PyMissingOrEmptyDocstring
@pytest.fixture
def facade_entry(monkeypatch):
    monkeypatch.setattr(guiwidgets_2.tk_facade, "Entry", mock := MagicMock())
    return mock


# noinspection PyMissingOrEmptyDocstring
@pytest.fixture
def facade_text(monkeypatch):
    monkeypatch.setattr(guiwidgets_2.tk_facade, "Text", mock := MagicMock())
    return mock


# noinspection PyMissingOrEmptyDocstring
@pytest.fixture
def facade_checkbox(monkeypatch):
    monkeypatch.setattr(guiwidgets_2.tk_facade, "Checkbutton", mock := MagicMock())
    return mock


# noinspection PyMissingOrEmptyDocstring
@pytest.fixture
def facade_treeview(monkeypatch):
    monkeypatch.setattr(guiwidgets_2.tk_facade, "Treeview", mock := MagicMock())
    return mock


# noinspection PyMissingOrEmptyDocstring
@pytest.fixture
def scrollbar(ttk, monkeypatch):
    monkeypatch.setattr(ttk, "Scrollbar", mock := MagicMock())
    return mock


# noinspection PyMissingOrEmptyDocstring
@pytest.fixture
def label(ttk, monkeypatch):
    monkeypatch.setattr(ttk, "Label", mock := MagicMock())
    return mock
