"""Test module."""

#  Copyright© 2019. Stephen Rigden.
#  Last modified 12/3/19, 10:05 AM by stephen.
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
from typing import Callable, Tuple, Union

import pytest

import guiwidgets


class TestMovieInit:
    
    def test_parent_initialized(self, class_patches):
        with self.movie_context() as movie_gui:
            assert movie_gui.parent == DummyTk()
    
    def test_callback_initialized(self, class_patches):
        with self.movie_context() as movie_gui:
            assert movie_gui.callback == movie_gui_callback
    
    def test_fields_initialized(self, class_patches):
        with self.movie_context() as movie_gui:
            for internal_name in guiwidgets.INTERNAL_NAMES:
                assert isinstance(movie_gui.fields[internal_name], guiwidgets.MovieField)
    
    def test_fields_label_text(self, class_patches):
        with self.movie_context() as movie_gui:
            for internal_name, label_text in zip(guiwidgets.INTERNAL_NAMES, guiwidgets.FIELD_TEXTS):
                assert movie_gui.fields[internal_name].label_text == label_text
    
    def test_fields_database_value(self, class_patches):
        with self.movie_context() as movie_gui:
            for internal_name, label_text in zip(guiwidgets.INTERNAL_NAMES, guiwidgets.FIELD_TEXTS):
                assert movie_gui.fields[internal_name].database_value == ''
    
    def test_fields_text_variable(self, class_patches):
        with self.movie_context() as movie_gui:
            for internal_name, label_text in zip(guiwidgets.INTERNAL_NAMES, guiwidgets.FIELD_TEXTS):
                assert isinstance(movie_gui.fields[internal_name].textvariable, guiwidgets.tk.StringVar)
    
    def test_fields_observer(self, class_patches):
        with self.movie_context() as movie_gui:
            for internal_name, label_text in zip(guiwidgets.INTERNAL_NAMES, guiwidgets.FIELD_TEXTS):
                assert isinstance(movie_gui.fields[internal_name].observer,
                                  guiwidgets.observerpattern.Observer)
    
    def test_parent_column_configured(self, class_patches):
        with self.movie_context() as movie_gui:
            assert movie_gui.parent.columnconfigure_calls[0] == ((0,), dict(weight=1))
    
    def test_parent_row_configured(self, class_patches):
        with self.movie_context() as movie_gui:
            assert movie_gui.parent.rowconfigure_calls[0] == ((0,), dict(weight=1))
    
    def test_outer_frame_created(self, class_patches):
        with self.movie_context() as movie_gui:
            assert movie_gui.outerframe == TtkFrame(parent=DummyTk())
    
    def test_outer_frame_column_configured(self, class_patches):
        with self.movie_context() as movie_gui:
            assert movie_gui.parent.children[0].columnconfigure_calls[0] == ((0,), dict(weight=1))
    
    def test_outer_frame_row_0_configured(self, class_patches):
        with self.movie_context() as movie_gui:
            assert movie_gui.parent.children[0].rowconfigure_calls[0] == ((0,), dict(weight=1))
    
    def test_outer_frame_row_1_configured(self, class_patches):
        with self.movie_context() as movie_gui:
            assert movie_gui.parent.children[0].rowconfigure_calls[1] == ((1,), dict(minsize=35))
    
    def test_outer_frame_gridded(self, class_patches):
        with self.movie_context() as movie_gui:
            outerframe = movie_gui.parent.children[0]
            assert outerframe.grid_calls[0] == dict(column=0, row=0, sticky='nsew')
    
    def test_body_frame_created(self, class_patches):
        with self.movie_context() as movie_gui:
            outerframe = movie_gui.parent.children[0]
            bodyframe = outerframe.children[0]
            assert bodyframe == TtkFrame(parent=outerframe, padding=(10, 25, 10, 0))
    
    def test_body_frame_gridded(self, class_patches):
        with self.movie_context() as movie_gui:
            outerframe = movie_gui.parent.children[0]
            bodyframe = outerframe.children[0]
            assert bodyframe.grid_calls[0] == dict(column=0, row=0, sticky='n')
    
    def test_body_frame_column_0_configured(self, class_patches):
        with self.movie_context() as movie_gui:
            call = movie_gui.parent.children[0].children[0].columnconfigure_calls[0]
            assert call == ((0,), dict(weight=1, minsize=30))
    
    def test_body_frame_column_1_configured(self, class_patches):
        with self.movie_context() as movie_gui:
            call = movie_gui.parent.children[0].children[0].columnconfigure_calls[1]
            assert call == ((1,), dict(weight=1))
    
    def test_labels_and_entries_created(self, class_patches):
        with self.movie_context() as movie_gui:
            outerframe = movie_gui.parent.children[0]
            bodyframe = outerframe.children[0]
            assert bodyframe.children
    
    def test_labels_created(self, class_patches):
        with self.movie_context() as movie_gui:
            outerframe = movie_gui.parent.children[0]
            bodyframe = outerframe.children[0]
            labels = bodyframe.children[::2]
            for label, text in zip(labels, guiwidgets.FIELD_TEXTS):
                assert label == TtkLabel(TtkFrame(TtkFrame(DummyTk()), padding=(10, 25, 10, 0)),
                                         text=text)
    
    # noinspection DuplicatedCode
    def test_labels_gridded(self, class_patches):
        with self.movie_context() as movie_gui:
            outerframe = movie_gui.parent.children[0]
            bodyframe = outerframe.children[0]
            labels = bodyframe.children[::2]
            for row_ix, label in enumerate(labels):
                assert label.grid_calls[0] == dict(column=0, row=row_ix, sticky='e', padx=5)
    
    def test_entries_created(self, class_patches):
        with self.movie_context() as movie_gui:
            outerframe = movie_gui.parent.children[0]
            bodyframe = outerframe.children[0]
            entries = bodyframe.children[1::2]
            for entry in entries:
                assert entry == TtkEntry(TtkFrame(TtkFrame(DummyTk()), padding=(10, 25, 10, 0)),
                                         textvariable=TkStringVar(), width=36)
    
    # noinspection DuplicatedCode
    def test_entries_gridded(self, class_patches):
        with self.movie_context() as movie_gui:
            outerframe = movie_gui.parent.children[0]
            bodyframe = outerframe.children[0]
            entries = bodyframe.children[1::2]
            for row_ix, entry in enumerate(entries):
                assert entry.grid_calls[0] == dict(column=1, row=row_ix)
    
    def test_neuron_linker_called(self, class_patches, monkeypatch):
        calls = []
        monkeypatch.setattr(guiwidgets.MovieGUI, 'neuron_linker',
                            lambda *args: calls.append(args))
        with self.movie_context() as movie_gui:
            assert calls == [
                    (movie_gui, 'title', movie_gui.title_year_neuron, movie_gui.field_callback),
                    (movie_gui, 'year', movie_gui.title_year_neuron, movie_gui.field_callback)]
    
    def test_buttonbox_created(self, class_patches):
        with self.movie_context() as movie_gui:
            outerframe = movie_gui.parent.children[0]
            buttonbox = outerframe.children[1]
            assert buttonbox == TtkFrame(parent=outerframe, padding=(5, 5, 10, 10))
    
    def test_buttonbox_gridded(self, class_patches):
        with self.movie_context() as movie_gui:
            outerframe = movie_gui.parent.children[0]
            buttonbox = outerframe.children[1]
            assert buttonbox.grid_calls[0] == dict(column=0, row=1, sticky='e')
    
    def test_commit_button_created(self, class_patches):
        with self.movie_context() as movie_gui:
            button = movie_gui.parent.children[0].children[1].children[0]
            assert button == TtkButton(parent=TtkFrame(parent=TtkFrame(parent=DummyTk()),
                                                       padding=(5, 5, 10, 10)),
                                       text='Commit', command=movie_gui.commit)
    
    def test_commit_button_gridded(self, class_patches):
        with self.movie_context() as movie_gui:
            button = movie_gui.parent.children[0].children[1].children[0]
            assert button.grid_calls[0] == dict(column=0, row=0)
    
    def test_commit_button_bound(self, class_patches):
        with self.movie_context() as movie_gui:
            button = movie_gui.parent.children[0].children[1].children[0]
            assert button.bind_calls[0][0] == '<Return>'
            button.bind_calls[0][1](button)
            assert button.invoke_calls[0]
    
    def test_commit_button_state_set(self, class_patches):
        with self.movie_context() as movie_gui:
            button = movie_gui.parent.children[0].children[1].children[0]
            assert button.state_calls[0][0] == 'disabled'
    
    # noinspection PyShadowingNames
    def test_neuron_register_called(self, class_patches, monkeypatch):
        calls = []
        monkeypatch.setattr(guiwidgets.MovieGUI, 'button_state_callback',
                            lambda movie_gui, button: calls.append(button, ))
        with self.movie_context() as movie_gui:
            button = movie_gui.parent.children[0].children[1].children[0]
            assert calls[0] == button
    
    def test_cancel_button_created(self, class_patches):
        with self.movie_context() as movie_gui:
            button = movie_gui.parent.children[0].children[1].children[1]
            assert button == TtkButton(parent=TtkFrame(parent=TtkFrame(parent=DummyTk()),
                                                       padding=(5, 5, 10, 10)),
                                       text='Cancel', command=movie_gui.destroy)
    
    def test_cancel_button_gridded(self, class_patches):
        with self.movie_context() as movie_gui:
            button = movie_gui.parent.children[0].children[1].children[1]
            assert button.grid_calls[0] == dict(column=1, row=0)
    
    def test_cancel_button_bound(self, class_patches):
        with self.movie_context() as movie_gui:
            button = movie_gui.parent.children[0].children[1].children[1]
            assert button.bind_calls[0][0] == '<Return>'
            button.bind_calls[0][1](button)
            assert button.invoke_calls[0]
    
    def test_cancel_button_focus_set(self, class_patches):
        with self.movie_context() as movie_gui:
            button = movie_gui.parent.children[0].children[1].children[1]
            assert button.focus_set_calls[0] is True
    
    def test_trace_add_called(self, class_patches, monkeypatch):
        calls = []
        monkeypatch.setattr(guiwidgets.MovieGUI, 'field_callback',
                            lambda *args: calls.append(args))
        with self.movie_context() as movie_gui:
            assert movie_gui.fields['title'].textvariable.trace_add_calls[0][0] == 'write'
            assert calls[0][0] == movie_gui
            assert calls[0][1] == 'title'
            assert isinstance(calls[0][2], guiwidgets.observerpattern.Neuron)
            # Are  'title' and 'year' fields linked to the same neuron?
            assert calls[0][2] == calls[1][2]
    
    def test_neuron_register_event_called(self, class_patches, monkeypatch):
        calls = []
        monkeypatch.setattr(guiwidgets.observerpattern.Neuron, 'register_event',
                            lambda *args: calls.append(args))
        with self.movie_context():
            assert calls[0][1] == 'title'
            assert calls[1][1] == 'year'
            # Are  'title' and 'year' fields linked to the same neuron?
            assert calls[0][0] == calls[1][0]
    
    def test_field_callback(self, class_patches):
        with self.movie_context() as movie_gui:
            neuron = movie_gui.title_year_neuron
            movie_gui.field_callback('year', neuron)()
            assert neuron.events == dict(title=False, year=True)
    
    def test_button_state_callback(self, class_patches):
        with self.movie_context() as movie_gui:
            commit = movie_gui.parent.children[0].children[1].children[0]
            movie_gui.button_state_callback(commit)(True)
            assert commit.state_calls == [['disabled'], ['!disabled']]
    
    def test_commit_method(self, class_patches):
        with self.movie_context() as movie_gui:
            movie_gui.destroy()
            assert movie_gui.outerframe.destroy_calls[0]
    
    def test_destroy_method(self, class_patches, monkeypatch):
        calls = []
        with self.movie_context() as movie_gui:
            monkeypatch.setattr(movie_gui, 'callback', lambda *args: calls.append(args))
            movie_gui.commit()
            assert calls[0][0] == dict(title='42', year='42', director='42',
                                       length='42', notes='42', tags='42')
            assert movie_gui.outerframe.destroy_calls[0]
    
    # noinspection PyMissingOrEmptyDocstring
    @pytest.fixture()
    def class_patches(self, monkeypatch):
        monkeypatch.setattr(guiwidgets.tk, 'Tk', DummyTk)
        monkeypatch.setattr(guiwidgets.tk, 'StringVar', TkStringVar)
        monkeypatch.setattr(guiwidgets.ttk, 'Frame', TtkFrame)
        monkeypatch.setattr(guiwidgets.ttk, 'Label', TtkLabel)
        monkeypatch.setattr(guiwidgets.ttk, 'Entry', TtkEntry)
        monkeypatch.setattr(guiwidgets.ttk, 'Button', TtkButton)
    
    # noinspection PyMissingOrEmptyDocstring
    @contextmanager
    def movie_context(self):
        # noinspection PyTypeChecker
        yield guiwidgets.MovieGUI(DummyTk(), movie_gui_callback)


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
    
    def columnconfigure(self, *args, **kwargs):
        self.columnconfigure_calls.append((args, kwargs))
    
    def rowconfigure(self, *args, **kwargs):
        self.rowconfigure_calls.append((args, kwargs))
    
    def bind(self, *args, **kwargs):
        self.bind_calls.append((args, kwargs))


# noinspection PyMissingOrEmptyDocstring
@dataclass
class TkStringVar:
    trace_add_calls: list = field(default_factory=list, init=False, repr=False, compare=False)
    
    def trace_add(self, *args):
        self.trace_add_calls.append(args)
    
    @staticmethod
    def get():
        return '42'


# noinspection PyMissingOrEmptyDocstring
@dataclass
class TtkFrame:
    """Test dummy for Ttk.Frame.

    The dummy Tk/Ttk classes need to mimic Tk's parent/child structure as explicit references are
    missing in the source code.
    """
    parent: Union[DummyTk, 'TtkFrame']
    padding: Union[Tuple[int, int], Tuple[int, int, int, int]] = None
    
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

    def __post_init__(self):
        self.parent.children.append(self)

    def grid(self, **kwargs):
        self.grid_calls.append(kwargs)


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


# noinspection PyUnusedLocal,PyMissingOrEmptyDocstring
def movie_gui_callback(movie_dict: guiwidgets.MovieDict):
    pass
