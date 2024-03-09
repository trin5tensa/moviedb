""" Test guiwidgets.

This module contains new tests written after Brian Okken's course and book on pytest in Fall 2022 together with
mocks from Python's unittest.mok module.

Strategy:
Detect any changes to calls to other functions and methods and changes to the arguments to those calls.
Changes in the API of called functions and methods are not part of this test suite.
"""

#  Copyright (c) 2023-2024. Stephen Rigden.
#  Last modified 3/9/24, 10:00 AM by stephen.
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

import tkinter.messagebox
from contextlib import contextmanager
from unittest.mock import MagicMock, call

import pytest
from pytest_check import check

import config
import guiwidgets_2

TEST_TK_ROOT = "test tk_root"
TEST_TITLE = "test moviedb"
TEST_VERSION = "Test version"


# noinspection PyMissingOrEmptyDocstring,DuplicatedCode
@pytest.mark.skip
class TestAddTagGUI:
    def test_post_init(
        self, monkeypatch, create_entry_fields, general_framing, create_buttons
    ):
        monkeypatch.setattr("guiwidgets_2.InputZone", mock_inputzone := MagicMock())
        monkeypatch.setattr("guiwidgets_2._focus_set", mock_focus_set := MagicMock())
        monkeypatch.setattr(
            "guiwidgets_2.AddTagGUI.create_buttons", mock_create_buttons := MagicMock()
        )
        _, body_frame, mock_buttonbox = general_framing()

        with self.addtaggui(monkeypatch) as cut:
            # Test initialize an internal dictionary.
            with check:
                create_entry_fields.assert_called_once_with(
                    guiwidgets_2.TAG_FIELD_NAMES, guiwidgets_2.TAG_FIELD_TEXTS
                )

            # Test create frames.
            with check:
                general_framing.assert_called_with(
                    cut.parent, type(cut).__name__.lower(), cut.destroy
                )

            # Test create label and field.
            with check:
                mock_inputzone.assert_called_once_with(body_frame)
            with check:
                mock_inputzone().add_entry_row.assert_called_once_with(
                    cut.entry_fields[guiwidgets_2.MOVIE_TAGS]
                )
            with check:
                mock_focus_set.assert_called_once_with(
                    cut.entry_fields[guiwidgets_2.MOVIE_TAGS].widget
                )
            with check:
                mock_create_buttons.assert_called_once_with(mock_buttonbox)

    def test_create_buttons(self, monkeypatch, create_entry_fields, general_framing):
        monkeypatch.setattr(
            "guiwidgets_2._create_button", mock_create_button := MagicMock()
        )
        monkeypatch.setattr("guiwidgets_2.ttk.Button", mock_button := MagicMock())
        monkeypatch.setattr("guiwidgets_2.AddTagGUI.enable_commit_button", MagicMock())
        _, _, mock_buttonbox = general_framing()

        with self.addtaggui(monkeypatch) as cut:
            column_num = guiwidgets_2.itertools.count()
            with check:
                mock_create_button.assert_has_calls(
                    [
                        call(
                            mock_buttonbox,
                            guiwidgets_2.COMMIT_TEXT,
                            column=next(column_num),
                            command=cut.commit,
                            default="disabled",
                        ),
                        call(
                            mock_buttonbox,
                            guiwidgets_2.CANCEL_TEXT,
                            column=next(column_num),
                            command=cut.destroy,
                            default="active",
                        ),
                    ]
                )

            tag_field = cut.entry_fields[guiwidgets_2.MOVIE_TAGS]
            with check:
                tag_field.observer.register.assert_called_once_with(
                    cut.enable_commit_button(mock_button, tag_field)
                )

    @pytest.mark.skip
    def test_enable_save_button(self, monkeypatch, movie_patches):
        monkeypatch.setattr("guiwidgets_2.ttk.Button", mock_button := MagicMock())
        monkeypatch.setattr(
            "guiwidgets_2.enable_button", mock_enable_button := MagicMock()
        )
        with self.addtaggui(monkeypatch) as cut:
            tag_field = cut.entry_fields["dummy"]
            callback = cut.enable_commit_button(mock_button, tag_field)
            callback()
            with check:
                mock_enable_button.assert_called_once_with(mock_button, True)

    def test_commit(self, monkeypatch, create_entry_fields):
        mock_destroy_calls = []
        dummy_tag = "dummy tag"

        with self.addtaggui(monkeypatch) as cut:
            monkeypatch.setattr(
                cut,
                "destroy",
                lambda: mock_destroy_calls.append(True),
            )
            cut.entry_fields[guiwidgets_2.MOVIE_TAGS].textvariable.get.return_value = (
                dummy_tag
            )

            cut.commit()
            with check:
                cut.add_tag_callback.assert_called_once_with(dummy_tag)
            with check:
                check.equal(mock_destroy_calls, [True])

            # test null tag
            cut.entry_fields[guiwidgets_2.MOVIE_TAGS].textvariable.get.return_value = ""

            cut.commit()
            # cut.commit has been called twice but its `if tag` suite was executed once.
            with check:
                cut.add_tag_callback.assert_called_once_with(dummy_tag)
            with check:
                check.equal(mock_destroy_calls, [True])

    def test_destroy(self, monkeypatch, create_entry_fields):
        with self.addtaggui(monkeypatch) as cut:
            monkeypatch.setattr(cut, "outer_frame", mock_outer_frame := MagicMock())

            cut.destroy()
            mock_outer_frame.destroy.assert_called_once_with()

    @contextmanager
    def addtaggui(self, monkeypatch):
        yield guiwidgets_2.AddTagGUI(
            patch_config(monkeypatch).current.tk_root, add_tag_callback=MagicMock()
        )


