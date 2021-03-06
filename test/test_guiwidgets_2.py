"""Test module."""

#  Copyright© 2020. Stephen Rigden.
#  Last modified 6/24/20, 6:57 AM by stephen.
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
from contextlib import contextmanager
from typing import Callable, Optional, Tuple, Type

import pytest

import exception
import guiwidgets_2
from test.dummytk import (DummyTk, TkStringVar, TtkButton, TtkEntry, TtkFrame, TtkLabel,
                          TtkTreeview, TtkScrollbar)


Exc = Type[Optional[exception.DatabaseSearchFoundNothing]]


# noinspection PyMissingOrEmptyDocstring
@pytest.mark.usefixtures('patch_tk')
class TestAddMovieGUI:
    def test_create_entry_fields_called(self, monkeypatch):
        calls = []
        monkeypatch.setattr(guiwidgets_2, 'create_entry_fields', lambda *args: calls.append(args))
        monkeypatch.setattr(guiwidgets_2, 'create_input_form_fields', lambda *args: None)
        try:
            with self.add_movie_gui_context():
                pass
            
        # The monkeypatching of create_entry_fields causes a TypeError in code which is not the subject
        # of this test.
        except TypeError:
            pass
        finally:
            assert calls == [(guiwidgets_2.MOVIE_FIELD_NAMES, guiwidgets_2.MOVIE_FIELD_TEXTS)]

    def test_create_import_form_framing_called(self, monkeypatch):
        self.framing_calls = []
        monkeypatch.setattr(guiwidgets_2, 'create_input_form_framing', self.dummy_create_framing)
        with self.add_movie_gui_context() as add_movie_context:
            assert self.framing_calls == [add_movie_context.parent]
            
    def test_create_input_form_fields(self, monkeypatch):
        fields_calls = []
        monkeypatch.setattr(guiwidgets_2, 'create_input_form_fields',
                            lambda *args: fields_calls.append(args))
        monkeypatch.setattr(guiwidgets_2, 'create_input_form_framing', self.dummy_create_framing)
        monkeypatch.setattr(guiwidgets_2, 'focus_set', lambda *args: None)
        with self.add_movie_gui_context() as add_movie_context:
            assert fields_calls == [(self.dummy_body_frame, guiwidgets_2.MOVIE_FIELD_NAMES,
                                     add_movie_context.entry_fields)]
            
    def test_focus_set_called_for_title_field(self, monkeypatch):
        calls = []
        monkeypatch.setattr(guiwidgets_2, 'focus_set', lambda *args: calls.append(args))
        with self.add_movie_gui_context() as add_movie_context:
            assert calls == [(add_movie_context.entry_fields['title'].widget, )]
    
    def test_movie_tag_treeview_called(self, monkeypatch):
        with self.add_movie_gui_context() as add_movie_context:
            # noinspection PyTypeChecker
            assert add_movie_context.treeview == guiwidgets_2.MovieTagTreeview(
                    guiwidgets_2.TAG_TREEVIEW_INTERNAL_NAME,
                    body_frame=TtkFrame(parent=TtkFrame(parent=DummyTk(), padding=''),
                                        padding=(10, 25, 10, 0)),
                    row=5, column=0, label_text=guiwidgets_2.SELECT_TAGS_TEXT,
                    items=('tag 41', 'tag 42'), user_callback=add_movie_context.treeview_callback)
    
    def test_create_buttons(self, monkeypatch):
        calls = []
        monkeypatch.setattr(guiwidgets_2, 'create_button',
                            lambda *args, **kwargs: calls.append((args, kwargs)))
        with self.add_movie_gui_context() as add_movie_context:
            assert calls == [((TtkFrame(parent=TtkFrame(parent=DummyTk()), padding=(5, 5, 10, 10)),
                               guiwidgets_2.COMMIT_TEXT,),
                              dict(column=0, command=add_movie_context.commit, enabled=False)),
                             ((TtkFrame(parent=TtkFrame(parent=DummyTk()), padding=(5, 5, 10, 10)),
                               guiwidgets_2.CANCEL_TEXT,),
                              dict(column=1, command=add_movie_context.destroy, enabled=True))]
    
    def test_neuron_linked_to_button(self, monkeypatch):
        calls = []
        monkeypatch.setattr(guiwidgets_2, 'link_and_neuron_to_button', lambda *args: calls.append(args))
        monkeypatch.setattr(guiwidgets_2, 'link_field_to_neuron', lambda *args: None)
        with self.add_movie_gui_context() as add_movie_context:
            state_change = calls[0][0]
            buttonbox = add_movie_context.outer_frame.children[1]
            commit_button = buttonbox.children[0]
            state_change(True)
            state_change(False)
            assert commit_button.state_calls == [['disabled'], ['!disabled'], ['disabled']]

    # noinspection DuplicatedCode
    def test_notify_neuron_wrapper_called(self, monkeypatch):
        calls = []
        monkeypatch.setattr(guiwidgets_2, 'notify_neuron_wrapper', lambda *args: calls.append(args))
        with self.add_movie_gui_context() as add_movie_context:
            # Function is called twice for 'title' and 'year'.
            assert len(calls) == 2
            assert len(calls[0]) == len(calls[1]) == 3
            assert calls[0][0] == calls[1][0] == add_movie_context.entry_fields
            assert calls[0][1] == guiwidgets_2.MOVIE_FIELD_NAMES[0]
            assert calls[1][1] == guiwidgets_2.MOVIE_FIELD_NAMES[1]
            assert isinstance(calls[0][2], guiwidgets_2.neurons.AndNeuron)
            assert isinstance(calls[1][2], guiwidgets_2.neurons.AndNeuron)

    # noinspection DuplicatedCode
    def test_title_and_year_fields_linked_to_neuron(self, monkeypatch):
        calls = []
        monkeypatch.setattr(guiwidgets_2, 'link_field_to_neuron', lambda *args: calls.append(args))
        with self.add_movie_gui_context() as add_movie_context:
            # Function is called twice for 'title' and 'year'.
            assert len(calls) == 2
            assert len(calls[0]) == 4
            assert calls[0][0] == calls[1][0] == add_movie_context.entry_fields
            assert calls[0][1] == guiwidgets_2.MOVIE_FIELD_NAMES[0]
            assert calls[1][1] == guiwidgets_2.MOVIE_FIELD_NAMES[1]
            assert isinstance(calls[0][2], guiwidgets_2.neurons.AndNeuron)
            assert isinstance(calls[1][2], guiwidgets_2.neurons.AndNeuron)
            assert isinstance(calls[0][3], Callable)
            assert isinstance(calls[1][3], Callable)

    def test_treeview_callback_updates_selected_tags(self):
        with self.add_movie_gui_context() as add_movie_context:
            add_movie_context.treeview_callback(('tag 42', ))

    def test_commit_calls_callback(self):
        with self.add_movie_gui_context() as add_movie_context:
            add_movie_context.selected_tags = ['tag1', 'tag2']
            add_movie_context.commit()
            assert self.commit_callback_calls == ({'title': '4242', 'year': '4242', 'director': '4242',
                                                   'minutes': '4242', 'notes': '4242'},
                                                  ['tag1', 'tag2'])
            
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

    def test_clear_input_form_fields_called(self, monkeypatch):
        calls = []
        monkeypatch.setattr(guiwidgets_2, 'clear_input_form_fields', lambda *args: calls.append(args))
        with self.add_movie_gui_context() as add_movie_context:
            add_movie_context.commit()
            assert calls == [(add_movie_context.entry_fields,)]

    def test_treeview_clear_selection_called(self, monkeypatch):
        calls = []
        with self.add_movie_gui_context() as add_movie_context:
            monkeypatch.setattr(add_movie_context.treeview, 'clear_selection',
                                lambda: calls.append(True))
            add_movie_context.commit()
            assert calls == [True]

    def test_destroy_deletes_add_movie_form(self, monkeypatch):
        with self.add_movie_gui_context() as add_movie_context:
            add_movie_context.destroy()
            assert add_movie_context.outer_frame.destroy_calls == [True]

    @contextmanager
    def add_movie_gui_context(self):
        """Yield an AddMovieGUI object for testing."""
        parent = DummyTk()
        tags = ('tag 41', 'tag 42')
        # noinspection PyTypeChecker
        yield guiwidgets_2.AddMovieGUI(parent, self.dummy_commit_callback, tags)
    
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
    
    def test_create_input_form_fields_called(self, add_tag_gui_fixtures):
        self.create_input_form_fields_calls = []
        with self.add_tag_gui_context() as cm:
            assert self.create_input_form_fields_calls == [
                    (self.body_frame, guiwidgets_2.TAG_FIELD_NAMES,
                     cm.entry_fields)]
    
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
        self.create_input_form_fields_calls = []
        self.create_button_calls = []
        self.link_or_neuron_to_button_calls = []
        self.link_field_to_neuron_calls = []

        self.dummy_neuron = object()

        self.outer_frame = TtkFrame(DummyTk())
        self.body_frame = TtkFrame(self.outer_frame)
        self.buttonbox = TtkFrame(self.outer_frame)

        monkeypatch.setattr(guiwidgets_2, 'create_input_form_framing',
                            self.dummy_create_input_form_framing)
        monkeypatch.setattr(guiwidgets_2, 'create_input_form_fields',
                            lambda *args: self.create_input_form_fields_calls.append(args))
        monkeypatch.setattr(guiwidgets_2, 'create_button', self.dummy_create_button)
        monkeypatch.setattr(guiwidgets_2, 'link_or_neuron_to_button',
                            self.dummy_link_or_neuron_to_button)
        monkeypatch.setattr(guiwidgets_2, 'link_field_to_neuron',
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
        
        monkeypatch.setattr(guiwidgets_2, 'create_input_form_framing', dummy_create_input_form_framing)
        with self.search_tag_gui_context():
            assert create_input_form_framing_call == [(DummyTk(),), ]
    
    def test_create_input_form_fields_called(self, monkeypatch):
        create_input_form_fields_calls = []
        
        monkeypatch.setattr(guiwidgets_2, 'create_input_form_fields',
                            lambda *args: create_input_form_fields_calls.append(args))
        with self.search_tag_gui_context() as cm:
            assert create_input_form_fields_calls == [(cm.outer_frame.children[0],
                                                       guiwidgets_2.TAG_FIELD_NAMES, cm.entry_fields)]
    
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
        monkeypatch.setattr(guiwidgets_2, 'enable_button_wrapper',
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
    
        monkeypatch.setattr(guiwidgets_2, 'enable_button_wrapper', dummy_enable_button_wrapper)
    
        dummy_link_or_neuron_to_button_calls = []
        monkeypatch.setattr(guiwidgets_2, 'link_or_neuron_to_button',
                            lambda *args: dummy_link_or_neuron_to_button_calls.append(args))
    
        monkeypatch.setattr(guiwidgets_2, 'link_field_to_neuron', lambda *args: None)
        with self.search_tag_gui_context():
            assert dummy_link_or_neuron_to_button_calls == [(dummy_enable_button,)]
    
    def test_notify_neuron_wrapper_called(self, monkeypatch):
        dummy_neuron = object()
    
        # noinspection PyUnusedLocal,PyUnusedLocal
        def dummy_link_or_neuron_to_button(*args):
            return dummy_neuron
    
        monkeypatch.setattr(guiwidgets_2, 'link_or_neuron_to_button', dummy_link_or_neuron_to_button)
    
        dummy_notify_neuron_wrapper_calls = []
        monkeypatch.setattr(guiwidgets_2, 'notify_neuron_wrapper',
                            lambda *args: dummy_notify_neuron_wrapper_calls.append(args))
        monkeypatch.setattr(guiwidgets_2, 'link_field_to_neuron', lambda *args: None)
        with self.search_tag_gui_context() as cm:
            assert dummy_notify_neuron_wrapper_calls == [(cm.entry_fields,
                                                          guiwidgets_2.TAG_FIELD_NAMES[0],
                                                          dummy_neuron)]
    
    def test_link_field_to_neuron_called(self, monkeypatch):
        dummy_neuron = object()
    
        # noinspection PyUnusedLocal,PyUnusedLocal
        def dummy_link_or_neuron_to_button(*args):
            return dummy_neuron
    
        monkeypatch.setattr(guiwidgets_2, 'link_or_neuron_to_button', dummy_link_or_neuron_to_button)
    
        dummy_notify_neuron = object()
    
        # noinspection PyUnusedLocal,PyUnusedLocal
        def dummy_notify_neuron_wrapper(*args):
            return dummy_notify_neuron
    
        monkeypatch.setattr(guiwidgets_2, 'notify_neuron_wrapper', dummy_notify_neuron_wrapper)
    
        dummy_link_field_to_neuron_calls = []
        monkeypatch.setattr(guiwidgets_2, 'link_field_to_neuron',
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
    # def search_tag_gui_context(self, exc: guiwidgets_2.exception.DatabaseSearchFoundNothing = None):
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
        self.create_input_form_fields_calls = []
        with self.edit_tag_gui_context() as cm:
            assert self.create_input_form_fields_calls == [
                    (self.body_frame, guiwidgets_2.TAG_FIELD_NAMES,
                     cm.entry_fields)]
    
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
        self.create_input_form_fields_calls = []
        self.create_button_calls = []
        self.link_or_neuron_to_button_calls = []
        self.link_field_to_neuron_calls = []
        
        self.dummy_neuron = object()
        
        self.outer_frame = TtkFrame(DummyTk())
        self.body_frame = TtkFrame(self.outer_frame)
        self.buttonbox = TtkFrame(self.outer_frame)
        
        monkeypatch.setattr(guiwidgets_2, 'create_input_form_framing',
                            self.dummy_create_input_form_framing)
        monkeypatch.setattr(guiwidgets_2, 'create_input_form_fields',
                            lambda *args: self.create_input_form_fields_calls.append(args))
        monkeypatch.setattr(guiwidgets_2, 'create_button', self.dummy_create_button)
        monkeypatch.setattr(guiwidgets_2, 'link_or_neuron_to_button',
                            self.dummy_link_or_neuron_to_button)
        monkeypatch.setattr(guiwidgets_2, 'link_field_to_neuron',
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
                    height=10, selectmode='browse', )
    
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
        monkeypatch.setattr(guiwidgets_2, 'create_button', self.dummy_create_button)
    
    @contextmanager
    def select_gui_context(self):
        self.select_tag_callback_calls = []
        self.create_body_and_button_frames_calls = []
        self.create_button_calls = []
        # noinspection PyTypeChecker
        yield guiwidgets_2.SelectTagGUI(DummyTk(), self.dummy_select_tag_callback, self.tags_to_show)


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


def test_focus_set_calls_focus_set_on_entry(patch_tk):
    entry = guiwidgets_2.ttk.Entry(parent=DummyTk())
    guiwidgets_2.focus_set(entry)
    # noinspection PyUnresolvedReferences
    assert entry.focus_set_calls == [True]


def test_focus_set_calls_select_range_on_entry(patch_tk):
    entry = guiwidgets_2.ttk.Entry(parent=DummyTk())
    guiwidgets_2.focus_set(entry)
    # noinspection PyUnresolvedReferences
    assert entry.select_range_calls == [(0, 'end')]


def test_focus_set_calls_icursor_on_entry(patch_tk):
    entry = guiwidgets_2.ttk.Entry(parent=DummyTk())
    guiwidgets_2.focus_set(entry)
    # noinspection PyUnresolvedReferences
    assert entry.icursor_calls == [('end', )]


@pytest.mark.usefixtures('patch_tk')
class TestMovieTagTreeview:
    def test_label_created(self):
        with self.movie_tag_treeview_context() as cm:
            label = cm.body_frame.children[0]
            assert label.parent == TtkFrame(parent=DummyTk())
            assert label.text == guiwidgets_2.SELECT_TAGS_TEXT
            assert label.padding == (0, 2)
            
    def test_label_gridded(self):
        with self.movie_tag_treeview_context() as cm:
            label = cm.body_frame.children[0]
            assert label.grid_calls == [dict(column=cm.column, row=cm.row, sticky='ne', padx=5)]
            
    def test_treeview_frame_created(self):
        with self.movie_tag_treeview_context() as cm:
            treeview_frame = cm.body_frame.children[1]
            assert treeview_frame == TtkFrame(parent=TtkFrame(parent=DummyTk()), padding=5)

    def test_treeview_frame_gridded(self):
        with self.movie_tag_treeview_context() as cm:
            treeview_frame = cm.body_frame.children[1]
            assert treeview_frame.grid_calls == [dict(column=cm.column + 1, row=cm.row, sticky='w')]

    def test_treeview_created(self):
        with self.movie_tag_treeview_context() as cm:
            treeview_frame = cm.body_frame.children[1]
            treeview = treeview_frame.children[0]
            assert treeview == TtkTreeview(parent=TtkFrame(parent=TtkFrame(parent=DummyTk()), padding=5),
                                           columns=('tags',), height=10, show='tree', padding=5)

    def test_treeview_gridded(self):
        with self.movie_tag_treeview_context() as cm:
            treeview_frame = cm.body_frame.children[1]
            treeview = treeview_frame.children[0]
            assert treeview.grid_calls == [dict(column=0, row=0, sticky='w')]

    def test_treeview_column_width_set(self):
        with self.movie_tag_treeview_context() as cm:
            treeview_frame = cm.body_frame.children[1]
            treeview = treeview_frame.children[0]
            assert treeview.column_calls == [(('tags', ), dict(width=100))]

    def test_treeview_bind_called(self, monkeypatch):
        calls = []
        monkeypatch.setattr(guiwidgets_2.MovieTagTreeview, 'selection_callback_wrapper',
                            lambda *args: calls.append(args))
        with self.movie_tag_treeview_context() as cm:
            treeview_frame = cm.body_frame.children[1]
            treeview = treeview_frame.children[0]
            assert treeview.bind_calls[0][0] == ('<<TreeviewSelect>>', )
            assert calls == [(cm, cm.treeview, cm.user_callback)]

    def test_scrollbar_created(self):
        with self.movie_tag_treeview_context() as cm:
            treeview_frame = cm.body_frame.children[1]
            treeview, scrollbar = treeview_frame.children
            assert scrollbar == TtkScrollbar(treeview_frame, 'vertical', treeview.yview)

    def test_scrollbar_gridded(self):
        with self.movie_tag_treeview_context() as cm:
            treeview_frame = cm.body_frame.children[1]
            _, scrollbar = treeview_frame.children
            assert scrollbar.grid_calls == [dict(column=1, row=0)]

    def test_treeview_configured_with_scrollbar(self):
        with self.movie_tag_treeview_context() as cm:
            treeview_frame = cm.body_frame.children[1]
            treeview, scrollbar = treeview_frame.children
            assert treeview.configure_calls == [dict(yscrollcommand=scrollbar.set)]
            
    def test_treeview_populated_with_items(self):
        with self.movie_tag_treeview_context() as cm:
            treeview_frame = cm.body_frame.children[1]
            treeview = treeview_frame.children[0]
            assert treeview.insert_calls == [(('', 'end', 'tag 1'), dict(text='tag 1', tags='tags')),
                                             (('', 'end', 'tag 2'), dict(text='tag 2', tags='tags'))]

    def test_set_initial_selection(self):
        with self.movie_tag_treeview_context() as cm:
            treeview_frame = cm.body_frame.children[1]
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
            assert calls == [(guiwidgets_2.TAG_TREEVIEW_INTERNAL_NAME, True)]
        
    def test_observer_notify_called_with_unchanged_selection(self, monkeypatch):
        tree = TtkTreeview(TtkFrame(DummyTk()))
        calls = []
        with self.movie_tag_treeview_context() as cm:
            monkeypatch.setattr(cm.observer, 'notify',
                                lambda *args: calls.append(args))
            selection_callback = cm.selection_callback_wrapper(tree, lambda *args: None)
            cm.initial_selection = ['test tag', 'ignored tag']
            selection_callback()
            assert calls == [(guiwidgets_2.TAG_TREEVIEW_INTERNAL_NAME, False)]

    def test_clear_selection_calls_selection_set(self):
        with self.movie_tag_treeview_context() as cm:
            cm.clear_selection()
            assert cm.treeview.selection_set_calls == [()]

    # noinspection PyMissingOrEmptyDocstring
    @contextmanager
    def movie_tag_treeview_context(self):
        body_frame = guiwidgets_2.ttk.Frame(parent=DummyTk())
        row = 5
        column = 0
        label_text = guiwidgets_2.SELECT_TAGS_TEXT
        items = ['tag 1', 'tag 2']
        initial_selection = ['tag 1', ]
        yield guiwidgets_2.MovieTagTreeview(guiwidgets_2.TAG_TREEVIEW_INTERNAL_NAME, body_frame,
                                            row, column, label_text, items, lambda *args: None,
                                            initial_selection)


def test_create_entry_fields(patch_tk):
    names = ('test field',)
    texts = ('Test Field',)
    entry_fields = guiwidgets_2.create_entry_fields(names, texts)
    # noinspection PyTypeChecker
    assert entry_fields == {names[0]: guiwidgets_2.EntryField(label_text=texts[0], original_value='',
                                                              textvariable=TkStringVar(), )}


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
        yield guiwidgets_2.create_input_form_framing(DummyTk())


# noinspection PyMissingOrEmptyDocstring
@pytest.mark.usefixtures('patch_tk')
class TestCreateInputFormFields:
    original_tag = 'test original value'
    
    def test_columns_configured(self):
        with self.create_fields_context() as cm:
            body_frame, _ = cm
            assert body_frame.columnconfigure_calls == [((0,), dict(minsize=30, weight=1)),
                                                        ((1,), dict(weight=1))]
    
    def test_label_created(self):
        with self.create_fields_context() as cm:
            body_frame, _ = cm
            assert body_frame.children[0] == TtkLabel(parent=TtkFrame(parent=DummyTk(), padding=''),
                                                      text='Tag', padding='')
    
    def test_label_gridded(self):
        with self.create_fields_context() as cm:
            body_frame, entry_fields = cm
            assert body_frame.children[0].grid_calls == [dict(column=0, padx=5, row=0, sticky='e')]
    
    def test_entry_created(self):
        with self.create_fields_context() as cm:
            body_frame, _ = cm
            assert body_frame.children[1] == TtkEntry(parent=TtkFrame(parent=DummyTk()),
                                                      textvariable=TkStringVar(), width=36)
    
    def test_entry_gridded(self):
        with self.create_fields_context() as cm:
            body_frame, _ = cm
            assert body_frame.children[1].grid_calls == [dict(column=1, row=0)]
    
    def test_entry_added_to_entry_fields(self):
        with self.create_fields_context() as cm:
            _, entry_fields = cm
            assert entry_fields['tag'].widget == TtkEntry(parent=TtkFrame(parent=DummyTk(), ),
                                                          textvariable=TkStringVar(), width=36)
    
    def test_entry_text_variable_set(self):
        with self.create_fields_context() as cm:
            _, entry_fields = cm
            assert entry_fields['tag'].textvariable.set_calls == [(self.original_tag,)]
    
    @contextmanager
    def create_fields_context(self):
        body_frame = TtkFrame(DummyTk())
        names = ('tag',)
        entry_fields = dict(tag=guiwidgets_2.EntryField('Tag', ''))
        entry_fields['tag'].original_value = self.original_tag
        # noinspection PyTypeChecker
        guiwidgets_2.create_input_form_fields(body_frame, names, entry_fields)
        yield body_frame, entry_fields


@pytest.mark.usefixtures('patch_tk')
def test_clear_input_form_fields_calls_textvariable_set():
    textvariable = guiwidgets_2.tk.StringVar()
    # noinspection PyTypeChecker
    entry_field = guiwidgets_2.EntryField('label', 'original value', textvariable=textvariable)
    entry_fields = dict(test_entry=entry_field)
    guiwidgets_2.clear_input_form_fields(entry_fields)
    # noinspection PyUnresolvedReferences
    assert entry_fields['test_entry'].textvariable.set_calls == [('',)]


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
        yield guiwidgets_2.create_button(buttonbox, text, column, lambda: None, enabled)


def test_enable_button_wrapper(patch_tk):
    # noinspection PyTypeChecker
    button = TtkButton(DummyTk(), 'Dummy Button')
    # noinspection PyTypeChecker
    enable_button = guiwidgets_2.enable_button_wrapper(button)
    enable_button(True)
    assert button.state_calls == [['!disabled']]


def test_link_or_neuron_to_button():
    # noinspection PyMissingOrEmptyDocstring
    def change_button_state(): pass
    
    neuron = guiwidgets_2.link_or_neuron_to_button(change_button_state)
    assert isinstance(neuron, guiwidgets_2.neurons.OrNeuron)
    assert neuron.notifees == [change_button_state]


def test_link_and_neuron_to_button():
    # noinspection PyMissingOrEmptyDocstring
    def change_button_state(): pass
    
    neuron = guiwidgets_2.link_and_neuron_to_button(change_button_state)
    assert isinstance(neuron, guiwidgets_2.neurons.AndNeuron)
    assert neuron.notifees == [change_button_state]


def test_link_field_to_neuron_trace_add_called(patch_tk, dummy_entry_fields):
    name = 'tag'
    neuron = guiwidgets_2.neurons.OrNeuron()
    notify_neuron = guiwidgets_2.notify_neuron_wrapper(dummy_entry_fields, name, neuron)
    guiwidgets_2.link_field_to_neuron(dummy_entry_fields, name, neuron, notify_neuron)
    # noinspection PyUnresolvedReferences
    assert dummy_entry_fields['tag'].textvariable.trace_add_calls == [('write', notify_neuron)]


def test_link_field_to_neuron_register_event_called(patch_tk, dummy_entry_fields):
    name = 'tag'
    neuron = guiwidgets_2.neurons.OrNeuron()
    notifee = DummyActivateButton()
    neuron.register(notifee)
    notify_neuron = guiwidgets_2.notify_neuron_wrapper(dummy_entry_fields, name, neuron)
    guiwidgets_2.link_field_to_neuron(dummy_entry_fields, name, neuron, notify_neuron)
    assert not notifee.state
    notify_neuron()
    assert notifee.state


def test_notify_neuron_wrapper(patch_tk, dummy_entry_fields):
    name = 'tag'
    neuron = guiwidgets_2.neurons.OrNeuron()
    notifee = DummyActivateButton()
    neuron.register(notifee)
    notify_neuron = guiwidgets_2.notify_neuron_wrapper(dummy_entry_fields, name, neuron)
    
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
    return dict(tag=guiwidgets_2.EntryField('Tag', ''))


# noinspection PyMissingOrEmptyDocstring
class DummyActivateButton:
    state = None
    
    def __call__(self, state):
        self.state = state


# noinspection PyMissingOrEmptyDocstring,DuplicatedCode
@pytest.fixture()
def patch_tk(monkeypatch):
    monkeypatch.setattr(guiwidgets_2.tk, 'Tk', DummyTk)
    monkeypatch.setattr(guiwidgets_2.tk, 'StringVar', TkStringVar)
    monkeypatch.setattr(guiwidgets_2.ttk, 'Frame', TtkFrame)
    monkeypatch.setattr(guiwidgets_2.ttk, 'Label', TtkLabel)
    monkeypatch.setattr(guiwidgets_2.ttk, 'Entry', TtkEntry)
    monkeypatch.setattr(guiwidgets_2.ttk, 'Button', TtkButton)
    monkeypatch.setattr(guiwidgets_2.ttk, 'Treeview', TtkTreeview)
    monkeypatch.setattr(guiwidgets_2.ttk, 'Scrollbar', TtkScrollbar)
