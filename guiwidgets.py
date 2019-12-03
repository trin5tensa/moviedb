"""GUI Windows.

This module includes windows for presenting data supplied to it and returning entered data to its
callers.
"""

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

import tkinter as tk
import tkinter.ttk as ttk
from dataclasses import dataclass, field
from typing import Callable, Dict, List, TypedDict

import observerpattern


INTERNAL_NAMES = ('title', 'year', 'director', 'length', 'notes', 'tags')
FIELD_TEXTS = ('Title *', 'Year *', 'Director', 'Length (minutes)', 'Notes', 'Tags')
COMMIT_TEXT = 'Commit'
CANCEL_TEXT = 'Cancel'


class MovieDict(TypedDict, total=False):
    """A dictionary of movie fields."""
    title: str
    year: int
    director: str
    minutes: int
    notes: str
    tags: List[str]


@dataclass
class MovieGUI:
    """ Create a form for entering or editing a movie."""
    parent: tk.Tk
    # On exit this callback will be called with a dictionary of fields and user entered values.
    callback: Callable[[MovieDict], None]
    
    caller_fields: MovieDict = field(default_factory=dict)
    outerframe: ttk.Frame = field(default=None, init=False, repr=False)
    fields: Dict[str, 'MovieField'] = field(default_factory=dict, init=False, repr=False)
    title_year_neuron: observerpattern.Neuron = field(default_factory=observerpattern.Neuron,
                                                      init=False, repr=False)
    
    def __post_init__(self):
        self.fields = {internal_name: MovieField(field_text, self.caller_fields.get(internal_name, ''))
                       for internal_name, field_text
                       in zip(INTERNAL_NAMES, FIELD_TEXTS)}
        
        self.parent.columnconfigure(0, weight=1)
        self.parent.rowconfigure(0, weight=1)
        
        self.outerframe = ttk.Frame(self.parent)
        self.outerframe.grid(column=0, row=0, sticky='nsew')
        self.outerframe.columnconfigure(0, weight=1)
        self.outerframe.rowconfigure(0, weight=1)
        self.outerframe.rowconfigure(1, minsize=35)
        
        self.create_body(self.outerframe)
        self.create_buttonbox(self.outerframe)
    
    def create_body(self, outerframe: ttk.Frame):
        """Create the body of the form."""
        bodyframe = ttk.Frame(outerframe, padding=(10, 25, 10, 0))
        bodyframe.grid(column=0, row=0, sticky='n')
        bodyframe.columnconfigure(0, weight=1, minsize=30)
        bodyframe.columnconfigure(1, weight=1)
        
        # moviedb-#94
        #   Make tags field into multiple choice from caller supplied list. New tags permitted.
        for row_ix, internal_name in enumerate(INTERNAL_NAMES):
            label = ttk.Label(bodyframe, text=self.fields[internal_name].label_text)
            label.grid(column=0, row=row_ix, sticky='e', padx=5)
            entry = ttk.Entry(bodyframe, textvariable=self.fields[internal_name].textvariable, width=36)
            entry.grid(column=1, row=row_ix)
        
        # Link title and year fields to a single neuron.
        self.neuron_linker('title', self.title_year_neuron, self.field_callback)
        self.neuron_linker('year', self.title_year_neuron, self.field_callback)
    
    def create_buttonbox(self, outerframe: ttk.Frame):
        """Create the buttons."""
        buttonbox = ttk.Frame(outerframe, padding=(5, 5, 10, 10))
        buttonbox.grid(column=0, row=1, sticky='e')
        
        # Commit button
        commit = ttk.Button(buttonbox, text=COMMIT_TEXT, command=self.commit)
        commit.grid(column=0, row=0)
        commit.bind('<Return>', lambda event, b=commit: b.invoke())
        commit.state(['disabled'])
        self.title_year_neuron.register(self.button_state_callback(commit))
        
        # Cancel button
        cancel = ttk.Button(buttonbox, text=CANCEL_TEXT, command=self.destroy)
        cancel.grid(column=1, row=0)
        cancel.bind('<Return>', lambda event, b=cancel: b.invoke())
        cancel.focus_set()
    
    def neuron_linker(self, internal_name: str, neuron: observerpattern.Neuron,
                      field_callback: Callable):
        """Link a field to a neuron."""
        self.fields[internal_name].textvariable.trace_add('write',
                                                          field_callback(internal_name, neuron))
        neuron.register_event(internal_name)
    
    def field_callback(self, internal_name: str, neuron: observerpattern.Neuron) -> Callable:
        """Create the callback for an observed field.
        
        This will be registered as the 'trace_add' callback for an entry field."""
        
        def change_neuron_state():
            """Call the neuron when the field changes,"""
            state = (self.fields[internal_name].textvariable.get()
                     != self.fields[internal_name].database_value)
            neuron(internal_name, state)
        
        return change_neuron_state
    
    @staticmethod
    def button_state_callback(button: ttk.Button) -> Callable:
        """Create the callback for a button.
        
        This will be registered with a neuron as s notifee."""
        
        def change_button_state(state: bool):
            """Enable or disable the commit button when the title or year field change."""
            if state:
                button.state(['!disabled'])
            else:
                button.state(['disabled'])
        
        return change_button_state
    
    def commit(self):
        """The user clicked the commit button."""
        return_fields = {internal_name: movie_field.textvariable.get()
                         for internal_name, movie_field in self.fields.items()}
        self.callback(return_fields)
        self.destroy()
    
    def destroy(self):
        """Destroy all widgets of this class."""
        self.outerframe.destroy()


@dataclass
class MovieField:
    """A support class for attributes of a gui field."""
    label_text: str
    database_value: str
    textvariable: tk.StringVar = None
    observer: observerpattern.Observer = None
    
    def __post_init__(self):
        self.textvariable = tk.StringVar()
        self.observer = observerpattern.Observer()
