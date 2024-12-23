"""Test Module."""

#  Copyright© 2024. Stephen Rigden.
#  Last modified 12/21/24, 1:31 PM by stephen.
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
from contextlib import contextmanager
from unittest.mock import MagicMock, call

import pytest
from pytest_check import check

import guiwidgets_2
from globalconstants import *
from guiwidgets_2 import (
    TITLE_TEXT,
    YEAR_TEXT,
    DIRECTOR_TEXT,
    COMMIT_TEXT,
    DELETE_TEXT,
    MOVIE_DELETE_MESSAGE,
)


# noinspection PyMissingOrEmptyDocstring
class TestMovieGUI:
    def test_post_init(
        self,
        mock_tk,
        ttk,
        moviegui_framing,
        movie_user_input_frame,
        movie_fill_buttonbox,
        movie_tmdb_results_frame,
        tag_init_button_enablements,
    ):
        # noinspection PyTypeChecker
        guiwidgets_2.MovieGUI(mock_tk, tmdb_search_callback=lambda: None, all_tags=None)
        with check:
            moviegui_framing.assert_called_once_with(mock_tk)
        outer_frame, body_frame, buttonbox, tmdb_frame = moviegui_framing()
        with check:
            movie_user_input_frame.assert_called_once_with(body_frame)
        with check:
            movie_fill_buttonbox.assert_called_once_with(buttonbox)
        with check:
            movie_tmdb_results_frame.assert_called_once_with(tmdb_frame)
        with check:
            tag_init_button_enablements.assert_called_once_with({})

    def test_framing(
        self,
        mock_tk,
        ttk,
        movie_user_input_frame,
        movie_fill_buttonbox,
        movie_tmdb_results_frame,
    ):
        with self.moviegui(mock_tk) as cut:
            frame = ttk.Frame()
            check.equal(
                ttk.Frame.call_args_list,
                [
                    call(
                        mock_tk, padding=10, name=type(cut).__name__.lower()
                    ),  # outer frame
                    call(frame, padding=10),  # input_zone
                    call(frame, padding=10),  # internet zone
                    call(frame, padding=10),  # input form
                    call(frame, padding=(5, 5, 10, 10)),  # buttonbox
                    call(),
                ],
            )
            check.equal(
                frame.grid.call_args_list,
                [
                    call(column=0, row=0, sticky="nsew"),  # outer frame
                    call(column=0, row=0, sticky="nw"),  # input_zone
                    call(column=1, row=0, sticky="nw"),  # internet zone
                    call(column=0, row=0, sticky="new"),  # input form
                    call(column=0, row=1, sticky="ne"),  # buttonbox
                ],
            )
            check.equal(
                frame.columnconfigure.call_args_list,
                [
                    call(0, weight=1),  # outer frame
                    call(1, weight=1000),  # outer frame
                    call(0, weight=1, minsize=25),  # input zone
                    call(0, weight=1, minsize=25),  # internet zone
                ],
            )
            check.equal(frame.rowconfigure.call_args_list, [call(0)])  # outer frame
            check.equal(
                guiwidgets_2.config.current.escape_key_dict[type(cut).__name__.lower()],
                cut.destroy,
            )

    def test_user_input_frame(
        self,
        mock_tk,
        ttk,
        moviegui_framing,
        movie_fill_buttonbox,
        movie_tmdb_results_frame,
        input_zone,
        patterns_entry,
        patterns_text,
        patterns_treeview,
        focus_set,
    ):
        # noinspection PyTypeChecker
        cut = guiwidgets_2.MovieGUI(
            mock_tk, tmdb_search_callback=lambda: None, all_tags=None
        )
        _, body_frame, _, _ = moviegui_framing()
        with check:
            input_zone.assert_called_once_with(body_frame)

        # Test four entry rows
        with check:
            patterns_entry.assert_has_calls(
                [
                    call(guiwidgets_2.TITLE_TEXT, body_frame),
                    call(guiwidgets_2.YEAR_TEXT, body_frame),
                    call(guiwidgets_2.DIRECTOR_TEXT, body_frame),
                    call(guiwidgets_2.DURATION_TEXT, body_frame),
                ]
            )
        with check:
            input_zone().add_entry_row.assert_has_calls(
                [
                    call(patterns_entry()),
                    call(patterns_entry()),
                    call(patterns_entry()),
                    call(patterns_entry()),
                ]
            )
        with check:
            focus_set.assert_called_once_with(
                cut.entry_fields[guiwidgets_2.TITLE].widget
            )

        # Test text row
        with check:
            patterns_text.assert_called_once_with(guiwidgets_2.NOTES_TEXT, body_frame)
        with check:
            input_zone().add_text_row.assert_called_once_with(
                cut.entry_fields[guiwidgets_2.NOTES]
            )

        # Test TREEVIEW row
        with check:
            patterns_treeview.assert_called_once_with(
                guiwidgets_2.MOVIE_TAGS_TEXT, body_frame
            )
        with check:
            input_zone().add_treeview_row.assert_called_once_with(
                cut.entry_fields[guiwidgets_2.MOVIE_TAGS], cut.all_tags
            )

    def test_tmdb_results_frame(
        self,
        mock_tk,
        ttk,
        moviegui_framing,
        movie_fill_buttonbox,
        input_zone,
        patterns,
        focus_set,
        movie_tmdb_consumer,
        movie_tmdb_search,
    ):
        # noinspection PyTypeChecker
        cut = guiwidgets_2.MovieGUI(
            mock_tk, tmdb_search_callback=lambda: None, all_tags=None
        )
        _, _, _, tmdb_frame = moviegui_framing()

        check.equal(cut.tmdb_treeview, ttk.Treeview())
        with check:
            ttk.Treeview.assert_has_calls(
                [
                    call(
                        tmdb_frame,
                        columns=(TITLE, YEAR, DIRECTOR),
                        show=["headings"],
                        height=20,
                        selectmode="browse",
                    ),
                    call().column(TITLE, width=300, stretch=True),
                    call().heading(TITLE, text=TITLE_TEXT, anchor="w"),
                    call().column(YEAR, width=40, stretch=True),
                    call().heading(YEAR, text=YEAR_TEXT, anchor="w"),
                    call().column(DIRECTOR, width=200, stretch=True),
                    call().heading(DIRECTOR, text=DIRECTOR_TEXT, anchor="w"),
                    call().grid(column=0, row=0, sticky="nsew"),
                    call().bind("<<TreeviewSelect>>", func=cut.tmdb_treeview_callback),
                ]
            )
        with check:
            movie_tmdb_consumer.assert_called_once_with()
        with check:
            # noinspection PyUnresolvedReferences
            cut.entry_fields[
                guiwidgets_2.TITLE
            ].observer.register.assert_called_once_with(movie_tmdb_search)

    def test_fill_buttonbox(
        self,
        mock_tk,
        ttk,
        moviegui_framing,
        movie_user_input_frame,
        movie_tmdb_results_frame,
        movie_create_buttons,
        create_button,
        itertools,
    ):
        # noinspection PyTypeChecker
        cut = guiwidgets_2.MovieGUI(
            mock_tk, tmdb_search_callback=lambda: None, all_tags=None
        )
        _, _, buttonbox, _ = moviegui_framing()
        with check:
            itertools.count.assert_called_once_with()
        with check:
            movie_create_buttons.assert_called_once_with(buttonbox, itertools.count())
        with check:
            create_button.assert_called_once_with(
                buttonbox,
                guiwidgets_2.CANCEL_TEXT,
                column=next(
                    itertools.count(),
                ),
                command=cut.destroy,
                default="active",
            )

    def test_create_buttons(
        self,
        mock_tk,
        ttk,
        moviegui_framing,
        movie_user_input_frame,
        movie_fill_buttonbox,
        movie_tmdb_results_frame,
    ):
        # noinspection PyTypeChecker
        cut = guiwidgets_2.MovieGUI(
            mock_tk, tmdb_search_callback=lambda: None, all_tags=None
        )
        with check.raises(NotImplementedError):
            # noinspection PyTypeChecker
            cut._create_buttons(object(), object())

    def test_tmdb_search(
        self,
        mock_tk,
        ttk,
        moviegui_framing,
        movie_fill_buttonbox,
        movie_tmdb_results_frame,
        input_zone,
        patterns,
    ):
        dummy_last_event_id = "42"
        dummy_substring = "substring"

        # noinspection PyTypeChecker
        cut = guiwidgets_2.MovieGUI(
            mock_tk, tmdb_search_callback=lambda: None, all_tags=None
        )
        cut.entry_fields[guiwidgets_2.TITLE].current_value = dummy_substring
        cut.last_text_event_id = dummy_last_event_id

        cut.tmdb_search()
        with check:
            # noinspection PyUnresolvedReferences
            cut.parent.after_cancel.assert_called_once_with(dummy_last_event_id)
        with check:
            # noinspection PyUnresolvedReferences
            cut.parent.after.assert_called_once_with(
                cut.last_text_queue_timer,
                cut.tmdb_search_callback,
                dummy_substring,
                cut.tmdb_work_queue,
            )

    def test_tmdb_consumer_with_empty_queue(
        self,
        mock_tk,
        ttk,
        moviegui_framing,
        movie_user_input_frame,
        movie_fill_buttonbox,
        movie_tmdb_results_frame,
    ):
        # noinspection PyTypeChecker
        cut = guiwidgets_2.MovieGUI(
            mock_tk, tmdb_search_callback=lambda: None, all_tags=None
        )
        cut.tmdb_work_queue = MagicMock()
        cut.tmdb_treeview = MagicMock()
        cut.tmdb_work_queue.get_nowait.side_effect = guiwidgets_2.queue.Empty
        cut.tmdb_consumer()

        # Test 'try' and 'except' clauses: An empty queue will skip the `else` clause.
        with check:
            cut.tmdb_treeview.delete.assert_not_called()

        # Test 'finally' clause
        with check:
            # noinspection PyUnresolvedReferences
            cut.parent.after.assert_called_once_with(
                cut.work_queue_poll,
                cut.tmdb_consumer,
            )

    def test_tmdb_consumer_with_items_in_queue(
        self,
        mock_tk,
        ttk,
        moviegui_framing,
        movie_user_input_frame,
        movie_fill_buttonbox,
        movie_tmdb_results_frame,
    ):
        title = "Movie"
        year = "4242"
        directors = ["Director 1", "Director 2"]
        director_cc = "Director 1, Director 2"
        treeview_items = [{TITLE: title, YEAR: year, DIRECTOR: directors}]
        item_id = "42"

        # noinspection PyTypeChecker
        cut = guiwidgets_2.MovieGUI(
            mock_tk, tmdb_search_callback=lambda: None, all_tags=None
        )
        cut.tmdb_work_queue = MagicMock()
        cut.tmdb_treeview = MagicMock()

        # Test 'try' and 'else' clause
        cut.tmdb_work_queue.get_nowait.return_value = treeview_items
        cut.tmdb_treeview.get_children.return_value = treeview_items
        cut.tmdb_treeview.insert.return_value = item_id
        cut.tmdb_consumer()

        with check:
            cut.tmdb_treeview.delete.assert_called_with(*treeview_items)
        with check:
            cut.tmdb_treeview.insert.assert_called_once_with(
                "",
                "end",
                values=(
                    title,
                    year,
                    director_cc,
                ),
            )

        # test 'finally' clause
        with check:
            # noinspection PyUnresolvedReferences
            cut.parent.after.assert_called_once_with(
                cut.work_queue_poll,
                cut.tmdb_consumer,
            )
        check.equal(cut.tmdb_movies[item_id], treeview_items[0])

    def test_tmdb_treeview_callback_with_selection(
        self,
        mock_tk,
        ttk,
        moviegui_framing,
        movie_user_input_frame,
        movie_fill_buttonbox,
        movie_tmdb_results_frame,
    ):
        title = "Movie"
        year = "4242"
        directors = "Director 1, Director 2"
        item_id = "42"

        # noinspection PyTypeChecker
        cut = guiwidgets_2.MovieGUI(
            mock_tk, tmdb_search_callback=lambda: None, all_tags=None
        )
        cut.tmdb_treeview = MagicMock()
        cut.tmdb_movies[item_id] = {TITLE: title, YEAR: year, DIRECTOR: directors}
        movie_keys = cut.tmdb_movies[item_id].keys()
        for k in cut.tmdb_movies[item_id].keys():
            cut.entry_fields[k] = MagicMock()

        # Test current values are updated.
        cut.tmdb_treeview.selection.return_value = [item_id]
        for k in cut.tmdb_movies[item_id].keys():
            cut.entry_fields[k].current_value = ""
        cut.tmdb_treeview_callback()
        check.equal(cut.tmdb_movies[item_id].keys(), movie_keys)
        for k in movie_keys:
            check.equal(cut.entry_fields[k].current_value, cut.tmdb_movies[item_id][k])

    def test_tmdb_treeview_callback_without_selection(
        self,
        mock_tk,
        ttk,
        moviegui_framing,
        movie_user_input_frame,
        movie_fill_buttonbox,
        movie_tmdb_results_frame,
    ):
        title = "Movie"
        year = "4242"
        directors = "Director 1, Director 2"
        item_id = "42"

        # noinspection PyTypeChecker
        cut = guiwidgets_2.MovieGUI(
            mock_tk, tmdb_search_callback=lambda: None, all_tags=None
        )
        cut.tmdb_treeview = MagicMock()
        cut.tmdb_movies[item_id] = {TITLE: title, YEAR: year, DIRECTOR: directors}
        for k in cut.tmdb_movies[item_id].keys():
            cut.entry_fields[k] = MagicMock()
        cut.tmdb_treeview.selection.return_value = []
        for k in cut.tmdb_movies[item_id].keys():
            cut.entry_fields[k].current_value = ""

        cut.tmdb_treeview_callback()
        # Code returns without updating cut.entry_fields[TITLE].current_value
        check.equal(cut.entry_fields[TITLE].current_value, "")

    # noinspection PyUnresolvedReferences
    def test_destroy(
        self,
        mock_tk,
        ttk,
        moviegui_framing,
        movie_user_input_frame,
        movie_fill_buttonbox,
        movie_tmdb_results_frame,
    ):
        # noinspection PyTypeChecker
        cut = guiwidgets_2.MovieGUI(
            mock_tk, tmdb_search_callback=lambda: None, all_tags=None
        )
        cut.destroy()
        with check:
            cut.parent.after_cancel.assert_called_once_with(cut.recall_id)
        with check:
            cut.outer_frame.destroy.assert_called_once_with()

    @contextmanager
    def moviegui(self, mock_tk):
        hold_dict = guiwidgets_2.config.current
        guiwidgets_2.config.current = guiwidgets_2.config.CurrentConfig()
        guiwidgets_2.config.current.escape_key_dict = {}
        # noinspection PyTypeChecker
        yield guiwidgets_2.MovieGUI(
            mock_tk, tmdb_search_callback=lambda: None, all_tags=None
        )
        guiwidgets_2.config.current = hold_dict


