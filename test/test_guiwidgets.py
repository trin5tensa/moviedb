"""Test module."""

#  Copyright© 2020. Stephen Rigden.
#  Last modified 4/12/20, 8:50 AM by stephen.
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
from dataclasses import dataclass, field
from typing import Callable, Sequence, Tuple, Union

import pytest

import exception
import guiwidgets


# noinspection PyMissingOrEmptyDocstring
class TestAddMovieGUI:
    
    # Test Basic Initialization
    
    def test_parent_initialized(self, patch_tk):
        with self.movie_context() as movie_gui:
            assert movie_gui.parent == DummyTk()
    
    def test_callback_initialized(self, patch_tk):
        with self.movie_context() as movie_gui:
            assert movie_gui.callback == movie_gui_callback
    
    def test_fields_initialized(self, patch_tk):
        with self.movie_context() as movie_gui:
            for internal_name in guiwidgets.INTERNAL_NAMES:
                assert isinstance(movie_gui.entry_fields[internal_name], guiwidgets.EntryField)
    
    def test_fields_label_text(self, patch_tk):
        with self.movie_context() as movie_gui:
            for internal_name, label_text in zip(guiwidgets.INTERNAL_NAMES, guiwidgets.FIELD_TEXTS):
                assert movie_gui.entry_fields[internal_name].label_text == label_text
    
    def test_fields_database_value(self, patch_tk):
        with self.movie_context() as movie_gui:
            for internal_name, label_text in zip(guiwidgets.INTERNAL_NAMES, guiwidgets.FIELD_TEXTS):
                assert movie_gui.entry_fields[internal_name].original_value == ''
    
    def test_fields_text_variable(self, patch_tk):
        with self.movie_context() as movie_gui:
            for internal_name, label_text in zip(guiwidgets.INTERNAL_NAMES, guiwidgets.FIELD_TEXTS):
                assert isinstance(movie_gui.entry_fields[internal_name].textvariable,
                                  guiwidgets.tk.StringVar)
    
    def test_fields_observer(self, patch_tk):
        with self.movie_context() as movie_gui:
            for internal_name, label_text in zip(guiwidgets.INTERNAL_NAMES, guiwidgets.FIELD_TEXTS):
                assert isinstance(movie_gui.entry_fields[internal_name].observer,
                                  guiwidgets.neurons.Observer)
    
    def test_outer_frame_created(self, patch_tk):
        with self.movie_context() as movie_gui:
            assert movie_gui.outer_frame == TtkFrame(parent=DummyTk())
    
    def test_outer_frame_column_configured(self, patch_tk):
        with self.movie_context() as movie_gui:
            assert movie_gui.parent.children[0].columnconfigure_calls[0] == ((0,), dict(weight=1))
    
    def test_outer_frame_row_0_configured(self, patch_tk):
        with self.movie_context() as movie_gui:
            assert movie_gui.parent.children[0].rowconfigure_calls[0] == ((0,), dict(weight=1))
    
    def test_outer_frame_row_1_configured(self, patch_tk):
        with self.movie_context() as movie_gui:
            assert movie_gui.parent.children[0].rowconfigure_calls[1] == ((1,), dict(minsize=35))
    
    def test_outer_frame_gridded(self, patch_tk):
        with self.movie_context() as movie_gui:
            outerframe = movie_gui.parent.children[0]
            assert outerframe.grid_calls[0] == dict(column=0, row=0, sticky='nsew')
    
    # Test Body Initialization
    
    def test_body_frame_created(self, patch_tk):
        with self.movie_context() as movie_gui:
            outerframe = movie_gui.parent.children[0]
            bodyframe = outerframe.children[0]
            assert bodyframe == TtkFrame(parent=outerframe, padding=(10, 25, 10, 0))
    
    def test_body_frame_gridded(self, patch_tk):
        with self.movie_context() as movie_gui:
            outerframe = movie_gui.parent.children[0]
            bodyframe = outerframe.children[0]
            assert bodyframe.grid_calls[0] == dict(column=0, row=0, sticky='n')
    
    def test_body_frame_column_0_configured(self, patch_tk):
        with self.movie_context() as movie_gui:
            call = movie_gui.parent.children[0].children[0].columnconfigure_calls[0]
            assert call == ((0,), dict(weight=1, minsize=30))
    
    def test_body_frame_column_1_configured(self, patch_tk):
        with self.movie_context() as movie_gui:
            call = movie_gui.parent.children[0].children[0].columnconfigure_calls[1]
            assert call == ((1,), dict(weight=1))
    
    def test_labels_and_entries_created(self, patch_tk):
        with self.movie_context() as movie_gui:
            outerframe = movie_gui.parent.children[0]
            bodyframe = outerframe.children[0]
            assert bodyframe.children
    
    def test_labels_created(self, patch_tk):
        with self.movie_context() as movie_gui:
            outerframe = movie_gui.parent.children[0]
            bodyframe = outerframe.children[0]
            labels = bodyframe.children[::2]
            for label, text in zip(labels, guiwidgets.FIELD_TEXTS):
                assert label == TtkLabel(TtkFrame(TtkFrame(DummyTk()), padding=(10, 25, 10, 0)),
                                         text=text)
    
    # noinspection DuplicatedCode
    def test_labels_gridded(self, patch_tk):
        with self.movie_context() as movie_gui:
            outerframe = movie_gui.parent.children[0]
            bodyframe = outerframe.children[0]
            labels = bodyframe.children[:4:2]
            for row_ix, label in enumerate(labels):
                assert label.grid_calls[0] == dict(column=0, row=row_ix, sticky='e', padx=5)
    
    def test_entries_created(self, patch_tk):
        with self.movie_context() as movie_gui:
            outerframe = movie_gui.parent.children[0]
            bodyframe = outerframe.children[0]
            entries = bodyframe.children[1:4:2]
            for entry in entries:
                assert entry == TtkEntry(TtkFrame(TtkFrame(DummyTk()), padding=(10, 25, 10, 0)),
                                         textvariable=TkStringVar(), width=36)
    
    def test_neuron_created(self, patch_tk):
        with self.movie_context() as movie_gui:
            assert movie_gui.commit_neuron.events == dict(title=False, year=True)
    
    def test_minutes_initialized_to_100(self, patch_tk):
        with self.movie_context() as movie_gui:
            assert movie_gui.entry_fields['minutes'].textvariable.set_calls[0][0] == '100'
    
    def test_minutes_callbacks_configured(self, patch_tk):
        with self.movie_context() as movie_gui:
            config_calls = movie_gui.entry_fields['minutes'].widget.config_calls[0]
            assert config_calls == dict(validate='key',
                                        validatecommand=('test registered_callback', '%S'))
    
    def test_year_initialized_to_2020(self, patch_tk):
        with self.movie_context() as movie_gui:
            assert movie_gui.entry_fields['year'].textvariable.set_calls[0][0] == '2020'
    
    def test_year_callbacks_configured(self, patch_tk):
        with self.movie_context() as movie_gui:
            config_calls = movie_gui.entry_fields['year'].widget.config_calls[0]
            assert config_calls == dict(validate='key',
                                        validatecommand=('test registered_callback', '%S'))
    
    # noinspection DuplicatedCode
    def test_entries_gridded(self, patch_tk):
        with self.movie_context() as movie_gui:
            outerframe = movie_gui.parent.children[0]
            bodyframe = outerframe.children[0]
            entries = bodyframe.children[1:4:2]
            for row_ix, entry in enumerate(entries):
                assert entry.grid_calls[0] == dict(column=1, row=row_ix)
    
    def test_tags_label_called(self, patch_tk):
        with self.movie_context() as movie_gui:
            outerframe = movie_gui.parent.children[0]
            bodyframe = outerframe.children[0]
            label = bodyframe.children[-2::2]
            assert label[0] == TtkLabel(TtkFrame(TtkFrame(DummyTk()), padding=(10, 25, 10, 0)),
                                        text=guiwidgets.SELECT_TAGS_TEXT, padding=(0, 2))
    
    def test_tags_label_gridded(self, patch_tk):
        with self.movie_context() as movie_gui:
            outerframe = movie_gui.parent.children[0]
            bodyframe = outerframe.children[0]
            label = bodyframe.children[-2::2]
            assert label[0].grid_calls[0] == dict(column=0, row=5, sticky='ne', padx=5)
    
    def test_tags_frame_created(self, patch_tk):
        with self.movie_context() as movie_gui:
            outerframe = movie_gui.parent.children[0]
            bodyframe = outerframe.children[0]
            assert bodyframe.children[-1] == TtkFrame(parent=TtkFrame(parent=TtkFrame(
                    parent=DummyTk()), padding=(10, 25, 10, 0)), padding=5)
    
    def test_tags_frame_gridded(self, patch_tk):
        with self.movie_context() as movie_gui:
            outerframe = movie_gui.parent.children[0]
            bodyframe = outerframe.children[0]
            assert bodyframe.children[-1].grid_calls[0] == dict(column=1, row=5, sticky='w')
    
    def test_tree_created(self, patch_tk):
        with self.movie_context() as movie_gui:
            outerframe = movie_gui.parent.children[0]
            bodyframe = outerframe.children[0]
            tags_frame = bodyframe.children[-1]
            assert tags_frame.children[0] == TtkTreeview(parent=TtkFrame(parent=TtkFrame(
                    parent=TtkFrame(parent=DummyTk()), padding=(10, 25, 10, 0)), padding=5),
                    columns=('tags',), height=12, selectmode='extended', show='tree', padding=5)
    
    def test_tree_gridded(self, patch_tk):
        with self.movie_context() as movie_gui:
            outerframe = movie_gui.parent.children[0]
            bodyframe = outerframe.children[0]
            tags_frame = bodyframe.children[-1]
            tree = tags_frame.children[0]
            assert tree.grid_calls[0] == dict(column=0, row=0, sticky='w')
    
    def test_tree_column_sized(self, patch_tk):
        with self.movie_context() as movie_gui:
            outerframe = movie_gui.parent.children[0]
            bodyframe = outerframe.children[0]
            tags_frame = bodyframe.children[-1]
            tree = tags_frame.children[0]
            assert tree.column_calls[0] == (('tags',), dict(width=100))
    
    def test_tree_tag_bind(self, patch_tk):
        with self.movie_context() as movie_gui:
            outerframe = movie_gui.parent.children[0]
            bodyframe = outerframe.children[0]
            tags_frame = bodyframe.children[-1]
            tree = tags_frame.children[0]
            assert tree.bind_calls[0][0] == ('<<TreeviewSelect>>',)
            
            tree.bind_calls[0][1]['func']()
            assert movie_gui.selected_tags == ['test tag 1', 'test tag 2']
    
    def test_tree_insert(self, patch_tk):
        with self.movie_context() as movie_gui:
            outerframe = movie_gui.parent.children[0]
            bodyframe = outerframe.children[0]
            tags_frame = bodyframe.children[-1]
            tree = tags_frame.children[0]
            assert tree.insert_calls == [(('', 'end', tag), dict(text=tag, tags='tags'))
                                         for tag in movie_gui.all_tags]
    
    def test_scrollbar_created(self, patch_tk):
        with self.movie_context() as movie_gui:
            outerframe = movie_gui.parent.children[0]
            bodyframe = outerframe.children[0]
            tags_frame = bodyframe.children[-1]
            tree, scrollbar = tags_frame.children
            assert scrollbar == TtkScrollbar(tags_frame, orient=guiwidgets.tk.VERTICAL,
                                             command=tree.yview)
    
    def test_scrollbar_gridded(self, patch_tk):
        with self.movie_context() as movie_gui:
            outerframe = movie_gui.parent.children[0]
            bodyframe = outerframe.children[0]
            tags_frame = bodyframe.children[-1]
            tree, scrollbar = tags_frame.children
            assert scrollbar.grid_calls[0] == dict(column=1, row=0)
    
    def test_tree_configured_with_scrollbar(self, patch_tk):
        with self.movie_context() as movie_gui:
            outerframe = movie_gui.parent.children[0]
            bodyframe = outerframe.children[0]
            tags_frame = bodyframe.children[-1]
            tree, scrollbar = tags_frame.children
            assert tree.configure_calls[0] == dict(yscrollcommand=scrollbar.set)

    def test_neuron_linker_called(self, patch_tk, monkeypatch):
        calls = []
        monkeypatch.setattr(guiwidgets.AddMovieGUI, 'neuron_linker',
                            lambda *args: calls.append(args))
        with self.movie_context() as movie_gui:
            assert calls == [
                    (movie_gui, 'title', movie_gui.commit_neuron, movie_gui.neuron_callback),
                    (movie_gui, 'year', movie_gui.commit_neuron, movie_gui.neuron_callback, True)]

    def test_movie_treeview_call(self, patch_tk, patch_movie_treeview):
        sentinel = object()
        with self.movie_context():
            assert treeview_call[0][1] == guiwidgets.TAG_TREEVIEW_INTERNAL_NAME
            assert treeview_call[0][2] == TtkFrame(parent=TtkFrame(parent=DummyTk(),
                                                                   padding=''), padding=(10, 25, 10, 0))
            assert treeview_call[0][3] == 5
            assert treeview_call[0][4] == 0
            assert treeview_call[0][5] == 'Select tags'
            assert treeview_call[0][6] == ('test tag 1', 'test tag 2')
            assert treeview_call[0][7](sentinel) == sentinel

    # Test Buttonbox Initialization

    def test_buttonbox_created(self, patch_tk):
        with self.movie_context() as movie_gui:
            outerframe = movie_gui.parent.children[0]
            buttonbox = outerframe.children[1]
            assert buttonbox == TtkFrame(parent=outerframe, padding=(5, 5, 10, 10))

    def test_buttonbox_gridded(self, patch_tk):
        with self.movie_context() as movie_gui:
            outerframe = movie_gui.parent.children[0]
            buttonbox = outerframe.children[1]
            assert buttonbox.grid_calls[0] == dict(column=0, row=1, sticky='e')
    
    def test_commit_button_created(self, patch_tk):
        with self.movie_context() as movie_gui:
            button = movie_gui.parent.children[0].children[1].children[0]
            assert button == TtkButton(parent=TtkFrame(parent=TtkFrame(parent=DummyTk()),
                                                       padding=(5, 5, 10, 10)),
                                       text='Commit', command=movie_gui.commit)
    
    def test_commit_button_gridded(self, patch_tk):
        with self.movie_context() as movie_gui:
            button = movie_gui.parent.children[0].children[1].children[0]
            assert button.grid_calls[0] == dict(column=0, row=0)
    
    # noinspection DuplicatedCode
    def test_commit_button_bound(self, patch_tk):
        with self.movie_context() as movie_gui:
            button = movie_gui.parent.children[0].children[1].children[0]
            assert button.bind_calls[0][0] == '<Return>'
            button.bind_calls[0][1](button)
            assert button.invoke_calls[0]
    
    def test_commit_button_state_set(self, patch_tk):
        with self.movie_context() as movie_gui:
            button = movie_gui.parent.children[0].children[1].children[0]
            assert button.state_calls[0][0] == 'disabled'
    
    # noinspection PyShadowingNames
    def test_neuron_register_called(self, patch_tk, monkeypatch):
        calls = []
        monkeypatch.setattr(guiwidgets.AddMovieGUI, 'button_state_callback',
                            lambda movie_gui, button: calls.append(button, ))
        with self.movie_context() as movie_gui:
            button = movie_gui.parent.children[0].children[1].children[0]
            assert calls[0] == button
    
    def test_cancel_button_created(self, patch_tk):
        with self.movie_context() as movie_gui:
            button = movie_gui.parent.children[0].children[1].children[1]
            assert button == TtkButton(parent=TtkFrame(parent=TtkFrame(parent=DummyTk()),
                                                       padding=(5, 5, 10, 10)),
                                       text='Cancel', command=movie_gui.destroy)
    
    def test_cancel_button_gridded(self, patch_tk):
        with self.movie_context() as movie_gui:
            button = movie_gui.parent.children[0].children[1].children[1]
            assert button.grid_calls[0] == dict(column=1, row=0)
    
    def test_cancel_button_bound(self, patch_tk):
        with self.movie_context() as movie_gui:
            button = movie_gui.parent.children[0].children[1].children[1]
            assert button.bind_calls[0][0] == '<Return>'
            button.bind_calls[0][1](button)
            assert button.invoke_calls[0]
    
    def test_cancel_button_focus_set(self, patch_tk):
        with self.movie_context() as movie_gui:
            button = movie_gui.parent.children[0].children[1].children[1]
            assert button.focus_set_calls[0] is True
    
    # Test Neuron Link Initialization
    
    def test_trace_add_called(self, patch_tk, monkeypatch):
        calls = []
        monkeypatch.setattr(guiwidgets.AddMovieGUI, 'neuron_callback',
                            lambda *args: calls.append(args))
        with self.movie_context() as movie_gui:
            assert movie_gui.entry_fields['title'].textvariable.trace_add_calls[0][0] == 'write'
            assert calls[0][0] == movie_gui
            assert calls[0][1] == 'title'
            assert isinstance(calls[0][2], guiwidgets.neurons.AndNeuron)
            # Are  'title' and 'year' fields linked to the same neuron?
            assert calls[0][2] == calls[1][2]
    
    def test_neuron_register_event_called(self, patch_tk, monkeypatch):
        calls = []
        monkeypatch.setattr(guiwidgets.neurons.AndNeuron, 'register_event',
                            lambda *args: calls.append(args))
        with self.movie_context():
            assert calls[0][1] == 'title'
            assert calls[1][1] == 'year'
            # Are  'title' and 'year' fields linked to the same neuron?
            assert calls[0][0] == calls[1][0]
    
    # Test Miscellaneous Methods
    
    def test_field_callback(self, patch_tk):
        with self.movie_context() as movie_gui:
            neuron = movie_gui.commit_neuron
            movie_gui.neuron_callback('year', neuron)()
            assert neuron.events == dict(title=False, year=True)

    def test_button_state_with_true_callback(self, patch_tk):
        with self.movie_context() as movie_gui:
            commit = movie_gui.parent.children[0].children[1].children[0]
            movie_gui.button_state_callback(commit)(True)
            assert commit.state_calls == [['disabled'], ['!disabled']]

    def test_button_state_with_false_callback(self, patch_tk):
        with self.movie_context() as movie_gui:
            commit = movie_gui.parent.children[0].children[1].children[0]
            movie_gui.button_state_callback(commit)(False)
            assert commit.state_calls == [['disabled'], ['disabled']]

    def test_validate_true_int(self, patch_tk):
        with self.movie_context() as movie_gui:
            assert movie_gui.validate_int('42')

    def test_validate_false_int(self, patch_tk):
        with self.movie_context() as movie_gui:
            valid_int = movie_gui.validate_int('forty two')
            assert movie_gui.parent.bell_calls == [True]
            assert not valid_int
    
    def test_validate_int_within_range(self, patch_tk):
        with self.movie_context() as movie_gui:
            assert movie_gui.validate_int_range(42, 40, 50)
            assert not movie_gui.validate_int_range(42, 42, 50)
            assert not movie_gui.validate_int_range(42, 40, 42)
    
    def test_commit_calls_validate_int_range(self, patch_tk, monkeypatch):
        calls = []
        
        def dummy_validate_int_range(result: bool) -> Callable:
            # noinspection PyShadowingNames
            def validate_int_range(*args):
                calls.append(args)
                return result
            
            return validate_int_range
        
        with self.movie_context() as movie_gui:
            validate_int_range = dummy_validate_int_range(True)
            monkeypatch.setattr(movie_gui, 'callback', lambda *args: None)
            monkeypatch.setattr(movie_gui, 'validate_int_range', validate_int_range)
            movie_gui.commit()
            assert calls == [(4242, 1877, 10000)]
    
    def test_commit_calls_validate_int_range_with_invalid_year(self, patch_tk, monkeypatch):
        with self.movie_context() as movie_gui:
            monkeypatch.setattr(movie_gui, 'callback', lambda *args: None)
            monkeypatch.setattr(movie_gui, 'validate_int_range', lambda *args: False)
            messagebox = TkMessagebox()
            monkeypatch.setattr(guiwidgets, 'messagebox', messagebox)
            movie_gui.commit()
            assert messagebox.showinfo_calls == [dict(parent=DummyTk(), message='Invalid year.',
                                                      detail='The year must be between 1877 and 10000.')]
    
    def test_commit_callback_method(self, patch_tk, monkeypatch):
        calls = []
        with self.movie_context() as movie_gui:
            monkeypatch.setattr(movie_gui, 'callback', lambda *args: calls.append(args))
            movie_gui.commit()
            assert calls[0][0] == dict(title='4242', year='4242', director='4242',
                                       minutes='4242', notes='4242')
            assert movie_gui.outer_frame.destroy_calls[0]
    
    def test_commit_callback_exception(self, patch_tk, monkeypatch):
        def dummy_callback():
            # noinspection PyUnusedLocal
            def callback(*args, **kwargs):
                raise exception.MovieDBConstraintFailure

            return callback
        
        with self.movie_context() as movie_gui:
            monkeypatch.setattr(movie_gui, 'callback', dummy_callback())
            messagebox = TkMessagebox()
            monkeypatch.setattr(guiwidgets, 'messagebox', messagebox)
            movie_gui.commit()
            assert messagebox.showinfo_calls == [dict(
                    parent=DummyTk(), message='Database constraint failure.',
                    detail='A movie with this title and year is already present in the database.')]

    def test_commit_calls_destroy(self, patch_tk, monkeypatch):
        calls = []
        with self.movie_context() as movie_gui:
            monkeypatch.setattr(movie_gui, 'callback', lambda *args: None)
            monkeypatch.setattr(movie_gui, 'destroy', lambda *args: calls.append(True))
            movie_gui.commit()
            assert calls == [True]

    def test_treeview_callback(self, patch_tk):
        sentinel = object()
        with self.movie_context() as movie_gui:
            movie_gui.treeview_callback([sentinel])
            assert movie_gui.selected_tags == [sentinel]

    def test_destroy_method(self, patch_tk):
        with self.movie_context() as movie_gui:
            movie_gui.destroy()
            assert movie_gui.outer_frame.destroy_calls[0]

    # noinspection PyMissingOrEmptyDocstring
    @contextmanager
    def movie_context(self):
        global treeview_call
        treeview_call = []
        tags = ('test tag 1', 'test tag 2')
        # noinspection PyTypeChecker
        yield guiwidgets.AddMovieGUI(DummyTk(), all_tags=tags,
                                     callback=movie_gui_callback)


