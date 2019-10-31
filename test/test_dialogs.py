"""Test module."""

#  Copyright© 2019. Stephen Rigden.
#  Last modified 10/31/19, 11:48 AM by stephen.
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
from dataclasses import dataclass, field
from typing import Dict, Tuple, Union

import pytest

import dialogs


# noinspection PyMissingOrEmptyDocstring
class TestDialogInitAndCall:
    
    # Test implied __init__
    def test_parent_init(self, class_patches):
        with self.init_context(dict(ok='OK', cancel='Cancel')) as dialog:
            assert dialog.parent == TtkFrame(DummyTk())
    
    # Tests of __post_init__
    
    def test_buttons_init(self, class_patches):
        with self.init_context(dict(ok='OK', cancel='Cancel')) as dialog:
            buttonbox = dialog.outer_button_frame.children.pop()
            buttons = buttonbox.children
            assert dialog.buttons == dict(ok=dialogs.Button('OK', buttons.popleft()),
                                          cancel=dialogs.Button('Cancel', buttons.popleft()))

    def test_destroy_button(self, class_patches):
        with self.init_context(dict(ok='OK', cancel='Cancel')) as dialog:
            assert dialog.destroy_button == 'cancel'

    def test_toplevel_window_created(self, class_patches):
        with self.init_context(dict(ok='OK', cancel='Cancel')) as dialog:
            assert dialog.window == TkToplevel(TtkFrame(DummyTk()))

    def test_withdraw_called(self, class_patches):
        with self.init_context(dict(ok='OK', cancel='Cancel')) as dialog:
            assert dialog.window.withdraw_calls.popleft()

    def test_transient_called(self, class_patches):
        with self.init_context(dict(ok='OK', cancel='Cancel')) as dialog:
            assert dialog.window.transient_calls.popleft()

    def test_grab_set_called(self, class_patches):
        with self.init_context(dict(ok='OK', cancel='Cancel')) as dialog:
            assert dialog.window.grab_set_calls.popleft()

    def test_resizable_called(self, class_patches):
        with self.init_context(dict(ok='OK', cancel='Cancel')) as dialog:
            assert dialog.window.resizable_calls.popleft() == dict(width=False, height=False)

    def test_title_called(self, class_patches):
        with self.init_context(dict(ok='OK', cancel='Cancel'), title='test title') as dialog:
            assert dialog.window.title_calls.popleft() == ('test title',)

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
    
    def test_buttonbox_packed(self, class_patches):
        with self.init_context(dict(ok='OK', cancel='Cancel')) as dialog:
            buttonbox_frame = dialog.outer_button_frame.children[0]
            assert buttonbox_frame.pack_calls.popleft() == (dict(side='right'))
    
    def test_buttonbox_packed_with_single_button(self, class_patches):
        with self.init_context(dict(ok='OK')) as dialog:
            buttonbox_frame = dialog.outer_button_frame.children[0]
            assert buttonbox_frame.pack_calls.popleft() == {}
    
    def test_make_button_called(self, class_patches):
        with self.init_context(dict(ok='OK', cancel='Cancel')) as dialog:
            buttonbox_frame = dialog.outer_button_frame.children[0]
            assert self.make_button_args == [(buttonbox_frame, 'ok', dialog.do_button_action),
                                             (buttonbox_frame, 'cancel', dialog.destroy), ]
    
    def test_button_clicked_initialized_to_none(self, class_patches):
        with self.init_context(dict(ok='OK', cancel='Cancel')) as dialog:
            assert dialog.button_clicked is None
    
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
        with self.init_context(dict(ok='OK', cancel='Cancel')) as dialog:
            buttonbox = dialog.outer_button_frame.children.popleft()
            cancel_button = buttonbox.children.pop()
            assert cancel_button.focus_set_calls
    
    def test_bind_called(self, class_patches):
        with self.init_context(dict(ok='OK', cancel='Cancel')) as dialog:
            assert dialog.window.bind_calls.popleft() == ('<Return>', dialog.do_button_action)
            assert dialog.window.bind_calls.popleft() == ('<Escape>', dialog.destroy)
    
    def test_protocol_called(self, class_patches):
        with self.init_context(dict(ok='OK', cancel='Cancel')) as dialog:
            actual_call = dialog.window.protocol_calls[0]
            assert actual_call[0] == 'WM_DELETE_WINDOW'
    
            destroy_call = actual_call[1]
            destroy_call()
            assert self.destroy_called_with.popleft() == dict(button_name='cancel')

    def test_set_geometry_called(self, class_patches):
        with self.init_context(dict(ok='OK', cancel='Cancel')):
            assert self.set_geometry_called

    def test_deiconify_called(self, class_patches):
        with self.init_context(dict(ok='OK', cancel='Cancel')) as dialog:
            dialog()
            assert dialog.window.deiconify_calls.popleft()

    def test_wait_window_called(self, class_patches):
        with self.init_context(dict(ok='OK', cancel='Cancel')) as dialog:
            dialog()
            assert dialog.window.wait_window_calls.popleft()

    def test_clicked_button_returned(self, class_patches):
        with self.init_context(dict(ok='OK', cancel='Cancel')) as dialog:
            dialog.button_clicked = 'test clicked button'
            assert dialog() == 'test clicked button'

    @pytest.fixture()
    def class_patches(self, monkeypatch):
        monkeypatch.setattr(dialogs.tk, 'Tk', DummyTk)
        monkeypatch.setattr(dialogs.tk, 'Toplevel', TkToplevel)
        monkeypatch.setattr(dialogs.ttk, 'Button', TtkButton)
        monkeypatch.setattr(dialogs.ttk, 'Frame', TtkFrame)
        monkeypatch.setattr(dialogs.ModalDialog, 'make_button', self.make_button)
        monkeypatch.setattr(dialogs.ModalDialog, 'make_body', self.make_body)
        monkeypatch.setattr(dialogs.ModalDialog, 'set_geometry', self.set_geometry)
        monkeypatch.setattr(dialogs.ModalDialog, 'destroy', self.destroy)
    
    @contextmanager
    def init_context(self, buttons: Dict[str, str], title=None):
        self.make_button_args = []
        self.make_body_args = []
        self.set_geometry_called = False
        self.destroy_called_with = deque()
        # noinspection PyTypeChecker
        yield dialogs.ModalDialog(TtkFrame(DummyTk()), buttons, title)
    
    def make_button(self, *args):
        self.make_button_args.append(args)
        parent, name, _ = args
        return dialogs.ttk.Button(parent, text=name, name=name)
    
    def make_body(self, *args):
        self.make_body_args.append(args)
        return None
    
    def set_geometry(self):
        self.set_geometry_called = True
    
    def destroy(self, **kwargs):
        self.destroy_called_with.append(kwargs)