def test_add_movie_init_with_movie_bag(monkeypatch):
    # Arrange
    monkeypatch.setattr(guiwidgets_2.ttk, "Entry", MagicMock(name="Entry"))
    monkeypatch.setattr(guiwidgets_2.tk, "StringVar", MagicMock(name="StringVar"))

    monkeypatch.setattr(
        guiwidgets_2.MovieGUI,
        "framing",
        MagicMock(
            name="framing",
            return_value=(
                MagicMock(name="outer_frame"),
                MagicMock(name="body_frame"),
                MagicMock(name="buttonbox"),
                MagicMock(name="tmdb_frame"),
            ),
        ),
    )
    monkeypatch.setattr(guiwidgets_2, "InputZone", MagicMock(name="InputZone"))

    monkeypatch.setattr(
        guiwidgets_2.MovieGUI, "fill_buttonbox", MagicMock(name="fill_buttonbox")
    )
    monkeypatch.setattr(
        guiwidgets_2.MovieGUI,
        "tmdb_results_frame",
        MagicMock(name="tmdb_results_frame"),
    )
    monkeypatch.setattr(
        guiwidgets_2,
        "init_button_enablements",
        MagicMock(name="init_button_enablements"),
    )

    movie_bag = MovieBag(
        title="test title",
        year=MovieInteger(4242),
        directors={"Donald Director", "Delphine Directrice"},
        duration=MovieInteger("42"),
        # Notes intentionally omitted
        synopsis="Boy meets girl.",
        movie_tags={"tag 1", "tag 2"},
    )

    # Act
    cut = guiwidgets_2.AddMovieGUI(
        MagicMock(name="tk/tcl parent"),
        tmdb_search_callback=MagicMock(),
        all_tags=[],
        prepopulate=movie_bag,
    )

    # Assert
    check.equal(cut.entry_fields["title"].original_value, movie_bag["title"])
    check.equal(cut.entry_fields["year"].original_value, str(int(movie_bag["year"])))
    check.equal(
        cut.entry_fields["director"].original_value,
        ", ".join(director for director in movie_bag["directors"]),
    )
    check.equal(
        cut.entry_fields["minutes"].original_value, str(int(movie_bag["duration"]))
    )
    # check.equal(cut.entry_fields["notes"].original_value, movie_bag["notes"])
    # synopsis is not used in GUI2 but is expected for GUI3.
    # This test will fail when GUI3 is implemented.
    check.equal(cut.entry_fields.get("synopsis"), None)

    check.equal(cut.entry_fields["tags"].original_value, movie_bag["movie_tags"])