# noinspection PyMissingOrEmptyDocstring
@pytest.mark.skip
class TestEditTagGUI:
    dummy_tag = "dummy tag"

    # noinspection DuplicatedCode
    def test_post_init(
        self, monkeypatch, create_entry_fields, general_framing, create_buttons
    ):
        monkeypatch.setattr("guiwidgets_2.InputZone", mock_inputzone := MagicMock())
        monkeypatch.setattr("guiwidgets_2._focus_set", mock_focus_set := MagicMock())
        monkeypatch.setattr(
            "guiwidgets_2.EditTagGUI.create_buttons", mock_create_buttons := MagicMock()
        )
        _, body_frame, mock_buttonbox = general_framing()

        with self.edittaggui(monkeypatch) as cut:
            # Test initialize an internal dictionary.
            with check:
                create_entry_fields.assert_called_once_with(
                    guiwidgets_2.TAG_FIELD_NAMES, guiwidgets_2.TAG_FIELD_TEXTS
                )
            check.equal(
                cut.entry_fields[guiwidgets_2.MOVIE_TAGS].original_value,
                self.dummy_tag,
            )

            # Test create outer frames to hold fields and buttons.
            with check:
                general_framing.assert_called_with(
                    cut.parent, type(cut).__name__.lower(), cut.destroy
                )

            # Test create field label and field entry widgets.
            with check:
                mock_inputzone.assert_called_once_with(body_frame)
            with check:
                mock_inputzone().add_entry_row.assert_called_once_with(
                    cut.entry_fields[guiwidgets_2.MOVIE_TAGS]
                )
            with check:
                mock_focus_set.assert_called_once_with(
                    cut.entry_fields[guiwidgets_2.MOVIE_TAGS].widget
                )
            with check:
                mock_create_buttons.assert_called_once_with(mock_buttonbox)

    # noinspection DuplicatedCode
    def test_create_buttons(self, monkeypatch, create_entry_fields, general_framing):
        monkeypatch.setattr(
            "guiwidgets_2._create_button", mock_create_button := MagicMock()
        )
        monkeypatch.setattr("guiwidgets_2.ttk.Button", mock_button := MagicMock())
        monkeypatch.setattr("guiwidgets_2.EditTagGUI.enable_commit_button", MagicMock())
        _, _, mock_buttonbox = general_framing()

        with self.edittaggui(monkeypatch) as cut:
            column_num = guiwidgets_2.itertools.count()
            with check:
                mock_create_button.assert_has_calls(
                    [
                        call(
                            mock_buttonbox,
                            guiwidgets_2.COMMIT_TEXT,
                            column=next(column_num),
                            command=cut.commit,
                            default="disabled",
                        ),
                        call(
                            mock_buttonbox,
                            guiwidgets_2.DELETE_TEXT,
                            column=next(column_num),
                            command=cut.delete,
                            default="active",
                        ),
                        call(
                            mock_buttonbox,
                            guiwidgets_2.CANCEL_TEXT,
                            column=next(column_num),
                            command=cut.destroy,
                            default="active",
                        ),
                    ]
                )

            tag_field = cut.entry_fields[guiwidgets_2.MOVIE_TAGS]
            with check:
                tag_field.observer.register.assert_called_once_with(
                    cut.enable_commit_button(mock_button, tag_field)
                )

    # noinspection DuplicatedCode
    @pytest.mark.skip
    def test_enable_save_button(self, monkeypatch, movie_patches):
        monkeypatch.setattr("guiwidgets_2.ttk.Button", mock_button := MagicMock())
        monkeypatch.setattr(
            "guiwidgets_2.enable_button", mock_enable_button := MagicMock()
        )
        with self.edittaggui(monkeypatch) as cut:
            tag_field = cut.entry_fields["dummy"]
            callback = cut.enable_commit_button(mock_button, tag_field)
            callback()
            with check:
                mock_enable_button.assert_called_once_with(mock_button, True)

    # noinspection DuplicatedCode
    def test_commit(self, monkeypatch, create_entry_fields):
        with self.edittaggui(monkeypatch) as cut:
            monkeypatch.setattr(cut, "destroy", mock_destroy := MagicMock())
            monkeypatch.setattr(cut, "delete", mock_delete := MagicMock())

            # test with non empty tag
            cut.commit()
            with check:
                cut.edit_tag_callback.assert_called_once_with(
                    cut.entry_fields[guiwidgets_2.MOVIE_TAGS].textvariable.get()
                )
            with check:
                mock_destroy.assert_called_once_with()

            # test with empty tag
            cut.entry_fields[guiwidgets_2.MOVIE_TAGS].textvariable.get.return_value = ""
            cut.commit()
            with check:
                mock_delete.assert_called_once_with()

    # noinspection DuplicatedCode
    @pytest.mark.skip
    def test_delete(self, monkeypatch, create_entry_fields):
        monkeypatch.setattr(
            "guiwidgets_2.gui_askyesno", mock_gui_askyesno := MagicMock()
        )
        focus_set_calls = []
        monkeypatch.setattr(
            "guiwidgets_2._focus_set",
            lambda *args: focus_set_calls.append(*args),
        )
        with self.edittaggui(monkeypatch) as cut:
            monkeypatch.setattr(cut, "destroy", mock_destroy := MagicMock())

            # User responds 'No' - Do not delete movie.
            mock_gui_askyesno.return_value = False
            cut.delete()
            with check:
                mock_gui_askyesno.assert_called_once_with(
                    message=f"Do you want to delete tag '{self.dummy_tag}'?",
                    icon="question",
                    default="no",
                    parent=cut.parent,
                )
            # It's called twice: Once in __post_init__ and secondly if user clicks no in delete dialog.
            with check:
                cut.entry_fields[
                    guiwidgets_2.MOVIE_TAGS
                ].textvariable.set.assert_has_calls(
                    [
                        call(self.dummy_tag),
                        call(self.dummy_tag),
                    ]
                )
            widget = cut.entry_fields[guiwidgets_2.MOVIE_TAGS].widget
            # It's called twice: Once in __post_init__ and secondly if user clicks no in delete dialog.
            check.equal(
                focus_set_calls,
                [widget, widget],
            )

            # User responds 'Yes' - Go ahead and delete movie.
            mock_gui_askyesno.return_value = True
            cut.delete()
            with check:
                cut.delete_tag_callback.assert_called_once_with()
            with check:
                mock_destroy.assert_called_once_with()

    def test_destroy(self, monkeypatch, create_entry_fields):
        with self.edittaggui(monkeypatch) as cut:
            monkeypatch.setattr(cut, "outer_frame", mock_outer_frame := MagicMock())

            cut.destroy()
            mock_outer_frame.destroy.assert_called_once_with()

    @contextmanager
    def edittaggui(self, monkeypatch):
        yield guiwidgets_2.EditTagGUI(
            patch_config(monkeypatch).current.tk_root,
            tag=self.dummy_tag,
            delete_tag_callback=MagicMock(),
            edit_tag_callback=MagicMock(),
        )