# noinspection PyMissingOrEmptyDocstring
class TestEditMovieGUI:
    
    def test_tree_selection_add(self, patch_tk, class_fixtures):
        with self.movie_context() as movie_gui:
            outerframe = movie_gui.parent.children[0]
            bodyframe = outerframe.children[0]
            tags_frame = bodyframe.children[-1]
            tree = tags_frame.children[0]
            assert tree.selection_add_calls == [(('test selected tag',),)]
    
    def test_entry_field_original_value_set(self, patch_tk, class_fixtures):
        with self.movie_context() as movie_gui:
            expected = dict(title='Test Movie', year=2050, director='Test Director', minutes=142,
                            notes='Test note')
            original_values = {field_name: movie_gui.entry_fields[field_name].original_value
                               for field_name in movie_gui.entry_fields}
            assert original_values == expected
    
    def test_text_variable_set_called(self, patch_tk, class_fixtures):
        with self.movie_context() as movie_gui:
            expected = dict(title='Test Movie', year=2050, director='Test Director', minutes=142,
                            notes='Test note')
            # The code initializes some textvariable values to a non space value (in [0]). This test
            # requires the latest and final entry (in [-1])
            original_values = {
                    field_name: movie_gui.entry_fields[field_name].textvariable.set_calls[-1][0]
                    for field_name in movie_gui.entry_fields}
            assert original_values == expected
    
    def test_neuron_linker_called(self, patch_tk, class_fixtures):
        with self.movie_context() as movie_gui:
            internal_names = []
            neurons = []
            callbacks = []
            initial_values = []
            for link in self.neuron_linker_args:
                try:
                    _, internal_name, neuron, callback = link
                except ValueError:
                    _, internal_name, neuron, callback, initial_value = link
                    initial_values.append(initial_value)
                internal_names.append(internal_name)
                callbacks.append(callback)
                neurons.append(neuron)

            assert internal_names == ['title', 'year', 'director', 'minutes', 'notes']
            for neuron in neurons:
                assert isinstance(neuron, guiwidgets.neurons.OrNeuron)
            for callback in callbacks:
                assert callback == movie_gui.neuron_callback
            assert initial_values == []

    def test_treeview_observer_registered(self, patch_tk, class_fixtures):
        self.tag_treeview_observer_args = []
        with self.movie_context():
            for args in self.tag_treeview_observer_args:
                assert isinstance(args[1], Callable)
        assert len(self.tag_treeview_observer_args) == 2

    def test_observer_notified(self, patch_tk, monkeypatch):
        notify_calls = []
    
        def dummy_notify(*args):
            notify_calls.append(args[1:])
    
        monkeypatch.setattr(guiwidgets.neurons.Observer, 'notify', dummy_notify)
        with self.movie_context() as movie_gui:
            outerframe = movie_gui.parent.children[0]
            bodyframe = outerframe.children[0]
            tags_frame = bodyframe.children[-1]
            tree = tags_frame.children[0]
            tree.bind_calls[0][1]['func']()
            assert notify_calls[0] == (guiwidgets.TAG_TREEVIEW_INTERNAL_NAME, True)

    # noinspection PyMissingOrEmptyDocstring
    @contextmanager
    def movie_context(self):
        self.neuron_linker_args = []
        all_tag_names = ('test tag 1', 'test tag 2')
        movie = guiwidgets.config.MovieUpdateDef(title='Test Movie', year=2050,
                                                 director='Test Director', minutes=142,
                                                 notes='Test note', tags=('test selected tag',))
        # noinspection PyTypeChecker
        yield guiwidgets.EditMovieGUI(DummyTk(), all_tag_names, movie_gui_callback, movie)

    neuron_linker_args = []
    tag_treeview_observer_args = []

    @pytest.fixture
    def class_fixtures(self, monkeypatch):
        monkeypatch.setattr(guiwidgets.MovieGUIBase, 'neuron_linker',
                            lambda *args: self.neuron_linker_args.append(args))
        monkeypatch.setattr(guiwidgets.MovieGUIBase.tag_treeview_observer, 'register',
                            lambda *args: self.tag_treeview_observer_args.append(args))