# noinspection PyMissingOrEmptyDocstring
class TestAddMovieGUI:
    def test_create_buttons(
        self,
        mock_tk,
        ttk,
        moviegui_framing,
        movie_fill_buttonbox,
        movie_tmdb_results_frame,
        input_zone,
        patterns,
        create_button,
        addmovie_enable_commit_button,
    ):
        # noinspection PyTypeChecker
        cut = guiwidgets_2.AddMovieGUI(
            mock_tk, tmdb_search_callback=lambda: None, all_tags=None
        )
        column_num = guiwidgets_2.itertools.count()
        cut._create_buttons(movie_fill_buttonbox, column_num)

        with check:
            create_button.assert_called_once_with(
                movie_fill_buttonbox,
                COMMIT_TEXT,
                column=0,
                command=cut.commit,
                default="normal",
            )
        with check:
            # noinspection PyUnresolvedReferences
            cut.enable_commit_button.assert_has_calls(
                [
                    call(
                        create_button(), cut.entry_fields[TITLE], cut.entry_fields[YEAR]
                    ),
                    call(
                        create_button(), cut.entry_fields[TITLE], cut.entry_fields[YEAR]
                    ),
                ]
            )

    def test_enable_commit_button(
        self,
        mock_tk,
        moviegui_framing,
        movie_fill_buttonbox,
        movie_tmdb_results_frame,
        input_zone,
        patterns,
        create_button,
        enable_button,
        monkeypatch,
    ):
        # noinspection PyTypeChecker
        cut = guiwidgets_2.AddMovieGUI(
            mock_tk, tmdb_search_callback=lambda: None, all_tags=None
        )

        monkeypatch.setitem(cut.entry_fields, TITLE, MagicMock())
        monkeypatch.setitem(cut.entry_fields, YEAR, MagicMock())
        callback = cut.enable_commit_button(
            create_button(), cut.entry_fields[TITLE], cut.entry_fields[YEAR]
        )

        # noinspection PyUnresolvedReferences
        cut.entry_fields[TITLE].has_data.return_value = False
        # noinspection PyUnresolvedReferences
        cut.entry_fields[YEAR].has_data.return_value = False
        callback()

        # noinspection PyUnresolvedReferences
        cut.entry_fields[YEAR].has_data.return_value = True
        callback()

        # noinspection PyUnresolvedReferences
        cut.entry_fields[TITLE].has_data.return_value = True
        # noinspection PyUnresolvedReferences
        cut.entry_fields[YEAR].has_data.return_value = False
        callback()

        # noinspection PyUnresolvedReferences
        cut.entry_fields[YEAR].has_data.return_value = True
        callback()

        with check:
            enable_button.assert_has_calls(
                [
                    call(create_button(), False),
                    call(create_button(), False),
                    call(create_button(), False),
                    call(create_button(), True),
                ]
            )

    def test_commit(
        self,
        mock_tk,
        ttk,
        moviegui_framing,
        movie_fill_buttonbox,
        movie_tmdb_results_frame,
        input_zone,
        patterns,
        messagebox,
    ):
        dummy_current_values = iter("abcdef")
        dummy_tmdb_treeview_children = ("x", "y", "z")
        dummy_msg = "dummy message"
        add_movie_callback = MagicMock()

        # noinspection PyTypeChecker
        cut = guiwidgets_2.AddMovieGUI(
            mock_tk,
            tmdb_search_callback=lambda: None,
            all_tags=None,
            add_movie_callback=add_movie_callback,
        )
        for k in cut.entry_fields.keys():
            cut.entry_fields[k] = MagicMock()
            cut.entry_fields[k].current_value = next(dummy_current_values)
        cut.tmdb_treeview = MagicMock()
        cut.tmdb_treeview.get_children.return_value = dummy_tmdb_treeview_children

        cut.commit()
        with check:
            # noinspection PyUnresolvedReferences
            cut.add_movie_callback.assert_called_once_with(
                {
                    TITLE: "a",
                    YEAR: "b",
                    DIRECTOR: "c",
                    DURATION: "d",
                    NOTES: "e",
                    MOVIE_TAGS: "f",
                }
            )
        for v in cut.entry_fields.values():
            with check:
                # noinspection PyUnresolvedReferences
                v.clear_current_value.assert_called_once_with()
        with check:
            cut.tmdb_treeview.delete.assert_called_once_with(
                *dummy_tmdb_treeview_children
            )

        # Exception tests
        cut.add_movie_callback.side_effect = [
            guiwidgets_2.exception.MovieDBConstraintFailure
        ]
        cut.commit()
        cut.add_movie_callback.side_effect = (
            guiwidgets_2.exception.MovieYearConstraintFailure(
                dummy_msg,
            )
        )
        cut.commit()
        with check:
            messagebox.showinfo.assert_has_calls(
                [
                    call(
                        parent=cut.parent,
                        message="Database constraint failure.",
                        detail="A movie with this title and year is already "
                        "present in the database.",
                    ),
                    call(parent=cut.parent, message=dummy_msg),
                ]
            )


