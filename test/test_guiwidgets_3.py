"""test_guiwidgets_pbo

This module contains new tests written after Brian Okken's course and book on pytest in Fall 2022.

Test strategies are noted for each class but, in general, they test the interface with other code and not the
internal implementation of widgets.
"""
#  Copyright (c) 2023-2023. Stephen Rigden.
#  Last modified 1/31/23, 1:31 PM by stephen.
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
from unittest.mock import Mock

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
        # todo Can typing.Protocol fix the dummytk typing problem?
        cut = guiwidgets_2.AddMovieGUI(DummyTk(), lambda: None, lambda: None, self.tags)
        search_string = 'tmdb search substring'
        cut.entry_fields[cut.title].textvariable.set_for_test(search_string)

        typing_callback = cut.call_title_notifees(cut.commit_neuron)
        typing_callback()

        #The search call was placed on the mock event loop from which it must be retrieved for interrogation…
        _, call = cut.parent.after_calls.popitem()
        check.equal(len(call), 3, 'Wrong number of arguments in call to self.parent.after.')
        delay, tmdb_search_callback, args = call
        check.equal(len(args), 2, 'Wrong number of arguments in call to self.paren t.after.')
        text, queue_ = args

        check.between(delay, 99, 1001, 'Timing rate is outside the expected range of values. (last_text_queue_timer)')
        check.is_(tmdb_search_callback, cut.tmdb_search_callback, "Expected callback function missing.")
        check.equal(text, search_string, 'Search string should be the contents of the title textvariable.')
        check.equal(queue_, cut.tmdb_work_queue, 'The work queue should be self.tmdb_work_queue.')

    def test_retrieve_movie_from_tmdb_results_queue(self, check):
        """ Confirm that:
        Movies found in AddMovieGUI's queue are moved to the treeview and to tmdb_movies.
        A call to tmdb_consumer is replaced on the mock tkinter event loop.
        """
        cut = guiwidgets_2.AddMovieGUI(DummyTk(), lambda: None, lambda: None, self.tags)
        cut.tmdb_work_queue.put(self.test_movies)
        cut.tmdb_treeview.set_mock_children(['garbage1', 'garbage2'])

        cut.tmdb_consumer()

        check.is_false(cut.tmdb_treeview.items, 'Old items not cleared from treeview.')
        args, kwargs = cut.tmdb_treeview.insert_calls[0]
        check.equal(args, ('', 'end'), 'Unexpected treeview arguments for id and position.' )

        check.equal(kwargs, {'values': (self.test_movies[0]['title'], self.test_movies[0]['year'],
                                        self.test_movies[0]['director'],)}, '')
        check.equal(cut.tmdb_movies, {'I001': self.test_movies[0]},
                    'The movie was not added to the self.tmdb_movies dict.')

        item = cut.parent.after_calls.popitem()
        _, args = item
        delay, consumer_func, args = args
        check.between(delay, 9, 51, 'Polling rate is outside the expected range of values. (self.work_queue_poll)')
        check.equal(consumer_func, cut.tmdb_consumer)
        check.equal(args, (), 'cut.tmdb_consumer should have no arguments.')

    def test_move_user_selection_to_input_form(self, check):
        """Confirm that the input form is populated by a user selection from the list of movies."""
        callback = Mock()
        cut = guiwidgets_2.AddMovieGUI(DummyTk(), callback, lambda: None, self.tags)
        for k, v in cut.entry_fields.items():
            if k == guiwidgets_2.MOVIE_FIELD_NAMES[-1]:
                cut.notes_widget.delete('1.0', 'end')
                cut.notes_widget.insert('1.0', self.test_movies[0][k], '')
            else:
                v.textvariable.set_for_test(self.test_movies[0][k])

        cut.commit()

        callback.assert_called_once_with(cut.return_fields, ())


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
