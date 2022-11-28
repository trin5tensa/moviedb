"""Test module."""

#  Copyright (c) 2022-2022. Stephen Rigden.
#  Last modified 11/28/22, 2:31 PM by stephen.
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
from dataclasses import dataclass, field
from typing import Callable, Sequence

import pytest

import exception
import guiwidgets
from test.dummytk import DummyTk, TkStringVar, TtkButton, TtkEntry, TtkFrame, TtkLabel


# noinspection PyMissingOrEmptyDocstring
class TestEditMovieGUI:
    
    def test_delete_button_created(self, patch_tk, class_fixtures):
        with self.movie_context() as movie_gui:
            button = movie_gui.parent.children[0].children[1].children[1]
            assert button == TtkButton(parent=TtkFrame(parent=TtkFrame(parent=DummyTk()),
                                                       padding=(5, 5, 10, 10)),
                                       text='Delete', command=movie_gui.delete)
    
    def test_delete_button_gridded(self, patch_tk, class_fixtures):
        with self.movie_context() as movie_gui:
            button = movie_gui.parent.children[0].children[1].children[1]
            assert button.grid_calls[0] == dict(column=1, row=0)
    
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
    
    def test_delete_calls_askyesno_dialog(self, patch_tk, monkeypatch):
        calls = []
        with self.movie_context() as movie_gui:
            monkeypatch.setattr(guiwidgets.messagebox, 'askyesno',
                                lambda **kwargs: calls.append(kwargs))
            monkeypatch.setattr(movie_gui, 'delete_callback', lambda movie: None)
            monkeypatch.setattr(movie_gui, 'destroy', lambda: None)
            guiwidgets.CommonButtonbox.delete(movie_gui)
            assert calls == [dict(message='Do you want to delete this movie?',
                                  icon='question', default='no', parent=DummyTk())]
    
    def test_delete_callback_method(self, patch_tk, monkeypatch):
        calls = []
        with self.movie_context() as movie_gui:
            monkeypatch.setattr(guiwidgets.messagebox, 'askyesno', lambda **kwargs: True)
            monkeypatch.setattr(movie_gui, 'delete_callback', lambda movie: calls.append(movie))
            monkeypatch.setattr(movie_gui, 'destroy', lambda: None)
            movie_gui.delete()
            assert calls == [dict(title='Test Movie', year=2050)]
    
    def test_delete_calls_destroy(self, patch_tk, monkeypatch):
        calls = []
        with self.movie_context() as movie_gui:
            monkeypatch.setattr(guiwidgets.messagebox, 'askyesno', lambda **kwargs: True)
            monkeypatch.setattr(movie_gui, 'delete_callback', lambda movie: None)
            monkeypatch.setattr(movie_gui, 'destroy', lambda: calls.append(True))
            movie_gui.delete()
            assert calls == [True]
    
    def test_focus_set_on_title_field(self, patch_tk, monkeypatch):
        calls = []
        monkeypatch.setattr(guiwidgets, '_focus_set', lambda *args: calls.append(args))
        with self.movie_context():
            trace_add_callback = calls[0][0].textvariable.trace_add_callback
            assert calls == [(TtkEntry(parent=TtkFrame(parent=TtkFrame(parent=DummyTk(), padding=''),
                                                       padding=(10, 25, 10, 0)),
                                       textvariable=TkStringVar(trace_add_callback=trace_add_callback), width=36),)]
    
    def test_focus_set_to_notes(self, patch_tk):
        with self.movie_context() as movie_gui:
            assert movie_gui.entry_fields['notes'].widget.focus_set_calls == [True]
    
    def test_all_notes_test_selected(self, patch_tk):
        with self.movie_context() as movie_gui:
            assert movie_gui.entry_fields['notes'].widget.select_range_calls == [(0, 'end')]
    
    def test_cursor_placed_at_end_of_notes_entry(self, patch_tk):
        with self.movie_context() as movie_gui:
            assert movie_gui.entry_fields['notes'].widget.icursor_calls == [('end',)]
    
    # noinspection PyMissingOrEmptyDocstring
    @contextmanager
    def movie_context(self):
        self.neuron_linker_args = []
        all_tag_names = ('test tag 1', 'test tag 2')
        movie = guiwidgets.config.MovieUpdateDef(title='Test Movie', year=2050,
                                                 director='Test Director', minutes=142,
                                                 notes='Test note', tags=('test selected tag',))
        # noinspection PyTypeChecker
        yield guiwidgets.EditMovieGUI(DummyTk(), dummy_commit_callback, dummy_delete_callback,
                                      ['commit', 'delete'], all_tag_names, movie)
    
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
        monkeypatch.setattr(guiwidgets, '_focus_set', lambda *args: None)
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
    
    def test_focus_set_called(self, patch_tk, monkeypatch):
        calls = []
        monkeypatch.setattr(guiwidgets, '_focus_set', lambda *args: calls.append(True))
        with self.movie_context():
            assert calls == [True]
    
    # noinspection DuplicatedCode
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
    
    # noinspection PyShadowingNames
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
        monkeypatch.setattr(guiwidgets, '_focus_set', lambda *args: None)
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
            trace_add_callback = movie_gui.entry_fields['title'].widget.textvariable.trace_add_callback
            assert movie_gui.entry_fields['title'].widget == TtkEntry(parent=TtkFrame(
                    parent=TtkFrame(parent=DummyTk(), padding=''), padding=(10, 25, 10, 0)),
                    textvariable=TkStringVar(trace_add_callback=trace_add_callback), width=36)
    
    def test_create_entry_grids_entry_widget(self, patch_tk):
        with self.movie_context() as movie_gui:
            assert movie_gui.entry_fields['title'].widget.grid_calls == [dict(column=1, row=0)]
    
    def test_create_entry_links_neuron(self, patch_tk, monkeypatch):
        calls = []
        monkeypatch.setattr(guiwidgets.SearchMovieGUI, 'neuron_linker', lambda *args: calls.append(args))
        with self.movie_context() as movie_gui:
            assert calls[0] == (movie_gui, 'title',
                                movie_gui.search_button_neuron, movie_gui.neuron_callback)
    
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
    
    # @pytest.mark.skip('Test dependency discovered')
    # def test_callback_called(self, patch_tk):
    #     with self.movie_context() as movie_gui:
    #         movie_gui.selected_tags = ['tag 1', 'tag 2']
    #         movie_gui.search()
    #         assert commit_callback_calls == [(dict(director='4242', minutes=['4242', '4242'],
    #                                                notes='4242', title='4242', year=['4242', '4242'], ),
    #                                           ['tag 1', 'tag 2'])]
    
    def test_callback_raises_movie_search_found_nothing(self, patch_tk, monkeypatch):
        # noinspection PyUnusedLocal
        def callback(*args):
            raise exception.DatabaseSearchFoundNothing
        
        messagebox_calls = []
        monkeypatch.setattr(guiwidgets, 'gui_messagebox', lambda *args: messagebox_calls.append(args))
        tags = []
        # noinspection PyTypeChecker
        movie_gui = guiwidgets.SearchMovieGUI(DummyTk(), callback, tags)
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
        yield guiwidgets.SearchMovieGUI(DummyTk(), dummy_commit_callback, tags)


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
    
    # @pytest.mark.skip('Test dependency discovered')
    # def test_treeview_binds_callback(self, patch_tk, monkeypatch):
    #     # noinspection PyUnusedLocal
    #     def selection(*args):
    #         return ["'\'Hello Mum\', 1954'"]
    #
    #     monkeypatch.setattr(TtkTreeview, 'selection', selection)
    #     with self.select_movie_context() as movie_gui:
    #         outerframe = movie_gui.parent.children[0]
    #         bodyframe = outerframe.children[0]
    #         treeview = bodyframe.children[0]
    #         assert treeview.bind_calls[0][0] == ('<<TreeviewSelect>>',)
    #
    #         treeview.bind_calls[0][1]['func']()
    #         assert commit_callback_calls[2] == ('Hello Mum', 1954)
    
    def test_widget_is_destroyed(self, patch_tk, monkeypatch):
        destroy_called = False
        
        # noinspection PyUnusedLocal
        def mock_destroy(*args):
            nonlocal destroy_called
            destroy_called = True
        
        # noinspection PyUnusedLocal
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
        yield guiwidgets.SelectMovieGUI(DummyTk(), self.fake_movie_generator(), dummy_commit_callback)


# noinspection PyMissingOrEmptyDocstring,DuplicatedCode
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


# noinspection PyMissingOrEmptyDocstring,DuplicatedCode
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


# noinspection PyMissingOrEmptyDocstring,DuplicatedCode
@dataclass
class TkMessagebox:
    """A test double for Tk.Messagebox."""
    showinfo_calls: list = field(default_factory=list, init=False, repr=False, compare=False)
    
    def showinfo(self, **kwargs):
        self.showinfo_calls.append(kwargs)


# noinspection PyMissingOrEmptyDocstring,DuplicatedCode
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


commit_callback_calls = []


# noinspection PyUnusedLocal,PyMissingOrEmptyDocstring
def dummy_commit_callback(movie_dict: guiwidgets.config.MovieTypedDict, tags: Sequence[str]):
    commit_callback_calls.append((movie_dict, tags))


delete_callback_calls = []


# noinspection PyUnusedLocal,PyMissingOrEmptyDocstring
def dummy_delete_callback(movie_dict: guiwidgets.config.MovieTypedDict, tags: Sequence[str]):
    delete_callback_calls.append((movie_dict, tags))
