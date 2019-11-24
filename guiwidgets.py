"""GUI Windows.

This module includes windows for presenting data supplied to it and returning entered data to its
callers.
"""

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

# moviedb-#94
#   Create generic movie input form with:
#       Body frame with input fields. Investigate multiple selection options for tags.
#       Button frame for buttons
#       Observers: Commit button is only active if title and year have values

import tkinter as tk
import tkinter.ttk as ttk
# Python package imports
from dataclasses import dataclass, field
from typing import Callable, List, TypedDict

# Constants
import observerpattern


# Third party package imports
# Project Imports


INTERNAL_NAMES = ('title *', 'year *', 'director', 'length', 'notes', 'tags')
FIELD_TEXTS = ('Title', 'Year', 'Director', 'Length (minutes)', 'Notes', 'Tags')


# API Classes, DataClasses, and TypedDicts


class MovieDict(TypedDict, total=False):
    """A dictionary of movie fields."""
    title: str
    year: int
    director: str
    minutes: int
    notes: str
    tag: List[str]


@dataclass
class MovieGUI:
    parent: tk.Tk
    callback: Callable[[MovieDict], None]
    
    input: MovieDict = field(default_factory=dict, init=False)
    
    def __post_init__(self):
        self.parent.columnconfigure(0, weight=1)
        self.parent.rowconfigure(0, weight=1)
        
        outerframe = ttk.Frame(self.parent)
        outerframe.grid(column=0, row=0, sticky='nsew')
        outerframe.columnconfigure(0, weight=1)
        outerframe.rowconfigure(0, weight=1)
        
        self.create_body(outerframe)
        self.create_buttonbox(outerframe)
        self.create_neurons()
    
    def create_body(self, parent: ttk.Frame):
        bodyframe = ttk.Frame(parent, padding=(10, 25))
        bodyframe.grid(column=0, row=0, sticky='n')
        bodyframe.columnconfigure(0, weight=1, minsize=30)
        bodyframe.columnconfigure(1, weight=1)
        
        fields = {internal_name: MovieField(field_text)
                  for internal_name, field_text
                  in zip(INTERNAL_NAMES, FIELD_TEXTS)}
        # moviedb-#94
        #   Make tags field into multiple choice
        for row_ix, internal_name in enumerate(INTERNAL_NAMES):
            label = ttk.Label(bodyframe, text=fields[internal_name].label_text)
            label.grid(column=0, row=row_ix, sticky='w', padx=5)
            entry = ttk.Entry(bodyframe, textvariable=fields[internal_name].textvariable, width=36)
            entry.grid(column=1, row=row_ix)
    
    def create_buttonbox(self, parent: ttk.Frame):
        # moviedb-#94
        #   Create buttonbox frame
        #   Grid buttonbox frame
        #   Create buttons
        #   Set 'Commit' button callback to the commit_callback method.
        #   Set 'Cancel' button callback to the destroy method.
        #   Set enable/disable'Commit' button depending on changed title and year values
        pass
    
    def create_neurons(self):
        # moviedb-#94
        #   Set actions resulting from observer notificatons.
        pass
    
    def commit_callback(self):
        # moviedb-#94
        #   Call the supplied commit callback with user entered fields values.
        #   Process exceptions (seperate module to handle plethora of SQL exceptions?)
        #   Call destroy
        pass
    
    def destroy(self):
        # moviedb-#94
        #   Destroy the outer frome and its children
        pass


# API Functions


# Internal Module Classes, DataClasses, and TypedDicts
@dataclass
class MovieField:
    label_text: str
    textvariable: tk.StringVar = None
    observer: observerpattern.Observer = None
    
    def __post_init__(self):
        self.textvariable = tk.StringVar()
        self.observer = observerpattern.Observer()

# Internal Module Functions
