"""GUI Windows.

This module includes windows for presenting data supplied to it and returning entered data to its
callers.
"""

#  Copyright© 2019. Stephen Rigden.
#  Last modified 12/7/19, 2:55 PM by stephen.
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
from typing import Callable, Dict, List, Sequence, TypedDict

import observerpattern


INTERNAL_NAMES = ('title', 'year', 'director', 'length', 'notes')
FIELD_TEXTS = ('Title *', 'Year *', 'Director', 'Length (minutes)', 'Notes')
COMMIT_TEXT = 'Commit'
CANCEL_TEXT = 'Cancel'
SELECT_TAGS_TEXT = 'Select tags'


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
    # List of all tags in the database.
    tags: Sequence[str]
    # On exit this callback will be called with a dictionary of fields and user entered values.
    callback: Callable[[MovieDict], None]
    
    caller_fields: MovieDict = field(default_factory=dict)
    outer_frame: ttk.Frame = field(default=None, init=False, repr=False)
    entry_fields: Dict[str, 'MovieField'] = field(default_factory=dict, init=False, repr=False)
    title_year_neuron: observerpattern.Neuron = field(default_factory=observerpattern.Neuron,
                                                      init=False, repr=False)
    selected_tags: List[str] = field(default_factory=list, init=False, repr=False)
    
    def __post_init__(self):
        self.entry_fields = {internal_name: MovieField(field_text,
                                                       self.caller_fields.get(internal_name, ''))
                             for internal_name, field_text
                             in zip(INTERNAL_NAMES, FIELD_TEXTS)}
        
        self.parent.columnconfigure(0, weight=1)
        self.parent.rowconfigure(0, weight=1)
        
        self.outer_frame = ttk.Frame(self.parent)
        self.outer_frame.grid(column=0, row=0, sticky='nsew')
        self.outer_frame.columnconfigure(0, weight=1)
        self.outer_frame.rowconfigure(0, weight=1)
        self.outer_frame.rowconfigure(1, minsize=35)
        
        self.create_body(self.outer_frame)
        self.create_buttonbox(self.outer_frame)
    
    def create_body(self, outerframe: ttk.Frame):
        """Create the body of the form."""
        body_frame = ttk.Frame(outerframe, padding=(10, 25, 10, 0))
        body_frame.grid(column=0, row=0, sticky='n')
        body_frame.columnconfigure(0, weight=1, minsize=30)
        body_frame.columnconfigure(1, weight=1)
    
        # Entry fields
        for row_ix, internal_name in enumerate(INTERNAL_NAMES):
            label = ttk.Label(body_frame, text=self.entry_fields[internal_name].label_text)
            label.grid(column=0, row=row_ix, sticky='e', padx=5)
            entry = ttk.Entry(body_frame, textvariable=self.entry_fields[internal_name].textvariable,
                              width=36)
            entry.grid(column=1, row=row_ix)
    
        # Tag selection treeview
        # moviedb-#95 The tags of an existing record should be shown as selected.
        label = ttk.Label(body_frame, text=SELECT_TAGS_TEXT)
        label.grid(column=0, row=6, sticky='e', padx=5)
        tags_frame = ttk.Frame(body_frame, padding=5)
        tags_frame.grid(column=1, row=6, sticky='w')
        tree = ttk.Treeview(tags_frame, columns=('tags',), height=5, selectmode='extended',
                            show='tree', padding=5)
        tree.grid(column=0, row=0, sticky='w')
        tree.column('tags', width=100)
        for tag in self.tags:
            tree.insert('', 'end', tag, text=tag, tags='tags')
        tree.tag_bind('tags', '<<TreeviewSelect>>', callback=self.treeview_callback(tree))
        scrollbar = ttk.Scrollbar(tags_frame, orient=tk.VERTICAL, command=tree.yview)
        scrollbar.grid(column=1, row=0)
        tree.configure(yscrollcommand=scrollbar.set)
    
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
        self.entry_fields[internal_name].textvariable.trace_add('write',
                                                                field_callback(internal_name, neuron))
        neuron.register_event(internal_name)
    
    def field_callback(self, internal_name: str, neuron: observerpattern.Neuron) -> Callable:
        """Create the callback for an observed field.
        
        This will be registered as the 'trace_add' callback for an entry field.
        """
    
        # noinspection PyUnusedLocal
        def change_neuron_state(*args):
            """Call the neuron when the field changes.
            
            Args:
                *args: Not used. Required to match unused arguments from caller..
            """
            state = (self.entry_fields[internal_name].textvariable.get()
                     != self.entry_fields[internal_name].database_value)
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
    
    def treeview_callback(self, tree: ttk.Treeview):
        """Create a callback which will be called whenever the user selection is changed.
        
        Args:
            tree:

        Returns: The callback.
        """
        
        # noinspection PyUnusedLocal
        def update_tag_selection(*args):
            """Save the newly changed user selection.
            
            Args:
                *args: Not used. Needed for compatibility with Tk:Tcl caller.
            """
            self.selected_tags = tree.selection()
        
        return update_tag_selection
    
    def commit(self):
        """The user clicked the commit button."""
        return_fields = {internal_name: movie_field.textvariable.get()
                         for internal_name, movie_field in self.entry_fields.items()}
        self.callback(return_fields, self.selected_tags)
        self.destroy()
    
    def destroy(self):
        """Destroy all widgets of this class."""
        self.outer_frame.destroy()


@dataclass
class MovieField:
    """A support class for attributes of a gui entry field."""
    label_text: str
    database_value: str
    textvariable: tk.StringVar = None
    observer: observerpattern.Observer = None
    
    def __post_init__(self):
        self.textvariable = tk.StringVar()
        self.observer = observerpattern.Observer()
