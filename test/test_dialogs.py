"""Test module."""

#  Copyright© 2019. Stephen Rigden.
#  Last modified 10/24/19, 1:57 PM by stephen.
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

from collections import deque
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Dict, Union

import pytest

import dialogs


# noinspection PyMissingOrEmptyDocstring
class TestDialogInit:
    
    def test_parent_init(self, class_patches):
        with self.init_context(dict(ok='OK', cancel='Cancel')) as dialog:
            assert dialog.parent == TtkFrame(DummyTk())
    
    def test_buttons_init(self, class_patches):
        print()
        with self.init_context(dict(ok='OK', cancel='Cancel')) as dialog:
            buttonbox = dialog.outer_button_frame.children.pop()
            buttons = buttonbox.children
            assert dialog.buttons == dict(ok=dialogs.Button('OK', buttons.popleft()),
                                          cancel=dialogs.Button('Cancel', buttons.popleft()))
    
    def test_cancel_button(self, class_patches):
        with self.init_context(dict(ok='OK', cancel='Cancel')) as dialog:
            assert dialog.cancel_button == 'cancel'
    
    def test_toplevel_window_created(self, class_patches):
        with self.init_context(dict(ok='OK', cancel='Cancel')) as dialog:
            assert dialog.window == TkToplevel(TtkFrame(DummyTk()))
    
    def test_transient_called(self, class_patches):
        with self.init_context(dict(ok='OK', cancel='Cancel')) as dialog:
            assert dialog.window.transient_called
    
    def test_resizable_called(self, class_patches):
        with self.init_context(dict(ok='OK', cancel='Cancel')) as dialog:
            assert dialog.window.resizable_called_with == dict(width=False, height=False)
    
    def test_outer_button_frame_created(self, class_patches):
        with self.init_context(dict(ok='OK', cancel='Cancel')) as dialog:
            assert dialog.outer_button_frame == TtkFrame(TkToplevel(TtkFrame(DummyTk())))
    
    def test_outer_button_frame_gridded(self, class_patches):
        with self.init_context(dict(ok='OK', cancel='Cancel')) as dialog:
            assert dialog.outer_button_frame.grid_calls.popleft() == dict(row=1, sticky=dialogs.tk.EW)
    
    def test_buttonbox_created(self, class_patches):
        with self.init_context(dict(ok='OK', cancel='Cancel')) as dialog:
            expected = TtkFrame(dialog.outer_button_frame, padding=dialogs.BODY_PADDING)
            buttonbox_frame = dialog.outer_button_frame.children[0]
            assert buttonbox_frame == expected
    
    def test_make_button_called(self, class_patches):
        with self.init_context(dict(ok='OK', cancel='Cancel')) as dialog:
            buttonbox_frame = dialog.outer_button_frame.children[0]
            assert self.make_button_args == [(buttonbox_frame, 'ok', dialog.do_button_action),
                                             (buttonbox_frame, 'cancel', dialog.destroy), ]
    
    def test_body_frame_created(self, class_patches):
        with self.init_context(dict(ok='OK', cancel='Cancel')) as dialog:
            assert dialog.body_frame == TtkFrame(dialog.window, padding=dialogs.BODY_PADDING)
    
    def test_body_frame_gridded(self, class_patches):
        with self.init_context(dict(ok='OK', cancel='Cancel')) as dialog:
            assert dialog.body_frame.grid_calls.popleft() == dict(row=0, sticky=dialogs.tk.NSEW)
    
    def test_make_body_called(self, class_patches):
        with self.init_context(dict(ok='OK', cancel='Cancel')) as dialog:
            assert self.make_body_args[0][0] == dialog.body_frame
    
    def test_initial_focus_set_to_cancel_button(self, class_patches):
        print()
        with self.init_context(dict(ok='OK', cancel='Cancel')) as dialog:
            buttonbox = dialog.outer_button_frame.children.pop()
            cancel_button = buttonbox.children.pop()
            assert id(dialog.initial_focus) == id(cancel_button)
    
    def test_bind_called(self, class_patches):
        with self.init_context(dict(ok='OK', cancel='Cancel')) as dialog:
            assert dialog.window.bind_args.popleft() == ('<Return>', dialog.do_button_action)
            assert dialog.window.bind_args.popleft() == ('<Escape>', dialog.destroy)
    
    def test_protocol_called(self, class_patches):
        print()
        with self.init_context(dict(ok='OK', cancel='Cancel')) as dialog:
            assert (dialog.window.protocol_args.popleft() ==
                    'WM_DELETE_WINDOW',
                    lambda: dialog.destroy(button_name=dialog.cancel_button))
    
    def test_set_geometry_called(self, class_patches):
        with self.init_context(dict(ok='OK', cancel='Cancel')):
            assert self.set_geometry_called
    
    def test_wait_window_called(self, class_patches):
        with self.init_context(dict(ok='OK', cancel='Cancel')) as dialog:
            assert dialog.window.wait_window_called
    
    @pytest.fixture()
    def class_patches(self, monkeypatch):
        monkeypatch.setattr(dialogs.tk, 'Tk', DummyTk)
        monkeypatch.setattr(dialogs.tk, 'Toplevel', TkToplevel)
        monkeypatch.setattr(dialogs.ttk, 'Button', TtkButton)
        monkeypatch.setattr(dialogs.ttk, 'Frame', TtkFrame)
        monkeypatch.setattr(dialogs.Dialog, 'make_button', self.make_button)
        monkeypatch.setattr(dialogs.Dialog, 'make_body', self.make_body)
        monkeypatch.setattr(dialogs.Dialog, 'set_geometry', self.set_geometry)
    
    @contextmanager
    def init_context(self, buttons: Dict[str, str]):
        self.make_button_args = []
        self.make_body_args = []
        self.set_geometry_called = False
        # noinspection PyTypeChecker
        yield dialogs.Dialog(TtkFrame(DummyTk()), buttons)
    
    def make_button(self, *args):
        self.make_button_args.append(args)
        return dialogs.ttk.Button(args[0])
    
    def make_body(self, *args):
        self.make_body_args.append(args)
        return None
    
    def set_geometry(self):
        self.set_geometry_called = True


