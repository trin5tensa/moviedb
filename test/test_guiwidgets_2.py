"""Test module."""

#  Copyright (c) 2022-2022. Stephen Rigden.
#  Last modified 11/11/22, 8:43 AM by stephen.
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
from typing import Callable, List, Optional, Tuple, Type

import pytest

import exception
import guiwidgets_2
from test.dummytk import (DummyTk, TkStringVar, TkToplevel, TtkButton, TtkCheckbutton, TtkEntry,
                          TtkFrame, TtkLabel, TtkScrollbar, TtkTreeview, )


Exc = Type[Optional[exception.DatabaseSearchFoundNothing]]


# noinspection PyMissingOrEmptyDocstring
@pytest.mark.usefixtures('patch_tk')
class TestAddMovieGUI:
    def test_create_import_form_framing_called(self, monkeypatch):
        self.framing_calls = []
        monkeypatch.setattr(guiwidgets_2, '_create_input_form_framing', self.dummy_create_framing)
        with self.add_movie_gui_context() as add_movie_context:
            assert self.framing_calls == [add_movie_context.parent]
            
    def test_create_input_form_fields(self, monkeypatch):
        add_entry_row_calls = []
        monkeypatch.setattr(guiwidgets_2._LabelFieldWidget, 'add_entry_row',
                            lambda *args: add_entry_row_calls.append(args))
        monkeypatch.setattr(guiwidgets_2, '_create_input_form_framing', self.dummy_create_framing)
        monkeypatch.setattr(guiwidgets_2, '_focus_set', lambda *args: None)
        with self.add_movie_gui_context():
            field_texts = tuple(label[1].label_text for label in add_entry_row_calls)
            assert field_texts == guiwidgets_2.MOVIE_FIELD_TEXTS
            
    def test_focus_set_called_for_title_field(self, monkeypatch):
        calls = []
        monkeypatch.setattr(guiwidgets_2, '_focus_set', lambda *args: calls.append(args))
        with self.add_movie_gui_context() as add_movie_context:
            assert calls == [(add_movie_context.entry_fields['title'].widget,)]

    def test_add_treeview_row_called(self, monkeypatch):
        calls = []
        monkeypatch.setattr(guiwidgets_2._LabelFieldWidget, 'add_treeview_row',
                            lambda *args, **kwargs: calls.append((args, kwargs)))
        with self.add_movie_gui_context() as add_movie_context:
            assert len(calls) == 1
            assert len(calls[0]) == 2
            assert isinstance(calls[0][0][0], guiwidgets_2._LabelFieldWidget)
            assert calls[0][1]['items'] == ('tag 41', 'tag 42')
            assert calls[0][1]['callers_callback'] == add_movie_context.treeview_callback

    def test_create_buttons(self, monkeypatch):
        calls = []
        monkeypatch.setattr(guiwidgets_2, '_create_button',
                            lambda *args, **kwargs: calls.append((args, kwargs)))
        with self.add_movie_gui_context() as add_movie_context:
            assert calls == [((TtkFrame(parent=TtkFrame(parent=DummyTk()), padding=(5, 5, 10, 10)),
                               guiwidgets_2.COMMIT_TEXT,),
                              dict(column=0, command=add_movie_context.commit, enabled=False)),
                             ((TtkFrame(parent=TtkFrame(parent=DummyTk()), padding=(5, 5, 10, 10)),
                               guiwidgets_2.CANCEL_TEXT,),
                              dict(column=1, command=add_movie_context.destroy, enabled=True))]
    
    def test_neuronic_network_enables_and_disables_commit_button(self):
        with self.add_movie_gui_context() as add_movie_context:
            # Get the fields' callbacks.
            outer_frame = add_movie_context.outer_frame
            body_frame = outer_frame.children[0]
            title = body_frame.children[1]
            title_callback = title.textvariable.trace_add_callback
            year = body_frame.children[3]
            year_callback = year.textvariable.trace_add_callback
            
            # Get the commit button.
            buttonbox = outer_frame.children[1]
            commit_button = buttonbox.children[0]
            
            # Initialize title and year text variables to ''
            title.textvariable.set_for_test('')
            year.textvariable.set_for_test('')
            
            # Simulate user entering 'Movie Title' into title field
            title.textvariable.set_for_test('Movie Title')
            title_callback()

            # Simulate user entering '1942' into year field
            year.textvariable.set_for_test('1942')
            year_callback()
            
            # Simulate user entering '' into title field
            title.textvariable.set_for_test('')
            title_callback()

            # Button state history should be:
            # disabled - Initial state
            # disabled - User enters 'Movie Title'
            # enabled - User enters '1942'
            # disabled - User enters '' into title field
            assert commit_button.state_calls == [['disabled'], ['disabled'], ['!disabled'], ['disabled']]
            
    def test_entry_field_dictionary_initialized_with_title_observer(self):
        with self.add_movie_gui_context() as add_movie_context:
            assert isinstance(add_movie_context.entry_fields['title'].observer, guiwidgets_2.neurons.Observer)
            
    def test_entry_field_dictionary_initialized_with_year_observer(self, monkeypatch):
        test_return = 'Test return'
        monkeypatch.setattr(guiwidgets_2, '_create_the_fields_observer', lambda *args: test_return)
        with self.add_movie_gui_context() as add_movie_context:
            assert add_movie_context.entry_fields['year'].observer == test_return
            
    def test_neuronic_network_invokes_tmdb_lookup(self, monkeypatch):
        calls = []
        monkeypatch.setattr(guiwidgets_2.AddMovieGUI, 'tmdb_search', lambda *args: calls.append(args))
        movie_title = 'Movie Title'
    
        with self.add_movie_gui_context() as add_movie_context:
            # Get the fields' callbacks.
            outer_frame = add_movie_context.outer_frame
            body_frame = outer_frame.children[0]
            title = body_frame.children[1]
            title_callback = title.textvariable.trace_add_callback
        
            # Simulate user entering 'Movie Title' into title field
            title.textvariable.set_for_test(movie_title)
            title_callback()
            assert calls[0][1] == movie_title
            
    def test_tmdb_search_call_is_registered_in_event_queue(self):
        expected = 'substring test text'
        with self.add_movie_gui_context() as add_movie_context:
            add_movie_context.tmdb_search(expected)
            event_id = add_movie_context.last_text_event_id
            try:
                _, _, args = add_movie_context.parent.after_calls[event_id]
            except KeyError:
                raise KeyError('The TMDB search was not scheduled in the Tkinter event queue.')
            text, _ = args
            assert text == expected

    def test_tmdb_search_ignores_empty_title_string(self):
        title_string = ''
        with self.add_movie_gui_context() as add_movie_context:
            add_movie_context.tmdb_search(title_string)
            assert add_movie_context.last_text_event_id == ''

    def test_tmdb_search_removes_previous_events(self):
        expected = 'substring test text'
        short_string = 'substrin'
        with self.add_movie_gui_context() as add_movie_context:
            add_movie_context.tmdb_search(short_string)
            event_id = add_movie_context.last_text_event_id
            add_movie_context.tmdb_search(expected)
            try:
                add_movie_context.parent.after_calls[event_id]
            except KeyError:
                pass
            else:
                assert False, "An expired event has not been removed from Tkinter's event queue."

    def test_treeview_callback_updates_selected_tags(self):
        with self.add_movie_gui_context() as add_movie_context:
            add_movie_context.treeview_callback(('tag 42',))

    def test_tmdb_consumer_polling_initiated(self, monkeypatch):
        calls = []
        monkeypatch.setattr(guiwidgets_2.AddMovieGUI, 'tmdb_consumer', lambda *args: calls.append(True))
        with self.add_movie_gui_context():
            assert calls == [True], "Consumer work queue polling not started."
            
    def test_get_work_package_from_queue(self, monkeypatch):
        calls = []
        monkeypatch.setattr('guiwidgets_2.queue.LifoQueue.get_nowait', lambda *args: calls.append((args, True)))
        with self.add_movie_gui_context() as add_movie:
            queue = add_movie.tmdb_work_queue
            assert (calls == queue, True)
            
    def test_work_package_printed_to_stdout(self, capsys):
        with self.add_movie_gui_context() as add_movie:
            test_work_package = 'test work package'
            add_movie.tmdb_work_queue.put(test_work_package)
            add_movie.tmdb_consumer()
            captured = capsys.readouterr()
            assert test_work_package in captured.out, f'{test_work_package} was not printed.'
    
    def test_tmdb_consumer_recalled(self):
        with self.add_movie_gui_context() as add_movie:
            k, v = add_movie.parent.after_calls.popitem()
            delay, callback, args = v
            assert delay == add_movie.work_queue_poll
            assert callback == add_movie.tmdb_consumer

    def test_moviedb_constraint_failure_displays_message(self, monkeypatch):
        # noinspection PyUnusedLocal
        def dummy_commit(*args):
            raise exception.MovieDBConstraintFailure
        
        monkeypatch.setattr(self, 'dummy_commit_callback', dummy_commit)
        calls = []
        monkeypatch.setattr(guiwidgets_2.messagebox, 'showinfo', lambda **kwargs: calls.append(kwargs))
        with self.add_movie_gui_context() as add_movie_context:
            add_movie_context.commit()
            assert calls == [{'detail': 'A movie with this title and year is already present '
                                        'in the database.',
                              'message': 'Database constraint failure.', 'parent': DummyTk()}]
            
    def test_movie_year_constraint_failure_displays_message(self, monkeypatch):
        message = "Invalid year '42'"
        
        # noinspection PyUnusedLocal
        def dummy_commit(*args):
            raise exception.MovieYearConstraintFailure(message)
        
        monkeypatch.setattr(self, 'dummy_commit_callback', dummy_commit)
        calls = []
        monkeypatch.setattr(guiwidgets_2.messagebox, 'showinfo', lambda **kwargs: calls.append(kwargs))
        with self.add_movie_gui_context() as add_movie_context:
            add_movie_context.commit()
            assert calls == [dict(message=message, parent=DummyTk())]

    def test_destroy_deletes_add_movie_form(self, monkeypatch):
        with self.add_movie_gui_context() as add_movie_context:
            add_movie_context.destroy()
            assert add_movie_context.outer_frame.destroy_calls == [True]

    def test_destroy_ends_tmdb_consumer_polling(self, monkeypatch):
        with self.add_movie_gui_context() as add_movie_context:
            event_id = list(add_movie_context.parent.after_calls.keys())[0]
            add_movie_context.search_queue_event_id = event_id
            add_movie_context.destroy()
            test_fail_msg = 'TMDB Work queue polling not cancelled'
            assert add_movie_context.parent.after_cancel_calls == [[(event_id,)]], test_fail_msg

    @contextmanager
    def add_movie_gui_context(self):
        """Yield an AddMovieGUI object for testing."""
        parent = DummyTk()
        tags = ('tag 41', 'tag 42')
        # noinspection PyTypeChecker
        yield guiwidgets_2.AddMovieGUI(parent, self.dummy_commit_callback, self.dummy_tmdb_search_callback, tags)
    
    framing_calls = []
    dummy_body_frame = TtkFrame(DummyTk())
    
    def dummy_create_framing(self, parent) -> Tuple[TtkFrame, TtkFrame, TtkFrame]:
        dummy_outer_frame = TtkFrame(DummyTk())
        dummy_buttonbox = TtkFrame(DummyTk())
        self.framing_calls.append(parent)
        return dummy_outer_frame, self.dummy_body_frame, dummy_buttonbox
    
    commit_callback_calls = None
    
    def dummy_commit_callback(self, *args):
        self.commit_callback_calls = args
        
    def dummy_tmdb_search_callback(self, *args):
        pass