# noinspection PyMissingOrEmptyDocstring,DuplicatedCode
@pytest.mark.skip
class TestSearchTagGUI:
    def test_post_init(self, monkeypatch, create_entry_fields, general_framing):
        monkeypatch.setattr("guiwidgets_2.InputZone", mock_inputzone := MagicMock())
        monkeypatch.setattr("guiwidgets_2._focus_set", mock_focus_set := MagicMock())
        monkeypatch.setattr(
            "guiwidgets_2.SearchTagGUI.create_buttons",
            mock_create_buttons := MagicMock(),
        )

        _, body_frame, mock_buttonbox = general_framing()

        with self.searchtaggui(monkeypatch) as cut:
            # Test initialize an internal dictionary.
            with check:
                create_entry_fields.assert_called_once_with(
                    guiwidgets_2.TAG_FIELD_NAMES, guiwidgets_2.TAG_FIELD_TEXTS
                )

            # Test create frames.
            with check:
                general_framing.assert_called_with(
                    cut.parent, type(cut).__name__.lower(), cut.destroy
                )

            # Test create label and field.
            with check:
                mock_inputzone.assert_called_once_with(body_frame)
            with check:
                mock_inputzone().add_entry_row.assert_called_once_with(
                    cut.entry_fields[guiwidgets_2.MOVIE_TAGS]
                )
            with check:
                mock_focus_set.assert_called_once_with(
                    cut.entry_fields[guiwidgets_2.MOVIE_TAGS].widget
                )
            with check:
                mock_create_buttons.assert_called_once_with(mock_buttonbox)

    def test_create_buttons(self, monkeypatch, create_entry_fields, general_framing):
        monkeypatch.setattr(
            "guiwidgets_2._create_button", mock_create_button := MagicMock()
        )
        monkeypatch.setattr("guiwidgets_2.ttk.Button", mock_button := MagicMock())
        monkeypatch.setattr(
            "guiwidgets_2.SearchTagGUI.enable_search_button", MagicMock()
        )
        _, _, mock_buttonbox = general_framing()

        with self.searchtaggui(monkeypatch) as cut:
            column_num = guiwidgets_2.itertools.count()
            with check:
                mock_create_button.assert_has_calls(
                    [
                        call(
                            mock_buttonbox,
                            guiwidgets_2.SEARCH_TEXT,
                            column=next(column_num),
                            command=cut.search,
                            default="disabled",
                        ),
                        call(
                            mock_buttonbox,
                            guiwidgets_2.CANCEL_TEXT,
                            column=next(column_num),
                            command=cut.destroy,
                            default="active",
                        ),
                    ]
                )

            tag_field = cut.entry_fields[guiwidgets_2.MOVIE_TAGS]
            with check:
                tag_field.observer.register.assert_called_once_with(
                    cut.enable_search_button(mock_button, tag_field)
                )

    @pytest.mark.skip
    def test_enable_search_button(self, monkeypatch, movie_patches):
        monkeypatch.setattr("guiwidgets_2.ttk.Button", mock_button := MagicMock())
        monkeypatch.setattr(
            "guiwidgets_2.enable_button", mock_enable_button := MagicMock()
        )
        with self.searchtaggui(monkeypatch) as cut:
            tag_field = cut.entry_fields["dummy"]
            callback = cut.enable_search_button(mock_button, tag_field)
            callback()
            with check:
                mock_enable_button.assert_called_once_with(mock_button, True)

    def test_search(self, monkeypatch, create_entry_fields):
        monkeypatch.setattr(
            guiwidgets_2, "gui_messagebox", mock_guimessgebox := MagicMock()
        )
        with self.searchtaggui(monkeypatch) as cut:
            monkeypatch.setattr(cut, "destroy", mock_destroy := MagicMock())

            # Regular control flow
            cut.search()
            with check:
                cut.search_tag_callback.assert_called_once_with(
                    cut.entry_fields[guiwidgets_2.MOVIE_TAGS].textvariable.get()
                )
            with check:
                mock_destroy.assert_called_once_with()

            # Exception DatabaseSearchFoundNothing control flow
            cut.search_tag_callback.side_effect = (
                guiwidgets_2.exception.DatabaseSearchFoundNothing
            )
            cut.search()
            with check:
                mock_guimessgebox.assert_called_once_with(
                    cut.parent,
                    guiwidgets_2.NO_MATCH_MESSAGE,
                    guiwidgets_2.NO_MATCH_DETAIL,
                )

    def test_destroy(self, monkeypatch, create_entry_fields):
        with self.searchtaggui(monkeypatch) as cut:
            monkeypatch.setattr(cut, "outer_frame", mock_outer_frame := MagicMock())

            cut.destroy()
            mock_outer_frame.destroy.assert_called_once_with()

    @contextmanager
    def searchtaggui(self, monkeypatch):
        yield guiwidgets_2.SearchTagGUI(
            patch_config(monkeypatch).current.tk_root, search_tag_callback=MagicMock()
        )


