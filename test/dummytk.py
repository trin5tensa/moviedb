"""Test support module for Tk dummies."""

#  Copyright (c) 2022-2023. Stephen Rigden.
#  Last modified 1/9/23, 8:37 AM by stephen.
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
import itertools
from dataclasses import dataclass, field
from typing import Callable, Literal, Sequence, Tuple, Union, TypeVar

ParentType = TypeVar('ParentType', 'DummyTk', 'TkToplevel', 'TtkFrame')

# noinspection PyMissingOrEmptyDocstring,DuplicatedCode
@dataclass
class DummyTk:
    """Test dummy for Tk.

    The dummy Tk/Ttk classes need to mimic Tk's parent/child structure as explicit references are
    not required in the source code."""
    children: list = field(default_factory=list, init=False, repr=False, compare=False)

    columnconfigure_calls: list = field(default_factory=list, init=False, repr=False, compare=False)
    rowconfigure_calls: list = field(default_factory=list, init=False, repr=False, compare=False)
    bind_calls: list = field(default_factory=list, init=False, repr=False, compare=False)
    bell_calls: list = field(default_factory=list, init=False, repr=False, compare=False)
    after_calls: dict = field(default_factory=dict, init=False, repr=False, compare=False)
    after_cancel_calls: list = field(default_factory=list, init=False, repr=False, compare=False)

    # This is used to generate unique event queue ids
    event_id = itertools.count()

    def columnconfigure(self, *args, **kwargs):
        self.columnconfigure_calls.append((args, kwargs))

    def rowconfigure(self, *args, **kwargs):
        self.rowconfigure_calls.append((args, kwargs))

    def bind(self, *args, **kwargs):
        self.bind_calls.append((args, kwargs))

    def bell(self):
        self.bell_calls.append(True)

    def after(self, *args):
        event_id = next(self.event_id)
        delay = args[0]
        callback = args[1]
        args2 = args[2:]
        self.after_calls[event_id] = (delay, callback, args2)
        return event_id

    def after_cancel(self, *args):
        cancel_id, = args
        del self.after_calls[cancel_id]
        self.after_cancel_calls.append([args])


# noinspection PyMissingOrEmptyDocstring,DuplicatedCode
@dataclass
class TkToplevel:
    """
    Test dummy for Tk.Toplevel.

    The dummy Tk/Ttk classes need to mimic Tk's parent/child structure as explicit references are
    missing in the source code.
    """
    parent: ParentType
    children: list = field(default_factory=list, init=False, repr=False, compare=False)
    destroy_calls: list = field(default_factory=list, init=False, repr=False, compare=False)

    def __post_init__(self):
        self.parent.children.append(self)

    def destroy(self):
        self.destroy_calls.append(True)


# noinspection PyMissingOrEmptyDocstring,DuplicatedCode
@dataclass
class TkStringVar:
    trace_add_calls: list = field(default_factory=list, init=False, repr=False, compare=False)
    set_calls: list = field(default_factory=list, init=False, repr=False, compare=False)
    value: str = '4242'
    trace_add_callback: Callable = None

    def trace_add(self, *args):
        _, self.trace_add_callback = args
        self.trace_add_calls.append(args)

    def set(self, *args):
        self.set_calls.append(args)

    def get(self):
        return self.value

    def set_for_test(self, value):
        self.value = value