# noinspection DuplicatedCode,PyMissingOrEmptyDocstring
@pytest.mark.usefixtures('patch_tk')
class TestAddTagGUI:
    
    def test_add_tag_gui_created(self):
        with self.add_tag_gui_context() as cm:
            assert cm.parent == DummyTk()
            assert cm.add_tag_callback == self.dummy_add_tag_callback
    
    def test_create_entry_fields_called(self, add_tag_gui_fixtures):
        with self.add_tag_gui_context() as cm:
            assert cm.entry_fields['tag'].label_text == 'Tag'
    
    def test_create_input_form_framing_called(self, add_tag_gui_fixtures):
        self.create_input_form_framing_calls = []
        with self.add_tag_gui_context():
            assert self.create_input_form_framing_calls == [(DummyTk(),)]
    
    def test_add_entry_row_called(self, add_tag_gui_fixtures):
        with self.add_tag_gui_context():
            assert len(self.add_entry_row_calls) == 1
            assert self.add_entry_row_calls[0][1].label_text == 'Tag'
    
    def test_create_button_called(self, add_tag_gui_fixtures):
        self.create_button_calls = []
        with self.add_tag_gui_context() as cm:
            assert self.create_button_calls == [
                    ((TtkFrame(parent=TtkFrame(parent=DummyTk())), 'Commit'),
                     dict(column=0, command=cm.commit, enabled=False)),
                    ((TtkFrame(parent=TtkFrame(parent=DummyTk())), 'Cancel'),
                     dict(column=1, command=cm.destroy))]
    
    def test_focus_set_on_cancel_button(self, add_tag_gui_fixtures):
        with self.add_tag_gui_context():
            cancel_button = self.buttonbox.children[1]
            assert cancel_button.focus_set_calls == [True]
    
    def test_link_or_neuron_to_button(self, add_tag_gui_fixtures):
        with self.add_tag_gui_context():
            enable_button = self.link_or_neuron_to_button_calls[0][0]
            enable_button(True)
            enable_button(False)
            
            commit_button = self.buttonbox.children[0]
            assert commit_button.state_calls == [['!disabled'], ['disabled']]

    def test_link_field_to_neuron(self, add_tag_gui_fixtures):
        with self.add_tag_gui_context():
            calls = self.link_field_to_neuron_calls[0]
            assert len(calls) == 4
            assert calls[0]['tag'].label_text == 'Tag'
            assert calls[1] == guiwidgets_2.TAG_FIELD_NAMES[0]
            assert calls[2] == self.dummy_neuron
            assert isinstance(calls[3], Callable)
    
    def test_commit_calls_add_tag_callback(self, add_tag_gui_fixtures):
        with self.add_tag_gui_context() as cm:
            cm.commit()
            assert self.add_tag_callback_calls == [('4242',)]
    
    def test_destroy_destroys_outer_frame(self, add_tag_gui_fixtures):
        with self.add_tag_gui_context() as cm:
            cm.commit()
            assert cm.outer_frame.destroy_calls == [True]
    
    def dummy_add_tag_callback(self, *args):
        self.add_tag_callback_calls.append(args)
    
    def dummy_create_input_form_framing(self, *args):
        self.create_input_form_framing_calls.append(args)
        return self.outer_frame, self.body_frame, self.buttonbox
    
    def dummy_create_button(self, *args, **kwargs):
        self.create_button_calls.append((args, kwargs))
        return TtkButton(self.buttonbox, 'Test Button')
    
    def dummy_link_or_neuron_to_button(self, *args):
        self.link_or_neuron_to_button_calls.append(args)
        return self.dummy_neuron
    
    @contextmanager
    def add_tag_gui_context(self):
        # noinspection PyTypeChecker
        yield guiwidgets_2.AddTagGUI(DummyTk(), self.dummy_add_tag_callback)

    @pytest.fixture
    def add_tag_gui_fixtures(self, monkeypatch):
        self.add_tag_callback_calls = []
        self.create_entry_fields_calls = []
        self.create_input_form_framing_calls = []
        self.add_entry_row_calls = []
        self.create_button_calls = []
        self.link_or_neuron_to_button_calls = []
        self.link_field_to_neuron_calls = []

        self.dummy_neuron = object()

        self.outer_frame = TtkFrame(DummyTk())
        self.body_frame = TtkFrame(self.outer_frame)
        self.buttonbox = TtkFrame(self.outer_frame)

        monkeypatch.setattr(guiwidgets_2, '_create_input_form_framing',
                            self.dummy_create_input_form_framing)
        monkeypatch.setattr(guiwidgets_2._LabelFieldWidget, 'add_entry_row',
                            lambda *args: self.add_entry_row_calls.append(args))
        monkeypatch.setattr(guiwidgets_2, '_create_button', self.dummy_create_button)
        monkeypatch.setattr(guiwidgets_2, '_create_button_orneuron',
                            self.dummy_link_or_neuron_to_button)
        monkeypatch.setattr(guiwidgets_2, '_link_field_to_neuron',
                            lambda *args: self.link_field_to_neuron_calls.append(args))


