"""Test module."""

#  Copyright© 2020. Stephen Rigden.
#  Last modified 1/1/20, 8:57 AM by stephen.
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
class TestMovieGUI:
    
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
    
    def test_minutes_initialized_to_0(self, patch_tk):
        with self.movie_context() as movie_gui:
            assert movie_gui.entry_fields['minutes'].textvariable.set_calls[0][0] == '0'
    
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
            assert label[0].grid_calls[0] == dict(column=0, row=6, sticky='ne', padx=5)
    
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
            assert bodyframe.children[-1].grid_calls[0] == dict(column=1, row=6, sticky='w')
    
    def test_tree_created(self, patch_tk):
        with self.movie_context() as movie_gui:
            outerframe = movie_gui.parent.children[0]
            bodyframe = outerframe.children[0]
            tags_frame = bodyframe.children[-1]
            assert tags_frame.children[0] == TtkTreeview(parent=TtkFrame(parent=TtkFrame(
                    parent=TtkFrame(parent=DummyTk()), padding=(10, 25, 10, 0)), padding=5),
                    columns=('tags',), height=5, selectmode='extended', show='tree', padding=5)
    
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
    
    def test_tree_insert(self, patch_tk):
        with self.movie_context() as movie_gui:
            outerframe = movie_gui.parent.children[0]
            bodyframe = outerframe.children[0]
            tags_frame = bodyframe.children[-1]
            tree = tags_frame.children[0]
            assert tree.insert_calls == [(('', 'end', tag), dict(text=tag, tags='tags'))
                                         for tag in movie_gui.tags]
    
    def test_tree_tag_bind(self, patch_tk):
        with self.movie_context() as movie_gui:
            outerframe = movie_gui.parent.children[0]
            bodyframe = outerframe.children[0]
            tags_frame = bodyframe.children[-1]
            tree = tags_frame.children[0]
            assert tree.tag_bind_calls[0][0] == ('tags', '<<TreeviewSelect>>')
            
            tree.tag_bind_calls[0][1]['callback']()
            assert movie_gui.selected_tags == ['test tag 1', 'test tag 2']
    
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
        monkeypatch.setattr(guiwidgets.MovieGUI, 'neuron_linker',
                            lambda *args: calls.append(args))
        with self.movie_context() as movie_gui:
            assert calls == [
                    (movie_gui, 'title', movie_gui.commit_neuron, movie_gui.neuron_callback),
                    (movie_gui, 'year', movie_gui.commit_neuron, movie_gui.neuron_callback, True)]
    
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
        monkeypatch.setattr(guiwidgets.MovieGUI, 'button_state_callback',
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
        monkeypatch.setattr(guiwidgets.MovieGUI, 'neuron_callback',
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
    
    def test_button_state_callback(self, patch_tk):
        with self.movie_context() as movie_gui:
            commit = movie_gui.parent.children[0].children[1].children[0]
            movie_gui.button_state_callback(commit)(True)
            assert commit.state_calls == [['disabled'], ['!disabled']]
    
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
                    detail='This title and year are already present in the database.')]
    
    def test_commit_calls_destroy(self, patch_tk, monkeypatch):
        calls = []
        with self.movie_context() as movie_gui:
            monkeypatch.setattr(movie_gui, 'callback', lambda *args: None)
            monkeypatch.setattr(movie_gui, 'destroy', lambda *args: calls.append(True))
            movie_gui.commit()
            assert calls == [True]
    
    def test_destroy_method(self, patch_tk):
        with self.movie_context() as movie_gui:
            movie_gui.destroy()
            assert movie_gui.outer_frame.destroy_calls[0]
    
    # noinspection PyMissingOrEmptyDocstring
    @contextmanager
    def movie_context(self):
        tags = ('test tag 1', 'test tag 2')
        # noinspection PyTypeChecker
        yield guiwidgets.MovieGUI(DummyTk(), tags, movie_gui_callback)