# noinspection PyMissingOrEmptyDocstring
class TestDialogMakeButton:
    
    # noinspection PyTypeChecker
    def test_button_object_created(self, class_patches):
        with self.make_button_context(dict(ok='OK', cancel='Cancel')) as (ok_button, cancel_button):
            assert ok_button == TtkButton(TtkFrame(TtkFrame(TkToplevel(TtkFrame(DummyTk()))),
                                                   dialogs.BODY_PADDING),
                                          text='OK', name='ok')
            assert cancel_button == TtkButton(TtkFrame(TtkFrame(TkToplevel(TtkFrame(DummyTk()))),
                                                       dialogs.BODY_PADDING),
                                              text='Cancel', name='cancel')
    
    def test_ok_button_command_configured(self, class_patches):
        with self.make_button_context(dict(ok='OK', cancel='Cancel')) as (ok_button, cancel_button):
            config = ok_button.configure_calls.popleft()
            config['command']('ok')
            assert self.do_button_action_calls.popleft() == dict(button_name='ok')
    
    def test_cancel_button_command_configured(self, class_patches):
        with self.make_button_context(dict(ok='OK', cancel='Cancel')) as (ok_button, cancel_button):
            config = cancel_button.configure_calls.popleft()
            config['command']('cancel')
            assert self.destroy_calls.popleft() == dict(button_name='cancel')
    
    def test_button_packed(self, class_patches):
        with self.make_button_context(dict(ok='OK', cancel='Cancel')) as (ok_button, _):
            assert ok_button.pack_calls.popleft() == dict(side='left', padx=dialogs.BUTTON_PADDING,
                                                          pady=dialogs.BUTTON_PADDING)
    
    def test_ok_button_bound(self, class_patches):
        with self.make_button_context(dict(ok='OK', cancel='Cancel')) as (ok_button, _):
            key, command = ok_button.bind_calls.popleft()
            assert key == '<Return>'
            command('<Button-1>')
            assert ok_button.invoke_calls.popleft()
    
    def test_cancel_button_bound(self, class_patches):
        with self.make_button_context(dict(ok='OK', cancel='Cancel')) as (_, cancel_button):
            key, command = cancel_button.bind_calls.popleft()
            assert key == '<Return>'
            command('<Button-1>')
            assert cancel_button.invoke_calls.popleft()
    
    @pytest.fixture()
    def class_patches(self, monkeypatch):
        monkeypatch.setattr(dialogs.tk, 'Tk', DummyTk)
        monkeypatch.setattr(dialogs.tk, 'Toplevel', TkToplevel)
        monkeypatch.setattr(dialogs.ttk, 'Button', TtkButton)
        monkeypatch.setattr(dialogs.ttk, 'Frame', TtkFrame)
        monkeypatch.setattr(dialogs.ModalDialog, 'make_body', lambda *args: None)
        monkeypatch.setattr(dialogs.ModalDialog, 'destroy', self.destroy)
        monkeypatch.setattr(dialogs.ModalDialog, 'do_button_action', self.do_button_action)
    
    @contextmanager
    def make_button_context(self, buttons: Dict[str, str]) -> Tuple['TtkButton', 'TtkButton']:
        self.destroy_calls = deque()
        self.do_button_action_calls = deque()
        # noinspection PyTypeChecker
        dialog = dialogs.ModalDialog(TtkFrame(DummyTk()), buttons)
        outer_frame = dialog.outer_button_frame
        inner_frame = outer_frame.children.popleft()
        ok_button = inner_frame.children.popleft()
        cancel_button = inner_frame.children.popleft()
        yield ok_button, cancel_button
    
    def destroy(self, **kwargs):
        self.destroy_calls.append(kwargs)
    
    def do_button_action(self, **kwargs):
        self.do_button_action_calls.append(kwargs)


