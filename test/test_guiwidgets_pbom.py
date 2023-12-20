""" Test guiwidgets.

This module contains new tests written after Brian Okken's course and book on pytest in Fall 2022 together with
mocks from Python's unittest.mok module.

Strategy:
Detect any changes to calls to other functions and methods and changes to the arguments to those calls.
Changes in the API of called functions and methods are not part of this test suite.
"""
#  Copyright (c) 2023-2023. Stephen Rigden.
#  Last modified 12/16/23, 7:04 AM by stephen.
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


# noinspection PyMissingOrEmptyDocstring
class TestMovieGUI:
    def test_post_init(
        self,
        monkeypatch,
        create_entry_fields,
        original_values,
        movie_framing,
        set_initial_tag_selection,
        create_buttons,
    ):
        movie_framing.return_value = [
            MagicMock(),
            mock_body_frame := MagicMock(),
            mock_buttonbox := MagicMock(),
            mock_internet_frame := MagicMock(),
        ]

        monkeypatch.setattr("guiwidgets_2._InputZone", mock_inputzone := MagicMock())
        monkeypatch.setattr("guiwidgets_2._focus_set", mock_focus_set := MagicMock())
        monkeypatch.setattr("guiwidgets_2.ttk.Treeview", mock_treeview := MagicMock())
        monkeypatch.setattr("guiwidgets_2.itertools.count", MagicMock())
        monkeypatch.setattr(
            "guiwidgets_2._create_button", mock_create_button := MagicMock()
        )
        monkeypatch.setattr(
            "guiwidgets_2.MovieGUI.tmdb_consumer", mock_tmdb_consumer := MagicMock()
        )

        with self.moviegui(monkeypatch) as cut:
            # Test initialize an internal dictionary.
            with check:
                create_entry_fields.assert_called_once_with(
                    guiwidgets_2.MOVIE_FIELD_NAMES, guiwidgets_2.MOVIE_FIELD_TEXTS
                )
            check.equal(cut.title, guiwidgets_2.MOVIE_FIELD_NAMES[0])
            with check:
                original_values.assert_called_once_with()
            cut.entry_fields.fromkeys(guiwidgets_2.MOVIE_FIELD_NAMES)

            # Test create frames.
            with check:
                movie_framing.assert_called_once_with(cut.parent)
            with check:
                mock_inputzone.assert_called_once_with(mock_body_frame)

            # Test create labels and entry widgets.
            check.equal(mock_inputzone().add_entry_row.call_count, 4)
            arg = cut.entry_fields["dummy"]
            with check:
                mock_inputzone().add_entry_row.assert_has_calls(
                    [call(arg), call(arg), call(arg), call(arg)]
                )
            with check:
                mock_focus_set.assert_called_once_with(
                    cut.entry_fields[cut.title].widget
                )

            # Test create label and text widget.
            with check:
                mock_inputzone().add_text_row.assert_called_once_with(
                    cut.entry_fields["dummy"]
                )

            # Test create a label and treeview for movie tags.
            with check:
                mock_inputzone().add_treeview_row.assert_called_once_with(
                    "Tags",
                    items=["test tag 1", "test tag 2", "test tag 3"],
                    callers_callback=cut.tags_treeview_callback,
                )
            with check:
                set_initial_tag_selection.assert_called_once_with()

            # Test create a treeview for movies retrieved from tmdb.
            with check:
                mock_treeview.assert_called_once_with(
                    mock_internet_frame,
                    columns=("title", "year", "director"),
                    show=["headings"],
                    height=20,
                    selectmode="browse",
                )
            check.equal(cut.tmdb_treeview.column.call_count, 3)
            with check:
                cut.tmdb_treeview.column.assert_has_calls(
                    [
                        call("title", width=300, stretch=True),
                        call("year", width=40, stretch=True),
                        call("director", width=200, stretch=True),
                    ]
                )
            check.equal(cut.tmdb_treeview.heading.call_count, 3)
            with check:
                cut.tmdb_treeview.heading.assert_has_calls(
                    [
                        call("title", text="Title", anchor="w"),
                        call("year", text="Year", anchor="w"),
                        call("director", text="Director", anchor="w"),
                    ]
                )
            with check:
                cut.tmdb_treeview.grid.assert_called_once_with(
                    column=0, row=0, sticky="nsew"
                )
            with check:
                cut.tmdb_treeview.bind.assert_called_once_with(
                    "<<TreeviewSelect>>", func=cut.tmdb_treeview_callback
                )

            # Test populate buttonbox with buttons.
            column_num = guiwidgets_2.itertools.count()
            with check:
                create_buttons.assert_called_once_with(mock_buttonbox, column_num)
            with check:
                mock_create_button.assert_called_once_with(
                    mock_buttonbox,
                    guiwidgets_2.CANCEL_TEXT,
                    column=next(column_num),
                    command=cut.destroy,
                    default="active",
                )

            # Test start the tmdb_work_queue polling
            with check:
                mock_tmdb_consumer.assert_called_once_with()

    def test_original_values(self, monkeypatch, create_entry_fields):
        with pytest.raises(NotImplementedError):
            with self.moviegui(monkeypatch):
                pass

    def test_initial_tag_selection(
        self,
        monkeypatch,
        create_entry_fields,
        original_values,
    ):
        with pytest.raises(NotImplementedError):
            with self.moviegui(monkeypatch):
                pass

    def test_create_buttons(
        self,
        monkeypatch,
        create_entry_fields,
        original_values,
        movie_framing,
        set_initial_tag_selection,
    ):
        with pytest.raises(NotImplementedError):
            with self.moviegui(monkeypatch):
                pass

    def test_call_title_notifees(self, monkeypatch, movie_patches):
        with self.moviegui(monkeypatch) as cut:
            func = cut.call_title_notifees(mock_commit_neuron := MagicMock())
            monkeypatch.setattr(
                "guiwidgets_2.MovieGUI.tmdb_search", mock_tmdb_search := MagicMock()
            )
            cut.entry_fields[
                cut.title
            ].textvariable.get.return_value = mock_text = "mock text"
            cut.entry_fields[
                cut.title
            ].original_value = mock_original_text = "mock original text"
            func(mock_commit_neuron)

            with check:
                mock_tmdb_search.assert_called_once_with(mock_text)
            with check:
                mock_commit_neuron.assert_called_once_with(
                    cut.title, mock_text != mock_original_text
                )

    def test_tmdb_search(self, monkeypatch, movie_patches):
        with self.moviegui(monkeypatch) as cut:
            substring = "mock substring"
            cut.tmdb_search(substring)
            with check:
                assert cut.parent.after.mock_calls[1] == call(
                    cut.last_text_queue_timer,
                    cut.tmdb_search_callback,
                    substring,
                    cut.tmdb_work_queue,
                )

            # First call only
            with check:
                cut.parent.after_cancel.assert_not_called()

            # Second and subsequent calls
            cut.tmdb_search(substring)
            with check:
                cut.parent.after_cancel.assert_called_once_with(cut.last_text_event_id)

    def test_tmdb_consumer(self, monkeypatch, movie_patches):
        items = ["child 1", "child 2"]
        title = "test title"
        year = 2042
        director = "test director"
        minutes = 142
        notes = "test notes"

        with self.moviegui(monkeypatch) as cut:
            movie = [
                config.MovieTypedDict(
                    title=title,
                    year=year,
                    director=[director],
                    minutes=minutes,
                    notes=notes,
                ),
            ]
            cut.tmdb_work_queue.put(movie)
            monkeypatch.setattr(cut, "tmdb_treeview", mock_tmdb_treeview := MagicMock())
            mock_tmdb_treeview.get_children.return_value = items
            # This tmdb_movies item should be cleared by the function under test.
            cut.tmdb_movies["dummy"] = "garbage"

            # test with item in queue ('else' branch executed)
            cut.tmdb_consumer()
            with check:
                cut.tmdb_treeview.get_children.assert_called_once_with()
            with check:
                cut.tmdb_treeview.delete.assert_called_once_with(*items)
            with check:
                cut.tmdb_treeview.insert.assert_called_once_with(
                    "", "end", values=(title, year, director)
                )
            check.equal(
                list(cut.tmdb_movies.values()),
                [
                    dict(
                        title=title,
                        year=year,
                        director=director,
                        minutes=minutes,
                        notes=notes,
                    ),
                ],
            )

            # test with no items in queue ('else' branch not executed)
            cut.tmdb_movies["dummy"] = "garbage"
            cut.tmdb_consumer()
            check.is_true("dummy" in cut.tmdb_movies)

            # test finally branch
            with check:
                cut.parent.after.assert_has_calls(
                    [
                        call(cut.work_queue_poll, cut.tmdb_consumer),
                        call(cut.work_queue_poll, cut.tmdb_consumer),
                        call(cut.work_queue_poll, cut.tmdb_consumer),
                    ]
                )

    def test_tags_treeview_callback(self, monkeypatch, movie_patches):
        reselection = ("a", "b", "c")
        with self.moviegui(monkeypatch) as cut:
            cut.tags_treeview_callback(reselection)
        check.equal(cut.selected_tags, reselection)

    def test_tmdb_treeview_callback(self, monkeypatch, movie_patches):
        dummy_item_id = "dummy_item_id"
        dummy_entry_fields = {
            guiwidgets_2.MOVIE_FIELD_NAMES[-1]: (mock_notes := MagicMock()),
            guiwidgets_2.MOVIE_FIELD_NAMES[0]: (mock_title := MagicMock()),
        }

        with self.moviegui(monkeypatch) as cut:
            monkeypatch.setattr(cut, "tmdb_treeview", mock_tmdb_treeview := MagicMock())
            mock_tmdb_treeview.selection.return_value = [dummy_item_id]
            monkeypatch.setattr(cut, "notes_widget", mock_notes_widget := MagicMock())
            cut.entry_fields = dummy_entry_fields
            cut.tmdb_movies = {dummy_item_id: dummy_entry_fields}

            cut.tmdb_treeview_callback()
            with check:
                mock_notes_widget.delete.assert_called_once_with("1.0", "end")
            with check:
                mock_notes_widget.insert.assert_called_once_with(
                    "1.0", mock_notes, ("font_tag",)
                )
            textvariable_set = cut.entry_fields[
                guiwidgets_2.MOVIE_FIELD_NAMES[0]
            ].textvariable.set
            with check:
                textvariable_set.assert_called_once_with(mock_title)

    def test_destroy(self, monkeypatch, movie_patches):
        with self.moviegui(monkeypatch) as cut:
            cut.destroy()
            with check:
                cut.parent.after_cancel.assert_called_once_with(cut.recall_id)
            with check:
                cut.outer_frame.destroy.assert_called_once_with()

    def test_framing(
        self,
        monkeypatch,
        create_entry_fields,
        original_values,
        set_initial_tag_selection,
        create_buttons,
        ttk_frame,
    ):
        with self.moviegui(monkeypatch) as cut:
            with check:
                cut.outer_frame.assert_has_calls(
                    [
                        call.grid(column=0, row=0, sticky="nsew"),
                        call.columnconfigure(0, weight=1),
                        call.columnconfigure(1, weight=1000),
                        call.rowconfigure(0),
                        call.grid(column=0, row=0, sticky="nw"),
                        call.columnconfigure(0, weight=1, minsize=25),
                        call.grid(column=1, row=0, sticky="nw"),
                        call.columnconfigure(0, weight=1, minsize=25),
                        call.grid(column=0, row=0, sticky="new"),
                        call.grid(column=0, row=1, sticky="ne"),
                    ]
                )

            check.equal(
                guiwidgets_2.config.current.escape_key_dict[type(cut).__name__.lower()],
                cut.destroy,
            )

    @contextmanager
    def moviegui(self, monkeypatch):
        # noinspection PyTypeChecker
        yield guiwidgets_2.MovieGUI(
            patch_config(monkeypatch).current.tk_root,
            tmdb_search_callback=MagicMock(),
            all_tags=[
                "test tag 1",
                "test tag 2",
                "test tag 3",
            ],
        )