# noinspection PyMissingOrEmptyDocstring
class TestSearchMovieGUI:
    
    # Test Basic Initialization
    
    def test_parent_initialized(self, patch_tk):
        with self.movie_context() as movie_gui:
            assert movie_gui.parent == DummyTk()
            assert movie_gui.all_tags == ('test tag 1', 'test tag 2')
            assert isinstance(movie_gui.callback, Callable)
    
    # Test create body
    
    def test_create_simple_body_item_called(self, patch_tk, monkeypatch):
        calls = []
        monkeypatch.setattr(guiwidgets.SearchMovieGUI, 'create_body_item',
                            lambda *args: calls.append(args))
        with self.movie_context() as movie_gui:
            assert calls == [(movie_gui, TtkFrame(parent=TtkFrame(parent=DummyTk(), padding=''),
                                                  padding=(10, 25, 10, 0)), 'title', 'Title', 0),
                             (movie_gui, TtkFrame(parent=TtkFrame(parent=DummyTk(), padding=''),
                                                  padding=(10, 25, 10, 0)), 'director', 'Director', 2),
                             (movie_gui, TtkFrame(parent=TtkFrame(parent=DummyTk(), padding=''),
                                                  padding=(10, 25, 10, 0)), 'notes', 'Notes', 4), ]
    
    def test_create_min_max_body_item_called(self, patch_tk, monkeypatch):
        calls = []
        monkeypatch.setattr(guiwidgets.SearchMovieGUI, 'create_min_max_body_item',
                            lambda *args: calls.append(args))
        with self.movie_context() as movie_gui:
            assert calls == [(movie_gui, TtkFrame(parent=TtkFrame(parent=DummyTk(), padding=''),
                                                  padding=(10, 25, 10, 0)), 'year', 'Year', 1),
                             (movie_gui, TtkFrame(parent=TtkFrame(parent=DummyTk(), padding=''),
                                                  padding=(10, 25, 10, 0)), 'minutes',
                              'Length (minutes)', 3), ]

    def test_create_tag_treeview_called(self, patch_tk, patch_movie_treeview):
        with self.movie_context():
            assert treeview_call[0][1] == guiwidgets.TAG_TREEVIEW_INTERNAL_NAME
            assert treeview_call[0][2] == TtkFrame(parent=TtkFrame(parent=DummyTk(),
                                                                   padding=''), padding=(10, 25, 10, 0))
            assert treeview_call[0][3] == 5
            assert treeview_call[0][4] == 0
            assert treeview_call[0][5] == 'Select tags'
            assert treeview_call[0][6] == ('test tag 1', 'test tag 2')
            assert treeview_call[0][7]('test signal') == 'test signal'

    def test_treeview_observer_registered(self, patch_tk, monkeypatch):
        self.tag_treeview_observer_args = []
        monkeypatch.setattr(guiwidgets.MovieGUIBase.tag_treeview_observer, 'register',
                            lambda *args: self.tag_treeview_observer_args.append(args))
        with self.movie_context():
            for args in self.tag_treeview_observer_args:
                assert isinstance(args[1], Callable)
        assert len(self.tag_treeview_observer_args) == 2

    # Test create body item

    def test_body_item_ttk_label_called(self, patch_tk):
        with self.movie_context() as movie_gui:
            outerframe = movie_gui.parent.children[0]
            body_frame = outerframe.children[0]
            first_label = body_frame.children[0]
            assert first_label == TtkLabel(parent=TtkFrame(parent=TtkFrame(parent=DummyTk(), padding=''),
                                                           padding=(10, 25, 10, 0)),
                                           text='Title', padding='')
    
    def test_body_item_ttk_label_gridded(self, patch_tk):
        with self.movie_context() as movie_gui:
            outerframe = movie_gui.parent.children[0]
            body_frame = outerframe.children[0]
            first_label = body_frame.children[0]
            assert first_label.grid_calls == [dict(column=0, padx=5, row=0, sticky='e')]
    
    def test_body_item_create_entry_called(self, patch_tk, monkeypatch):
        calls = []
        monkeypatch.setattr(guiwidgets.SearchMovieGUI, 'create_entry',
                            lambda *args: calls.append(args))
        monkeypatch.setattr(guiwidgets.SearchMovieGUI, 'create_min_max_body_item', lambda *args: None)
        with self.movie_context() as movie_gui:
            assert calls == [(movie_gui, TtkFrame(parent=TtkFrame(parent=DummyTk(), padding=''),
                                                  padding=(10, 25, 10, 0)), 'title', 1, 0, 36),
                             (movie_gui, TtkFrame(parent=TtkFrame(parent=DummyTk(), padding=''),
                                                  padding=(10, 25, 10, 0)), 'director', 1, 2, 36),
                             (movie_gui, TtkFrame(parent=TtkFrame(parent=DummyTk(), padding=''),
                                                  padding=(10, 25, 10, 0)), 'notes', 1, 4, 36), ]
    
    # Test create min-max body item
    
    def test_min_max_body_item_ttk_label_called(self, patch_tk):
        with self.movie_context() as movie_gui:
            outerframe = movie_gui.parent.children[0]
            body_frame = outerframe.children[0]
            year_label = body_frame.children[2]
            assert year_label == TtkLabel(parent=TtkFrame(parent=TtkFrame(parent=DummyTk(), padding=''),
                                                          padding=(10, 25, 10, 0)),
                                          text='Year (min, max)', padding='')
    
    def test_min_max_body_item_ttk_label_gridded(self, patch_tk):
        with self.movie_context() as movie_gui:
            outerframe = movie_gui.parent.children[0]
            body_frame = outerframe.children[0]
            year_label = body_frame.children[2]
            assert year_label.grid_calls == [dict(column=0, padx=5, row=1, sticky='e')]
    
    def test_min_max_body_item_frame_created(self, patch_tk):
        with self.movie_context() as movie_gui:
            outerframe = movie_gui.parent.children[0]
            body_frame = outerframe.children[0]
            year_max_min_frame = body_frame.children[3]
            assert year_max_min_frame == TtkFrame(parent=TtkFrame(
                    parent=TtkFrame(parent=DummyTk(), padding=''),
                    padding=(10, 25, 10, 0)), padding=(2, 0))
    
    def test_min_max_body_item_frame_gridded(self, patch_tk):
        with self.movie_context() as movie_gui:
            outerframe = movie_gui.parent.children[0]
            body_frame = outerframe.children[0]
            year_max_min_frame = body_frame.children[3]
            assert year_max_min_frame.grid_calls == [dict(column=1, row=1, sticky='w')]
    
    def test_min_max_body_item_entries_created_and_gridded(self, patch_tk, monkeypatch):
        with self.movie_context() as movie_gui:
            outerframe = movie_gui.parent.children[0]
            body_frame = outerframe.children[0]
            year_max_min_frame = body_frame.children[3]
            assert year_max_min_frame.children[0].grid_calls == [dict(column=0, row=0)]
            assert year_max_min_frame.children[1].grid_calls == [dict(column=1, row=0)]
    
    def test_validate_int_registered(self, patch_tk, monkeypatch):
        with self.movie_context() as movie_gui:
            outerframe = movie_gui.parent.children[0]
            body_frame = outerframe.children[0]
            year_max_min_frame = body_frame.children[3]
            for child in range(2):
                calls = year_max_min_frame.children[child].register_calls
                assert calls == [(movie_gui.validate_int,)]
    
    def test_integer_validation_configured_upon_entry(self, patch_tk, monkeypatch):
        with self.movie_context() as movie_gui:
            outerframe = movie_gui.parent.children[0]
            body_frame = outerframe.children[0]
            year_max_min_frame = body_frame.children[3]
            assert year_max_min_frame.children[0].config_calls == [
                    dict(validate='key', validatecommand=('test registered_callback', '%S'))]
            assert year_max_min_frame.children[1].config_calls == [
                    dict(validate='key', validatecommand=('test registered_callback', '%S'))]
    
    # Test create entry
    
    def test_create_entry_creates_ttk_entry(self, patch_tk):
        with self.movie_context() as movie_gui:
            assert movie_gui.entry_fields['title'].widget == TtkEntry(parent=TtkFrame(
                    parent=TtkFrame(parent=DummyTk(), padding=''), padding=(10, 25, 10, 0)),
                    textvariable=TkStringVar(), width=36)
    
    def test_create_entry_grids_entry_widget(self, patch_tk):
        with self.movie_context() as movie_gui:
            assert movie_gui.entry_fields['title'].widget.grid_calls == [dict(column=1, row=0)]
    
    def test_create_entry_links_neuron(self, patch_tk, monkeypatch):
        calls = []
        monkeypatch.setattr(guiwidgets.SearchMovieGUI, 'neuron_linker', lambda *args: calls.append(args))
        with self.movie_context() as movie_gui:
            assert calls[0] == (movie_gui, 'title', movie_gui.search_neuron, movie_gui.neuron_callback)
    
    # Test create buttonbox
    
    def test_buttonbox_created(self, patch_tk):
        with self.movie_context() as movie_gui:
            outerframe = movie_gui.parent.children[0]
            buttonbox = outerframe.children[1]
            assert buttonbox == TtkFrame(parent=outerframe, padding=(5, 5, 10, 10))
    
    def test_buttonbox_gridded(self, patch_tk):
        with self.movie_context() as movie_gui:
            outerframe = movie_gui.parent.children[0]
            buttonbox = outerframe.children[1]
            assert buttonbox.grid_calls[0] == dict(column=0, row=1, sticky='e')
    
    def test_search_button_created(self, patch_tk):
        with self.movie_context() as movie_gui:
            button = movie_gui.parent.children[0].children[1].children[0]
            assert button == TtkButton(parent=TtkFrame(parent=TtkFrame(parent=DummyTk()),
                                                       padding=(5, 5, 10, 10)),
                                       text='Search', command=movie_gui.search)
    
    def test_search_button_gridded(self, patch_tk):
        with self.movie_context() as movie_gui:
            button = movie_gui.parent.children[0].children[1].children[0]
            assert button.grid_calls[0] == dict(column=0, row=0)
    
    # noinspection DuplicatedCode
    def test_search_button_bound(self, patch_tk):
        with self.movie_context() as movie_gui:
            button = movie_gui.parent.children[0].children[1].children[0]
            assert button.bind_calls[0][0] == '<Return>'
            button.bind_calls[0][1](button)
            assert button.invoke_calls[0]
    
    def test_search_button_state_set(self, patch_tk):
        with self.movie_context() as movie_gui:
            button = movie_gui.parent.children[0].children[1].children[0]
            assert button.state_calls[0][0] == 'disabled'
    
    # noinspection PyShadowingNames
    def test_neuron_register_called(self, patch_tk, monkeypatch):
        calls = []
        monkeypatch.setattr(guiwidgets.SearchMovieGUI, 'button_state_callback',
                            lambda movie_gui, button: calls.append(button, ))
        with self.movie_context() as movie_gui:
            button = movie_gui.parent.children[0].children[1].children[0]
            assert calls[0] == button
    
    def test_cancel_button_created(self, patch_tk, monkeypatch):
        calls = []
        monkeypatch.setattr(guiwidgets.SearchMovieGUI, 'create_cancel_button',
                            (lambda *args, **kwargs:
                             calls.append((args, kwargs))))
        with self.movie_context() as movie_gui:
            outerframe = movie_gui.parent.children[0]
            buttonbox = outerframe.children[1]
            assert calls == [((movie_gui, buttonbox), dict(column=1))]
    
    # Test search
    
    def test_callback_called(self, patch_tk):
        with self.movie_context() as movie_gui:
            movie_gui.selected_tags = ['tag 1', 'tag 2']
            movie_gui.search()
            assert callback_calls == [(dict(director='4242', minutes=['4242', '4242'], notes='4242',
                                            title='4242', year=['4242', '4242'], ), ['tag 1', 'tag 2'])]
    
    def test_callback_raises_movie_search_found_nothing(self, patch_tk, monkeypatch):
        # noinspection PyUnusedLocal
        def callback(*args):
            raise exception.MovieSearchFoundNothing

        messagebox_calls = []
        monkeypatch.setattr(guiwidgets, 'gui_messagebox', lambda *args: messagebox_calls.append(args))
        tags = []
        # noinspection PyTypeChecker
        movie_gui = guiwidgets.SearchMovieGUI(DummyTk(), tags, callback)
        movie_gui.search()
        assert messagebox_calls == [(DummyTk(), 'No matches',
                                     'There are no matching movies in the database.')]
    
    def test_destroy_called(self, patch_tk, monkeypatch):
        called = []
        monkeypatch.setattr(guiwidgets.MovieGUIBase, 'destroy', lambda *args: called.append(True))
        with self.movie_context() as movie_gui:
            movie_gui.search()
            assert called.pop()
    
    # noinspection PyMissingOrEmptyDocstring
    @contextmanager
    def movie_context(self):
        global treeview_call
        treeview_call = []
        tags = ('test tag 1', 'test tag 2')
        # noinspection PyTypeChecker
        yield guiwidgets.SearchMovieGUI(DummyTk(), tags, movie_gui_callback)


