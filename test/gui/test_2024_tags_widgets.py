""" Test module. """

#  Copyright© 2025. Stephen Rigden.
#  Last modified 3/4/25, 7:12 AM by stephen.
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
from guiwidgets_2 import tk_facade


# noinspection PyMissingOrEmptyDocstring,DuplicatedCode
class TestSelectTagGUI:
    test_tag_1 = "test tag 1"
    test_tag_2 = "test tag 2"
    test_tag_3 = "test tag 3"
    dummy_tags_to_show = [test_tag_1, test_tag_2, test_tag_3]
    mock_select_tag_callback = MagicMock()

    @pytest.mark.skip("Moved create_button")
    def test_post_init(self, mock_tk, ttk, framing, monkeypatch):
        monkeypatch.setattr(
            guiwidgets_2.SelectTagGUI, "selection_callback", MagicMock()
        )
        monkeypatch.setattr(
            guiwidgets_2,
            "create_button",
            mock_create_button := MagicMock(),
        )

        cut = guiwidgets_2.SelectTagGUI(
            mock_tk,
            select_tag_callback=self.mock_select_tag_callback,
            tags_to_show=self.dummy_tags_to_show,
        )

        with check:
            framing.assert_called_once_with(
                cut.parent, type(cut).__name__.lower(), cut.destroy
            )
        _, body_frame, buttonbox = framing()
        with check:
            ttk.Treeview.assert_called_once_with(
                body_frame, columns=[], height=10, selectmode="browse"
            )
        tree = ttk.Treeview()
        with check:
            tree.grid.assert_called_once_with(column=0, row=0, sticky="w")
        with check:
            tree.column.assert_called_once_with("#0", width=350)
        with check:
            tree.heading.assert_called_once_with(
                "#0", text=guiwidgets_2.MOVIE_TAGS_TEXT
            )
        with check:
            tree.insert.assert_has_calls(
                [
                    call(
                        "",
                        "end",
                        iid=self.test_tag_1,
                        text=self.test_tag_1,
                        values=[],
                        tags=guiwidgets_2.MOVIE_TAGS,
                        open=True,
                    ),
                    call(
                        "",
                        "end",
                        iid=self.test_tag_2,
                        text=self.test_tag_2,
                        values=[],
                        tags=guiwidgets_2.MOVIE_TAGS,
                        open=True,
                    ),
                    call(
                        "",
                        "end",
                        iid=self.test_tag_3,
                        text=self.test_tag_3,
                        values=[],
                        tags=guiwidgets_2.MOVIE_TAGS,
                        open=True,
                    ),
                ]
            )
        with check:
            # noinspection PyUnresolvedReferences
            cut.selection_callback.assert_called_once_with(tree)
        with check:
            tree.bind.assert_called_once_with(
                "<<TreeviewSelect>>", func=cut.selection_callback(tree)
            )
        with check:
            mock_create_button.assert_called_once_with(
                buttonbox, guiwidgets_2.CANCEL_TEXT, 0, cut.destroy, default="active"
            )

    @pytest.mark.skip("Moved create_input_form_framing")
    def test_selection_callback(self, mock_tk, ttk, framing, monkeypatch):
        cut = guiwidgets_2.SelectTagGUI(
            mock_tk,
            select_tag_callback=self.mock_select_tag_callback,
            tags_to_show=self.dummy_tags_to_show,
        )
        monkeypatch.setattr(cut, "destroy", mock_destroy := MagicMock())
        tree = ttk.Treeview()

        callback = cut.selection_callback(tree)
        callback()

        with check:
            tree.selection.assert_called_once_with()
        with check:
            mock_destroy.assert_called_once_with()
        tag = tree.selection()[0]
        with check:
            self.mock_select_tag_callback.assert_called_once_with(tag)

    @pytest.mark.skip("Moved create_input_form_framing")
    def test_destroy(self, mock_tk, ttk, framing, monkeypatch):
        cut = guiwidgets_2.SelectTagGUI(
            mock_tk,
            select_tag_callback=self.mock_select_tag_callback,
            tags_to_show=self.dummy_tags_to_show,
        )

        cut.destroy()

        with check:
            # noinspection PyUnresolvedReferences
            cut.outer_frame.destroy.assert_called_once_with()