# noinspection PyMissingOrEmptyDocstring
class TestAddMovieGUI:
    def test_original_values(self, monkeypatch, movie_patches, ttk_stringvar):
        with self.addmoviegui(monkeypatch) as cut:
            entry = "tags"
            cut.entry_fields = dict(
                [
                    (
                        entry,
                        guiwidgets_2._EntryField(
                            "dummy label", original_value="garbage"
                        ),
                    ),
                ]
            )

            cut.original_values()
            check.equal(cut.entry_fields[entry].original_value, "")

    def test_set_initial_tag_selection(self, monkeypatch, movie_patches):
        with self.addmoviegui(monkeypatch) as cut:
            monkeypatch.setattr(
                cut.tags_treeview, "selection_set", mock_selection_set := MagicMock()
            )

            cut.set_initial_tag_selection()
            with check:
                mock_selection_set.assert_not_called()

    def test_create_buttons(self, monkeypatch, movie_patches, ttk_frame):
        with self.addmoviegui(monkeypatch) as cut:
            monkeypatch.setattr(
                "guiwidgets_2._create_button", mock_create_button := MagicMock()
            )
            monkeypatch.setattr(
                "guiwidgets_2._create_buttons_andneuron",
                mock_create_buttons_andneuron := MagicMock(),
            )
            monkeypatch.setattr(
                "guiwidgets_2._enable_button", mock_enable_button := MagicMock()
            )
            column_num = guiwidgets_2.itertools.count()

            cut._create_buttons(ttk_frame, column_num)
            with check:
                mock_create_button.assert_called_once_with(
                    ttk_frame,
                    guiwidgets_2.COMMIT_TEXT,
                    column=0,
                    command=cut.commit,
                    default="normal",
                )
            with check:
                mock_enable_button.assert_has_calls(
                    [call(mock_create_button()), call()(False)]
                )
            title = guiwidgets_2.MOVIE_FIELD_NAMES[0]
            year = guiwidgets_2.MOVIE_FIELD_NAMES[1]
            with check:
                mock_create_buttons_andneuron.assert_has_calls(
                    [
                        call(mock_enable_button()),
                        call().register_event(year),
                        call().register_event(title),
                    ]
                )

    # noinspection DuplicatedCode
    def test_commit(self, monkeypatch, movie_patches):
        monkeypatch.setattr(
            "guiwidgets_2.messagebox.showinfo", mock_showinfo := MagicMock()
        )
        with self.addmoviegui(monkeypatch) as cut:
            monkeypatch.setattr(cut, "notes_widget", MagicMock())
            monkeypatch.setattr(cut, "tags_treeview", MagicMock())
            monkeypatch.setattr(cut, "tmdb_treeview", MagicMock())

            # Test control path when there are no exceptions.
            cut.commit()
            with check:
                cut.add_movie_callback.assert_called_once_with(
                    cut.return_fields, cut.selected_tags
                )
            with check:
                mock_showinfo.assert_not_called()
            with check:
                cut.notes_widget.assert_has_calls(
                    [call.get("1.0", "end"), call.delete("1.0", "end")]
                )
            with check:
                cut.tags_treeview.clear_selection.assert_called_once_with()
            with check:
                cut.tmdb_treeview.assert_has_calls(
                    [
                        call.get_children(),
                        call.get_children().__iter__(),
                        call.get_children().__len__(),
                        call.delete(),
                    ]
                )

            # Test exception paths.
            monkeypatch.setattr(
                guiwidgets_2.exception.MovieYearConstraintFailure, "args", "garbage"
            )
            monkeypatch.setattr(
                cut, "add_movie_callback", mock_add_movie_callback := MagicMock()
            )
            mock_add_movie_callback.side_effect = (
                guiwidgets_2.exception.MovieDBConstraintFailure
            )
            cut.commit()

            mock_add_movie_callback.side_effect = (
                guiwidgets_2.exception.MovieYearConstraintFailure
            )
            cut.commit()

            with check:
                mock_showinfo.assert_has_calls(
                    [
                        call(
                            parent=cut.parent,
                            message=guiwidgets_2.exception.MovieDBConstraintFailure.msg,
                            detail=guiwidgets_2.exception.MovieDBConstraintFailure.detail,
                        ),
                        call(
                            parent=cut.parent,
                            message=guiwidgets_2.exception.MovieYearConstraintFailure.args[
                                0
                            ],
                        ),
                    ]
                )

    @contextmanager
    def addmoviegui(self, monkeypatch):
        # noinspection PyTypeChecker
        yield guiwidgets_2.AddMovieGUI(
            patch_config(monkeypatch).current.tk_root,
            tmdb_search_callback=MagicMock(),
            all_tags=[
                "test tag 1",
                "test tag 2",
                "test tag 3",
            ],
            add_movie_callback=MagicMock(),
        )