# noinspection PyMissingOrEmptyDocstring
class TestSelectMovieGUI:
    
    # Test Basic Initialization
    
    def test_parent_initialized(self, patch_tk):
        with self.select_movie_context() as movie_gui:
            assert movie_gui.parent == DummyTk()
            assert isinstance(movie_gui.callback, Callable)
    
    # Test Create Body
    
    def test_treeview_called(self, patch_tk):
        with self.select_movie_context() as movie_gui:
            outerframe = movie_gui.parent.children[0]
            bodyframe = outerframe.children[0]
            treeview = bodyframe.children[0]
            assert treeview == TtkTreeview(parent=TtkFrame(parent=TtkFrame(
                    parent=DummyTk(), padding=''), padding=(10, 25, 10, 0)),
                    columns=('year', 'director', 'minutes', 'notes'), height=25, selectmode='browse')
    
    def test_treeview_gridded(self, patch_tk):
        with self.select_movie_context() as movie_gui:
            outerframe = movie_gui.parent.children[0]
            bodyframe = outerframe.children[0]
            treeview = bodyframe.children[0]
            assert treeview.grid_calls == [dict(column=0, row=0, sticky='w')]
    
    def test_treeview_column_widths_set(self, patch_tk):
        with self.select_movie_context() as movie_gui:
            outerframe = movie_gui.parent.children[0]
            bodyframe = outerframe.children[0]
            treeview = bodyframe.children[0]
            assert treeview.column_calls == [(('#0',), dict(width=350)), (('year',), dict(width=50)),
                                             (('director',), dict(width=100)),
                                             (('minutes',), dict(width=50)),
                                             (('notes',), dict(width=350)), ]
    
    def test_treeview_column_headings_set(self, patch_tk):
        with self.select_movie_context() as movie_gui:
            outerframe = movie_gui.parent.children[0]
            bodyframe = outerframe.children[0]
            treeview = bodyframe.children[0]
            assert treeview.heading_calls == [(('#0',), dict(text='Title')),
                                              (('year',), dict(text='Year')),
                                              (('director',), dict(text='Director')),
                                              (('minutes',), dict(text='Length (minutes)')),
                                              (('notes',), dict(text='Notes')), ]
    
    def test_treeview_movies_inserted(self, patch_tk):
        with self.select_movie_context() as movie_gui:
            outerframe = movie_gui.parent.children[0]
            bodyframe = outerframe.children[0]
            treeview = bodyframe.children[0]
            assert treeview.insert_calls == [(('', 'end'),
                                              dict(iid="('Test Title', 2020)", tags='title',
                                                   text='Test Title',
                                                   values=(2020, 'Director', 200, 'NB')))]
    
    def test_treeview_binds_callback(self, patch_tk, monkeypatch):
        # noinspection PyUnusedLocal
        def selection(*args):
            return ["'Hello Mum, 1954'"]

        monkeypatch.setattr(TtkTreeview, 'selection', selection)
        with self.select_movie_context() as movie_gui:
            outerframe = movie_gui.parent.children[0]
            bodyframe = outerframe.children[0]
            treeview = bodyframe.children[0]
            assert treeview.bind_calls[0][0] == ('<<TreeviewSelect>>',)
    
            treeview.bind_calls[0][1]['func']()
            assert callback_calls[2] == ('Hello Mum', 1954)

    def test_widget_is_destroyed(self, patch_tk, monkeypatch):
        destroy_called = False
    
        def mock_destroy(*args):
            nonlocal destroy_called
            destroy_called = True
    
        def selection(*args):
            return ["'Hello Mum, 1954'"]
    
        monkeypatch.setattr(TtkTreeview, 'selection', selection)
        monkeypatch.setattr(guiwidgets.SelectMovieGUI, 'destroy', mock_destroy)
        with self.select_movie_context() as movie_gui:
            outerframe = movie_gui.parent.children[0]
            bodyframe = outerframe.children[0]
            treeview = bodyframe.children[0]
            _, kwargs = treeview.bind_calls[0]
            treeview.bind_calls[0][1]['func']()
            assert destroy_called

    # Test create buttonbox

    def test_buttonbox_created(self, patch_tk):
        with self.select_movie_context() as movie_gui:
            outerframe = movie_gui.parent.children[0]
            buttonbox = outerframe.children[1]
            assert buttonbox == TtkFrame(parent=outerframe, padding=(5, 5, 10, 10))

    def test_buttonbox_gridded(self, patch_tk):
        with self.select_movie_context() as movie_gui:
            outerframe = movie_gui.parent.children[0]
            buttonbox = outerframe.children[1]
            assert buttonbox.grid_calls[0] == dict(column=0, row=1, sticky='e')

    def test_cancel_button_created(self, patch_tk, monkeypatch):
        create_cancel_button_calls = []
        monkeypatch.setattr(guiwidgets.MovieGUIBase, 'create_cancel_button',
                            lambda *args, **kwargs: create_cancel_button_calls.append((args, kwargs)))
        with self.select_movie_context() as movie_gui:
            outerframe = movie_gui.parent.children[0]
            buttonbox = outerframe.children[1]
            assert create_cancel_button_calls[0][0][1] == buttonbox
            assert create_cancel_button_calls[0][1] == dict(column=0)

    # Class Support Methods

    @staticmethod
    def fake_movie_generator():
        yield dict(title='Test Title', year=2020, director='Director', minutes=200, notes='NB')

    # noinspection PyMissingOrEmptyDocstring
    @contextmanager
    def select_movie_context(self):
        # noinspection PyTypeChecker
        yield guiwidgets.SelectMovieGUI(DummyTk(), self.fake_movie_generator(), movie_gui_callback)