# noinspection PyMissingOrEmptyDocstring
@pytest.mark.usefixtures('patch_tk')
class TestSearchTagGUI:
    def test_search_tag_gui_created(self):
        with self.search_tag_gui_context() as cm:
            assert cm.parent == DummyTk()
            callback = self.callback_wrapper()
            sentinel = 'test pattern'
            callback(sentinel)
            assert self.dummy_search_tag_callback_calls == [sentinel]
    
    def test_internal_dictionary_created(self):
        with self.search_tag_gui_context() as cm:
            assert cm.entry_fields['tag'].label_text == 'Tag'
    
    def test_create_input_form_framing_called(self, monkeypatch):
        create_input_form_framing_call = []
        
        def dummy_create_input_form_framing(*args):
            create_input_form_framing_call.append(args)
            return TtkFrame(DummyTk()), TtkFrame(DummyTk()), TtkFrame(DummyTk())
        
        monkeypatch.setattr(guiwidgets_2, '_create_input_form_framing', dummy_create_input_form_framing)
        with self.search_tag_gui_context():
            assert create_input_form_framing_call == [(DummyTk(),), ]
    
    def test_add_entry_row_called(self, monkeypatch):
        add_entry_row_calls = []
        monkeypatch.setattr(guiwidgets_2._LabelFieldWidget, 'add_entry_row',
                            lambda *args: add_entry_row_calls.append(args))
        with self.search_tag_gui_context():
            assert add_entry_row_calls[0][1].label_text == 'Tag'
    
    def test_search_button_created(self):
        with self.search_tag_gui_context() as cm:
            buttonbox = cm.outer_frame.children[1]
            search_button = buttonbox.children[0]
            assert search_button == TtkButton(buttonbox, guiwidgets_2.SEARCH_TEXT, command=cm.search)
    
    def test_cancel_button_created(self):
        with self.search_tag_gui_context() as cm:
            buttonbox = cm.outer_frame.children[1]
            cancel_button = buttonbox.children[1]
            assert cancel_button == TtkButton(buttonbox, guiwidgets_2.CANCEL_TEXT, command=cm.destroy)
    
    def test_focus_set_on_cancel_button(self):
        with self.search_tag_gui_context() as cm:
            buttonbox = cm.outer_frame.children[1]
            cancel_button = buttonbox.children[1]
            assert cancel_button.focus_set_calls == [True]
    
    def test_enable_button_wrapper_called(self, monkeypatch):
        dummy_enable_button_wrapper_calls = []
        monkeypatch.setattr(guiwidgets_2, '_enable_button',
                            lambda *args: dummy_enable_button_wrapper_calls.append(args))
        with self.search_tag_gui_context() as cm:
            buttonbox = cm.outer_frame.children[1]
            search_button = buttonbox.children[0]
            assert dummy_enable_button_wrapper_calls == [(search_button,)]
    
    def test_link_or_neuron_to_button_called(self, monkeypatch):
        dummy_enable_button = object()
    
        # noinspection PyUnusedLocal,PyUnusedLocal
        def dummy_enable_button_wrapper(*args):
            return dummy_enable_button
    
        monkeypatch.setattr(guiwidgets_2, '_enable_button', dummy_enable_button_wrapper)
    
        dummy_link_or_neuron_to_button_calls = []
        monkeypatch.setattr(guiwidgets_2, '_create_button_orneuron',
                            lambda *args: dummy_link_or_neuron_to_button_calls.append(args))
    
        monkeypatch.setattr(guiwidgets_2, '_link_field_to_neuron', lambda *args: None)
        with self.search_tag_gui_context():
            assert dummy_link_or_neuron_to_button_calls == [(dummy_enable_button,)]
    
    def test_notify_neuron_wrapper_called(self, monkeypatch):
        dummy_neuron = object()
    
        # noinspection PyUnusedLocal,PyUnusedLocal
        def dummy_link_or_neuron_to_button(*args):
            return dummy_neuron
    
        monkeypatch.setattr(guiwidgets_2, '_create_button_orneuron', dummy_link_or_neuron_to_button)
    
        dummy_notify_neuron_wrapper_calls = []
        monkeypatch.setattr(guiwidgets_2, '_create_the_fields_observer',
                            lambda *args: dummy_notify_neuron_wrapper_calls.append(args))
        monkeypatch.setattr(guiwidgets_2, '_link_field_to_neuron', lambda *args: None)
        with self.search_tag_gui_context() as cm:
            assert dummy_notify_neuron_wrapper_calls == [(cm.entry_fields,
                                                          guiwidgets_2.TAG_FIELD_NAMES[0],
                                                          dummy_neuron)]
    
    def test_link_field_to_neuron_called(self, monkeypatch):
        dummy_neuron = object()
    
        # noinspection PyUnusedLocal,PyUnusedLocal
        def dummy_link_or_neuron_to_button(*args):
            return dummy_neuron
    
        monkeypatch.setattr(guiwidgets_2, '_create_button_orneuron', dummy_link_or_neuron_to_button)
    
        dummy_notify_neuron = object()
    
        # noinspection PyUnusedLocal,PyUnusedLocal
        def dummy_notify_neuron_wrapper(*args):
            return dummy_notify_neuron
    
        monkeypatch.setattr(guiwidgets_2, '_create_the_fields_observer', dummy_notify_neuron_wrapper)
    
        dummy_link_field_to_neuron_calls = []
        monkeypatch.setattr(guiwidgets_2, '_link_field_to_neuron',
                            lambda *args: dummy_link_field_to_neuron_calls.append(args))
    
        with self.search_tag_gui_context() as cm:
            assert dummy_link_field_to_neuron_calls == [(cm.entry_fields,
                                                         guiwidgets_2.TAG_FIELD_NAMES[0],
                                                         dummy_neuron, dummy_notify_neuron)]

    def test_search_method_calls_the_search_tag_callback(self):
        with self.search_tag_gui_context() as cm:
            field = guiwidgets_2.TAG_FIELD_NAMES[0]
            dummy_search_pattern = cm.entry_fields[field].textvariable.get()
            cm.search()
            assert self.dummy_search_tag_callback_calls == [dummy_search_pattern]

    def test_failed_search_calls_messagebox(self, monkeypatch):
        message = 'No matches'
        detail = 'There are no matching tags in the database.'
        dummy_gui_messagebox_calls = []
        monkeypatch.setattr(guiwidgets_2, 'gui_messagebox',
                            lambda *args: dummy_gui_messagebox_calls.append(args))
    
        exc: Exc = exception.DatabaseSearchFoundNothing
        with self.search_tag_gui_context(exc) as cm:
            cm.search()
            assert dummy_gui_messagebox_calls == [(cm.parent, message, detail)]

    def test_search_method_calls_the_destroy_method(self, monkeypatch):
        dummy_destroy_calls = []
        monkeypatch.setattr(guiwidgets_2.SearchTagGUI, 'destroy',
                            lambda *args: dummy_destroy_calls.append(True))
        with self.search_tag_gui_context() as cm:
            cm.search()
            assert dummy_destroy_calls == [True]

    def test_destroy_method_calls_tk_destroy(self):
        with self.search_tag_gui_context() as cm:
            cm.destroy()
            assert cm.outer_frame.destroy_calls == [True]

    dummy_search_tag_callback_calls = None

    def callback_wrapper(self, exc: Exc = None):
        def dummy_search_tag_callback(pattern: str):
            if exc:
                raise exc
            else:
                self.dummy_search_tag_callback_calls.append(pattern)
    
        return dummy_search_tag_callback

    @contextmanager
    def search_tag_gui_context(self, exc: Exception = None):
        self.dummy_search_tag_callback_calls = []
        parent = DummyTk()
        try:
            # noinspection PyTypeChecker
            yield guiwidgets_2.SearchTagGUI(parent, self.callback_wrapper(exc))
        finally:
            self.dummy_search_tag_callback_calls = None