# noinspection PyMissingOrEmptyDocstring,DuplicatedCode
class TestPreferencesGUI:
    @pytest.mark.skip("Moved create_button")
    def test_post_init(
        self,
        mock_tk,
        ttk,
        framing,
        facade_entry,
        facade_checkbutton,
        input_zone,
        create_button,
        monkeypatch,
    ):
        test_api_key = "test api key"
        test_do_not_ask = False
        mock_save_callback = MagicMock()

        monkeypatch.setattr(
            guiwidgets_2.PreferencesGUI,
            "enable_save_button",
            mock_enable_save_button := MagicMock(),
        )

        cut = guiwidgets_2.PreferencesGUI(
            mock_tk,
            api_key=test_api_key,
            do_not_ask=test_do_not_ask,
            save_callback=mock_save_callback,
        )

        check.equal(cut.toplevel, mock_tk.Toplevel())
        with check:
            framing.assert_called_once_with(
                cut.toplevel, type(cut).__name__.lower(), cut.destroy
            )
        outer_frame, body_frame, buttonbox = framing()
        check.equal(cut.outer_frame, outer_frame)
        with check:
            input_zone.assert_called_once_with(body_frame)
        with check:
            # noinspection PyUnresolvedReferences
            tk_facade.Entry.assert_called_once_with(cut.api_key_text, body_frame)
        check.equal(cut.entry_fields[cut.api_key_name].original_value, test_api_key)
        with check:
            input_zone().add_entry_row.assert_called_once_with(
                cut.entry_fields[cut.api_key_name]
            )
        with check:
            # noinspection PyUnresolvedReferences
            tk_facade.Checkbutton.assert_called_once_with(cut.use_tmdb_text, body_frame)
        check.equal(cut.entry_fields[cut.use_tmdb_name].original_value, test_do_not_ask)
        with check:
            input_zone().add_checkbox_row.assert_called_once_with(
                cut.entry_fields[cut.use_tmdb_name]
            )
        with check:
            create_button.assert_has_calls(
                [
                    call(
                        buttonbox,
                        guiwidgets_2.SAVE_TEXT,
                        column=0,
                        command=cut.save,
                        default="disabled",
                    ),
                    call(
                        buttonbox,
                        guiwidgets_2.CANCEL_TEXT,
                        column=1,
                        command=cut.destroy,
                        default="active",
                    ),
                ]
            )
        with check:
            mock_enable_save_button.assert_has_calls(
                [
                    call(create_button()),
                    call(create_button()),
                ]
            )
        with check:
            for v in cut.entry_fields.values():
                # noinspection PyUnresolvedReferences
                v.observer.register.assert_called_once_with(
                    cut.enable_save_button(create_button())
                )

    @pytest.mark.skip("Moved enable_button")
    def test_enable_save_button(
        self,
        mock_tk,
        ttk,
        framing,
        facade_entry,
        facade_checkbutton,
        monkeypatch,
    ):
        test_api_key = "test api key"
        test_do_not_ask = False
        mock_save_callback = MagicMock()
        save_button = ttk.Button
        monkeypatch.setattr(
            guiwidgets_2,
            "enable_button",
            mock_enable_button := MagicMock(),
        )

        cut = guiwidgets_2.PreferencesGUI(
            mock_tk,
            api_key=test_api_key,
            do_not_ask=test_do_not_ask,
            save_callback=mock_save_callback,
        )
        callback = cut.enable_save_button(save_button)

        # noinspection PyUnresolvedReferences
        cut.entry_fields[cut.api_key_name].changed.return_value = False
        # noinspection PyUnresolvedReferences
        cut.entry_fields[cut.use_tmdb_name].changed.return_value = False
        callback()
        # noinspection PyUnresolvedReferences
        cut.entry_fields[cut.use_tmdb_name].changed.return_value = True
        callback()
        # noinspection PyUnresolvedReferences
        cut.entry_fields[cut.api_key_name].changed.return_value = True
        callback()
        # noinspection PyUnresolvedReferences
        cut.entry_fields[cut.use_tmdb_name].changed.return_value = False
        callback()

        with check:
            mock_enable_button.assert_has_calls(
                [
                    call(save_button, False),
                    call(save_button, True),
                    call(save_button, True),
                    call(save_button, True),
                ]
            )

    @pytest.mark.skip("Moved create_input_form_framing")
    def test_save(
        self,
        mock_tk,
        ttk,
        framing,
        facade_entry,
        facade_checkbutton,
        monkeypatch,
    ):
        test_api_key = "test api key"
        test_do_not_ask = False
        mock_save_callback = MagicMock()

        cut = guiwidgets_2.PreferencesGUI(
            mock_tk,
            api_key=test_api_key,
            do_not_ask=test_do_not_ask,
            save_callback=mock_save_callback,
        )
        monkeypatch.setattr(cut, "destroy", mock_destroy := MagicMock())
        cut.entry_fields[cut.api_key_name].current_value = test_api_key
        cut.entry_fields[cut.use_tmdb_name].current_value = test_do_not_ask

        cut.save()
        with check:
            # noinspection PyUnresolvedReferences
            cut.save_callback.assert_called_once_with(test_api_key, test_do_not_ask)
        with check:
            mock_destroy.assert_called_once_with()

    @pytest.mark.skip("Moved create_input_form_framing")
    def test_destroy(
        self,
        mock_tk,
        ttk,
        framing,
        facade_entry,
        facade_checkbutton,
    ):
        test_api_key = "test api key"
        test_do_not_ask = False
        mock_save_callback = MagicMock()

        cut = guiwidgets_2.PreferencesGUI(
            mock_tk,
            api_key=test_api_key,
            do_not_ask=test_do_not_ask,
            save_callback=mock_save_callback,
        )

        cut.destroy()
        with check:
            # noinspection PyUnresolvedReferences
            cut.toplevel.destroy.assert_called_once_with()


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
def framing(monkeypatch):
    monkeypatch.setattr("guiwidgets_2.create_input_form_framing", mock := MagicMock())
    mock.return_value = [MagicMock(), MagicMock(), MagicMock()]
    return mock