def test_gui_messagebox(monkeypatch):
    calls = []
    monkeypatch.setattr(guiwidgets.messagebox, 'showinfo',
                        lambda *args, **kwargs: calls.append((args, kwargs)))
    parent = DummyTk()
    message = 'test message'
    detail = 'test detail'
    # noinspection PyTypeChecker
    guiwidgets.gui_messagebox(parent, message, detail)
    assert calls == [((parent, message),
                      dict(detail=detail, icon='info'))]


def test_gui_askopenfilename(monkeypatch):
    calls = []
    monkeypatch.setattr(guiwidgets.filedialog, 'askopenfilename', lambda **kwargs: calls.append(kwargs))
    parent = DummyTk()
    filetypes = (('test filetypes',),)
    # noinspection PyTypeChecker
    guiwidgets.gui_askopenfilename(parent, filetypes)
    assert calls == [(dict(parent=parent, filetypes=filetypes))]


# noinspection PyMissingOrEmptyDocstring
@dataclass
class DummyTk:
    """Test dummy for Tk.

    The dummy Tk/Ttk classes need to mimic Tk's parent/child structure as explicit references are
    missing in the source code."""
    children: list = field(default_factory=list, init=False, repr=False, compare=False)
    
    columnconfigure_calls: list = field(default_factory=list, init=False, repr=False, compare=False)
    rowconfigure_calls: list = field(default_factory=list, init=False, repr=False, compare=False)
    bind_calls: list = field(default_factory=list, init=False, repr=False, compare=False)
    bell_calls: list = field(default_factory=list, init=False, repr=False, compare=False)

    def columnconfigure(self, *args, **kwargs):
        self.columnconfigure_calls.append((args, kwargs))

    def rowconfigure(self, *args, **kwargs):
        self.rowconfigure_calls.append((args, kwargs))

    def bind(self, *args, **kwargs):
        self.bind_calls.append((args, kwargs))

    def bell(self):
        self.bell_calls.append(True)


