"""test_guiwidgets_pbo

This module contains new tests written after Brian Okken's course and book on pytest in Fall 2022.

Test strategies are noted for each class but, in general, they test the interface with other code and not the
internal implementation of widgets.
"""
#  Copyright (c) 2023-2023. Stephen Rigden.
#  Last modified 1/28/23, 8:30 AM by stephen.
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

import pytest

import config
import guiwidgets_2
from test.dummytk import (DummyTk, TkStringVar, TkToplevel, TkText, TtkButton, TtkCheckbutton, TtkEntry,
                          TtkFrame, TtkLabel, TtkScrollbar, TtkTreeview, )


@pytest.mark.usefixtures('patch_tk')
class TestAddMovieGUI:
    """ Test AddMovieGUI for:
    Partial completion of the movie title initiates an Internet search for matching movies.
    Matching movies are retrieved from AddMovieGUI's queue.
    The input form is populated by a user selection from the list of movies.
    Sending data for database commitment when the commit method is called.
    All external calls and user GUI interactions will be mocked or simulated.
    """
    tags = ('tag 41', 'tag 42')
    test_movies = [config.MovieTypedDict(title='test title', year=4242,
                                         director=['Test Director', 'Test Director II'], minutes=142,
                                         notes='Another fine "test_add_movie"', ), ]

    def test_tmdb_search(self, check):
        """Confirm that a change to the title field makes a delayed call to tmdb_search_callback."""
        cut = guiwidgets_2.AddMovieGUI(DummyTk(), lambda: None, lambda: None, self.tags)
        search_string = 'tmdb search substring'
        milliseconds = 1000
        cut.entry_fields[cut.title].textvariable.set_for_test(search_string)

        typing_callback = cut.call_title_notifees(cut.commit_neuron)
        typing_callback()

        _, call = cut.parent.after_calls.popitem()
        delay, tmdb_search_callback, args = call
        text, queue_ = args

        check.between(delay, 99, milliseconds, 1001)
        check.is_(tmdb_search_callback, cut.tmdb_search_callback)
        check.equal(text, search_string)
        check.equal(queue_, cut.tmdb_work_queue)

    def test_retrieve_movie_from_tmdb_results_queue(self, check):
        """Confirm that movies found in AddMovieGUI's queue are moved to the treeview and to tmdb_movies."""
        cut = guiwidgets_2.AddMovieGUI(DummyTk(), lambda: None, lambda: None, self.tags)
        cut.tmdb_work_queue.put(self.test_movies)
        cut.tmdb_treeview.set_mock_children(['garbage1', 'garbage2'])

        cut.tmdb_consumer()

        check.is_false(cut.tmdb_treeview.items, 'Old items not cleared from treeview.')
        args, kwargs = cut.tmdb_treeview.insert_calls[0]
        check.equal(args, ('', 'end'), 'Unexpected treeview arguments for id and position.' )
        check.equal(kwargs, {'values': ('test title', 4242, 'Test Director, Test Director II')})
        check.equal(cut.tmdb_movies, {'I001': self.test_movies[0]})

    def test_move_user_selection_to_input_form(self, check):
        """Confirm that the input form is populated by a user selection from the list of movies."""

        # todo check widgets are empty
        # todo call cut.tmdb_treeview_callback
        # todo check text widgets correctly updated
        # todo check entry widgets correctly updated
        check.is_true(False)



# noinspection PyMissingOrEmptyDocstring,DuplicatedCode
@pytest.fixture()
def patch_tk(monkeypatch):
    monkeypatch.setattr(guiwidgets_2.tk, 'Tk', DummyTk)
    monkeypatch.setattr(guiwidgets_2.tk, 'Toplevel', TkToplevel)
    monkeypatch.setattr(guiwidgets_2.tk, 'Text', TkText)
    monkeypatch.setattr(guiwidgets_2.tk, 'StringVar', TkStringVar)
    monkeypatch.setattr(guiwidgets_2.ttk, 'Frame', TtkFrame)
    monkeypatch.setattr(guiwidgets_2.ttk, 'Label', TtkLabel)
    monkeypatch.setattr(guiwidgets_2.ttk, 'Entry', TtkEntry)
    monkeypatch.setattr(guiwidgets_2.ttk, 'Checkbutton', TtkCheckbutton)
    monkeypatch.setattr(guiwidgets_2.ttk, 'Button', TtkButton)
    monkeypatch.setattr(guiwidgets_2.ttk, 'Treeview', TtkTreeview)
    monkeypatch.setattr(guiwidgets_2.ttk, 'Scrollbar', TtkScrollbar)
