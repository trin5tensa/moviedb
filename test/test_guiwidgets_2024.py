""" Test patterns.py """

#  Copyright (c) 2024-2024. Stephen Rigden.
#  Last modified 3/2/24, 10:51 AM by stephen.
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

#  Copyright (c) 2024-2024. Stephen Rigden.
#  Last modified 3/1/24, 3:13 PM by stephen.
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
from globalconstants import *
from guiwidgets_2 import TITLE_TEXT, YEAR_TEXT, DIRECTOR_TEXT


# noinspection PyMissingOrEmptyDocstring
class TestMovieGUI:
    def test_post_init(
        self, mock_tk, framing, user_input_frame, fill_buttonbox, tmdb_results_frame
    ):
        # noinspection PyTypeChecker
        guiwidgets_2.MovieGUI(mock_tk, tmdb_search_callback=lambda: None, all_tags=None)
        with check:
            framing.assert_called_once_with(mock_tk)
        outer_frame, body_frame, buttonbox, tmdb_frame = framing()
        with check:
            user_input_frame.assert_called_once_with(body_frame)
        with check:
            fill_buttonbox.assert_called_once_with(buttonbox)
        with check:
            tmdb_results_frame.assert_called_once_with(tmdb_frame)

    def test_framing(
        self, mock_tk, ttk, user_input_frame, fill_buttonbox, tmdb_results_frame
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
        framing,
        fill_buttonbox,
        tmdb_results_frame,
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
        _, body_frame, _, _ = framing()
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
        framing,
        fill_buttonbox,
        input_zone,
        patterns_entry,
        patterns_text,
        patterns_treeview,
        focus_set,
        tmdb_consumer,
        tmdb_search,
    ):
        # noinspection PyTypeChecker
        cut = guiwidgets_2.MovieGUI(
            mock_tk, tmdb_search_callback=lambda: None, all_tags=None
        )
        _, _, _, tmdb_frame = framing()

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
            tmdb_consumer.assert_called_once_with()
        with check:
            # noinspection PyUnresolvedReferences
            cut.entry_fields[
                guiwidgets_2.TITLE
            ].observer.register.assert_called_once_with(tmdb_search)

    def test_fill_buttonbox(
        self,
        mock_tk,
        framing,
        user_input_frame,
        tmdb_results_frame,
        create_buttons,
        create_button,
        itertools,
    ):
        # noinspection PyTypeChecker
        cut = guiwidgets_2.MovieGUI(
            mock_tk, tmdb_search_callback=lambda: None, all_tags=None
        )
        _, _, buttonbox, _ = framing()
        with check:
            itertools.count.assert_called_once_with()
        with check:
            create_buttons.assert_called_once_with(buttonbox, itertools.count())
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

    def test_set_initial_tag_selection(
        self, mock_tk, framing, user_input_frame, fill_buttonbox, tmdb_results_frame
    ):
        # noinspection PyTypeChecker
        cut = guiwidgets_2.MovieGUI(
            mock_tk, tmdb_search_callback=lambda: None, all_tags=None
        )
        with check.raises(NotImplementedError):
            cut.set_initial_tag_selection()

    def test_create_buttons(
        self, mock_tk, framing, user_input_frame, fill_buttonbox, tmdb_results_frame
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
        framing,
        fill_buttonbox,
        tmdb_results_frame,
        input_zone,
        patterns_entry,
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
        self, mock_tk, framing, user_input_frame, fill_buttonbox, tmdb_results_frame
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

        # Test 'finally 'clause
        with check:
            # noinspection PyUnresolvedReferences
            cut.parent.after.assert_called_once_with(
                cut.work_queue_poll,
                cut.tmdb_consumer,
            )

    def test_tmdb_consumer_with_items_in_queue(
        self, mock_tk, framing, user_input_frame, fill_buttonbox, tmdb_results_frame
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
        self, mock_tk, framing, user_input_frame, fill_buttonbox, tmdb_results_frame
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
        self, mock_tk, framing, user_input_frame, fill_buttonbox, tmdb_results_frame
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
        self, mock_tk, framing, user_input_frame, fill_buttonbox, tmdb_results_frame
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
def tk_parent_type(monkeypatch):
    monkeypatch.setattr(guiwidgets_2, "TkParentType", mock := MagicMock)
    return mock


# noinspection PyMissingOrEmptyDocstring
@pytest.fixture
def framing(monkeypatch):
    monkeypatch.setattr(guiwidgets_2.MovieGUI, "framing", mock := MagicMock())
    mock.return_value = (MagicMock(), MagicMock(), MagicMock(), MagicMock())
    return mock


# noinspection PyMissingOrEmptyDocstring
@pytest.fixture
def user_input_frame(monkeypatch):
    monkeypatch.setattr(guiwidgets_2.MovieGUI, "user_input_frame", mock := MagicMock())
    return mock


# noinspection PyMissingOrEmptyDocstring
@pytest.fixture
def fill_buttonbox(monkeypatch):
    monkeypatch.setattr(guiwidgets_2.MovieGUI, "fill_buttonbox", mock := MagicMock())
    return mock


# noinspection PyMissingOrEmptyDocstring
@pytest.fixture
def tmdb_results_frame(monkeypatch):
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
def patterns_entry(monkeypatch):
    monkeypatch.setattr(guiwidgets_2.patterns, "Entry", mock := MagicMock())
    return mock


# noinspection PyMissingOrEmptyDocstring
@pytest.fixture
def patterns_text(monkeypatch):
    monkeypatch.setattr(guiwidgets_2.patterns, "Text", mock := MagicMock())
    return mock


# noinspection PyMissingOrEmptyDocstring
@pytest.fixture
def patterns_treeview(monkeypatch):
    monkeypatch.setattr(guiwidgets_2.patterns, "Treeview", mock := MagicMock())
    return mock


# noinspection PyMissingOrEmptyDocstring
@pytest.fixture
def focus_set(monkeypatch):
    monkeypatch.setattr(guiwidgets_2, "focus_set", mock := MagicMock())
    return mock


# noinspection PyMissingOrEmptyDocstring
@pytest.fixture
def create_buttons(monkeypatch):
    monkeypatch.setattr(guiwidgets_2.MovieGUI, "_create_buttons", mock := MagicMock())
    return mock


# noinspection PyMissingOrEmptyDocstring
@pytest.fixture
def create_button(monkeypatch):
    monkeypatch.setattr(guiwidgets_2, "create_button", mock := MagicMock())
    return mock


# noinspection PyMissingOrEmptyDocstring
@pytest.fixture
def itertools(monkeypatch):
    monkeypatch.setattr(guiwidgets_2, "itertools", mock := MagicMock())
    return mock


# noinspection PyMissingOrEmptyDocstring
@pytest.fixture
def tmdb_consumer(monkeypatch):
    monkeypatch.setattr(guiwidgets_2.MovieGUI, "tmdb_consumer", mock := MagicMock())
    return mock


# noinspection PyMissingOrEmptyDocstring
@pytest.fixture
def tmdb_search(monkeypatch):
    monkeypatch.setattr(guiwidgets_2.MovieGUI, "tmdb_search", mock := MagicMock())
    return mock
