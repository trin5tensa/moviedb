"""test_guiwidgets_pbo

This module contains new tests written after Brian Okken's course and book on pytest in Fall 2022.

Test strategies are noted for each class but, in general, they test the interface with other code and not the
internal implementation of widgets.
"""
#  Copyright (c) 2023-2023. Stephen Rigden.
#  Last modified 10/2/23, 8:21 AM by stephen.
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
from unittest.mock import MagicMock

import pytest

import config
import guiwidgets_2
from test.dummytk import (DummyTk, TkStringVar, TkToplevel, TkText, TtkButton, TtkCheckbutton, TtkEntry,
                          TtkFrame, TtkLabel, TtkScrollbar, TtkTreeview, )


# noinspection PyTypeChecker,PyUnresolvedReferences
@pytest.mark.skip('Rewrite in pbom')
@pytest.mark.usefixtures('patch_tk')
class TestAddMovieGUI:
    """ Test AddMovieGUI and MovieGUI for:
            Initiation of an Internet search for matching movies whenever the user stops typing,
            Retrieval of search results from MovieGUI's queue.Queue,
            Display of the movies,
            Database commitment of the input data,
            Closure of the input form.

    All external calls and user GUI interactions will be mocked or simulated.
    """
    tags = ('tag 41', 'tag 42')
    test_movies = [config.MovieTypedDict(title='test title', year=4242,
                                         director=['Test Director', 'Test Director II'], minutes=142,
                                         notes='Another fine "test_add_movie"', ), ]

    def test_tmdb_search(self, check):
        """Confirm that a change to the title field makes a delayed call to tmdb_search_callback."""
        guiwidgets_2.config.current = MagicMock()
        cut = guiwidgets_2.AddMovieGUI(DummyTk(), lambda: None, self.tags, add_movie_callback=lambda: None)
        search_string = 'tmdb search substring'
        cut.entry_fields[cut.title].textvariable.set_for_test(search_string)
        cut.parent.after_calls = {}
        cut.parent.after_cancel_calls = []

        search_callback = cut.call_title_notifees(cut.commit_neuron)
        search_callback()

        # The search call was placed on the mock event loop from which it must be retrieved for interrogation…
        call = [v for v in cut.parent.after_calls.values()][0]
        check.equal(len(call), 3, 'Wrong number of arguments in call to self.parent.after.')
        delay, tmdb_search_callback, args = call
        check.equal(len(args), 2, 'Wrong number of arguments in call to self.parent.after.')
        text, queue_ = args

        check.between(delay, 99, 1001, 'Timing rate is outside the expected range of values. (last_text_queue_timer)')
        check.is_(tmdb_search_callback, cut.tmdb_search_callback, "Expected callback function missing.")
        check.equal(text, search_string, 'Search string should be the contents of the title textvariable.')
        check.equal(queue_, cut.tmdb_work_queue, 'The work queue should be self.tmdb_work_queue.')

        # Call the search method directly a second time to remove the event from the event queue.
        cut.tmdb_search('garbage')
        event_id = int(cut.last_text_event_id) - 1
        check.equal(cut.parent.after_cancel_calls, [[(event_id, )]])

    def test_retrieve_movie_from_tmdb_results_queue(self, check):
        """ Confirm that:
        Movies found in MovieGUI's queue are moved to the treeview and to tmdb_movies.
        The polling call to tmdb_consumer is replaced on the mock tkinter event loop.
        """
        guiwidgets_2.config.current = MagicMock()
        cut = guiwidgets_2.AddMovieGUI(DummyTk(), lambda: None, self.tags, add_movie_callback=lambda: None)
        cut.tmdb_work_queue.put(self.test_movies)
        cut.tmdb_treeview.set_mock_children(['garbage1', 'garbage2'])

        cut.tmdb_consumer()

        check.is_false(cut.tmdb_treeview.items, 'Old items not cleared from treeview.')
        args, kwargs = cut.tmdb_treeview.insert_calls[0]
        check.equal(args, ('', 'end'), 'Unexpected treeview arguments for id and position.')

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

    def test_commit_a_movie(self, check):
        """Confirm that the input form is populated by a user selection from the list of movies."""
        guiwidgets_2.config.current = MagicMock()
        callback = MagicMock()
        cut = guiwidgets_2.AddMovieGUI(DummyTk(), lambda: None, self.tags, add_movie_callback=callback)
        for k, v in cut.entry_fields.items():
            if k == guiwidgets_2.MOVIE_FIELD_NAMES[-1]:
                cut.notes_widget.delete('1.0', 'end')
                # noinspection PyTypedDict
                cut.notes_widget.insert('1.0', self.test_movies[0][k], '')
            else:
                # noinspection PyTypedDict
                v.textvariable.set_for_test(self.test_movies[0][k])

        cut.commit()

        callback.assert_called_once_with(cut.return_fields, ())

    def test_invalid_key_exception_alerts_user(self, monkeypatch):
        """Confirm an invalid title and year combination presents an alert."""
        guiwidgets_2.config.current = MagicMock()
        parent = DummyTk()
        exc = guiwidgets_2.exception.MovieDBConstraintFailure
        callback = MagicMock(side_effect=exc, name='mock commit callback')
        messagebox = MagicMock(name='mock messagebox')
        monkeypatch.setattr('guiwidgets_2.messagebox', messagebox)

        cut = guiwidgets_2.AddMovieGUI(parent, lambda: None, self.tags, add_movie_callback=callback)
        cut.commit()

        messagebox.showinfo.assert_called_once_with(parent=parent, message=exc.msg, detail=exc.detail)

    def test_invalid_movie_year_exception_alerts_user(self, monkeypatch):
        """Confirm an invalid year presents an alert."""
        guiwidgets_2.config.current = MagicMock()
        parent = DummyTk()
        exc = guiwidgets_2.exception.MovieYearConstraintFailure
        exc.args = ('test arg 1', 'test arg 2')
        callback = MagicMock(side_effect=exc, name='mock commit callback')
        messagebox = MagicMock(name='mock messagebox')
        monkeypatch.setattr('guiwidgets_2.messagebox', messagebox)

        cut = guiwidgets_2.AddMovieGUI(parent, lambda: None, self.tags, add_movie_callback=callback)
        cut.commit()

        messagebox.showinfo.assert_called_once_with(parent=parent, message=exc.args[0])

    def test_tags_treeview_callback(self):
        guiwidgets_2.config.current = MagicMock()
        cut = guiwidgets_2.AddMovieGUI(DummyTk(), lambda: None, self.tags, add_movie_callback=lambda: None)
        selection = ('tag1', 'tag2')
        cut.tags_treeview_callback(selection)
        assert cut.selected_tags == selection

    def test_tmdb_treeview_callback(self, check):
        guiwidgets_2.config.current = MagicMock()
        cut = guiwidgets_2.AddMovieGUI(DummyTk(), lambda: None, self.tags, add_movie_callback=lambda: None)
        item_id = 'I001'
        cut.tmdb_movies = {item_id: self.test_movies[0]}
        cut.notes_widget.insert_calls = []
        cut.notes_widget.delete_calls = []
        cut.tmdb_treeview.selection_set(item_id, )
        entry_keys = list(cut.entry_fields.keys())[:-1]
        for k in entry_keys:
            cut.entry_fields[k].textvariable.set_calls = []

        cut.tmdb_treeview_callback()

        check.equal(cut.notes_widget.insert_calls, [('1.0', self.test_movies[0]['notes'], ('font_tag', ))])
        check.equal(cut.notes_widget.delete_calls, [('1.0', 'end')])
        for k in entry_keys:
            # noinspection PyTypedDict
            check.equal(cut.entry_fields[k].textvariable.set_calls[0][0],
                        self.test_movies[0][k])

    def test_tmdb_treeview_deselection(self, check):
        """The user has deselected the chosen movie so test that the input form fields have *not* been altered."""
        guiwidgets_2.config.current = MagicMock()
        cut = guiwidgets_2.AddMovieGUI(DummyTk(), lambda: None, self.tags, add_movie_callback=lambda: None)
        # noinspection PyArgumentList
        cut.tmdb_treeview.selection_set()
        entry_keys = list(cut.entry_fields.keys())[:-1]
        for k in entry_keys:
            cut.entry_fields[k].textvariable.set_calls = []

        cut.tmdb_treeview_callback()

        for k in entry_keys:
            check.equal(cut.entry_fields[k].textvariable.set_calls, [])

    def test_destroy(self, check):
        guiwidgets_2.config.current = MagicMock()
        cut = guiwidgets_2.AddMovieGUI(DummyTk(), lambda: None, self.tags, add_movie_callback=lambda: None)
        cut.outer_frame.destroy_calls = []
        cut.parent.after_cancel_calls = []
        event_id = [[tuple(cut.parent.after_calls.keys())]]

        cut.destroy()

        check.equal(cut.parent.after_cancel_calls, event_id,
                    'An expected call to cease polling of queue.Queue was not made.')
        if len(cut.outer_frame.destroy_calls) != 1:
            check.equal(len(cut.outer_frame.destroy_calls), 1,
                        'An expected call to the destroy method was not made.')
        else:
            check.is_true(cut.outer_frame.destroy_calls[0])