# noinspection DuplicatedCode,PyMissingOrEmptyDocstring
@pytest.mark.usefixtures('patch_tk')
class TestEditTagGUI:
    test_tag = 'test_tag'
    
    def test_edit_tag_gui_created(self):
        with self.edit_tag_gui_context() as cm:
            assert cm.parent == DummyTk()
            assert cm.tag == self.test_tag
            assert cm.delete_tag_callback == self.dummy_delete_tag_callback
            assert cm.edit_tag_callback == self.dummy_edit_tag_callback
    
    def test_create_entry_fields_called(self, edit_tag_gui_fixtures):
        with self.edit_tag_gui_context() as cm:
            assert cm.entry_fields['tag'].label_text == 'Tag'
    
    def test_create_entry_fields_updated_with_original_value(self, edit_tag_gui_fixtures):
        with self.edit_tag_gui_context() as cm:
            assert cm.entry_fields['tag'].original_value == self.test_tag
    
    def test_create_input_form_framing_called(self, edit_tag_gui_fixtures):
        self.create_input_form_framing_calls = []
        with self.edit_tag_gui_context():
            assert self.create_input_form_framing_calls == [(DummyTk(),)]
    
    def test_create_input_form_fields_called(self, edit_tag_gui_fixtures):
        self.add_entry_row_calls = []
        with self.edit_tag_gui_context():
            assert self.add_entry_row_calls[0][1].label_text == 'Tag'
    
    def test_create_button_called(self, edit_tag_gui_fixtures):
        self.create_button_calls = []
        with self.edit_tag_gui_context() as cm:
            assert self.create_button_calls == [
                    ((TtkFrame(parent=TtkFrame(parent=DummyTk())), 'Commit'),
                     dict(column=0, command=cm.commit, enabled=False)),
                    ((TtkFrame(parent=TtkFrame(parent=DummyTk())), 'Delete'),
                     dict(column=1, command=cm.delete)),
                    ((TtkFrame(parent=TtkFrame(parent=DummyTk())), 'Cancel'),
                     dict(column=2, command=cm.destroy))]
    
    def test_focus_set_on_cancel_button(self, edit_tag_gui_fixtures):
        with self.edit_tag_gui_context():
            cancel_button = self.buttonbox.children[2]
            assert cancel_button.focus_set_calls == [True]
    
    def test_link_or_neuron_to_button(self, edit_tag_gui_fixtures):
        with self.edit_tag_gui_context():
            enable_button = self.link_or_neuron_to_button_calls[0][0]
            enable_button(True)
            enable_button(False)
            
            commit_button = self.buttonbox.children[0]
            assert commit_button.state_calls == [['!disabled'], ['disabled']]
    
    def test_link_field_to_neuron(self, edit_tag_gui_fixtures):
        with self.edit_tag_gui_context():
            calls = self.link_field_to_neuron_calls[0]
            assert len(calls) == 4
            assert calls[0]['tag'].label_text == 'Tag'
            assert calls[1] == guiwidgets_2.TAG_FIELD_NAMES[0]
            assert calls[2] == self.dummy_neuron
            assert isinstance(calls[3], Callable)
    
    def test_commit_calls_add_tag_callback(self, edit_tag_gui_fixtures):
        with self.edit_tag_gui_context() as cm:
            cm.commit()
            assert self.edit_tag_callback_calls == [('4242',)]
    
    def test_delete_test_delete_calls_askyesno_dialog(self, patch_tk, delete_button_fixtures):
        with self.edit_tag_gui_context() as cm:
            cm.delete()
            assert self.askyesno_calls == [dict(message=f"Do you want to delete tag '{self.test_tag}'?",
                                                icon='question', default='no', parent=cm.parent)]
    
    def test_delete_calls_callback_method(self, patch_tk, delete_button_fixtures):
        self.delete_tag_callback_calls = []
        with self.edit_tag_gui_context() as cm:
            cm.delete()
            assert self.delete_tag_callback_calls == [True]

    def test_delete_calls_destroy(self, patch_tk, delete_button_fixtures):
        with self.edit_tag_gui_context() as cm:
            cm.delete()
            assert self.destroy_calls == [True]

    def test_destroy_destroys_outer_frame(self, edit_tag_gui_fixtures):
        with self.edit_tag_gui_context() as cm:
            cm.commit()
            assert cm.outer_frame.destroy_calls == [True]

    def dummy_delete_tag_callback(self):
        self.delete_tag_callback_calls.append(True)

    def dummy_edit_tag_callback(self, *args):
        self.edit_tag_callback_calls.append(args)

    def dummy_create_input_form_framing(self, *args):
        self.create_input_form_framing_calls.append(args)
        return self.outer_frame, self.body_frame, self.buttonbox

    def dummy_create_button(self, *args, **kwargs):
        self.create_button_calls.append((args, kwargs))
        return TtkButton(self.buttonbox, 'Test Button')
    
    def dummy_link_or_neuron_to_button(self, *args):
        self.link_or_neuron_to_button_calls.append(args)
        return self.dummy_neuron
    
    @contextmanager
    def edit_tag_gui_context(self):
        # noinspection PyTypeChecker
        yield guiwidgets_2.EditTagGUI(DummyTk(), self.test_tag, self.dummy_delete_tag_callback,
                                      self.dummy_edit_tag_callback)
    
    @pytest.fixture
    def edit_tag_gui_fixtures(self, monkeypatch):
        self.edit_tag_callback_calls = []
        self.create_entry_fields_calls = []
        self.create_input_form_framing_calls = []
        self.add_entry_row_calls = []
        self.create_button_calls = []
        self.link_or_neuron_to_button_calls = []
        self.link_field_to_neuron_calls = []
        
        self.dummy_neuron = object()
        
        self.outer_frame = TtkFrame(DummyTk())
        self.body_frame = TtkFrame(self.outer_frame)
        self.buttonbox = TtkFrame(self.outer_frame)
        
        monkeypatch.setattr(guiwidgets_2, '_create_input_form_framing',
                            self.dummy_create_input_form_framing)
        monkeypatch.setattr(guiwidgets_2._LabelFieldWidget, 'add_entry_row',
                            lambda *args: self.add_entry_row_calls.append(args))
        monkeypatch.setattr(guiwidgets_2, '_create_button', self.dummy_create_button)
        monkeypatch.setattr(guiwidgets_2, '_create_button_orneuron',
                            self.dummy_link_or_neuron_to_button)
        monkeypatch.setattr(guiwidgets_2, '_link_field_to_neuron',
                            lambda *args: self.link_field_to_neuron_calls.append(args))
    
    askyesno_calls = []
    delete_tag_callback_calls = []
    
    def dummy_askyesno(self, **kwargs):
        self.askyesno_calls.append(kwargs)
        return True

    @pytest.fixture
    def delete_button_fixtures(self, monkeypatch):
        self.askyesno_calls = []
        self.destroy_calls = []
        monkeypatch.setattr(guiwidgets_2.messagebox, 'askyesno', self.dummy_askyesno)
        monkeypatch.setattr(guiwidgets_2.EditTagGUI, 'destroy',
                            lambda *args: self.destroy_calls.append(True))