def test_edit_movie_init_with_movie_bag(monkeypatch):
    # Arrange
    monkeypatch.setattr(guiwidgets_2.ttk, "Entry", MagicMock(name="Entry"))
    monkeypatch.setattr(guiwidgets_2.tk, "StringVar", MagicMock(name="StringVar"))
    monkeypatch.setattr(
        guiwidgets_2.MovieGUI,
        "framing",
        MagicMock(
            name="framing",
            return_value=(
                MagicMock(name="outer_frame"),
                MagicMock(name="body_frame"),
                MagicMock(name="buttonbox"),
                MagicMock(name="tmdb_frame"),
            ),
        ),
    )
    monkeypatch.setattr(guiwidgets_2, "InputZone", MagicMock(name="InputZone"))
    monkeypatch.setattr(
        guiwidgets_2.MovieGUI, "fill_buttonbox", MagicMock(name="fill_buttonbox")
    )
    monkeypatch.setattr(
        guiwidgets_2.MovieGUI,
        "tmdb_results_frame",
        MagicMock(name="tmdb_results_frame"),
    )
    monkeypatch.setattr(
        guiwidgets_2,
        "init_button_enablements",
        MagicMock(name="init_button_enablements"),
    )

    movie_bag = MovieBag(
        title="test title",
        year=MovieInteger(4242),
        directors={"Donald Director", "Delphine Directrice"},
        duration=MovieInteger("42"),
        # Notes intentionally omitted
        synopsis="Boy meets girl.",
        movie_tags={"tag 1", "tag 2"},
    )

    # Act
    cut = guiwidgets_2.EditMovieGUI(
        MagicMock(name="tk/tcl parent"),
        tmdb_search_callback=MagicMock(),
        all_tags=[],
        prepopulate=movie_bag,
    )

    # Assert
    check.equal(cut.entry_fields["title"].original_value, movie_bag["title"])
    check.equal(cut.entry_fields["year"].original_value, str(int(movie_bag["year"])))
    check.equal(
        cut.entry_fields["director"].original_value,
        ", ".join(director for director in movie_bag["directors"]),
    )
    check.equal(
        cut.entry_fields["minutes"].original_value, str(int(movie_bag["duration"]))
    )
    # check.equal(cut.entry_fields["notes"].original_value, movie_bag["notes"])
    # synopsis is not used in GUI2 but is expected for GUI3.
    # This test will fail when GUI3 is implemented.
    check.equal(cut.entry_fields.get("synopsis"), None)

    check.equal(cut.entry_fields["tags"].original_value, movie_bag["movie_tags"])