# noinspection PyMissingOrEmptyDocstring,DuplicatedCode
@dataclass
class TtkFrame:
    """Test dummy for Ttk.Frame.

    The dummy Tk/Ttk classes need to mimic Tk's parent/child structure as explicit references are
    missing in the source code.
    """
    parent: ParentType
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
    parent: ParentType
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
    parent: ParentType
    textvariable: TkStringVar = None
    width: int = None

    grid_calls: list = field(default_factory=list, init=False, repr=False, compare=False)
    config_calls: list = field(default_factory=list, init=False, repr=False, compare=False)
    register_calls: list = field(default_factory=list, init=False, repr=False, compare=False)
    focus_set_calls: list = field(default_factory=list, init=False, repr=False, compare=False)
    select_range_calls: list = field(default_factory=list, init=False, repr=False, compare=False)
    icursor_calls: list = field(default_factory=list, init=False, repr=False, compare=False)

    def __post_init__(self):
        self.parent.children.append(self)

    def grid(self, **kwargs):
        self.grid_calls.append(kwargs)

    def config(self, **kwargs):
        self.config_calls.append(kwargs)

    def register(self, *args):
        self.register_calls.append(args)
        return 'test registered_callback'

    def focus_set(self):
        self.focus_set_calls.append(True)

    def select_range(self, *args):
        self.select_range_calls.append(args)

    def icursor(self, *args):
        self.icursor_calls.append(args)


# noinspection PyMissingOrEmptyDocstring,DuplicatedCode
@dataclass
class TtkCheckbutton:
    """Test dummy for Ttk.Checkbutton.

    The dummy Tk/Ttk classes need to mimic Tk's parent/child structure as explicit references are
    missing in the source code.
    """
    parent: ParentType
    text: str
    variable: TkStringVar
    width: int = None

    grid_calls: list = field(default_factory=list, init=False, repr=False, compare=False)

    def __post_init__(self):
        self.parent.children.append(self)

    def grid(self, **kwargs):
        self.grid_calls.append(kwargs)


# noinspection PyMissingOrEmptyDocstring,DuplicatedCode
@dataclass
class TtkButton:
    parent: ParentType
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
    parent: ParentType
    columns: Sequence[str] = field(default_factory=list)
    height: int = field(default=0)
    selectmode: Literal['browse', 'extended', 'none'] = field(default='extended')
    show: Literal['tree', 'headings'] = field(default='headings')
    padding: int = field(default=0)
    items: list[str] = field(default_factory=list, init=False, repr=False, compare=False)

    grid_calls: list = field(default_factory=list, init=False, repr=False, compare=False)
    column_calls: list = field(default_factory=list, init=False, repr=False, compare=False)
    heading_calls: list = field(default_factory=list, init=False, repr=False, compare=False)
    insert_calls: list = field(default_factory=list, init=False, repr=False, compare=False)
    bind_calls: list = field(default_factory=list, init=False, repr=False, compare=False)
    configure_calls: list = field(default_factory=list, init=False, repr=False, compare=False)
    selection_add_calls: list = field(default_factory=list, init=False, repr=False, compare=False)
    selection_set_calls: list = field(default_factory=list, init=False, repr=False, compare=False)

    def __post_init__(self):
        self.parent.children.append(self)

    def grid(self, **kwargs):
        self.grid_calls.append(kwargs)

    def column(self, *args, **kwargs):
        self.column_calls.append((args, kwargs))

    def heading(self, *args, **kwargs):
        self.heading_calls.append((args, kwargs))

    def insert(self, *args, **kwargs):
        self.insert_calls.append((args, kwargs))

    def bind(self, *args, **kwargs):
        self.bind_calls.append((args, kwargs))

    def yview(self, *args, **kwargs):
        pass

    def configure(self, **kwargs):
        self.configure_calls.append(kwargs)

    def selection_add(self, *args):
        self.selection_add_calls.append(args)

    def selection_set(self, *args):
        self.selection_set_calls.append(args)

    def set_mock_children(self, items: list[str]):
        self.items = items[:]

    def get_children(self):
        return self.items

    def delete(self, *args):
        self.items = list(set(self.items) - set(args))


    @staticmethod
    def selection():
        return ['test tag', 'ignored tag']


# noinspection PyMissingOrEmptyDocstring
@dataclass
class TtkScrollbar:
    parent: ParentType
    orient: Literal['horizontal', 'vertical']
    command: Callable

    grid_calls: list = field(default_factory=list, init=False, repr=False, compare=False)

    def __post_init__(self):
        self.parent.children.append(self)

    def grid(self, **kwargs):
        self.grid_calls.append(kwargs)

    def set(self):
        pass