# noinspection PyMissingOrEmptyDocstring
@pytest.mark.usefixtures('patch_tk')
class TestSelectTagGUI:
    tags_to_show = ['tag 1', 'tag 2']
    
    def test_select_tag_gui_created(self, select_tag_fixtures):
        with self.select_gui_context() as cm:
            assert cm.parent == DummyTk()
            assert cm.select_tag_callback == self.dummy_select_tag_callback
    
    def test_outer_frame_created(self, select_tag_fixtures):
        with self.select_gui_context() as cm:
            assert cm.outer_frame == TtkFrame(parent=DummyTk())
            # Check that it only has two children: The body frame and buttonbox frame.
            assert len(cm.outer_frame.children) == 2
    
    def test_body_frame_created(self, select_tag_fixtures):
        with self.select_gui_context() as cm:
            assert cm.outer_frame.children[0] == TtkFrame(parent=TtkFrame(parent=DummyTk()),
                                                          padding=(10, 25, 10, 0))
    
    def test_buttonbox_frame_created(self, select_tag_fixtures):
        with self.select_gui_context() as cm:
            assert cm.outer_frame.children[1] == TtkFrame(parent=TtkFrame(parent=DummyTk()),
                                                          padding=(5, 5, 10, 10))
    
    def test_treeview_created(self, select_tag_fixtures):
        with self.select_gui_context() as cm:
            assert cm.outer_frame.children[0].children[0] == TtkTreeview(
                    cm.outer_frame.children[0], columns=[],
                    height=10, selectmode='browse',)
    
    def test_treeview_gridded(self, select_tag_fixtures):
        with self.select_gui_context() as cm:
            tree = cm.outer_frame.children[0].children[0]
            assert tree.grid_calls == [dict(column=0, row=0, sticky='w')]
    
    def test_column_width_set(self, select_tag_fixtures):
        with self.select_gui_context() as cm:
            tree = cm.outer_frame.children[0].children[0]
            assert tree.column_calls == [(('#0',), dict(width=350))]
    
    def test_column_heading_set(self, select_tag_fixtures):
        with self.select_gui_context() as cm:
            tree = cm.outer_frame.children[0].children[0]
            assert tree.heading_calls == [(('#0',), dict(text=guiwidgets_2.TAG_FIELD_TEXTS[0]))]

    def test_rows_populated(self, select_tag_fixtures):
        with self.select_gui_context() as cm:
            tree = cm.outer_frame.children[0].children[0]
            assert tree.insert_calls == [
                    (('', 'end'), dict(iid=self.tags_to_show[0], text=self.tags_to_show[0],
                                       values=[], tags='tag')),
                    (('', 'end'), dict(iid=self.tags_to_show[1], text=self.tags_to_show[1],
                                       values=[], tags='tag')), ]

    def test_callback_bound_to_treeview(self, select_tag_fixtures, monkeypatch):
        sentinel = object()
    
        def dummy_wrapper(): return sentinel
    
        monkeypatch.setattr(guiwidgets_2.SelectTagGUI, 'selection_callback_wrapper',
                            lambda *args: dummy_wrapper)
        with self.select_gui_context() as cm:
            tree = cm.outer_frame.children[0].children[0]
            args_ = tree.bind_calls[0][0]
            assert args_ == ('<<TreeviewSelect>>',)
            kwargs = tree.bind_calls[0][1]
            assert len(kwargs) == 1
            assert kwargs['func']() == sentinel

    def test_cancel_button_created(self, select_tag_fixtures):
        with self.select_gui_context() as cm:
            assert self.create_button_calls == [(cm.outer_frame.children[1], guiwidgets_2.CANCEL_TEXT,
                                                 0, cm.destroy)]

    def test_select_tag_callback_called(self, select_tag_fixtures, monkeypatch):
        with self.select_gui_context() as cm:
            tree = cm.outer_frame.children[0].children[0]
            selection_callback = cm.selection_callback_wrapper(tree)
            selection_callback()
            assert self.select_tag_callback_calls == [('test tag',)]

    def test_destroy_called(self, select_tag_fixtures, monkeypatch):
        """This tests the call from selection_callback and not the cancel button callback."""
        destroy_calls = []
        monkeypatch.setattr(guiwidgets_2.SelectTagGUI, 'destroy',
                            lambda *args: destroy_calls.append(True))
        with self.select_gui_context() as cm:
            tree = cm.outer_frame.children[0].children[0]
            selection_callback = cm.selection_callback_wrapper(tree)
            selection_callback()
            assert destroy_calls == [True, ]

    def test_destroy_calls_tk_destroy(self, select_tag_fixtures):
        with self.select_gui_context() as cm:
            cm.destroy()
            assert cm.outer_frame.destroy_calls == [True, ]

    def dummy_select_tag_callback(self, *args):
        self.select_tag_callback_calls.append(args)

    def dummy_create_button(self, *args):
        self.create_button_calls.append(args)

    @pytest.fixture
    def select_tag_fixtures(self, monkeypatch):
        monkeypatch.setattr(guiwidgets_2.ttk, 'Frame', TtkFrame)
        monkeypatch.setattr(guiwidgets_2.ttk, 'Treeview', TtkTreeview)
        monkeypatch.setattr(guiwidgets_2, '_create_button', self.dummy_create_button)
    
    @contextmanager
    def select_gui_context(self):
        self.select_tag_callback_calls = []
        self.create_body_and_button_frames_calls = []
        self.create_button_calls = []
        # noinspection PyTypeChecker
        yield guiwidgets_2.SelectTagGUI(DummyTk(), self.dummy_select_tag_callback, self.tags_to_show)


# noinspection PyMissingOrEmptyDocstring
@pytest.mark.usefixtures('patch_tk')
class TestPreferencesGUI:
    api_key = 'test api key'
    do_not_ask = False
    save_callback_args: List[tuple] = []
    
    create_input_form_framing_calls = None

    def test_preferences_created(self):
        with self.preferences_context() as preferences_gui:
            assert preferences_gui.parent == DummyTk()
            assert preferences_gui.api_key == self.api_key
            assert preferences_gui.do_not_ask == self.do_not_ask
            assert preferences_gui.save_callback == self.dummy_save_callback
            assert preferences_gui.toplevel == TkToplevel(parent=DummyTk())
       
    def test_create_input_form_framing_called(self, monkeypatch):
        self.create_input_form_framing_calls = []
        monkeypatch.setattr(guiwidgets_2, '_create_input_form_framing', self.dummy_framing_call)
        with self.preferences_context() as preferences_gui:
            assert self.create_input_form_framing_calls == [(preferences_gui.toplevel,)]

    def test_create_entry_fields_called(self):
        with self.preferences_context() as preferences_gui:
            assert list(preferences_gui.entry_fields.keys()) == [preferences_gui.api_key_name,
                                                                 preferences_gui.use_tmdb_name, ]
    
    def test_set_original_value_called(self):
        with self.preferences_context() as preferences_gui:
            original_values = [preferences_gui.entry_fields[k].original_value
                               for k in preferences_gui.entry_fields]
            assert original_values == [self.api_key, self.do_not_ask]

    def test_add_label_called(self, monkeypatch):
        with self.preferences_context() as preferences_gui:
            toplevel = preferences_gui.parent.children[0]
            outer_frame = toplevel.children[0]
            body_frame = outer_frame.children[0]
            label = body_frame.children[0]
            # noinspection PyTypeChecker
            assert label == TtkLabel(parent=TtkFrame(
                    parent=TtkFrame(parent=TkToplevel(parent=DummyTk(),)),
                    padding=(10, 25, 10, 0)), text=preferences_gui.api_key_text)

    def test_add_entry_row_called(self, monkeypatch):
        with self.preferences_context() as preferences_gui:
            toplevel = preferences_gui.parent.children[0]
            outer_frame = toplevel.children[0]
            body_frame = outer_frame.children[0]
            entry = body_frame.children[1]
            # trace_add_callback is a unique closure.
            trace_add_callback = entry.textvariable.trace_add_callback
            # noinspection PyTypeChecker
            assert entry == TtkEntry(parent=TtkFrame(
                    parent=TtkFrame(parent=TkToplevel(parent=DummyTk(),)),
                    padding=(10, 25, 10, 0)),
                    textvariable=TkStringVar(trace_add_callback=trace_add_callback), width=36)

    def test_add_checkbox_row_called(self, monkeypatch):
        with self.preferences_context() as preferences_gui:
            toplevel = preferences_gui.parent.children[0]
            outer_frame = toplevel.children[0]
            body_frame = outer_frame.children[0]
            checkbutton = body_frame.children[2]
            # trace_add_callback is a unique closure.
            trace_add_callback = checkbutton.variable.trace_add_callback
            # noinspection PyTypeChecker
            assert checkbutton == TtkCheckbutton(parent=TtkFrame(
                    parent=TtkFrame(parent=TkToplevel(parent=DummyTk(),)),
                    padding=(10, 25, 10, 0)), text=preferences_gui.use_tmdb_text,
                    variable=TkStringVar(trace_add_callback=trace_add_callback), width=36)

    def test_focus_set_called(self, monkeypatch):
        calls = []
        monkeypatch.setattr(guiwidgets_2, '_focus_set', lambda *args: calls.append(args))
        with self.preferences_context() as preferences_gui:
            assert calls == [(preferences_gui.entry_fields[preferences_gui.api_key_name].widget,), ]
    
    def test_save_button_created(self, monkeypatch):
        with self.preferences_context() as preferences_gui:
            toplevel = preferences_gui.parent.children[0]
            outer_frame = toplevel.children[0]
            buttonbox_frame = outer_frame.children[1]
            save_button = buttonbox_frame.children[0]
            assert isinstance(save_button, TtkButton)
            # noinspection PyTypeChecker
            assert save_button.parent == TtkFrame(TtkFrame(TkToplevel(DummyTk())),
                                                  padding=(5, 5, 10, 10))
            assert save_button.text == guiwidgets_2.SAVE_TEXT
            assert isinstance(save_button.command, Callable)
    
    def test_cancel_button_created(self, monkeypatch):
        with self.preferences_context() as preferences_gui:
            toplevel = preferences_gui.parent.children[0]
            outer_frame = toplevel.children[0]
            buttonbox_frame = outer_frame.children[1]
            cancel_button = buttonbox_frame.children[1]
            assert isinstance(cancel_button, TtkButton)
            # noinspection PyTypeChecker
            assert cancel_button.parent == TtkFrame(TtkFrame(TkToplevel(DummyTk())),
                                                    padding=(5, 5, 10, 10))
            assert cancel_button.text == guiwidgets_2.CANCEL_TEXT
            assert isinstance(cancel_button.command, Callable)
    
    def test_neurons(self, monkeypatch):
        with self.preferences_context() as preferences_gui:
            ak_name = preferences_gui.api_key_name
            ak_entry_field = preferences_gui.entry_fields[ak_name]
            ak_original_value = ak_entry_field.original_value
            ak_textvariable = ak_entry_field.textvariable
            ak_textvariable.set_for_test('42')
            ak_observer = ak_entry_field.observer

            da_name = preferences_gui.use_tmdb_name
            da_entry_field = preferences_gui.entry_fields[da_name]
            da_original_value = da_entry_field.original_value
            da_textvariable = da_entry_field.textvariable
            da_textvariable.set_for_test(True)
            da_observer = da_entry_field.observer
            
            toplevel = preferences_gui.parent.children[0]
            outer_frame = toplevel.children[0]
            buttonbox_frame = outer_frame.children[1]
            save_button = buttonbox_frame.children[0]

            # Simulate api key different from original
            ak_observer()
            # Simulate don't ask different from original
            da_observer()
            # Simulate api key same as original
            ak_textvariable.set_for_test(ak_original_value)
            ak_observer()
            # Simulate don't ask same as original
            da_textvariable.set_for_test(da_original_value)
            da_observer()
            assert save_button.state_calls == [['disabled'], ['!disabled'], ['!disabled'],
                                               ['!disabled'], ['disabled']]
    
    def test_save_calls_save_callback(self, monkeypatch):
        calls = []
        with self.preferences_context() as preferences_gui:
            textvariable = preferences_gui.entry_fields[preferences_gui.api_key_name].textvariable.get()
            monkeypatch.setattr(preferences_gui, 'save_callback', lambda *args: calls.append(args))
            monkeypatch.setattr(preferences_gui, 'destroy', lambda *args: None)
            preferences_gui.save()
            assert calls == [(textvariable, textvariable == '1')]
        
    def test_save_calls_destroy(self, monkeypatch):
        calls = []
        with self.preferences_context() as preferences_gui:
            monkeypatch.setattr(preferences_gui, 'save_callback', lambda *args: None)
            monkeypatch.setattr(preferences_gui, 'destroy', lambda: calls.append(True))
            preferences_gui.save()
            assert calls == [True, ]
        
    def test_destroy_calls_toplevel_destroy(self):
        with self.preferences_context() as preferences_gui:
            preferences_gui.destroy()
            assert preferences_gui.toplevel.destroy_calls == [True]
    
    def dummy_save_callback(self, *args):
        self.save_callback_args.append(args)

    def dummy_framing_call(self, *args):
        self.create_input_form_framing_calls.append(args)
        return TtkFrame(DummyTk()), TtkFrame(DummyTk()), TtkFrame(DummyTk())

    @contextmanager
    def preferences_context(self):
        # noinspection PyTypeChecker
        yield guiwidgets_2.PreferencesGUI(DummyTk(), self.api_key, self.do_not_ask,
                                          self.dummy_save_callback)


