"""GUI Windows.

This module includes windows for presenting data supplied to it and returning entered data to its
callers.
"""

#  Copyright© 2019. Stephen Rigden.
#  Last modified 12/23/19, 7:34 AM by stephen.
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
from tkinter import filedialog, messagebox
from typing import Callable, Dict, List, Sequence, TypeVar

import exception
import observerpattern
from config import MovieDict


INTERNAL_NAMES = ('title', 'year', 'director', 'minutes', 'notes')
FIELD_TEXTS = ('Title *', 'Year *', 'Director', 'Length (minutes)', 'Notes')
COMMIT_TEXT = 'Commit'
CANCEL_TEXT = 'Cancel'
SELECT_TAGS_TEXT = 'Select tags'

ParentType = TypeVar('ParentType', tk.Tk, ttk.Frame)


@dataclass
class MovieGUI:
    """ Create a form for entering or editing a movie."""
    parent: tk.Tk
    # A list of all tags in the database.
    tags: Sequence[str]
    # On exit this callback will be called with a dictionary of fields and user entered values.
    callback: Callable[[MovieDict], None]
    # Fields of the movie supplied by the caller.
    caller_fields: MovieDict = field(default_factory=dict)
    # Tags of the movie record supplied by the caller.
    selected_tags: List[str] = field(default_factory=list)
    
    # All widgets of this class will be enclosed in this frame.
    outer_frame: ttk.Frame = field(default=None, init=False, repr=False)
    # A more convenient data structure for entry fields.
    entry_fields: Dict[str, 'EntryField'] = field(default_factory=dict, init=False, repr=False)
    # Neuron controlling enabled state of Commit button
    commit_neuron: observerpattern.Neuron = field(default_factory=observerpattern.Neuron,
                                                  init=False, repr=False)
    
    def __post_init__(self):
        self.outer_frame = ttk.Frame(self.parent)
        self.outer_frame.grid(column=0, row=0, sticky='nsew')
        self.outer_frame.columnconfigure(0, weight=1)
        self.outer_frame.rowconfigure(0, weight=1)
        self.outer_frame.rowconfigure(1, minsize=35)
        
        self.create_body(self.outer_frame)
        self.create_buttonbox(self.outer_frame)
    
    def create_body(self, outerframe: ttk.Frame):
        """Create the body of the form with a column for labels and another for user input fields."""
        # Initialize internal dictionary for field management.
        self.entry_fields = {internal_name: EntryField(field_text,
                                                       self.caller_fields.get(internal_name, ''))
                             for internal_name, field_text
                             in zip(INTERNAL_NAMES, FIELD_TEXTS)}
    
        body_frame = ttk.Frame(outerframe, padding=(10, 25, 10, 0))
        body_frame.grid(column=0, row=0, sticky='n')
        body_frame.columnconfigure(0, weight=1, minsize=30)
        body_frame.columnconfigure(1, weight=1)
    
        # Create entry fields and their labels.
        for row_ix, internal_name in enumerate(INTERNAL_NAMES):
            label = ttk.Label(body_frame, text=self.entry_fields[internal_name].label_text)
            label.grid(column=0, row=row_ix, sticky='e', padx=5)
            entry = ttk.Entry(body_frame, textvariable=self.entry_fields[internal_name].textvariable,
                              width=36)
            entry.grid(column=1, row=row_ix)
            self.entry_fields[internal_name].widget = entry
        
        # Customize title field.
        self.neuron_linker('title', self.commit_neuron, self.neuron_callback)
        
        # Customize minutes field.
        minutes = self.entry_fields['minutes']
        minutes.textvariable.set('0')
        registered_callback = minutes.widget.register(self.validate_int)
        minutes.widget.config(validate='key', validatecommand=(registered_callback, '%S'))
        
        # Customize year field.
        year = self.entry_fields['year']
        year.textvariable.set('2020')
        self.neuron_linker('year', self.commit_neuron, self.neuron_callback, True)
        registered_callback = year.widget.register(self.validate_int)
        year.widget.config(validate='key', validatecommand=(registered_callback, '%S'))
        
        # Create treeview for tag selection.
        # moviedb-#95 The tags of an existing record should be shown in the selected mode.
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
    
    def create_buttonbox(self, outerframe: ttk.Frame):
        """Create the buttons."""
        buttonbox = ttk.Frame(outerframe, padding=(5, 5, 10, 10))
        buttonbox.grid(column=0, row=1, sticky='e')
    
        # Commit button
        commit = ttk.Button(buttonbox, text=COMMIT_TEXT, command=self.commit)
        commit.grid(column=0, row=0)
        commit.bind('<Return>', lambda event, b=commit: b.invoke())
        commit.state(['disabled'])
        self.commit_neuron.register(self.button_state_callback(commit))
    
        # Cancel button
        cancel = ttk.Button(buttonbox, text=CANCEL_TEXT, command=self.destroy)
        cancel.grid(column=1, row=0)
        cancel.bind('<Return>', lambda event, b=cancel: b.invoke())
        cancel.focus_set()
    
    def neuron_linker(self, internal_name: str, neuron: observerpattern.Neuron,
                      neuron_callback: Callable, initial_state: bool = False):
        """Link a field to a neuron."""
        self.entry_fields[internal_name].textvariable.trace_add('write',
                                                                neuron_callback(internal_name, neuron))
        neuron.register_event(internal_name, initial_state)
    
    def neuron_callback(self, internal_name: str, neuron: observerpattern.Neuron) -> Callable:
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
                     != self.entry_fields[internal_name].original_value)
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
    
    def validate_int(self, user_input: str) -> bool:
        """Validate integer input by user.

        Use Case: Supports field validation by Tk
        """
        try:
            int(user_input)
        except ValueError:
            self.parent.bell()
        else:
            return True
        return False
    
    @staticmethod
    def validate_int_range(user_input: int, lowest: int = None, highest: int = None) -> bool:
        """Validate that user input is an integer within a valid range.

        Use Case: Supports field validation by Tk
        """
        # moviedb-#103 Delete this method if validation can be carried out by database integrity checks.
        lowest = user_input > lowest if lowest else True
        highest = user_input < highest if highest else True
        return lowest and highest
    
    def commit(self):
        """The user clicked the commit button."""
        return_fields = {internal_name: movie_field.textvariable.get()
                         for internal_name, movie_field in self.entry_fields.items()}
        
        # Validate the year range
        # moviedb-#103 Replace the literal range limits with the range limits from the SQL schema
        if not self.validate_int_range(int(return_fields['year']), 1877, 10000):
            msg = 'Invalid year.'
            detail = 'The year must be between 1877 and 10000.'
            messagebox.showinfo(parent=self.parent, message=msg, detail=detail)
            return
        
        # Commit and exit
        try:
            self.callback(return_fields, self.selected_tags)
        except exception.MovieDBConstraintFailure:
            msg = 'Database constraint failure.'
            detail = 'This title and year are already present in the database.'
            messagebox.showinfo(parent=self.parent, message=msg, detail=detail)
        else:
            self.destroy()
    
    def destroy(self):
        """Destroy all widgets of this class."""
        self.outer_frame.destroy()


def gui_messagebox(parent: ParentType, message: str, detail: str = '', icon: str = 'info'):
    """Present a Tk messagebox."""
    messagebox.showinfo(parent, message, detail=detail, icon=icon)


def gui_askopenfilename(parent: ParentType, filetypes: Sequence[Sequence[str]]):
    """Present a Tk askopenfilename."""
    return filedialog.askopenfilename(parent=parent, filetypes=filetypes)


@dataclass
class EntryField:
    """A support class for attributes of a gui entry field."""
    label_text: str
    original_value: str
    widget: ttk.Entry = None
    textvariable: tk.StringVar = None
    observer: observerpattern.Observer = None
    
    def __post_init__(self):
        self.textvariable = tk.StringVar()
        self.observer = observerpattern.Observer()