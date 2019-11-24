"""Test module."""

#  Copyright© 2019. Stephen Rigden.
#  Last modified 11/24/19, 12:40 PM by stephen.
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
from typing import Tuple, Union

import pytest

import guiwidgets


class TestMovieInit:
    
    def test_parent_initialized(self, class_patches):
        with self.movie_init_context() as movie_gui:
            assert movie_gui.parent == movie_gui.parent
    
    def test_callback_initialized(self, class_patches):
        with self.movie_init_context() as movie_gui:
            assert movie_gui.callback == movie_gui_callback
    
    def test_parent_column_configured(self, class_patches):
        with self.movie_init_context() as movie_gui:
            assert movie_gui.parent.columnconfigure_calls[0] == ((0,), dict(weight=1))
    
    def test_parent_row_configured(self, class_patches):
        with self.movie_init_context() as movie_gui:
            assert movie_gui.parent.rowconfigure_calls[0] == ((0,), dict(weight=1))
    
    def test_outer_frame_created(self, class_patches):
        with self.movie_init_context() as movie_gui:
            outerframe = movie_gui.parent.children[0]
            assert outerframe == TtkFrame(parent=DummyTk())
    
    def test_outer_frame_column_configured(self, class_patches):
        with self.movie_init_context() as movie_gui:
            assert movie_gui.parent.children[0].columnconfigure_calls[0] == ((0,), dict(weight=1))
    
    def test_outer_frame_row_configured(self, class_patches):
        with self.movie_init_context() as movie_gui:
            assert movie_gui.parent.children[0].rowconfigure_calls[0] == ((0,), dict(weight=1))
    
    def test_outer_frame_gridded(self, class_patches):
        with self.movie_init_context() as movie_gui:
            outerframe = movie_gui.parent.children[0]
            assert outerframe.grid_calls[0] == dict(column=0, row=0, sticky='nsew')
    
    def test_body_frame_created(self, class_patches):
        with self.movie_init_context() as movie_gui:
            outerframe = movie_gui.parent.children.pop()
            bodyframe = outerframe.children.pop()
            assert bodyframe == TtkFrame(parent=outerframe, padding=(10, 25))
    
    def test_body_frame_gridded(self, class_patches):
        with self.movie_init_context() as movie_gui:
            outerframe = movie_gui.parent.children.pop()
            bodyframe = outerframe.children.pop()
            assert bodyframe.grid_calls.pop() == dict(column=0, row=0, sticky='n')
    
    def test_body_frame_column_0_configured(self, class_patches):
        with self.movie_init_context() as movie_gui:
            call = movie_gui.parent.children[0].children[0].columnconfigure_calls[0]
            assert call == ((0,), dict(weight=1, minsize=30))
    
    def test_body_frame_column_1_configured(self, class_patches):
        with self.movie_init_context() as movie_gui:
            call = movie_gui.parent.children[0].children[0].columnconfigure_calls[1]
            assert call == ((1,), dict(weight=1))
    
    def test_labels_created(self, class_patches):
        with self.movie_init_context() as movie_gui:
            outerframe = movie_gui.parent.children[0]
            bodyframe = outerframe.children[0]
            labels = bodyframe.children[::2]
            for label, text in zip(labels, guiwidgets.FIELD_TEXTS):
                assert label == TtkLabel(TtkFrame(TtkFrame(DummyTk()), padding=(10, 25)), text=text)
    
    # noinspection DuplicatedCode
    def test_labels_gridded(self, class_patches):
        with self.movie_init_context() as movie_gui:
            outerframe = movie_gui.parent.children[0]
            bodyframe = outerframe.children[0]
            labels = bodyframe.children[::2]
            for row_ix, label in enumerate(labels):
                assert label.grid_calls[0] == dict(column=0, row=row_ix, sticky='w', padx=5)
    
    def test_entries_created(self, class_patches):
        with self.movie_init_context() as movie_gui:
            outerframe = movie_gui.parent.children[0]
            bodyframe = outerframe.children[0]
            entries = bodyframe.children[1::2]
            for entry in entries:
                assert entry == TtkEntry(TtkFrame(TtkFrame(DummyTk()), padding=(10, 25)),
                                         textvariable=TkStringVar(), width=36)
    
    # noinspection DuplicatedCode
    def test_entries_gridded(self, class_patches):
        with self.movie_init_context() as movie_gui:
            outerframe = movie_gui.parent.children[0]
            bodyframe = outerframe.children[0]
            entries = bodyframe.children[1::2]
            for row_ix, entry in enumerate(entries):
                assert entry.grid_calls[0] == dict(column=1, row=row_ix)
    
    # noinspection PyMissingOrEmptyDocstring
    @pytest.fixture()
    def class_patches(self, monkeypatch):
        monkeypatch.setattr(guiwidgets.tk, 'Tk', DummyTk)
        monkeypatch.setattr(guiwidgets.tk, 'StringVar', TkStringVar)
        monkeypatch.setattr(guiwidgets.ttk, 'Frame', TtkFrame)
        monkeypatch.setattr(guiwidgets.ttk, 'Label', TtkLabel)
        monkeypatch.setattr(guiwidgets.ttk, 'Entry', TtkEntry)
    
    # noinspection PyMissingOrEmptyDocstrin
    @contextmanager
    def movie_init_context(self):
        # noinspection PyTypeChecker
        movie_gui = guiwidgets.MovieGUI(DummyTk(), movie_gui_callback)
        yield movie_gui


@dataclass
class DummyTk:
    """Test dummy for Tk.

    The dummy Tk/Ttk classes need to mimic Tk's parent/child structure as explicit references are
    missing in the source code."""
    children: list = field(default_factory=list, init=False, repr=False, compare=False)
    
    columnconfigure_calls: list = field(default_factory=list, init=False, repr=False, compare=False)
    rowconfigure_calls: list = field(default_factory=list, init=False, repr=False, compare=False)
    
    def columnconfigure(self, *args, **kwargs):
        self.columnconfigure_calls.append((args, kwargs))
    
    def rowconfigure(self, *args, **kwargs):
        self.rowconfigure_calls.append((args, kwargs))


@dataclass
class TkStringVar:
    pass


@dataclass
class TtkFrame:
    """Test dummy for Ttk.Frame.

    The dummy Tk/Ttk classes need to mimic Tk's parent/child structure as explicit references are
    missing in the source code.
    """
    parent: Union[DummyTk, 'TtkFrame']
    padding: Tuple[int, int] = None
    
    children: list = field(default_factory=list, init=False, repr=False, compare=False)
    grid_calls: list = field(default_factory=list, init=False, repr=False, compare=False)
    columnconfigure_calls: list = field(default_factory=list, init=False, repr=False, compare=False)
    rowconfigure_calls: list = field(default_factory=list, init=False, repr=False, compare=False)
    
    def __post_init__(self):
        self.parent.children.append(self)
    
    def grid(self, **kwargs):
        self.grid_calls.append(kwargs)
    
    def columnconfigure(self, *args, **kwargs):
        self.columnconfigure_calls.append((args, kwargs))
    
    def rowconfigure(self, *args, **kwargs):
        self.rowconfigure_calls.append((args, kwargs))


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


def movie_gui_callback(movie_dict: guiwidgets.MovieDict):
    pass