@pytest.mark.usefixtures('patch_tk')
class TestFocusSet:
    
    def test_focus_set_calls_focus_set_on_entry(self, patch_tk):
        with self.focus_set_context() as entry:
            # noinspection PyUnresolvedReferences
            assert entry.focus_set_calls == [True]

    def test_focus_set_calls_select_range_on_entry(self, patch_tk):
        with self.focus_set_context() as entry:
            # noinspection PyUnresolvedReferences
            assert entry.select_range_calls == [(0, 'end')]

    def test_focus_set_calls_icursor_on_entry(self, patch_tk):
        with self.focus_set_context() as entry:
            # noinspection PyUnresolvedReferences
            assert entry.icursor_calls == [('end',)]
        
    @contextmanager
    def focus_set_context(self):
        entry = guiwidgets_2.ttk.Entry(parent=DummyTk())
        guiwidgets_2._focus_set(entry)
        yield entry


@pytest.mark.usefixtures('patch_tk')
class TestLabelFieldWidget:
    
    def test_label_field_widget_created(self):
        with self.labelfield_context() as labelfield:
            assert labelfield.parent == TtkFrame(DummyTk())
            assert labelfield.col_0_width == 30
            assert labelfield.col_1_width == 36
        
    def test_column_0_configure_called(self):
        with self.labelfield_context() as labelfield:
            args, kwargs = labelfield.parent.columnconfigure_calls[0]
            assert args == (0,)
            assert kwargs == dict(weight=1, minsize=labelfield.col_0_width)

    def test_column_1_configure_called(self):
        with self.labelfield_context() as labelfield:
            args, kwargs = labelfield.parent.columnconfigure_calls[1]
            assert args == (1,)
            assert kwargs == dict(weight=1)
            
    def test_add_entry_row_calls_create_label(self, dummy_entry_field, monkeypatch):
        create_label_calls = []
        monkeypatch.setattr(guiwidgets_2._LabelFieldWidget, '_create_label',
                            lambda *args: create_label_calls.append(args))
        with self.labelfield_context() as labelfield:
            labelfield.add_entry_row(dummy_entry_field)
            _, entry_field, row = create_label_calls[0]
            assert create_label_calls == [(labelfield, dummy_entry_field.label_text, 0)]
        
    def test_add_entry_row_creates_entry(self, dummy_entry_field):
        with self.labelfield_context() as labelfield:
            labelfield.add_entry_row(dummy_entry_field)
            assert dummy_entry_field.widget == TtkEntry(parent=TtkFrame(parent=DummyTk()),
                                                        textvariable=TkStringVar(value='4242'),
                                                        width=36)

    def test_add_entry_row_grids_entry(self, dummy_entry_field):
        with self.labelfield_context() as labelfield:
            labelfield.add_entry_row(dummy_entry_field)
            # noinspection PyUnresolvedReferences
            assert dummy_entry_field.widget.grid_calls == [dict(column=1, row=0)]

    def test_add_entry_row_creates_checkbutton(self, dummy_entry_field):
        with self.labelfield_context() as labelfield:
            labelfield.add_checkbox_row(dummy_entry_field)
            # noinspection PyTypeChecker
            assert dummy_entry_field.widget == TtkCheckbutton(
                    parent=TtkFrame(parent=DummyTk()), text=dummy_entry_field.label_text,
                    variable=dummy_entry_field.textvariable,
                    width=guiwidgets_2._LabelFieldWidget.col_1_width)
        
    def test_add_entry_row_grids_checkbutton(self, dummy_entry_field):
        with self.labelfield_context() as labelfield:
            labelfield.add_checkbox_row(dummy_entry_field)
            # noinspection PyUnresolvedReferences
            assert dummy_entry_field.widget.grid_calls == [dict(column=1, row=0)]

    def dummy_callers_callback(self):
        pass
    
    def test_add_treeview_row_calls_create_label(self, monkeypatch):
        items = ['tag 1', 'tag 2']
        with self.labelfield_context() as labelfield:
            calls = []
            monkeypatch.setattr(guiwidgets_2._LabelFieldWidget, '_create_label',
                                lambda *args: calls.append(args))
            labelfield.add_treeview_row(guiwidgets_2.SELECT_TAGS_TEXT, items,
                                        self.dummy_callers_callback)
            assert calls == [(labelfield, guiwidgets_2.SELECT_TAGS_TEXT, 0)]

    # noinspection PyPep8Naming
    def test_add_treeview_row_creates_MovieTagTreeview_object(self, monkeypatch):
        items = ['tag 1', 'tag 2']
        with self.labelfield_context() as labelfield:
            calls = []
            monkeypatch.setattr(guiwidgets_2, '_MovieTagTreeview', lambda *args: calls.append(args))
            labelfield.add_treeview_row(guiwidgets_2.SELECT_TAGS_TEXT, items,
                                        self.dummy_callers_callback)
            assert calls == [(labelfield.parent, 0, items, self.dummy_callers_callback)]

    # noinspection PyPep8Naming
    def test_add_treeview_row_returns_MovieTagTreeview_object(self, monkeypatch):
        items = ['tag 1', 'tag 2']
        with self.labelfield_context() as labelfield:
            movie_tag_treeview = labelfield.add_treeview_row(guiwidgets_2.SELECT_TAGS_TEXT, items,
                                                             self.dummy_callers_callback)
            assert isinstance(movie_tag_treeview, guiwidgets_2._MovieTagTreeview)

    def test_create_label_creates_label(self, dummy_entry_field):
        row = 0
        with self.labelfield_context() as labelfield:
            labelfield._create_label(dummy_entry_field.label_text, row)
            # noinspection PyTypeChecker
            assert labelfield.parent.children[0] == TtkLabel(TtkFrame(DummyTk()),
                                                             dummy_entry_field.label_text)

    def test_create_label_grids_label(self, dummy_entry_field):
        row = 0
        with self.labelfield_context() as labelfield:
            labelfield._create_label(dummy_entry_field, row)
            assert labelfield.parent.children[0].grid_calls == [{'column': 0, 'row': row,
                                                                 'sticky': 'e', 'padx': 5, }]

    @contextmanager
    def labelfield_context(self):
        parent_frame = TtkFrame(DummyTk())
        # noinspection PyTypeChecker
        yield guiwidgets_2._LabelFieldWidget(parent_frame)
        
    @pytest.fixture()
    def dummy_entry_field(self):
        return guiwidgets_2._EntryField("dummy field", original_value="dummy field value")
       
        