# noinspection PyMissingOrEmptyDocstring,DuplicatedCode
@pytest.mark.skip
class TestSelectTagGUI:
    TAGS_TO_SHOW = ["test tag 1", "test tag 2"]

    def test_post_init(self, monkeypatch, create_entry_fields, general_framing):
        monkeypatch.setattr("guiwidgets_2.ttk.Treeview", mock_tree := MagicMock())
        monkeypatch.setattr(
            guiwidgets_2.SelectTagGUI,
            "selection_callback",
            mock_selection_callback_wrapper := MagicMock(),
        )
        monkeypatch.setattr(
            "guiwidgets_2.create_button", mock_create_button := MagicMock()
        )
        _, body_frame, mock_buttonbox = general_framing()

        with self.selecttaggui(monkeypatch) as cut:
            # Test create outer frames to hold fields and buttons.
            with check:
                general_framing.assert_called_with(
                    cut.parent, type(cut).__name__.lower(), cut.destroy
                )

            # Test create and grid treeview
            with check:
                mock_tree.assert_called_once_with(
                    body_frame, columns=[], height=10, selectmode="browse"
                )
            with check:
                mock_tree().grid.assert_called_once_with(column=0, row=0, sticky="w")

            # Test specify column width and title
            with check:
                mock_tree().column.assert_called_once_with("#0", width=350)
            with check:
                mock_tree().heading.assert_called_once_with(
                    "#0", text=guiwidgets_2.MOVIE_TAGS_TEXT
                )

            # Test populate the treeview rows
            with check:
                mock_tree().insert.assert_has_calls(
                    [
                        call(
                            "",
                            "end",
                            iid=self.TAGS_TO_SHOW[0],
                            text=self.TAGS_TO_SHOW[0],
                            values=[],
                            tags=guiwidgets_2.MOVIE_TAGS,
                            open=True,
                        ),
                        call(
                            "",
                            "end",
                            iid=self.TAGS_TO_SHOW[1],
                            text=self.TAGS_TO_SHOW[1],
                            values=[],
                            tags=guiwidgets_2.MOVIE_TAGS,
                            open=True,
                        ),
                    ]
                )

            # Test bind the treeview callback
            with check:
                mock_tree().bind.assert_called_once_with(
                    "<<TreeviewSelect>>", func=mock_selection_callback_wrapper()
                )

            # Test create the button
            column_num = 0
            with check:
                mock_create_button.assert_called_once_with(
                    mock_buttonbox,
                    guiwidgets_2.CANCEL_TEXT,
                    column_num,
                    cut.destroy,
                    default="active",
                )

    def test_selection_callback(self, monkeypatch, create_entry_fields):
        monkeypatch.setattr("guiwidgets_2.ttk.Treeview", mock_tree := MagicMock())
        with self.selecttaggui(monkeypatch) as cut:
            monkeypatch.setattr(cut, "destroy", mock_destroy := MagicMock())
            func = cut.selection_callback(mock_tree())

            func()
            with check:
                cut.select_tag_callback.assert_called_once_with(
                    mock_tree().selection()[0]
                )
            with check:
                mock_destroy.assert_called_once_with()

    def test_destroy(self, monkeypatch, create_entry_fields):
        with self.selecttaggui(monkeypatch) as cut:
            monkeypatch.setattr(cut, "outer_frame", mock_outer_frame := MagicMock())

            cut.destroy()
            mock_outer_frame.destroy.assert_called_once_with()

    @contextmanager
    def selecttaggui(self, monkeypatch):
        yield guiwidgets_2.SelectTagGUI(
            patch_config(monkeypatch).current.tk_root,
            select_tag_callback=MagicMock(),
            tags_to_show=self.TAGS_TO_SHOW,
        )