# noinspection PyMissingOrEmptyDocstring
class TestEditMovieGUI:
    def test_original_values(self, monkeypatch, movie_patches, ttk_stringvar):
        with self.editmoviegui(monkeypatch) as cut:
            entry = "tags"
            cut.entry_fields = dict(
                [
                    (
                        entry,
                        guiwidgets_2._EntryField(
                            "dummy label", original_value="garbage"
                        ),
                    ),
                ]
            )

            cut.original_values()
            check.equal(cut.entry_fields[entry].original_value, ("test tag",))

    def test_set_initial_tag_selection(self, monkeypatch, movie_patches):
        with self.editmoviegui(monkeypatch) as cut:
            monkeypatch.setattr(
                cut.tags_treeview, "selection_set", mock_selection_set := MagicMock()
            )

            cut.set_initial_tag_selection()
            with check:
                mock_selection_set.assert_called_once_with(cut.old_movie["tags"])
            check.equal(cut.selected_tags, cut.old_movie["tags"])

    def test_create_buttons(self, monkeypatch, movie_patches, ttk_frame):
        with self.editmoviegui(monkeypatch) as cut:
            monkeypatch.setattr(
                "guiwidgets_2._create_button", mock_create_button := MagicMock()
            )
            column_num = guiwidgets_2.itertools.count()

            cut._create_buttons(ttk_frame, column_num)
            with check:
                mock_create_button.assert_has_calls(
                    [
                        call(
                            ttk_frame,
                            guiwidgets_2.COMMIT_TEXT,
                            column=0,
                            command=cut.commit,
                            default="active",
                        ),
                        call(
                            ttk_frame,
                            guiwidgets_2.DELETE_TEXT,
                            column=1,
                            command=cut.delete,
                            default="active",
                        ),
                    ]
                )

    # noinspection DuplicatedCode
    def test_commit(self, monkeypatch, movie_patches):
        monkeypatch.setattr(
            "guiwidgets_2.EditMovieGUI.destroy", mock_destroy := MagicMock()
        )
        monkeypatch.setattr(
            "guiwidgets_2.messagebox.showinfo", mock_showinfo := MagicMock()
        )

        with self.editmoviegui(monkeypatch) as cut:
            # Test control path when there are no exceptions.
            cut.commit()
            with check:
                cut.edit_movie_callback.assert_called_once_with(
                    cut.return_fields, cut.selected_tags
                )
            with check:
                mock_showinfo.assert_not_called()
            with check:
                mock_destroy.assert_called_once_with()

            # Test exception paths.
            monkeypatch.setattr(
                guiwidgets_2.exception.MovieYearConstraintFailure, "args", "garbage"
            )
            monkeypatch.setattr(
                cut, "edit_movie_callback", mock_edit_movie_callback := MagicMock()
            )
            mock_edit_movie_callback.side_effect = (
                guiwidgets_2.exception.MovieDBConstraintFailure
            )
            cut.commit()

            mock_edit_movie_callback.side_effect = (
                guiwidgets_2.exception.MovieYearConstraintFailure
            )
            cut.commit()

            with check:
                mock_showinfo.assert_has_calls(
                    [
                        call(
                            parent=cut.parent,
                            message=guiwidgets_2.exception.MovieDBConstraintFailure.msg,
                            detail=guiwidgets_2.exception.MovieDBConstraintFailure.detail,
                        ),
                        call(
                            parent=cut.parent,
                            message=guiwidgets_2.exception.MovieYearConstraintFailure.args[
                                0
                            ],
                        ),
                    ]
                )

    def test_delete(self, monkeypatch, movie_patches):
        monkeypatch.setattr(
            "guiwidgets_2.gui_askyesno", mock_gui_askyesno := MagicMock()
        )
        with self.editmoviegui(monkeypatch) as cut:
            monkeypatch.setattr(cut, "destroy", MagicMock())

            # User responds 'No' - Do not delete movie.
            mock_gui_askyesno.return_value = False
            cut.delete()
            with check:
                mock_gui_askyesno.assert_called_once_with(
                    message=guiwidgets_2.MOVIE_DELETE_MESSAGE,
                    icon=tkinter.messagebox.QUESTION,
                    parent=cut.parent,
                )

            # User responds 'Yes' - Go ahead and delete movie.
            mock_gui_askyesno.return_value = True
            cut.delete()
            with check:
                cut.delete_movie_callback.assert_called_once_with(
                    guiwidgets_2.config.FindMovieTypedDict()
                )
            with check:
                cut.destroy.assert_called_once_with()

    # noinspection PyArgumentList
    @contextmanager
    def editmoviegui(self, monkeypatch):
        old_movie = guiwidgets_2.config.MovieUpdateDef()
        old_movie["tags"] = ("test tag",)
        # noinspection PyTypeChecker
        yield guiwidgets_2.EditMovieGUI(
            patch_config(monkeypatch).current.tk_root,
            MagicMock(),  # tmdb_io_handler
            all_tags=[
                "test tag 1",
                "test tag 2",
                "test tag 3",
            ],
            old_movie=old_movie,
            edit_movie_callback=MagicMock(),
            delete_movie_callback=MagicMock(),
        )