# noinspection PyTypeChecker,PyUnresolvedReferences
@pytest.mark.skip('Rewrite in pbom')
@pytest.mark.usefixtures('patch_tk')
class TestEditMovieGUI:
    """ Test EditMovieGUI for:
        Calls to commit and delete.

    All external calls and user GUI interactions will be mocked or simulated.
    """
    tags = ['tag 41', 'tag 42']
    all_tags = tags + ['tag 43']
    old_movie = config.MovieUpdateDef(title='test old title',
                                      year=1942,
                                      director=['Test Old Director I', 'Test Old Director II'],
                                      minutes=92,
                                      notes='Another fine old "test_edit_movie"',
                                      tags=tags)

    def test_commit_a_movie(self, check):
        """Commit method should call the edit movie callback."""
        guiwidgets_2.config.current = MagicMock()
        edit_movie = MagicMock()
        delete_movie = MagicMock()
        cut = guiwidgets_2.EditMovieGUI(DummyTk(), lambda: None, self.all_tags,
                                        old_movie=self.old_movie, edit_movie_callback=edit_movie,
                                        delete_movie_callback=delete_movie)

        cut.commit()
        edit_movie.assert_called_once_with(cut.return_fields, self.tags)

    def test_invalid_key_exception_alerts_user(self, monkeypatch):
        """Confirm an invalid title and year combination presents an alert."""
        guiwidgets_2.config.current = MagicMock()
        parent = DummyTk()
        exc = guiwidgets_2.exception.MovieDBConstraintFailure
        callback = MagicMock(side_effect=exc, name='mock commit callback')
        messagebox = MagicMock(name='mock messagebox')
        monkeypatch.setattr('guiwidgets_2.messagebox', messagebox)

        cut = guiwidgets_2.EditMovieGUI(parent, lambda: None, self.tags,
                                        old_movie=self.old_movie,
                                        edit_movie_callback=callback)
        cut.commit()

        messagebox.showinfo.assert_called_once_with(parent=parent, message=exc.msg, detail=exc.detail)

    def test_invalid_movie_year_exception_alerts_user(self, monkeypatch):
        """Confirm an invalid year presents an alert."""
        guiwidgets_2.config.current = MagicMock()
        parent = DummyTk()

        exc = guiwidgets_2.exception.MovieYearConstraintFailure
        exc.args = ('test arg 1', 'test arg 2')
        callback = MagicMock(side_effect=exc, name='mock commit callback')
        messagebox = MagicMock(name='mock messagebox')
        monkeypatch.setattr('guiwidgets_2.messagebox', messagebox)

        cut = guiwidgets_2.EditMovieGUI(parent, lambda: None, self.tags,
                                        old_movie=self.old_movie,
                                        edit_movie_callback=callback)
        cut.commit()

        messagebox.showinfo.assert_called_once_with(parent=parent, message=exc.args[0])

    def test_delete_calls_confirmation_dialog(self, check, monkeypatch):
        guiwidgets_2.config.current = MagicMock()
        delete_movie_callback_arg = None
        destroy_called = False

        # noinspection PyMissingOrEmptyDocstring
        def mock_delete_movie_callback(movie):
            nonlocal delete_movie_callback_arg
            delete_movie_callback_arg = movie

        # noinspection PyMissingOrEmptyDocstring
        def mock_destroy():
            nonlocal destroy_called
            destroy_called = True

        askyesno = MagicMock(name='mock messagebox', return_value=True)
        monkeypatch.setattr('guiwidgets_2.gui_askyesno', askyesno)
        parent = DummyTk()
        callback = MagicMock(name='mock commit callback')
        cut = guiwidgets_2.EditMovieGUI(parent, lambda: None, self.tags,
                                        old_movie=self.old_movie,
                                        edit_movie_callback=callback)
        monkeypatch.setattr(cut, 'delete_movie_callback', mock_delete_movie_callback)
        monkeypatch.setattr(cut, 'destroy', mock_destroy)
        movie_to_delete = config.FindMovieTypedDict(title='test old title', year=[1942])

        cut.delete()

        check.equal(movie_to_delete, delete_movie_callback_arg)
        check.is_true(destroy_called)


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