# noinspection PyMissingOrEmptyDocstring
@dataclass
class TkStringVar:
    trace_add_calls: list = field(default_factory=list, init=False, repr=False, compare=False)
    set_calls: list = field(default_factory=list, init=False, repr=False, compare=False)
    
    def trace_add(self, *args):
        self.trace_add_calls.append(args)
    
    def set(self, *args):
        self.set_calls.append(args)
    
    @staticmethod
    def get():
        return '4242'


# noinspection PyMissingOrEmptyDocstring
@dataclass
class TtkFrame:
    """Test dummy for Ttk.Frame.

    The dummy Tk/Ttk classes need to mimic Tk's parent/child structure as explicit references are
    missing in the source code.
    """
    parent: Union[DummyTk, 'TtkFrame']
    padding: Union[int, Tuple[int, ...], str] = field(default='')
    
    children: list = field(default_factory=list, init=False, repr=False, compare=False)
    grid_calls: list = field(default_factory=list, init=False, repr=False, compare=False)
    columnconfigure_calls: list = field(default_factory=list, init=False, repr=False, compare=False)
    rowconfigure_calls: list = field(default_factory=list, init=False, repr=False, compare=False)
    destroy_calls: list = field(default_factory=list, init=False, repr=False, compare=False)
    
    def __post_init__(self):
        self.parent.children.append(self)
    
    def grid(self, **kwargs):
        self.grid_calls.append(kwargs)
    
    def columnconfigure(self, *args, **kwargs):
        self.columnconfigure_calls.append((args, kwargs))
    
    def rowconfigure(self, *args, **kwargs):
        self.rowconfigure_calls.append((args, kwargs))
    
    def destroy(self):
        self.destroy_calls.append(True)