# noinspection PyMissingOrEmptyDocstring,DuplicatedCode
class TestAddTagGUI:
    def test_post_init(
        self, monkeypatch, create_entry_fields, general_framing, create_buttons
    ):
        monkeypatch.setattr("guiwidgets_2._InputZone", mock_inputzone := MagicMock())
        monkeypatch.setattr("guiwidgets_2._focus_set", mock_focus_set := MagicMock())
        monkeypatch.setattr(
            "guiwidgets_2._create_button", mock_create_button := MagicMock()
        )
        monkeypatch.setattr(
            "guiwidgets_2._create_button_orneuron",
            mock_create_button_orneuron := MagicMock(),
        )
        monkeypatch.setattr(
            "guiwidgets_2._link_field_to_neuron",
            mock_link_field_to_neuron := MagicMock(),
        )
        monkeypatch.setattr(
            "guiwidgets_2._create_the_fields_observer",
            mock_create_the_fields_observer := MagicMock(),
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
                    cut.entry_fields[guiwidgets_2.TAG_FIELD_NAMES[0]]
                )
            with check:
                mock_focus_set.assert_called_once_with(
                    cut.entry_fields[guiwidgets_2.TAG_FIELD_NAMES[0]].widget
                )

            # Test populate buttonbox with commit and cancel buttons
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

            # Test link commit button to tag field
            with check:
                mock_link_field_to_neuron.assert_called_once_with(
                    cut.entry_fields,
                    guiwidgets_2.TAG_FIELD_NAMES[0],
                    mock_create_button_orneuron(),
                    mock_create_the_fields_observer(),
                )
            check.equal(
                cut.entry_fields[guiwidgets_2.TAG_FIELD_NAMES[0]].observer,
                mock_create_button_orneuron(),
            )

    def test_commit(self, monkeypatch, create_entry_fields):
        mock_destroy_calls = []
        dummy_tag = 'dummy tag'

        with self.addtaggui(monkeypatch) as cut:
            monkeypatch.setattr(
                cut,
                "destroy",
                lambda: mock_destroy_calls.append(True),
                )
            cut.entry_fields[guiwidgets_2.TAG_FIELD_NAMES[0]].textvariable.get.return_value = dummy_tag

            cut.commit()
            with check:
                cut.add_tag_callback.assert_called_once_with(dummy_tag)
            with check:
                check.equal(mock_destroy_calls, [True])

            # test null tag
            cut.entry_fields[guiwidgets_2.TAG_FIELD_NAMES[0]].textvariable.get.return_value = ''

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
class TestEditTagGUI:
    dummy_tag = "dummy tag"

    # noinspection DuplicatedCode
    def test_post_init(
        self, monkeypatch, create_entry_fields, general_framing, create_buttons
    ):
        monkeypatch.setattr("guiwidgets_2._InputZone", mock_inputzone := MagicMock())
        monkeypatch.setattr("guiwidgets_2._focus_set", mock_focus_set := MagicMock())
        monkeypatch.setattr(
            "guiwidgets_2._create_button", mock_create_button := MagicMock()
        )
        monkeypatch.setattr(
            "guiwidgets_2._create_button_orneuron",
            mock_create_button_orneuron := MagicMock(),
        )
        monkeypatch.setattr(
            "guiwidgets_2._link_field_to_neuron",
            mock_link_field_to_neuron := MagicMock(),
        )
        monkeypatch.setattr(
            "guiwidgets_2._create_the_fields_observer",
            mock_create_the_fields_observer := MagicMock(),
        )
        _, body_frame, mock_buttonbox = general_framing()

        with self.edittaggui(monkeypatch) as cut:
            # Test initialize an internal dictionary.
            with check:
                create_entry_fields.assert_called_once_with(
                    guiwidgets_2.TAG_FIELD_NAMES, guiwidgets_2.TAG_FIELD_TEXTS
                )
            check.equal(
                cut.entry_fields[guiwidgets_2.TAG_FIELD_NAMES[0]].original_value,
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
                    cut.entry_fields[guiwidgets_2.TAG_FIELD_NAMES[0]]
                )
            with check:
                mock_focus_set.assert_called_once_with(
                    cut.entry_fields[guiwidgets_2.TAG_FIELD_NAMES[0]].widget
                )

            # Test populate buttonbox with commit and cancel buttons
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

            # Test link commit button to tag field
            with check:
                mock_link_field_to_neuron.assert_called_once_with(
                    cut.entry_fields,
                    guiwidgets_2.TAG_FIELD_NAMES[0],
                    mock_create_button_orneuron(),
                    mock_create_the_fields_observer(),
                )
            check.equal(
                cut.entry_fields[guiwidgets_2.TAG_FIELD_NAMES[0]].observer,
                mock_create_button_orneuron(),
            )

    # noinspection DuplicatedCode
    def test_commit(self, monkeypatch, create_entry_fields):
        with self.edittaggui(monkeypatch) as cut:
            monkeypatch.setattr(cut, "destroy", mock_destroy := MagicMock())

            cut.commit()
            with check:
                cut.edit_tag_callback.assert_called_once_with(
                    cut.entry_fields[guiwidgets_2.TAG_FIELD_NAMES[0]].textvariable.get()
                )
            with check:
                mock_destroy.assert_called_once_with()

    # noinspection DuplicatedCode
    def test_delete(self, monkeypatch, create_entry_fields):
        monkeypatch.setattr(
            "guiwidgets_2.gui_askyesno", mock_gui_askyesno := MagicMock()
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
class TestSearchTagGUI:
    def test_post_init(self, monkeypatch, create_entry_fields, general_framing):
        monkeypatch.setattr("guiwidgets_2._InputZone", mock_inputzone := MagicMock())
        monkeypatch.setattr("guiwidgets_2._focus_set", mock_focus_set := MagicMock())
        monkeypatch.setattr(
            "guiwidgets_2._create_button", mock_create_button := MagicMock()
        )
        monkeypatch.setattr(
            "guiwidgets_2._create_button_orneuron",
            mock_create_button_orneuron := MagicMock(),
        )
        monkeypatch.setattr(
            "guiwidgets_2._link_field_to_neuron",
            mock_link_field_to_neuron := MagicMock(),
        )
        monkeypatch.setattr(
            "guiwidgets_2._create_the_fields_observer",
            mock_create_the_fields_observer := MagicMock(),
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
                    cut.entry_fields[guiwidgets_2.TAG_FIELD_NAMES[0]]
                )
            with check:
                mock_focus_set.assert_called_once_with(
                    cut.entry_fields[guiwidgets_2.TAG_FIELD_NAMES[0]].widget
                )

            # Test populate buttonbox with commit and cancel buttons
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

            # Test link commit button to tag field
            with check:
                mock_link_field_to_neuron.assert_called_once_with(
                    cut.entry_fields,
                    guiwidgets_2.TAG_FIELD_NAMES[0],
                    mock_create_button_orneuron(),
                    mock_create_the_fields_observer(),
                )
            check.equal(
                cut.entry_fields[guiwidgets_2.TAG_FIELD_NAMES[0]].observer,
                mock_create_button_orneuron(),
            )

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
                    cut.entry_fields[guiwidgets_2.TAG_FIELD_NAMES[0]].textvariable.get()
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
            "guiwidgets_2._create_button", mock_create_button := MagicMock()
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
                    "#0", text=guiwidgets_2.TAG_FIELD_TEXTS[0]
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
                            tags=guiwidgets_2.TAG_FIELD_NAMES[0],
                        ),
                        call(
                            "",
                            "end",
                            iid=self.TAGS_TO_SHOW[1],
                            text=self.TAGS_TO_SHOW[1],
                            values=[],
                            tags=guiwidgets_2.TAG_FIELD_NAMES[0],
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
class TestPreferencesGUI:
    api_key = "test api key"
    do_not_ask = False
    save_callback = "test save callback"

    def test_post_init(self, monkeypatch, create_entry_fields, general_framing):
        monkeypatch.setattr(guiwidgets_2.tk, "Toplevel", mock_toplevel := MagicMock())
        monkeypatch.setattr(
            guiwidgets_2, "_set_original_value", mock_set_original_value := MagicMock()
        )
        monkeypatch.setattr("guiwidgets_2._InputZone", mock_inputzone := MagicMock())
        monkeypatch.setattr("guiwidgets_2._focus_set", mock_focus_set := MagicMock())
        monkeypatch.setattr(
            "guiwidgets_2._create_button", mock_create_button := MagicMock()
        )
        monkeypatch.setattr(
            "guiwidgets_2._create_button_orneuron",
            mock_create_button_orneuron := MagicMock(),
        )
        monkeypatch.setattr(
            "guiwidgets_2._enable_button", mock_enable_button := MagicMock()
        )
        monkeypatch.setattr(
            "guiwidgets_2._create_the_fields_observer",
            mock_create_the_fields_observer := MagicMock(),
        )
        monkeypatch.setattr(
            "guiwidgets_2._link_field_to_neuron",
            mock_link_field_to_neuron := MagicMock(),
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

            # Test create outer frames t hold fields and buttons.
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

            # Test link save button to save neuron
            with check:
                mock_enable_button.assert_called_once_with(mock_create_button())
            with check:
                mock_create_button_orneuron.assert_called_once_with(
                    mock_enable_button()
                )

            # Test link api key field and 'tmdb don't ask' field to save neuron
            mock_neuron = mock_create_button_orneuron()
            with check:
                mock_create_the_fields_observer.assert_has_calls(
                    [
                        call(cut.entry_fields, cut.api_key_name, mock_neuron),
                        call(cut.entry_fields, cut.use_tmdb_name, mock_neuron),
                    ]
                )
            with check:
                mock_link_field_to_neuron.assert_has_calls(
                    [
                        call(
                            cut.entry_fields,
                            cut.api_key_name,
                            mock_neuron,
                            cut.entry_fields[cut.api_key_name].observer,
                        ),
                        call(
                            cut.entry_fields,
                            cut.use_tmdb_name,
                            mock_neuron,
                            cut.entry_fields[cut.use_tmdb_name].observer,
                        ),
                    ]
                )

    def test_save(self, monkeypatch, create_entry_fields, general_framing):
        monkeypatch.setattr(guiwidgets_2.tk, "Toplevel", MagicMock())
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
            print(f"{args=}")
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
        yield guiwidgets_2._create_body_and_button_frames(
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


class TestCreateEntryFields:
    def test_create_entry_fields(self, monkeypatch):
        dummy_name = "dummy name"
        internal_names = (dummy_name,)
        dummy_text = "dummy text"
        label_texts = (dummy_text,)
        monkeypatch.setattr("guiwidgets_2.tk", MagicMock())
        monkeypatch.setattr("guiwidgets_2.ttk", MagicMock())
        dummy_entry_field = guiwidgets_2._EntryField(dummy_text)

        result = guiwidgets_2._create_entry_fields(internal_names, label_texts)
        check.equal(result, {dummy_name: dummy_entry_field})


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
        "guiwidgets_2._create_input_form_framing", mock_framing := MagicMock()
    )
    mock_framing.return_value = [MagicMock(), MagicMock(), MagicMock()]
    return mock_framing


# noinspection PyMissingOrEmptyDocstring
@pytest.fixture
def ttk_stringvar(monkeypatch):
    monkeypatch.setattr("guiwidgets_2.tk.StringVar", MagicMock())