# noinspection PyMissingOrEmptyDocstring,DuplicatedCode
@pytest.mark.skip
class TestPreferencesGUI:
    api_key = "test api key"
    do_not_ask = False
    save_callback = "test save callback"

    def test_post_init(self, monkeypatch, create_entry_fields, general_framing):
        monkeypatch.setattr(guiwidgets_2.tk, "Toplevel", mock_toplevel := MagicMock())
        monkeypatch.setattr(
            guiwidgets_2, "_set_original_value", mock_set_original_value := MagicMock()
        )
        monkeypatch.setattr("guiwidgets_2.InputZone", mock_inputzone := MagicMock())
        monkeypatch.setattr("guiwidgets_2._focus_set", mock_focus_set := MagicMock())
        monkeypatch.setattr(
            "guiwidgets_2._create_button", mock_create_button := MagicMock()
        )
        monkeypatch.setattr(
            "guiwidgets_2.PreferencesGUI.enable_save_button", MagicMock()
        )

        _, body_frame, mock_buttonbox = general_framing()

        with self.preferencesgui(monkeypatch) as cut:
            # Test create a toplevel window
            with check:
                mock_toplevel.assert_called_once_with(cut.parent)

            # Test initialize an internal dictionary to simplify field data management.
            with check:
                create_entry_fields.assert_called_once_with(
                    (cut.api_key_name, cut.use_tmdb_name),
                    (cut.api_key_text, cut.use_tmdb_text),
                )
            with check:
                mock_set_original_value.assert_called_once_with(
                    cut.entry_fields,
                    {cut.api_key_name: cut.api_key, cut.use_tmdb_name: cut.do_not_ask},
                )

            # Test create outer frames to hold fields and buttons.
            check.equal(general_framing.call_count, 2)
            with check:
                general_framing.assert_has_calls(
                    [
                        call(),
                        call(cut.toplevel, type(cut).__name__.lower(), cut.destroy),
                    ]
                )

            # Test create labels and entry widgets.
            with check:
                mock_inputzone().add_entry_row.assert_called_once_with(
                    cut.entry_fields[cut.api_key_name]
                )
            with check:
                mock_inputzone().add_checkbox_row.assert_called_once_with(
                    cut.entry_fields[cut.use_tmdb_name]
                )
            with check:
                mock_focus_set.assert_called_once_with(
                    cut.entry_fields[cut.api_key_name].widget
                )

            # Test create buttons.
            check.equal(mock_create_button.call_count, 2)
            with check:
                mock_create_button.assert_has_calls(
                    [
                        call(
                            mock_buttonbox,
                            guiwidgets_2.SAVE_TEXT,
                            column=0,
                            command=cut.save,
                            default="disabled",
                        ),
                        call(
                            mock_buttonbox,
                            guiwidgets_2.CANCEL_TEXT,
                            column=1,
                            command=cut.destroy,
                            default="active",
                        ),
                    ]
                )

            # Test field observer registration
            # cut.entry_fields has been mocked so cut.entry_fields[<Any>] will always return
            # the same value.
            api_key_field = cut.entry_fields[cut.api_key_name]
            use_tmdb_field = cut.entry_fields[cut.use_tmdb_name]
            check.equal(api_key_field, use_tmdb_field)
            check.equal(use_tmdb_field.observer.register.call_count, 2)
            with check:
                use_tmdb_field.assert_has_calls(
                    [
                        call.observer.register(cut.enable_save_button()),
                        call.observer.register(cut.enable_save_button()),
                    ]
                )

    @pytest.mark.skip
    def test_enable_save_button(self, monkeypatch, movie_patches):
        monkeypatch.setattr(guiwidgets_2.tk, "Toplevel", MagicMock())
        monkeypatch.setattr("guiwidgets_2._focus_set", MagicMock())
        monkeypatch.setattr("guiwidgets_2.ttk.Button", mock_button := MagicMock())
        monkeypatch.setattr(
            "guiwidgets_2.enable_button", mock_enable_button := MagicMock()
        )
        with self.preferencesgui(monkeypatch) as cut:
            api_key = cut.entry_fields["dummy"]
            use_tmdb = cut.entry_fields["dummy"]
            callback = cut.enable_save_button(mock_button, api_key, use_tmdb)
            callback()
            with check:
                mock_enable_button.assert_called_once_with(mock_button, True)

    def test_save(self, monkeypatch, create_entry_fields, general_framing):
        monkeypatch.setattr(guiwidgets_2.tk, "Toplevel", mock_toplevel := MagicMock())
        monkeypatch.setattr("guiwidgets_2._focus_set", MagicMock())

        with self.preferencesgui(monkeypatch) as cut:
            monkeypatch.setattr(cut, "save_callback", mock_save_callback := MagicMock())
            monkeypatch.setattr(cut, "destroy", mock_destroy := MagicMock())

            cut.save()
            with check:
                mock_save_callback.assert_called_with(
                    cut.entry_fields[cut.api_key_name].textvariable.get(),
                    cut.entry_fields[cut.use_tmdb_name].textvariable.get() == "1",
                )
            with check:
                mock_destroy.assert_called_once_with()

    def test_destroy(self, monkeypatch, create_entry_fields, general_framing):
        monkeypatch.setattr(guiwidgets_2.tk, "Toplevel", mock_toplevel := MagicMock())
        monkeypatch.setattr("guiwidgets_2._focus_set", MagicMock())

        with self.preferencesgui(monkeypatch) as cut:
            cut.destroy()
            mock_toplevel().destroy.assert_called_once_with()

    @contextmanager
    def preferencesgui(self, monkeypatch):
        # noinspection PyTypeChecker
        yield guiwidgets_2.PreferencesGUI(
            patch_config(monkeypatch).current.tk_root,
            api_key=self.api_key,
            do_not_ask=self.do_not_ask,
            save_callback=self.test_callback(),
        )

    def test_callback(self):
        def func(*args):
            return args

        return func