# noinspection PyMissingOrEmptyDocstring
@pytest.fixture
def create_button(monkeypatch):
    monkeypatch.setattr(guiwidgets_2.common, "create_button", mock := MagicMock())
    return mock


# noinspection PyMissingOrEmptyDocstring
@pytest.fixture
def tag_init_button_enablements(monkeypatch):
    monkeypatch.setattr(
        guiwidgets_2.common, "init_button_enablements", mock := MagicMock()
    )
    return mock


# noinspection PyMissingOrEmptyDocstring
@pytest.fixture
def input_zone(monkeypatch):
    monkeypatch.setattr(guiwidgets_2, "InputZone", mock := MagicMock())
    return mock


# noinspection PyMissingOrEmptyDocstring
@pytest.fixture
def facade_entry(monkeypatch):
    monkeypatch.setattr(tk_facade, "Entry", mock := MagicMock())
    return mock


# noinspection PyMissingOrEmptyDocstring
@pytest.fixture
def facade_checkbutton(monkeypatch):
    monkeypatch.setattr(tk_facade, "Checkbutton", mock := MagicMock())
    return mock


# noinspection PyMissingOrEmptyDocstring
@pytest.fixture
def focus_set(monkeypatch):
    monkeypatch.setattr(guiwidgets_2, "focus_set", mock := MagicMock())
    return mock


# noinspection PyMissingOrEmptyDocstring
@pytest.fixture
def enable_button(monkeypatch):
    monkeypatch.setattr(guiwidgets_2, "enable_button", mock := MagicMock())
    return mock