# noinspection PyMissingOrEmptyDocstring
class TestEditMovieGUI:
    title = "dummy old title"
    year = 42
    director = "dummy old director"
    minutes = 142
    notes = "dummy old notes"
    tags = ("test tag 1", "test tag 2")

    def test_post_init(
        self,
        mock_tk,
        ttk,
        moviegui_framing,
        movie_fill_buttonbox,
        movie_tmdb_results_frame,
        input_zone,
        patterns,
    ):
        # noinspection PyTypeChecker
        cut = guiwidgets_2.EditMovieGUI(
            mock_tk,
            tmdb_search_callback=lambda: None,
            all_tags=None,
            old_movie=(self.old_movie()),
        )

        # patterns.Entry is mocked once and used four times.
        # mock.original_value retains the last update of `minutes`.
        check.equal(
            [cut.entry_fields[v].original_value for v in self.old_movie().keys()],
            [
                self.minutes,
                self.minutes,
                self.minutes,
                self.minutes,
                self.notes,
                self.tags,
            ],
        )

    def test_create_buttons(
        self,
        mock_tk,
        ttk,
        moviegui_framing,
        movie_fill_buttonbox,
        movie_tmdb_results_frame,
        input_zone,
        patterns,
        create_button,
        addmovie_enable_commit_button,
        monkeypatch,
    ):
        # noinspection PyTypeChecker
        cut = guiwidgets_2.EditMovieGUI(
            mock_tk,
            tmdb_search_callback=lambda: None,
            all_tags=None,
            old_movie=self.old_movie(),
        )
        column_num = guiwidgets_2.itertools.count()
        for k in cut.entry_fields.keys():
            cut.entry_fields[k] = MagicMock()
        monkeypatch.setattr(cut, "enable_buttons", mock_enable_buttons := MagicMock())

        cut._create_buttons(movie_fill_buttonbox, column_num)

        with check:
            create_button.assert_has_calls(
                [
                    call(
                        movie_fill_buttonbox,
                        COMMIT_TEXT,
                        column=0,
                        command=cut.commit,
                        default="disabled",
                    ),
                    call(
                        movie_fill_buttonbox,
                        DELETE_TEXT,
                        column=1,
                        command=cut.delete,
                        default="active",
                    ),
                ]
            )

        for v in cut.entry_fields.values():
            with check:
                # noinspection PyUnresolvedReferences
                v.observer.register.assert_called_once_with(mock_enable_buttons())
            with check:
                mock_enable_buttons.assert_has_calls(
                    [
                        call(create_button(), create_button()),
                        call(create_button(), create_button()),
                        call(create_button(), create_button()),
                        call(create_button(), create_button()),
                        call(create_button(), create_button()),
                        call(create_button(), create_button()),
                    ]
                )

    # noinspection PyUnresolvedReferences
    def test_enable_buttons(
        self,
        mock_tk,
        moviegui_framing,
        movie_fill_buttonbox,
        movie_tmdb_results_frame,
        input_zone,
        patterns,
        enable_button,
        monkeypatch,
    ):
        monkeypatch.setattr(guiwidgets_2, "create_button", commit_button := MagicMock())
        monkeypatch.setattr(guiwidgets_2, "create_button", delete_button := MagicMock())

        # noinspection PyTypeChecker
        cut = guiwidgets_2.EditMovieGUI(
            mock_tk,
            tmdb_search_callback=lambda: None,
            all_tags=None,
            old_movie=self.old_movie(),
        )
        for k in cut.entry_fields.keys():
            cut.entry_fields[k] = MagicMock()
            cut.entry_fields[k].changed.return_value = False
            cut.entry_fields[k].has_data.return_value = True
        callback = cut.enable_buttons(commit_button, delete_button)

        # No changes and database keys present: cb = False, db = True
        callback()

        # No changes and database keys missing: cb = False, db = True
        cut.entry_fields[TITLE].has_data.return_value = False
        callback()

        # Changes and database keys present: cb = True, db = False
        cut.entry_fields[TITLE].changed.return_value = True
        cut.entry_fields[TITLE].has_data.return_value = True
        callback()

        # Changes and database keys missing: cb = False, db = True
        cut.entry_fields[TITLE].changed.return_value = True
        cut.entry_fields[TITLE].has_data.return_value = False
        callback()

        with check:
            enable_button.assert_has_calls(
                [
                    # No changes and database keys present: cb = False, db = True
                    call(commit_button, False),
                    call(delete_button, True),
                    # No changes and database keys missing: cb = False, db = True
                    call(commit_button, False),
                    call(delete_button, True),
                    # Changes and database keys present: cb = True, db = False
                    call(commit_button, True),
                    call(delete_button, False),
                    # Changes and database keys missing: cb = False, db = True
                    call(commit_button, False),
                    call(delete_button, False),
                ]
            )

    def test_commit(
        self,
        mock_tk,
        ttk,
        moviegui_framing,
        movie_fill_buttonbox,
        movie_tmdb_results_frame,
        input_zone,
        patterns,
        messagebox,
        monkeypatch,
    ):
        dummy_current_values = iter("abcdef")
        dummy_msg = "dummy message"
        edit_movie_callback = MagicMock()
        delete_movie_callback = MagicMock()

        # noinspection PyTypeChecker
        cut = guiwidgets_2.EditMovieGUI(
            mock_tk,
            tmdb_search_callback=lambda: None,
            all_tags=None,
            old_movie=self.old_movie(),
            edit_movie_callback=edit_movie_callback,
            delete_movie_callback=delete_movie_callback,
        )
        monkeypatch.setattr(cut, "destroy", mock_destroy := MagicMock())
        for k in cut.entry_fields.keys():
            cut.entry_fields[k] = MagicMock()
            cut.entry_fields[k].current_value = next(dummy_current_values)

        cut.commit()
        with check:
            # noinspection PyUnresolvedReferences
            cut.edit_movie_callback.assert_called_once_with(
                {
                    TITLE: "a",
                    YEAR: "b",
                    DIRECTOR: "c",
                    DURATION: "d",
                    NOTES: "e",
                    MOVIE_TAGS: "f",
                }
            )
        with check:
            mock_destroy.assert_called_once_with()

        # Exception tests
        cut.edit_movie_callback.side_effect = [
            guiwidgets_2.exception.MovieDBConstraintFailure
        ]
        cut.commit()
        cut.edit_movie_callback.side_effect = (
            guiwidgets_2.exception.MovieYearConstraintFailure(
                dummy_msg,
            )
        )
        cut.commit()
        with check:
            messagebox.showinfo.assert_has_calls(
                [
                    call(
                        parent=cut.parent,
                        message="Database constraint failure.",
                        detail="A movie with this title and year is already "
                        "present in the database.",
                    ),
                    call(parent=cut.parent, message=dummy_msg),
                ]
            )

    def test_delete(
        self,
        mock_tk,
        ttk,
        moviegui_framing,
        movie_fill_buttonbox,
        movie_tmdb_results_frame,
        input_zone,
        patterns,
        monkeypatch,
    ):
        dummy_original_values = iter(("Mock Title", "4242"))
        monkeypatch.setattr(
            guiwidgets_2, "gui_askyesno", mock_gui_askyesno := MagicMock()
        )
        delete_movie_callback = MagicMock()
        # noinspection PyTypeChecker
        cut = guiwidgets_2.EditMovieGUI(
            mock_tk,
            tmdb_search_callback=lambda: None,
            all_tags=None,
            old_movie=self.old_movie(),
            delete_movie_callback=delete_movie_callback,
        )
        monkeypatch.setattr(cut, "destroy", MagicMock())
        movie = guiwidgets_2.config.FindMovieTypedDict()
        for k in [TITLE, YEAR]:
            cut.entry_fields[k] = MagicMock()
            cut.entry_fields[k].original_value = next(dummy_original_values)
            # noinspection PyTypedDict
            movie[k] = cut.entry_fields[k].original_value
        # noinspection PyTypedDict
        movie[YEAR] = [movie[YEAR]]

        # gui_askyesno returns False: destroy NOT called.
        mock_gui_askyesno.return_value = False
        cut.delete()
        with check:
            mock_gui_askyesno.assert_called_once_with(
                message=MOVIE_DELETE_MESSAGE, icon="question", parent=cut.parent
            )
        with check:
            # noinspection PyUnresolvedReferences
            cut.destroy.assert_not_called()

        # gui_askyesno returns True: destroy is called.
        mock_gui_askyesno.return_value = True
        cut.delete()
        with check:
            # noinspection PyUnresolvedReferences
            cut.delete_movie_callback.assert_called_once_with(movie)
        with check:
            # noinspection PyUnresolvedReferences
            cut.destroy.assert_called_once_with()

    def old_movie(self):
        return guiwidgets_2.config.MovieUpdateDef(
            title=self.title,
            year=self.year,
            director=self.director,
            minutes=self.minutes,
            notes=self.notes,
            tags=self.tags,
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
def moviegui_framing(monkeypatch):
    monkeypatch.setattr(guiwidgets_2.MovieGUI, "framing", mock := MagicMock())
    mock.return_value = (MagicMock(), MagicMock(), MagicMock(), MagicMock())
    return mock


# noinspection PyMissingOrEmptyDocstring
@pytest.fixture
def framing(monkeypatch):
    monkeypatch.setattr(guiwidgets_2, "create_input_form_framing", mock := MagicMock())
    mock.return_value = (MagicMock(), MagicMock(), MagicMock())
    return mock


# noinspection PyMissingOrEmptyDocstring
@pytest.fixture
def movie_user_input_frame(monkeypatch):
    monkeypatch.setattr(guiwidgets_2.MovieGUI, "user_input_frame", mock := MagicMock())
    return mock


# noinspection PyMissingOrEmptyDocstring
@pytest.fixture
def movie_fill_buttonbox(monkeypatch):
    monkeypatch.setattr(guiwidgets_2.MovieGUI, "fill_buttonbox", mock := MagicMock())
    return mock


# noinspection PyMissingOrEmptyDocstring
@pytest.fixture
def movie_tmdb_results_frame(monkeypatch):
    monkeypatch.setattr(
        guiwidgets_2.MovieGUI, "tmdb_results_frame", mock := MagicMock()
    )
    return mock


# noinspection PyMissingOrEmptyDocstring
@pytest.fixture
def input_zone(monkeypatch):
    monkeypatch.setattr(guiwidgets_2, "InputZone", mock := MagicMock())
    return mock


# noinspection PyMissingOrEmptyDocstring
@pytest.fixture
def patterns(patterns_entry, patterns_text, patterns_treeview):
    pass


# noinspection PyMissingOrEmptyDocstring
@pytest.fixture
def patterns_entry(monkeypatch):
    monkeypatch.setattr(guiwidgets_2.tk_facade, "Entry", mock := MagicMock())
    return mock


# noinspection PyMissingOrEmptyDocstring
@pytest.fixture
def patterns_text(monkeypatch):
    monkeypatch.setattr(guiwidgets_2.tk_facade, "Text", mock := MagicMock())
    return mock


# noinspection PyMissingOrEmptyDocstring
@pytest.fixture
def patterns_treeview(monkeypatch):
    monkeypatch.setattr(guiwidgets_2.tk_facade, "Treeview", mock := MagicMock())
    return mock


# noinspection PyMissingOrEmptyDocstring
@pytest.fixture
def focus_set(monkeypatch):
    monkeypatch.setattr(guiwidgets_2, "focus_set", mock := MagicMock())
    return mock


# noinspection PyMissingOrEmptyDocstring
@pytest.fixture
def movie_create_buttons(monkeypatch):
    monkeypatch.setattr(guiwidgets_2.MovieGUI, "_create_buttons", mock := MagicMock())
    return mock


# noinspection PyMissingOrEmptyDocstring
@pytest.fixture
def create_button(monkeypatch):
    monkeypatch.setattr(guiwidgets_2, "create_button", mock := MagicMock())
    return mock


# noinspection PyMissingOrEmptyDocstring
@pytest.fixture
def tag_init_button_enablements(monkeypatch):
    monkeypatch.setattr(guiwidgets_2, "init_button_enablements", mock := MagicMock())
    return mock


# noinspection PyMissingOrEmptyDocstring
@pytest.fixture
def itertools(monkeypatch):
    monkeypatch.setattr(guiwidgets_2, "itertools", mock := MagicMock())
    return mock


# noinspection PyMissingOrEmptyDocstring
@pytest.fixture
def movie_tmdb_consumer(monkeypatch):
    monkeypatch.setattr(guiwidgets_2.MovieGUI, "tmdb_consumer", mock := MagicMock())
    return mock


# noinspection PyMissingOrEmptyDocstring
@pytest.fixture
def movie_tmdb_search(monkeypatch):
    monkeypatch.setattr(guiwidgets_2.MovieGUI, "tmdb_search", mock := MagicMock())
    return mock


# noinspection PyMissingOrEmptyDocstring
@pytest.fixture
def addmovie_enable_commit_button(monkeypatch):
    monkeypatch.setattr(
        guiwidgets_2.AddMovieGUI, "enable_commit_button", mock := MagicMock()
    )
    return mock


# noinspection PyMissingOrEmptyDocstring
@pytest.fixture
def enable_button(monkeypatch):
    monkeypatch.setattr(guiwidgets_2, "enable_button", mock := MagicMock())
    return mock


# noinspection PyMissingOrEmptyDocstring
@pytest.fixture
def messagebox(monkeypatch):
    monkeypatch.setattr(guiwidgets_2, "messagebox", mock := MagicMock())
    return mock