@dataclass
class DummyTk:
    """Test dummy for Tk.
    
    The dummy Tk/Ttk classes need to mimic Tk's parent/child structure as explicit references are
    missing in the source code."""
    
    def __post_init__(self):
        self.children = []


# noinspection PyMissingOrEmptyDocstring
@dataclass
class TtkFrame:
    """Test dummy for Tk.Frame.
    
    The dummy Tk/Ttk classes need to mimic Tk's parent/child structure as explicit references are
    missing in the source code."""
    parent: Union[DummyTk, 'TkToplevel']
    padding: str = None
    
    def __post_init__(self):
        self.children = deque()
        self.parent.children.append(self)
        self.grid_calls = deque()
    
    def grid(self, **kwargs):
        self.grid_calls.append(kwargs)


# noinspection PyMissingOrEmptyDocstring
@dataclass
class TkToplevel:
    """Test dummy for Tk.Toplevel.

    The dummy Tk/Ttk classes need to mimic Tk's parent/child structure as explicit references are
    missing in the source code."""
    parent: TtkFrame
    
    def __post_init__(self):
        self.children = deque()
        self.parent.children.append(self)
        self.transient_called = False
        self.resizable_called_with = None
        self.wait_window_called = False
        self.bind_args = deque()
        self.protocol_args = deque()
    
    def transient(self):
        self.transient_called = True
    
    def resizable(self, **kwargs):
        self.resizable_called_with = kwargs
    
    def wait_window(self):
        self.wait_window_called = True
    
    def bind(self, *args):
        self.bind_args.append(args)
    
    def protocol(self, *args):
        self.protocol_args.append(args)


@dataclass
class TtkButton:
    """Test dummy for Tk.Button.

    The dummy Tk/Ttk classes need to mimic Tk's parent/child structure as explicit references are
    missing in the source code."""
    parent: TtkFrame
    
    def __post_init__(self):
        self.children = deque()
        self.parent.children.append(self)