# noinspection PyMissingOrEmptyDocstring
@dataclass
class TtkLabel:
    """Test dummy for Ttk.Label.

    The dummy Tk/Ttk classes need to mimic Tk's parent/child structure as explicit references are
    missing in the source code.
    """
    parent: TtkFrame
    text: str
    padding: Union[int, Tuple[int, ...], str] = field(default='')
    
    grid_calls: list = field(default_factory=list, init=False, repr=False, compare=False)
    
    def __post_init__(self):
        self.parent.children.append(self)
    
    def grid(self, **kwargs):
        self.grid_calls.append(kwargs)


# noinspection PyMissingOrEmptyDocstring
@dataclass
class TtkEntry:
    """Test dummy for Ttk.Entry.

    The dummy Tk/Ttk classes need to mimic Tk's parent/child structure as explicit references are
    missing in the source code.
    """
    parent: TtkFrame
    textvariable: TkStringVar = None
    width: int = None
    
    grid_calls: list = field(default_factory=list, init=False, repr=False, compare=False)
    config_calls: list = field(default_factory=list, init=False, repr=False, compare=False)
    register_calls: list = field(default_factory=list, init=False, repr=False, compare=False)

    def __post_init__(self):
        self.parent.children.append(self)

    def grid(self, **kwargs):
        self.grid_calls.append(kwargs)

    def config(self, **kwargs):
        self.config_calls.append(kwargs)

    def register(self, *args):
        self.register_calls.append(args)
        return 'test registered_callback'