@pytest.mark.usefixtures('patch_tk')
class TestMovieTagTreeview:
    def test_treeview_frame_created(self):
        with self.movie_tag_treeview_context() as cm:
            treeview_frame = cm.body_frame.children[0]
            assert treeview_frame == TtkFrame(parent=TtkFrame(parent=DummyTk()), padding=5)

    def test_treeview_frame_gridded(self):
        with self.movie_tag_treeview_context() as cm:
            treeview_frame = cm.body_frame.children[0]
            assert treeview_frame.grid_calls == [dict(column=1, row=cm.row, sticky='w')]

    def test_treeview_created(self):
        with self.movie_tag_treeview_context() as cm:
            treeview_frame = cm.body_frame.children[0]
            treeview = treeview_frame.children[0]
            assert treeview == TtkTreeview(parent=TtkFrame(parent=TtkFrame(parent=DummyTk()), padding=5),
                                           columns=('tags',), height=10, show='tree', padding=5)

    def test_treeview_gridded(self):
        with self.movie_tag_treeview_context() as cm:
            treeview_frame = cm.body_frame.children[0]
            treeview = treeview_frame.children[0]
            assert treeview.grid_calls == [dict(column=0, row=0, sticky='w')]

    def test_treeview_column_width_set(self):
        with self.movie_tag_treeview_context() as cm:
            treeview_frame = cm.body_frame.children[0]
            treeview = treeview_frame.children[0]
            assert treeview.column_calls == [(('tags',), dict(width=100))]

    def test_treeview_bind_called(self, monkeypatch):
        calls = []
        monkeypatch.setattr(guiwidgets_2._MovieTagTreeview, 'selection_callback_wrapper',
                            lambda *args: calls.append(args))
        with self.movie_tag_treeview_context() as cm:
            treeview_frame = cm.body_frame.children[0]
            treeview = treeview_frame.children[0]
            assert treeview.bind_calls[0][0] == ('<<TreeviewSelect>>',)
            assert calls == [(cm, cm.treeview, cm.callers_callback)]

    def test_scrollbar_created(self):
        with self.movie_tag_treeview_context() as cm:
            treeview_frame = cm.body_frame.children[0]
            treeview, scrollbar = treeview_frame.children
            assert scrollbar == TtkScrollbar(treeview_frame, 'vertical', treeview.yview)

    def test_scrollbar_gridded(self):
        with self.movie_tag_treeview_context() as cm:
            treeview_frame = cm.body_frame.children[0]
            _, scrollbar = treeview_frame.children
            assert scrollbar.grid_calls == [dict(column=1, row=0)]

    def test_treeview_configured_with_scrollbar(self):
        with self.movie_tag_treeview_context() as cm:
            treeview_frame = cm.body_frame.children[0]
            treeview, scrollbar = treeview_frame.children
            assert treeview.configure_calls == [dict(yscrollcommand=scrollbar.set)]
            
    def test_treeview_populated_with_items(self):
        with self.movie_tag_treeview_context() as cm:
            treeview_frame = cm.body_frame.children[0]
            treeview = treeview_frame.children[0]
            assert treeview.insert_calls == [(('', 'end', 'tag 1'), dict(text='tag 1', tags='tags')),
                                             (('', 'end', 'tag 2'), dict(text='tag 2', tags='tags'))]

    def test_set_initial_selection(self):
        with self.movie_tag_treeview_context() as cm:
            treeview_frame = cm.body_frame.children[0]
            treeview = treeview_frame.children[0]
            assert treeview.selection_add_calls == [(cm.initial_selection,)]
            
    def test_callback_called_with_current_user_selection(self):
        tree = TtkTreeview(TtkFrame(DummyTk()))
        calls = []
        with self.movie_tag_treeview_context() as cm:
            selection_callback = cm.selection_callback_wrapper(tree, lambda *args: calls.append(args))
            selection_callback()
            assert calls == [(['test tag', 'ignored tag'],)]
        
    def test_observer_notify_called_with_changed_selection(self, monkeypatch):
        tree = TtkTreeview(TtkFrame(DummyTk()))
        calls = []
        with self.movie_tag_treeview_context() as cm:
            monkeypatch.setattr(cm.observer, 'notify',
                                lambda *args: calls.append(args))
            selection_callback = cm.selection_callback_wrapper(tree, lambda *args: None)
            selection_callback()
            assert calls == [(True,)]
        
    def test_observer_notify_called_with_unchanged_selection(self, monkeypatch):
        tree = TtkTreeview(TtkFrame(DummyTk()))
        calls = []
        with self.movie_tag_treeview_context() as cm:
            monkeypatch.setattr(cm.observer, 'notify',
                                lambda *args: calls.append(args))
            selection_callback = cm.selection_callback_wrapper(tree, lambda *args: None)
            cm.initial_selection = ['test tag', 'ignored tag']
            selection_callback()
            assert calls == [(False,)]

    def test_clear_selection_calls_selection_set(self):
        with self.movie_tag_treeview_context() as cm:
            cm.clear_selection()
            assert cm.treeview.selection_set_calls == [()]

    # noinspection PyMissingOrEmptyDocstring
    @contextmanager
    def movie_tag_treeview_context(self):
        body_frame = guiwidgets_2.ttk.Frame(parent=DummyTk())
        row = 5
        items = ['tag 1', 'tag 2']
        initial_selection = ['tag 1', ]
        yield guiwidgets_2._MovieTagTreeview(body_frame, row, items, lambda *args: None,
                                             initial_selection)


# noinspection PyMissingOrEmptyDocstring
@pytest.mark.usefixtures('patch_tk')
class TestCreateBodyAndButtonFrames:
    
    def test_outer_frame_created(self):
        with self.call_context() as cm:
            outer_frame, body_frame, buttonbox = cm
            assert outer_frame == TtkFrame(parent=DummyTk())
    
    def test_outer_frame_gridded(self):
        with self.call_context() as cm:
            outer_frame, body_frame, buttonbox = cm
            assert outer_frame.grid_calls == [dict(column=0, row=0, sticky='nsew')]
    
    def test_outer_frame_column_configured(self):
        with self.call_context() as cm:
            outer_frame, body_frame, buttonbox = cm
            assert outer_frame.columnconfigure_calls == [((0,), dict(weight=1))]
    
    def test_outer_frame_row_configured(self):
        with self.call_context() as cm:
            outer_frame, body_frame, buttonbox = cm
            assert outer_frame.rowconfigure_calls == [((0,), dict(weight=1)),
                                                      ((1,), dict(minsize=35)), ]
    
    def test_body_frame_created(self):
        with self.call_context() as cm:
            outer_frame, body_frame, buttonbox = cm
            assert body_frame == TtkFrame(parent=outer_frame, padding=(10, 25, 10, 0))
    
    def test_body_frame_gridded(self):
        with self.call_context() as cm:
            outer_frame, body_frame, buttonbox = cm
            assert body_frame.grid_calls == [dict(column=0, row=0, sticky='n')]
    
    def test_buttonbox_created(self):
        with self.call_context() as cm:
            outer_frame, body_frame, buttonbox = cm
            assert buttonbox == TtkFrame(parent=outer_frame, padding=(5, 5, 10, 10))
    
    def test_buttonbox_gridded(self):
        with self.call_context() as cm:
            outer_frame, body_frame, buttonbox = cm
            assert buttonbox.grid_calls == [dict(column=0, row=1, sticky='e')]
    
    @contextmanager
    def call_context(self):
        # noinspection PyTypeChecker
        yield guiwidgets_2._create_input_form_framing(DummyTk())