# noinspection PyMissingOrEmptyDocstring
class TestCreateBodyAndButtonFrames:
    escape_key_callback = "test escape key callback"

    def test_framing(self, monkeypatch):
        monkeypatch.setattr("guiwidgets_2.ttk.Frame", mock_frame := MagicMock())
        mock_destroy = MagicMock(name="mock destroy")

        with self.create_frames(monkeypatch, mock_destroy) as fut:
            outer_frame, body_frame, buttonbox = fut
            check.equal(mock_frame.call_count, 3)
            check.equal(mock_frame().grid.call_count, 3)
            check.equal(mock_frame().columnconfigure.call_count, 1)
            with check:
                mock_frame.assert_has_calls(
                    [
                        call(
                            guiwidgets_2.config.current.tk_root,
                            name=self.escape_key_callback,
                        ),
                        call(outer_frame, padding=(10, 25, 10, 0)),
                        call(outer_frame, padding=(5, 5, 10, 10)),
                    ],
                    any_order=True,
                )
            check.equal(
                guiwidgets_2.config.current.escape_key_dict,
                {self.escape_key_callback: mock_destroy},
            )
            with check:
                outer_frame.assert_has_calls(
                    [
                        call.grid(column=0, row=0, sticky="nsew"),
                        call.columnconfigure(0, weight=1),
                    ]
                )
            with check:
                body_frame.grid.assert_has_calls([call(column=0, row=0, sticky="n")])
            with check:
                buttonbox.grid.assert_has_calls([call(column=0, row=1, sticky="e")])

    @contextmanager
    def create_frames(self, monkeypatch, mock_destroy):
        yield guiwidgets_2.create_body_and_button_frames(
            patch_config(monkeypatch).current.tk_root,
            self.escape_key_callback,
            mock_destroy,
        )