@dataclass
class DummyTk:
    """Test dummy for Tk.
    
    The dummy Tk/Ttk classes need to mimic Tk's parent/child structure as explicit references are
    missing in the source code."""
    children: deque = field(default_factory=deque, init=False, repr=False, compare=False)


# noinspection PyMissingOrEmptyDocstring
@dataclass
class TtkFrame:
    """Test dummy for Tk.Frame.
    
    The dummy Tk/Ttk classes need to mimic Tk's parent/child structure as explicit references are
    missing in the source code.
    """
    parent: Union[DummyTk, 'TkToplevel']
    padding: str = None
    
    children: deque = field(default_factory=deque, init=False, repr=False, compare=False)
    grid_calls: deque = field(default_factory=deque, init=False, repr=False, compare=False)
    pack_calls: deque = field(default_factory=deque, init=False, repr=False, compare=False)
    
    def __post_init__(self):
        self.parent.children.append(self)
    
    def grid(self, **kwargs):
        self.grid_calls.append(kwargs)
    
    def pack(self, **kwargs):
        self.pack_calls.append(kwargs)


# noinspection PyMissingOrEmptyDocstring
@dataclass
class TkToplevel:
    """Test dummy for Tk.Toplevel.

    The dummy Tk/Ttk classes need to mimic Tk's parent/child structure as explicit references are
    missing in the source code.
    """
    parent: TtkFrame

    children: deque = field(default_factory=deque, init=False, repr=False, compare=False)
    withdraw_calls: deque = field(default_factory=deque, init=False, repr=False, compare=False)
    transient_calls: deque = field(default_factory=deque, init=False, repr=False, compare=False)
    grab_set_calls: deque = field(default_factory=deque, init=False, repr=False, compare=False)
    resizable_calls: deque = field(default_factory=deque, init=False, repr=False, compare=False)
    title_calls: deque = field(default_factory=deque, init=False, repr=False, compare=False)
    wait_window_calls: deque = field(default_factory=deque, init=False, repr=False, compare=False)
    deiconify_calls: deque = field(default_factory=deque, init=False, repr=False, compare=False)
    bind_calls: deque = field(default_factory=deque, init=False, repr=False, compare=False)
    protocol_calls: deque = field(default_factory=deque, init=False, repr=False, compare=False)

    def __post_init__(self):
        self.parent.children.append(self)

    def transient(self):
        self.transient_calls.append(True)

    def withdraw(self):
        self.withdraw_calls.append(True)

    def grab_set(self):
        self.grab_set_calls.append(True)

    def title(self, *args):
        self.title_calls.append(args)

    def resizable(self, **kwargs):
        self.resizable_calls.append(kwargs)

    def wait_window(self):
        self.wait_window_calls.append(True)

    def deiconify(self):
        self.deiconify_calls.append(True)

    def bind(self, *args):
        self.bind_calls.append(args)

    def protocol(self, *args):
        self.protocol_calls.append(args)


# noinspection PyMissingOrEmptyDocstring
@dataclass
class TtkButton:
    """Test dummy for Tk.Button.

    The dummy Tk/Ttk classes need to mimic Tk's parent/child structure as explicit references are
    missing in the source code.
    """
    parent: TtkFrame
    text: str
    name: str
    
    children: deque = field(default_factory=deque, init=False, repr=False, compare=False)
    configure_calls: deque = field(default_factory=deque, init=False, repr=False, compare=False)
    pack_calls: deque = field(default_factory=deque, init=False, repr=False, compare=False)
    bind_calls: deque = field(default_factory=deque, init=False, repr=False, compare=False)
    invoke_calls: deque = field(default_factory=deque, init=False, repr=False, compare=False)
    focus_set_calls: deque = field(default_factory=deque, init=False, repr=False, compare=False)
    
    def __post_init__(self):
        self.parent.children.append(self)
    
    def configure(self, **kwargs):
        self.configure_calls.append(kwargs)

    def pack(self, **kwargs):
        self.pack_calls.append(kwargs)

    def bind(self, *args):
        self.bind_calls.append(args)

    def invoke(self):
        self.invoke_calls.append(True)

    def focus_set(self):
        self.focus_set_calls.append(True)