# noinspection PyMissingOrEmptyDocstring
@pytest.mark.usefixtures('patch_tk')
class TestCreateButton:
    
    def test_create_button_grid(self):
        with self.button_context() as button:
            assert button.grid_calls == [dict(column=0, row=0)]
    
    def test_create_button_bind(self):
        with self.button_context() as button:
            assert button.bind_calls[0][0] == '<Return>'
            assert isinstance(button.bind_calls[0][1], Callable)

    def test_disable_at_initialization(self):
        with self.button_context(False) as button:
            assert button.state_calls == [['disabled']]
    
    @contextmanager
    def button_context(self, enabled=True):
        buttonbox = TtkFrame(DummyTk())
        text = 'Dummy Button'
        column = 0
        # noinspection PyTypeChecker
        yield guiwidgets_2._create_button(buttonbox, text, column, lambda: None, enabled)


def test_gui_messagebox(monkeypatch):
    calls = []
    monkeypatch.setattr(guiwidgets_2.messagebox, 'showinfo',
                        lambda *args, **kwargs: calls.append((args, kwargs)))
    parent = DummyTk()
    message = 'test message'
    detail = 'test detail'
    # noinspection PyTypeChecker
    guiwidgets_2.gui_messagebox(parent, message, detail)
    assert calls == [((parent, message),
                      dict(detail=detail, icon='info'))]


def test_gui_askopenfilename(monkeypatch):
    calls = []
    monkeypatch.setattr(guiwidgets_2.filedialog, 'askopenfilename', lambda **kwargs: calls.append(
            kwargs))
    parent = DummyTk()
    filetypes = (('test filetypes',),)
    # noinspection PyTypeChecker
    guiwidgets_2.gui_askopenfilename(parent, filetypes)
    assert calls == [(dict(parent=parent, filetypes=filetypes))]


@pytest.mark.usefixtures('patch_tk')
def test_clear_input_form_fields_calls_textvariable_set():
    textvariable = guiwidgets_2.tk.StringVar()
    # noinspection PyTypeChecker
    entry_field = guiwidgets_2._EntryField('label', 'original value', textvariable=textvariable)
    entry_fields = dict(test_entry=entry_field)
    guiwidgets_2._clear_input_form_fields(entry_fields)
    # noinspection PyUnresolvedReferences
    assert entry_fields['test_entry'].textvariable.set_calls == [('original value',), ('',)]


def test_create_entry_fields(patch_tk):
    names = ('test field',)
    texts = ('Test Field',)
    entry_fields = guiwidgets_2._create_entry_fields(names, texts)
    # noinspection PyTypeChecker
    assert entry_fields == {names[0]: guiwidgets_2._EntryField(label_text=texts[0], original_value='',
                                                               textvariable=TkStringVar(),)}


def test_set_original_value(patch_tk):
    entry = 'test entry'
    test_label_text = 'test label text'
    test_original_value = 'test original value'

    entry_field = guiwidgets_2._EntryField(test_label_text)
    entry_fields = {entry: entry_field}
    original_values = {entry: test_original_value}
    guiwidgets_2._set_original_value(entry_fields, original_values)
    assert entry_field.original_value == test_original_value
    # noinspection PyUnresolvedReferences
    assert entry_field.textvariable.set_calls == [('',), (test_original_value,)]


def test_enable_button_wrapper(patch_tk):
    # noinspection PyTypeChecker
    button = TtkButton(DummyTk(), 'Dummy Button')
    # noinspection PyTypeChecker
    enable_button = guiwidgets_2._enable_button(button)
    enable_button(True)
    assert button.state_calls == [['!disabled']]


def test_link_or_neuron_to_button():
    # noinspection PyMissingOrEmptyDocstring
    def change_button_state(): pass
    
    neuron = guiwidgets_2._create_button_orneuron(change_button_state)
    assert isinstance(neuron, guiwidgets_2.neurons.OrNeuron)
    assert neuron.notifees == [change_button_state]


def test_link_and_neuron_to_button():
    # noinspection PyMissingOrEmptyDocstring
    def change_button_state(): pass
    
    neuron = guiwidgets_2._create_buttons_andneuron(change_button_state)
    assert isinstance(neuron, guiwidgets_2.neurons.AndNeuron)
    assert neuron.notifees == [change_button_state]


def test_link_field_to_neuron_trace_add_called(patch_tk, dummy_entry_fields):
    name = 'tag'
    neuron = guiwidgets_2.neurons.OrNeuron()
    notify_neuron = guiwidgets_2._create_the_fields_observer(dummy_entry_fields, name, neuron)
    guiwidgets_2._link_field_to_neuron(dummy_entry_fields, name, neuron, notify_neuron)
    # noinspection PyUnresolvedReferences
    assert dummy_entry_fields['tag'].textvariable.trace_add_calls == [('write', notify_neuron)]


def test_link_field_to_neuron_register_event_called(patch_tk, dummy_entry_fields):
    name = 'tag'
    neuron = guiwidgets_2.neurons.OrNeuron()
    notifee = DummyActivateButton()
    neuron.register(notifee)
    notify_neuron = guiwidgets_2._create_the_fields_observer(dummy_entry_fields, name, neuron)
    guiwidgets_2._link_field_to_neuron(dummy_entry_fields, name, neuron, notify_neuron)
    assert not notifee.state
    notify_neuron()
    assert notifee.state


def test_notify_neuron_wrapper(patch_tk, dummy_entry_fields):
    name = 'tag'
    neuron = guiwidgets_2.neurons.OrNeuron()
    notifee = DummyActivateButton()
    neuron.register(notifee)
    notify_neuron = guiwidgets_2._create_the_fields_observer(dummy_entry_fields, name, neuron)
    
    # Match tag field contents to original value thus 'activating' the button.
    notify_neuron()
    assert notifee.state
    
    # Change original value so 'new' value of '4242' appears to be no change thus 'deactivating'
    # the button.
    dummy_entry_fields['tag'].original_value = '4242'
    notify_neuron()
    assert not notifee.state


# noinspection PyMissingOrEmptyDocstring
@pytest.fixture
def dummy_entry_fields():
    # noinspection PyProtectedMember
    return dict(tag=guiwidgets_2._EntryField('Tag', ''))


# noinspection PyMissingOrEmptyDocstring
class DummyActivateButton:
    state = None
    
    def __call__(self, state):
        self.state = state
        

# noinspection PyMissingOrEmptyDocstring,DuplicatedCode
@pytest.fixture()
def patch_tk(monkeypatch):
    monkeypatch.setattr(guiwidgets_2.tk, 'Tk', DummyTk)
    monkeypatch.setattr(guiwidgets_2.tk, 'Toplevel', TkToplevel)
    monkeypatch.setattr(guiwidgets_2.tk, 'StringVar', TkStringVar)
    monkeypatch.setattr(guiwidgets_2.ttk, 'Frame', TtkFrame)
    monkeypatch.setattr(guiwidgets_2.ttk, 'Label', TtkLabel)
    monkeypatch.setattr(guiwidgets_2.ttk, 'Entry', TtkEntry)
    monkeypatch.setattr(guiwidgets_2.ttk, 'Checkbutton', TtkCheckbutton)
    monkeypatch.setattr(guiwidgets_2.ttk, 'Button', TtkButton)
    monkeypatch.setattr(guiwidgets_2.ttk, 'Treeview', TtkTreeview)
    monkeypatch.setattr(guiwidgets_2.ttk, 'Scrollbar', TtkScrollbar)