# noinspection PyMissingOrEmptyDocstring
class TestSearchGUI:
    
    # Test Basic Initialization
    
    def test_parent_initialized(self, patch_tk):
        with self.movie_context() as movie_gui:
            assert movie_gui.parent == DummyTk()
            assert movie_gui.tags == ('test tag 1', 'test tag 2')
            assert isinstance(movie_gui.callback, Callable)
    
    # Test create body
    
    def test_create_simple_body_item_called(self, patch_tk, monkeypatch):
        calls = []
        monkeypatch.setattr(guiwidgets.SearchGUI, 'create_body_item',
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
        monkeypatch.setattr(guiwidgets.SearchGUI, 'create_min_max_body_item',
                            lambda *args: calls.append(args))
        with self.movie_context() as movie_gui:
            assert calls == [(movie_gui, TtkFrame(parent=TtkFrame(parent=DummyTk(), padding=''),
                                                  padding=(10, 25, 10, 0)), 'year', 'Year', 1),
                             (movie_gui, TtkFrame(parent=TtkFrame(parent=DummyTk(), padding=''),
                                                  padding=(10, 25, 10, 0)), 'minutes',
                              'Length (minutes)', 3), ]
    
    def test_create_tag_treeview_called(self, patch_tk, monkeypatch):
        calls = []
        monkeypatch.setattr(guiwidgets.SearchGUI, 'create_tag_treeview',
                            lambda *args: calls.append(args))
        with self.movie_context() as movie_gui:
            assert calls == [(movie_gui, TtkFrame(parent=TtkFrame(parent=DummyTk(), padding=''),
                                                  padding=(10, 25, 10, 0)), 5), ]
    
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
        monkeypatch.setattr(guiwidgets.SearchGUI, 'create_entry',
                            lambda *args: calls.append(args))
        monkeypatch.setattr(guiwidgets.SearchGUI, 'create_min_max_body_item', lambda *args: None)
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
        monkeypatch.setattr(guiwidgets.SearchGUI, 'neuron_linker', lambda *args: calls.append(args))
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
        monkeypatch.setattr(guiwidgets.SearchGUI, 'button_state_callback',
                            lambda movie_gui, button: calls.append(button, ))
        with self.movie_context() as movie_gui:
            button = movie_gui.parent.children[0].children[1].children[0]
            assert calls[0] == button
    
    def test_cancel_button_created(self, patch_tk, monkeypatch):
        calls = []
        monkeypatch.setattr(guiwidgets.SearchGUI, 'create_cancel_button',
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
        def callback(*args):
            raise exception.MovieSearchFoundNothing
    
        messagebox_calls = []
        monkeypatch.setattr(guiwidgets, 'gui_messagebox', lambda *args:
        messagebox_calls.append(args))
        tags = []
        movie_gui = guiwidgets.SearchGUI(DummyTk(), tags, callback)
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
        tags = ('test tag 1', 'test tag 2')
        # noinspection PyTypeChecker
        yield guiwidgets.SearchGUI(DummyTk(), tags, movie_gui_callback)


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
    show: str
    padding: int
    
    grid_calls: list = field(default_factory=list, init=False, repr=False, compare=False)
    column_calls: list = field(default_factory=list, init=False, repr=False, compare=False)
    insert_calls: list = field(default_factory=list, init=False, repr=False, compare=False)
    tag_bind_calls: list = field(default_factory=list, init=False, repr=False, compare=False)
    yview_calls: list = field(default_factory=list, init=False, repr=False, compare=False)
    configure_calls: list = field(default_factory=list, init=False, repr=False, compare=False)
    
    def __post_init__(self):
        self.parent.children.append(self)
    
    def grid(self, **kwargs):
        self.grid_calls.append(kwargs, )
    
    def column(self, *args, **kwargs):
        self.column_calls.append((args, kwargs))
    
    def insert(self, *args, **kwargs):
        self.insert_calls.append((args, kwargs))

    def tag_bind(self, *args, **kwargs):
        self.tag_bind_calls.append((args, kwargs))

    def yview(self, *args, **kwargs):
        self.yview_calls.append((args, kwargs))

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


callback_calls = []


# noinspection PyUnusedLocal,PyMissingOrEmptyDocstring
def movie_gui_callback(movie_dict: guiwidgets.MovieDict, tags: Sequence[str]):
    callback_calls.append((movie_dict, tags))
