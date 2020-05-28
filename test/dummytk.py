"""Test support module for Tk dummies."""

#  Copyright© 2020. Stephen Rigden.
#  Last modified 5/28/20, 7:06 AM by stephen.
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

from dataclasses import dataclass, field
from typing import Callable, List, Literal, Tuple, Union


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


# noinspection PyMissingOrEmptyDocstring
@dataclass
class TtkTreeview:
    parent: TtkFrame
    columns: List[str] = field(default_factory=list)
    height: int = field(default=0)
    selectmode: Literal['browse', 'extended', 'none'] = field(default='extended')
    
    grid_calls: list = field(default_factory=list, init=False, repr=False, compare=False)
    column_calls: list = field(default_factory=list, init=False, repr=False, compare=False)
    heading_calls: list = field(default_factory=list, init=False, repr=False, compare=False)
    insert_calls: list = field(default_factory=list, init=False, repr=False, compare=False)
    bind_calls: list = field(default_factory=list, init=False, repr=False, compare=False)
    
    def __post_init__(self):
        self.parent.children.append(self)
    
    def grid(self, **kwargs):
        self.grid_calls.append(kwargs)
        pass
    
    def column(self, *args, **kwargs):
        self.column_calls.append((args, kwargs))

    def heading(self, *args, **kwargs):
        self.heading_calls.append((args, kwargs))

    def insert(self, *args, **kwargs):
        self.insert_calls.append((args, kwargs))

    def bind(self, *args, **kwargs):
        self.bind_calls.append((args, kwargs))

    @staticmethod
    def selection():
        return ['test tag', 'ignored tag']
