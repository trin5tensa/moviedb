"""Test module."""

#  Copyright© 2020. Stephen Rigden.
#  Last modified 5/14/20, 2:55 PM by stephen.
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

import guiwidgets_2


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
    
    def dummy_create_entry_fields(self, *args):
        self.create_entry_fields_calls.append(args)
        return self.dummy_entry_fields
    
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


def test_create_entry_fields(patch_tk):
    names = ('test field',)
    texts = ('Test Field',)
    entry_fields = guiwidgets_2.create_entry_fields(names, texts)
    # noinspection PyTypeChecker
    assert entry_fields == {names[0]: guiwidgets_2.EntryField(label_text=texts[0], original_value='',
                                                              textvariable=TkStringVar(), )}


@pytest.mark.usefixtures('patch_tk')
class TestCreateInputFormFraming:
    
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


@pytest.mark.usefixtures('patch_tk')
class TestCreateInputFormFields:
    
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
    
    @contextmanager
    def create_fields_context(self):
        body_frame = TtkFrame(DummyTk())
        names = ('tag',)
        entry_fields = dict(tag=guiwidgets_2.EntryField('Tag', ''))
        # noinspection PyTypeChecker
        guiwidgets_2.create_input_form_fields(body_frame, names, entry_fields)
        yield body_frame, entry_fields


@pytest.mark.usefixtures('patch_tk')
class TestCreateButton:
    
    def test_create_button_grid(self):
        with self.button_context() as button:
            assert button.grid_calls == [dict(column=0, row=0)]
    
    def test_create_button_bind(self):
        with self.button_context() as button:
            assert button.bind_calls[0][0] == '<Return>'
            assert isinstance(button.bind_calls[0][1], Callable)
    
    def test_disable_at_inititialization(self):
        with self.button_context(False) as button:
            assert button.state_calls == [['disabled']]
    
    @contextmanager
    def button_context(self, enabled=True):
        buttonbox = TtkFrame(DummyTk())
        text = 'Dummy Button'
        column = 0
        command = lambda: None
        # noinspection PyTypeChecker
        yield guiwidgets_2.create_button(buttonbox, text, column, command, enabled)


def test_enable_button_wrapper(patch_tk):
    # noinspection PyTypeChecker
    button = TtkButton(DummyTk(), 'Dummy Button')
    # noinspection PyTypeChecker
    enable_button = guiwidgets_2.enable_button_wrapper(button)
    enable_button(True)
    assert button.state_calls == [['!disabled']]


def test_link_or_neuron_to_button():
    def change_button_state(): pass
    
    neuron = guiwidgets_2.link_or_neuron_to_button(change_button_state)
    assert isinstance(neuron, guiwidgets_2.neurons.OrNeuron)
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
    assert notifee.state == None
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


@pytest.fixture
def dummy_entry_fields():
    return dict(tag=guiwidgets_2.EntryField('Tag', ''))


# noinspection PyMissingOrEmptyDocstring,DuplicatedCode
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


# noinspection PyMissingOrEmptyDocstring,DuplicatedCode
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


# noinspection PyMissingOrEmptyDocstring,DuplicatedCode
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


# noinspection PyMissingOrEmptyDocstring,DuplicatedCode
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


# noinspection PyMissingOrEmptyDocstring,DuplicatedCode
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


# noinspection PyMissingOrEmptyDocstring,DuplicatedCode
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
