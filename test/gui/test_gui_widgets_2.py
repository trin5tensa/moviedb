"""Test Module."""

#  Copyright© 2025. Stephen Rigden.
#  Last modified 3/28/25, 11:38 AM by stephen.
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
from guiwidgets_2 import tk_facade
from globalconstants import *
from guiwidgets_2 import (
    TITLE_TEXT,
    YEAR_TEXT,
    DIRECTORS_TEXT,
    COMMIT_TEXT,
    DELETE_TEXT,
)


# noinspection PyMissingOrEmptyDocstring
class TestMovieGUI:
    title = "dummy old title"
    year = 42
    director_1 = "dummy old director"
    director_2 = "dummy new director"
    directors = {director_1, director_2}
    duration = 142
    notes = "dummy old notes"
    tags = {"test tag 1", "test tag 2"}

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
            # noinspection PyUnresolvedReferences
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
        treeview_items = [{TITLE: title, YEAR: year, DIRECTORS: directors}]
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
            # noinspection PyUnresolvedReferences
            cut.tmdb_treeview.delete.assert_called_with(*treeview_items)
        with check:
            # noinspection PyUnresolvedReferences
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

    # noinspection DuplicatedCode
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
        directors = {"Director 1", "Director 2"}
        item_id = "42"

        # noinspection PyTypeChecker
        cut = guiwidgets_2.MovieGUI(
            mock_tk, tmdb_search_callback=lambda: None, all_tags=None
        )
        cut.tmdb_treeview = MagicMock()
        cut.tmdb_movies[item_id] = {TITLE: title, YEAR: year, DIRECTORS: directors}
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
            if k == guiwidgets_2.DIRECTORS:
                check.equal(
                    cut.entry_fields[k].current_value,
                    ", ".join(cut.tmdb_movies[item_id][k]),
                )

            else:
                check.equal(
                    cut.entry_fields[k].current_value, cut.tmdb_movies[item_id][k]
                )

    # noinspection DuplicatedCode
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
        cut.tmdb_movies[item_id] = {TITLE: title, YEAR: year, DIRECTORS: directors}
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
        # noinspection PyTypeChecker
        guiwidgets_2.config.current.escape_key_dict = {}
        # noinspection PyTypeChecker
        yield guiwidgets_2.MovieGUI(
            mock_tk, tmdb_search_callback=lambda: None, all_tags=None
        )
        guiwidgets_2.config.current = hold_dict


# noinspection PyMissingOrEmptyDocstring
class TestEditMovieGUI:
    title = "dummy old title"
    year = 42
    directors = "dummy old director"
    duration = 142
    notes = "dummy old notes"
    tags = ("test tag 1", "test tag 2")

    def old_movie(self):
        return MovieBag(
            title=self.title,
            year=MovieInteger(self.year),
            directors={self.directors},
            duration=MovieInteger(self.duration),
            notes=self.notes,
            tags=set(self.tags),
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


# noinspection PyMissingOrEmptyDocstring,DuplicatedCode
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


# noinspection PyMissingOrEmptyDocstring,DuplicatedCode
@pytest.fixture
def patterns_entry(monkeypatch):
    monkeypatch.setattr(tk_facade, "Entry", mock := MagicMock())
    return mock


# noinspection PyMissingOrEmptyDocstring
@pytest.fixture
def patterns_text(monkeypatch):
    monkeypatch.setattr(tk_facade, "Text", mock := MagicMock())
    return mock


# noinspection PyMissingOrEmptyDocstring
@pytest.fixture
def patterns_treeview(monkeypatch):
    monkeypatch.setattr(tk_facade, "Treeview", mock := MagicMock())
    return mock


# noinspection PyMissingOrEmptyDocstring
@pytest.fixture
def focus_set(monkeypatch):
    monkeypatch.setattr(guiwidgets_2, "focus_set", mock := MagicMock())
    return mock


# noinspection PyMissingOrEmptyDocstring,DuplicatedCode
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
    monkeypatch.setattr(
        guiwidgets_2.common, "init_button_enablements", mock := MagicMock()
    )
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


# noinspection PyMissingOrEmptyDocstring,DuplicatedCode
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