# noinspection PyMissingOrEmptyDocstring
@dataclass
class TtkButton:
    parent: TtkFrame
    text: str
    command: Callable = None
    
    grid_calls: list = field(default_factory=list, init=False, repr=False, compare=False)
    bind_calls: list = field(default_factory=list, init=False, repr=False, compare=False)
    state_calls: list = field(default_factory=list, init=False, repr=False, compare=False)
    focus_set_calls: list = field(default_factory=list, init=False, repr=False, compare=False)
    invoke_calls: list = field(default_factory=list, init=False, repr=False, compare=False)
    
    def __post_init__(self):
        self.parent.children.append(self)
    
    def grid(self, **kwargs):
        self.grid_calls.append(kwargs, )
    
    def bind(self, *args):
        self.bind_calls.append(args, )

    def state(self, state):
        self.state_calls.append(state)

    def focus_set(self):
        self.focus_set_calls.append(True)

    def invoke(self):
        self.invoke_calls.append(True)


# noinspection PyMissingOrEmptyDocstring
@dataclass
class TtkTreeview:
    parent: TtkFrame
    columns: Sequence[str]
    height: int
    selectmode: str
    
    show: str = field(default='tree headings')
    padding: int = field(default=0)
    
    grid_calls: list = field(default_factory=list, init=False, repr=False, compare=False)
    column_calls: list = field(default_factory=list, init=False, repr=False, compare=False)
    heading_calls: list = field(default_factory=list, init=False, repr=False, compare=False)
    insert_calls: list = field(default_factory=list, init=False, repr=False, compare=False)
    bind_calls: list = field(default_factory=list, init=False, repr=False, compare=False)
    yview_calls: list = field(default_factory=list, init=False, repr=False, compare=False)
    configure_calls: list = field(default_factory=list, init=False, repr=False, compare=False)
    selection_add_calls: list = field(default_factory=list, init=False, repr=False, compare=False)
    
    def __post_init__(self):
        self.parent.children.append(self)
    
    def grid(self, **kwargs):
        self.grid_calls.append(kwargs, )

    def column(self, *args, **kwargs):
        self.column_calls.append((args, kwargs))

    def heading(self, *args, **kwargs):
        self.heading_calls.append((args, kwargs))

    def insert(self, *args, **kwargs):
        self.insert_calls.append((args, kwargs))

    def bind(self, *args, **kwargs):
        self.bind_calls.append((args, kwargs))

    def yview(self, *args, **kwargs):
        self.yview_calls.append((args, kwargs))

    def selection_add(self, *args):
        self.selection_add_calls.append(args)

    def configure(self, **kwargs):
        self.configure_calls.append(kwargs)

    @staticmethod
    def selection():
        return ['test tag 1', 'test tag 2']


# noinspection PyMissingOrEmptyDocstring
@dataclass
class TtkScrollbar:
    parent: TtkFrame
    orient: str
    command: Callable
    
    set_calls: list = field(default_factory=list, init=False, repr=False, compare=False)
    grid_calls: list = field(default_factory=list, init=False, repr=False, compare=False)

    def __post_init__(self):
        self.parent.children.append(self)

    def set(self, *args, **kwargs):
        self.set_calls.append((args, kwargs))

    def grid(self, **kwargs):
        self.grid_calls.append(kwargs)


# noinspection PyMissingOrEmptyDocstring
@dataclass
class TkMessagebox:
    showinfo_calls: list = field(default_factory=list, init=False, repr=False, compare=False)
    
    def showinfo(self, **kwargs):
        self.showinfo_calls.append(kwargs)


# noinspection PyMissingOrEmptyDocstring
@pytest.fixture()
def patch_tk(monkeypatch):
    monkeypatch.setattr(guiwidgets.tk, 'Tk', DummyTk)
    monkeypatch.setattr(guiwidgets.tk, 'StringVar', TkStringVar)
    monkeypatch.setattr(guiwidgets.ttk, 'Frame', TtkFrame)
    monkeypatch.setattr(guiwidgets.ttk, 'Label', TtkLabel)
    monkeypatch.setattr(guiwidgets.ttk, 'Entry', TtkEntry)
    monkeypatch.setattr(guiwidgets.ttk, 'Button', TtkButton)
    monkeypatch.setattr(guiwidgets.ttk, 'Treeview', TtkTreeview)
    monkeypatch.setattr(guiwidgets.ttk, 'Scrollbar', TtkScrollbar)


treeview_call = []


# noinspection PyMissingOrEmptyDocstring
@dataclass
class DummyTreeview:
    internal_name: str
    body_frame: TtkFrame
    row: int
    column: int
    label_text: str
    items: Sequence[str]
    user_callback: Callable
    
    initial_selection: Sequence[str] = field(default_factory=tuple)
    
    def __call__(self):
        self.user_callback = self.treeview_callback()
        treeview_call.append((self, self.internal_name, self.body_frame, self.row, self.column,
                              self.label_text, self.items,
                              self.user_callback))
        return guiwidgets.neurons.Observer()
    
    @staticmethod
    def treeview_callback():
        def update_tag_selection(test_token):
            return test_token
        
        return update_tag_selection


# noinspection PyMissingOrEmptyDocstring
@pytest.fixture()
def patch_movie_treeview(monkeypatch):
    monkeypatch.setattr(guiwidgets, 'MovieTreeview', DummyTreeview)


callback_calls = []


# noinspection PyUnusedLocal,PyMissingOrEmptyDocstring
def movie_gui_callback(movie_dict: guiwidgets.config.MovieDef, tags: Sequence[str]):
    callback_calls.append((movie_dict, tags))