class TestGUIAskYesNo:
    def test_askyesno_called(self, monkeypatch):
        monkeypatch.setattr(
            guiwidgets_2.messagebox,
            "askyesno",
            mock_askyesno := MagicMock(name="mock_gui_askyesno"),
        )
        parent = MagicMock()
        message = "dummy message"

        guiwidgets_2.gui_askyesno(parent, message)
        mock_askyesno.assert_called_once_with(
            parent, message, detail="", icon="question", default="no"
        )


class TestEnableButton:
    def test_enable_button(self, monkeypatch):
        monkeypatch.setattr("guiwidgets_2.tk", MagicMock())
        monkeypatch.setattr("guiwidgets_2.ttk", mock_ttk := MagicMock())

        guiwidgets_2.enable_button(mock_ttk.Button, True)
        guiwidgets_2.enable_button(mock_ttk.Button, False)
        with check:
            mock_ttk.Button.assert_has_calls(
                [
                    call.state(["!disabled"]),
                    call.configure(default="active"),
                    call.state(["disabled"]),
                    call.configure(default="disabled"),
                ]
            )


# noinspection PyMissingOrEmptyDocstring
def patch_config(monkeypatch):
    dummy_current_config = guiwidgets_2.config.CurrentConfig()
    dummy_current_config.tk_root = MagicMock(name=TEST_TK_ROOT)
    dummy_current_config.escape_key_dict = {}
    dummy_persistent_config = guiwidgets_2.config.PersistentConfig(
        TEST_TITLE, TEST_VERSION
    )

    monkeypatch.setattr("guiwidgets_2.config", mock_config := MagicMock(name="config"))
    mock_config.current = dummy_current_config
    mock_config.persistent = dummy_persistent_config

    return mock_config


# noinspection PyMissingOrEmptyDocstring
@pytest.fixture
def movie_patches(
    create_entry_fields,
    original_values,
    movie_framing,
    set_initial_tag_selection,
    create_buttons,
):
    pass


# noinspection PyMissingOrEmptyDocstring
@pytest.fixture
def original_values(monkeypatch):
    monkeypatch.setattr(
        "guiwidgets_2.MovieGUI.original_values", mock_original_values := MagicMock()
    )
    return mock_original_values


# noinspection PyMissingOrEmptyDocstring
@pytest.fixture
def set_initial_tag_selection(monkeypatch):
    monkeypatch.setattr(
        "guiwidgets_2.MovieGUI.set_initial_tag_selection",
        mock_set_initial_tag_selection := MagicMock(),
    )
    return mock_set_initial_tag_selection


# noinspection PyMissingOrEmptyDocstring
@pytest.fixture
def create_buttons(monkeypatch):
    monkeypatch.setattr(
        "guiwidgets_2.MovieGUI._create_buttons", mock_create_buttons := MagicMock()
    )
    return mock_create_buttons


# noinspection PyMissingOrEmptyDocstring
@pytest.fixture
def create_entry_fields(monkeypatch):
    monkeypatch.setattr(
        "guiwidgets_2._create_entry_fields", mock_create_entry_fields := MagicMock()
    )
    return mock_create_entry_fields


# noinspection PyMissingOrEmptyDocstring
@pytest.fixture
def ttk_frame(monkeypatch):
    monkeypatch.setattr("guiwidgets_2.ttk.Frame", mock_ttk_frame := MagicMock())
    return mock_ttk_frame


# noinspection PyMissingOrEmptyDocstring
@pytest.fixture
def movie_framing(monkeypatch):
    monkeypatch.setattr("guiwidgets_2.MovieGUI.framing", mock_framing := MagicMock())
    mock_framing.return_value = [MagicMock(), MagicMock(), MagicMock(), MagicMock()]
    return mock_framing


# noinspection PyMissingOrEmptyDocstring
@pytest.fixture
def general_framing(monkeypatch):
    monkeypatch.setattr(
        "guiwidgets_2.create_input_form_framing", mock_framing := MagicMock()
    )
    mock_framing.return_value = [MagicMock(), MagicMock(), MagicMock()]
    return mock_framing


# noinspection PyMissingOrEmptyDocstring
@pytest.fixture
def ttk_stringvar(monkeypatch):
    monkeypatch.setattr("guiwidgets_2.tk.StringVar", MagicMock())
