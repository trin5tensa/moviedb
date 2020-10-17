"""GUI Windows.

This module includes windows for presenting data supplied to it and returning entered data to its
callers.
"""

#  Copyright© 2020. Stephen Rigden.
#  Last modified 6/23/20, 6:46 AM by stephen.
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

import itertools
import tkinter as tk
import tkinter.ttk as ttk
from dataclasses import dataclass, field
from tkinter import filedialog, messagebox
from typing import Callable, Dict, Mapping, Sequence, Tuple, TypeVar

import config
import exception
import neurons


MOVIE_FIELD_NAMES = ('title', 'year', 'director', 'minutes', 'notes',)
MOVIE_FIELD_TEXTS = ('Title', 'Year', 'Director', 'Length (minutes)', 'Notes',)
TAG_TREEVIEW_INTERNAL_NAME = 'tag treeview'
TAG_FIELD_NAMES = ('tag',)
TAG_FIELD_TEXTS = ('Tag',)
SELECT_TAGS_TEXT = 'Select tags'
SEARCH_TEXT = 'Search'
COMMIT_TEXT = 'Commit'
DELETE_TEXT = 'Delete'
CANCEL_TEXT = 'Cancel'

ParentType = TypeVar('ParentType', tk.Tk, ttk.Frame)


# moviedb-#201
#   Switch handlers module to use guiwidgets_2.AddMovieGUI
#   Integration test guiwidgets_2.AddMovieGUI
#   Rename guiwidgets.AddMovieGUI. This will be retained until the whole module is deleted.
#   Document deletion plan for guiwidgets.AddMovieGUI and why it cannot be deleted at this time.


@dataclass
class AddMovieGUI:
    """Create and manage a Tk input form which enables a user's supply of the data needed to
    add a movie."""
    
    parent: tk.Tk
    # On commit this callback will be called with a dictionary of fields and user entered values.
    commit_callback: Callable[[config.MovieTypedDict, Sequence[str]], None]

    selected_tags: Sequence[str] = field(default_factory=tuple, init=False, repr=False)
    # All widgets of this class will be enclosed in this frame.
    outer_frame: ttk.Frame = field(default=None, init=False, repr=False)
    # A more convenient data structure for entry fields.
    entry_fields: Dict[str, 'EntryField'] = field(default_factory=dict, init=False, repr=False)
    
    def __post_init__(self):
        # Initialize an internal dictionary to simplify field data management.
        self.entry_fields = create_entry_fields(MOVIE_FIELD_NAMES, MOVIE_FIELD_TEXTS)

        # Create outer frames to hold fields and buttons.
        self.outer_frame, body_frame, buttonbox = create_input_form_framing(self.parent)

        # Create labels and fields
        create_input_form_fields(body_frame, MOVIE_FIELD_NAMES, self.entry_fields)
        focus_set(self.entry_fields[MOVIE_FIELD_NAMES[0]].widget)
        
        # Create movie tags treeview
        # moviedb-#201 (5) Test MovieTreeview
        # moviedb-#201 (5) Code call to MovieTreeview

        # Populate buttonbox with commit and cancel buttons
        column_num = itertools.count()
        commit_button = create_button(buttonbox, COMMIT_TEXT, column=next(column_num),
                                      command=self.commit, enabled=False)
        create_button(buttonbox, CANCEL_TEXT, column=next(column_num),
                      command=self.destroy, enabled=False)
        
        # Link neuron to commit button
        button_enabler = enable_button_wrapper(commit_button)
        neuron = link_and_neuron_to_button(button_enabler)
        
        # Link neuron to title field
        notify_neuron = notify_neuron_wrapper(self.entry_fields, MOVIE_FIELD_NAMES[0], neuron)
        link_field_to_neuron(self.entry_fields, MOVIE_FIELD_NAMES[0], neuron, notify_neuron)

        # Link neuron to year field
        notify_neuron = notify_neuron_wrapper(self.entry_fields, MOVIE_FIELD_NAMES[1], neuron)
        link_field_to_neuron(self.entry_fields, MOVIE_FIELD_NAMES[1], neuron, notify_neuron)

    # moviedb-#201 (4) Test renamed AddMovieGUI.treeview_callback  (tag_selection_callback?)
    # moviedb-#201 (4) Code call to renamed AddMovieGUI.MovieTreeview

    def commit(self):
        """The user clicked the 'Commit' button."""
        return_fields = {internal_name: movie_field.textvariable.get()
                         for internal_name, movie_field in self.entry_fields.items()}
    
        # Validate the year range
        # moviedb-#103 SSOT: Replace the literal range limits with the range limits from the SQL schema.
        if not validate_int_range(int(return_fields['year']), 1877, 10000):
            msg = 'Invalid year.'
            detail = 'The year must be between 1877 and 10000.'
            messagebox.showinfo(parent=self.parent, message=msg, detail=detail)
            return
    
        # Commit and exit
        try:
            self.commit_callback(return_fields, self.selected_tags)
    
        # Alert user and stay on page
        except exception.MovieDBConstraintFailure:
            msg = 'Database constraint failure.'
            detail = 'A movie with this title and year is already present in the database.'
            messagebox.showinfo(parent=self.parent, message=msg, detail=detail)
    
    def destroy(self):
        """Destroy all widgets of this class."""
        self.outer_frame.destroy()


@dataclass
class AddTagGUI:
    """ Present a form for adding a tag to the user."""
    parent: tk.Tk
    add_tag_callback: Callable[[str], None]
    
    # The main outer frame of this class.
    outer_frame: ttk.Frame = field(default=None, init=False, repr=False)
    
    # An internal dictionary to simplify field data management.
    entry_fields: Dict[str, 'EntryField'] = field(default_factory=dict, init=False, repr=False)
    
    # noinspection DuplicatedCode
    def __post_init__(self):
        # Initialize an internal dictionary to simplify field data management.
        self.entry_fields = create_entry_fields(TAG_FIELD_NAMES, TAG_FIELD_TEXTS)
        
        # Create outer frames to hold fields and buttons.
        self.outer_frame, body_frame, buttonbox = create_input_form_framing(self.parent)
        
        # Create label and field
        create_input_form_fields(body_frame, TAG_FIELD_NAMES, self.entry_fields)
        
        # Populate buttonbox with commit and cancel buttons
        column_num = itertools.count()
        commit_button = create_button(buttonbox, COMMIT_TEXT, column=next(column_num),
                                      command=self.commit, enabled=False)
        create_button(buttonbox, CANCEL_TEXT, column=next(column_num),
                      command=self.destroy).focus_set()
        
        # Link commit button to tag field
        button_enabler = enable_button_wrapper(commit_button)
        neuron = link_or_neuron_to_button(button_enabler)
        link_field_to_neuron(self.entry_fields, TAG_FIELD_NAMES[0], neuron,
                             notify_neuron_wrapper(self.entry_fields,
                                                   TAG_FIELD_NAMES[0], neuron))

    def commit(self):
        """The user clicked the 'Commit' button."""
        self.add_tag_callback(self.entry_fields[TAG_FIELD_NAMES[0]].textvariable.get())
        self.destroy()

    def destroy(self):
        """Destroy this instance's widgets."""
        self.outer_frame.destroy()


@dataclass
class SearchTagGUI:
    """Present a form for creating a search pattern which may be used to search the database for
    matching tags.
    """
    parent: tk.Tk
    search_tag_callback: Callable[[str], None]

    # The main outer frame of this class.
    outer_frame: ttk.Frame = field(default=None, init=False, repr=False)

    # An internal dictionary to simplify field data management.
    entry_fields: Dict[str, 'EntryField'] = field(default_factory=dict, init=False, repr=False)

    # noinspection DuplicatedCode,DuplicatedCode
    def __post_init__(self):
        """Create the Tk widget."""
    
        # Initialize an internal dictionary to simplify field data management.
        self.entry_fields = create_entry_fields(TAG_FIELD_NAMES, TAG_FIELD_TEXTS)
    
        # Create the outer frames to hold fields and buttons.
        self.outer_frame, body_frame, buttonbox = create_input_form_framing(self.parent)
    
        # Create the field label and field entry widgets.
        create_input_form_fields(body_frame, TAG_FIELD_NAMES, self.entry_fields)
        
        # Populate buttonbox with the search and cancel buttons.
        column_num = itertools.count()
        search_button = create_button(buttonbox, SEARCH_TEXT, column=next(column_num),
                                      command=self.search, enabled=False)
        create_button(buttonbox, CANCEL_TEXT, column=next(column_num),
                      command=self.destroy).focus_set()
        
        # Link the search button to the tag field.
        button_enabler = enable_button_wrapper(search_button)
        neuron = link_or_neuron_to_button(button_enabler)
        notify_neuron = notify_neuron_wrapper(self.entry_fields, TAG_FIELD_NAMES[0], neuron)
        link_field_to_neuron(self.entry_fields, TAG_FIELD_NAMES[0], neuron, notify_neuron)
    
    def search(self):
        """Respond to the user's click of the 'Search' button."""
        try:
            pattern = self.entry_fields[TAG_FIELD_NAMES[0]].textvariable.get()
            self.search_tag_callback(pattern)
        except exception.DatabaseSearchFoundNothing:
            # Warn user and give user the opportunity to reenter the search criteria.
            parent = self.parent
            message = 'No matches'
            detail = 'There are no matching tags in the database.'
            gui_messagebox(parent, message, detail)
        else:
            self.destroy()
    
    def destroy(self):
        """Destroy the Tk widgets of this class."""
        self.outer_frame.destroy()


@dataclass
class EditTagGUI:
    """ Present a form for editing or deleting a tag to the user."""
    parent: tk.Tk
    tag: str
    delete_tag_callback: Callable[[], None]
    edit_tag_callback: Callable[[str], None]

    # The main outer frame of this class.
    outer_frame: ttk.Frame = field(default=None, init=False, repr=False)

    # An internal dictionary to simplify field data management.
    entry_fields: Dict[str, 'EntryField'] = field(default_factory=dict, init=False, repr=False)

    # noinspection DuplicatedCode
    def __post_init__(self):
        # Initialize an internal dictionary to simplify field data management.
        self.entry_fields = create_entry_fields(TAG_FIELD_NAMES, TAG_FIELD_TEXTS)
        self.entry_fields[TAG_FIELD_NAMES[0]].original_value = self.tag
    
        # Create outer frames to hold fields and buttons.
        self.outer_frame, body_frame, buttonbox = create_input_form_framing(self.parent)
    
        # Create field label and field entry widgets.
        create_input_form_fields(body_frame, TAG_FIELD_NAMES, self.entry_fields)
    
        # Populate buttonbox with commit, delete, and cancel buttons
        column_num = itertools.count()
        commit_button = create_button(buttonbox, COMMIT_TEXT, column=next(column_num),
                                      command=self.commit, enabled=False)
        create_button(buttonbox, DELETE_TEXT, column=next(column_num), command=self.delete)
        create_button(buttonbox, CANCEL_TEXT, column=next(column_num),
                      command=self.destroy).focus_set()

        # Link commit button to tag field
        button_enabler = enable_button_wrapper(commit_button)
        neuron = link_or_neuron_to_button(button_enabler)
        notify_neuron = notify_neuron_wrapper(self.entry_fields, TAG_FIELD_NAMES[0], neuron)
        link_field_to_neuron(self.entry_fields, TAG_FIELD_NAMES[0], neuron, notify_neuron)
    
    def commit(self):
        """The user clicked the 'Commit' button."""
        self.edit_tag_callback(self.entry_fields[TAG_FIELD_NAMES[0]].textvariable.get())
        self.destroy()
    
    def delete(self):
        """The user clicked the 'Delete' button.
        
        Get the user's confirmation of deletion with a dialog window. Either exit the method or call
        the registered deletion callback."""
        if messagebox.askyesno(message=f"Do you want to delete tag '{self.tag}'?",
                               icon='question', default='no', parent=self.parent):
            self.delete_tag_callback()
            self.destroy()
    
    def destroy(self):
        """Destroy this instance's widgets."""
        self.outer_frame.destroy()


@dataclass
class SelectTagGUI:
    """Allow the user to select one tag record from a Tk treeview of tag records."""
    parent: tk.Tk
    select_tag_callback: Callable[[str], None]
    tags_to_show: Sequence[str]
    
    # The main outer frame of this class.
    outer_frame: ttk.Frame = field(default=None, init=False, repr=False)
    
    def __post_init__(self):
        # Create outer frames to hold fields and buttons.
        self.outer_frame, body_frame, buttonbox = create_body_and_button_frames(self.parent)
        
        # Create and grid treeview
        tree = ttk.Treeview(body_frame, columns=[], height=10, selectmode='browse')
        tree.grid(column=0, row=0, sticky='w')
        
        # Specify column width and title
        tree.column('#0', width=350)
        tree.heading('#0', text=TAG_FIELD_TEXTS[0])
        
        # Populate the treeview rows
        for tag in self.tags_to_show:
            tree.insert('', 'end', iid=tag, text=tag, values=[], tags=TAG_FIELD_NAMES[0])
        
        # Bind the treeview callback
        tree.bind('<<TreeviewSelect>>', func=self.selection_callback_wrapper(tree))
        
        # Create the button
        column_num = 0
        create_button(buttonbox, CANCEL_TEXT, column_num, self.destroy)

    def selection_callback_wrapper(self, tree: ttk.Treeview) -> Callable:
        """Call the callback provided by the caller and destroy all Tk widgets associated with this
        class.
        
        Args:
            tree:

        Returns:
            The callback.
        """
    
        # noinspection PyUnusedLocal
        def selection_callback(*args):
            """Save the newly changed user selection.

            Args:
                *args: Not used. Needed for compatibility with Tk:Tcl caller.
            """
            tag = tree.selection()[0]
            self.select_tag_callback(tag)
            self.destroy()
    
        return selection_callback
    
    def destroy(self):
        """Destroy all Tk widgets associated with this class."""
        self.outer_frame.destroy()


def gui_messagebox(parent: ParentType, message: str, detail: str = '', icon: str = 'info'):
    """Present a Tk messagebox."""
    messagebox.showinfo(parent, message, detail=detail, icon=icon)


def gui_askopenfilename(parent: ParentType, filetypes: Sequence[Sequence[str]]):
    """Present a Tk askopenfilename."""
    return filedialog.askopenfilename(parent=parent, filetypes=filetypes)


def focus_set(entry: ttk.Entry):
    """Set initial focus for this class."""
    entry.focus_set()
    entry.select_range(0, tk.END)
    entry.icursor(tk.END)


@dataclass
class EntryField:
    """A support class for attributes of a gui entry field."""
    label_text: str
    original_value: str
    widget: ttk.Entry = None
    textvariable: tk.StringVar = None
    observer: neurons.Observer = field(default_factory=neurons.Observer, init=False, repr=False)
    
    def __post_init__(self):
        self.textvariable = tk.StringVar()


@dataclass
class MovieTagTreeview:
    """Create and manage a treeview and a descriptive label.
    
    The user callback will be called whenever the user has changes the selection. The observer will
    also be notified with a boolean message stating if the current selection differs from the original
    selection.
    """
    
    # Internal name of treeview
    internal_name: str

    # The frame which contains the treeview.
    body_frame: ttk.Frame
    # The tk grid row of the label and treeview within the frame's grid.
    row: int
    # The tk grid column of the label within the frame's grid. The treeview will be
    #   placed in the cell to the right.
    column: int
    label_text: str
    # A list of all the items which will be displayed in the treeview.
    items: Sequence[str]
    # Caller's callback for notification of reselection.
    user_callback: Callable[[Sequence[str]], None]

    # Items to be selected on opening.
    initial_selection: Sequence[str] = field(default_factory=list)
    observer: neurons.Observer = field(default_factory=neurons.Observer, init=False)
    
    def __call__(self) -> neurons.Observer:
        # Create the label
        label = ttk.Label(self.body_frame, text=self.label_text, padding=(0, 2))
        label.grid(column=self.column, row=self.row, sticky='ne', padx=5)

        # Create a frame for the treeview and its scrollbar
        treeview_frame = ttk.Frame(self.body_frame, padding=5)
        treeview_frame.grid(column=self.column + 1, row=self.row, sticky='w')
        
        # Create the treeview
        treeview = ttk.Treeview(treeview_frame, columns=('tags',), height=10, selectmode='extended',
                                show='tree', padding=5)
        treeview.grid(column=0, row=0, sticky='w')
        treeview.column('tags', width=100)
        treeview.bind('<<TreeviewSelect>>',
                      func=self.selection_callback_wrapper(treeview, self.user_callback))
        
        # Create the scrollbar
        scrollbar = ttk.Scrollbar(treeview_frame, orient=tk.VERTICAL, command=treeview.yview)
        scrollbar.grid(column=1, row=0)
        treeview.configure(yscrollcommand=scrollbar.set)
        
        # Populate the treeview
        for item in self.items:
            treeview.insert('', 'end', item, text=item, tags='tags')
        treeview.selection_add(self.initial_selection)

        return self.observer

    def selection_callback_wrapper(self, treeview: ttk.Treeview,
                                   user_callback: Callable[[Sequence[str]], None]) -> Callable:
        """Create a callback which will be called whenever the user selection is changed.

        Args:
            treeview:
            user_callback:

        Returns: The callback.
        """
    
        # noinspection PyUnusedLocal
        # @wraps
        def selection_callback(*args):
            """Notify MovieTreeview's caller and observer's notifees.

            Args:
                *args: Not used. Needed for compatibility with Tk:Tcl caller.
            """
            current_selection = treeview.selection()
            user_callback(current_selection)
            self.observer.notify(self.internal_name,
                                 set(current_selection) != set(self.initial_selection))
    
        return selection_callback
    

def create_entry_fields(names: Sequence[str], texts: Sequence[str]) -> dict:
    """Create an internal dictionary to simplify field data management.
    
    Args:
        names: A sequence of names of the fields
        texts: A sequence of text to be seen by the user.

    Returns:
        key: The internal name of the field.
        value: An EntryField instance.
    """
    return {internal_name: EntryField(field_text, '')
            for internal_name, field_text in zip(names, texts)}


def create_body_and_button_frames(parent: tk.Tk) -> Tuple[ttk.Frame, ttk.Frame, ttk.Frame]:
    """Create the outer frames for an input form.

    This consists of an upper body and a lower buttonbox frame.
    
    Note: Do not call this function if thw input form has label and entry widgets. Use the higher
    level function create_input_form_framing.

    Args:
        parent: The Tk parent frame.

    Returns:
        Outer frame which contains the body and buttonbox frames.
        Body frame
        Buttonbox frame
    """
    outer_frame = ttk.Frame(parent)
    outer_frame.grid(column=0, row=0, sticky='nsew')
    outer_frame.columnconfigure(0, weight=1)
    
    body_frame = ttk.Frame(outer_frame, padding=(10, 25, 10, 0))
    body_frame.grid(column=0, row=0, sticky='n')
    
    buttonbox = ttk.Frame(outer_frame, padding=(5, 5, 10, 10))
    buttonbox.grid(column=0, row=1, sticky='e')
    
    return outer_frame, body_frame, buttonbox


def create_input_form_framing(parent: tk.Tk) -> Tuple[ttk.Frame, ttk.Frame, ttk.Frame]:
    """Create the outer frames for an input form.

    An input body frame has two columns, one for the field labels and one for the entry fields.
    
    Note: For a plain form without columns call the lower level function create_body_and_button_frames.

    Args:
        parent: The Tk parent frame.

    Returns:
        Outer frame which contains the body and buttonbox frames.
        Body frame
        Buttonbox frame
    """
    outer_frame, body_frame, buttonbox = create_body_and_button_frames(parent)
    outer_frame.rowconfigure(0, weight=1)
    outer_frame.rowconfigure(1, minsize=35)
    return outer_frame, body_frame, buttonbox


def create_input_form_fields(body_frame: ttk.Frame, names: Sequence[str],
                             entry_fields: Mapping[str, EntryField]):
    """Create the labels and fields for an entry form.
    
    Args:
        body_frame: The outer frame for the labels and fields.
        names: A sequence of names of the fields.
        entry_fields: A mapping of the field names to an instance of EntryField.
    """
    
    # Create a column for the labels.
    body_frame.columnconfigure(0, weight=1, minsize=30)
    # Create a column for the fields.
    body_frame.columnconfigure(1, weight=1)

    for row_ix, internal_name in enumerate(names):
        entry_field = entry_fields[internal_name]
        label = ttk.Label(body_frame, text=entry_field.label_text)
        label.grid(column=0, row=row_ix, sticky='e', padx=5)
        entry = ttk.Entry(body_frame, textvariable=entry_field.textvariable, width=36)
        entry.grid(column=1, row=row_ix)
        entry_field.widget = entry
        entry_field.textvariable.set(entry_field.original_value)


def create_button(buttonbox: ttk.Frame, text: str, column: int, command: Callable,
                  enabled: bool = True) -> ttk.Button:
    """Create a button
    
    Args:
        buttonbox: The enclosing buttonbox.
        text: The enclosing buttonbox.
        column: The index of the button in the buttonbox. '0' is leftmost position.
        command: The command to be executed when the button is clicked.
        enabled: Sets the initial enabled or disables state of the button.

    Returns:
        The button
    """
    button = ttk.Button(buttonbox, text=text, command=command)
    button.grid(column=column, row=0)
    button.bind('<Return>', lambda event, b=button: b.invoke())
    if not enabled:
        button.state(['disabled'])
    return button


def enable_button_wrapper(button: ttk.Button) -> Callable:
    """Create the callback for a button.

    This will be registered with a neuron as a notifee.
    
    Args:
        button:

    Returns:
        A callable which will set the enabled state of the button.
    """
    
    def enable_button(state: bool):
        """Enable or disable the button.
        
        Args:
            state:
        """
        if state:
            button.state(['!disabled'])
        else:
            button.state(['disabled'])
    
    return enable_button


def link_or_neuron_to_button(change_button_state: Callable) -> neurons.OrNeuron:
    """Create an "Or' neuron and link it to a button.
    
    Args:
        change_button_state:

    Returns:
        Neuron
    """
    neuron = neurons.OrNeuron()
    neuron.register(change_button_state)
    return neuron


def link_and_neuron_to_button(change_button_state: Callable) -> neurons.AndNeuron:
    """Create an "Or' neuron and link it to a button.
    
    Args:
        change_button_state:

    Returns:
        Neuron
    """
    neuron = neurons.AndNeuron()
    neuron.register(change_button_state)
    return neuron


def link_field_to_neuron(entry_fields: dict, name: str, neuron: neurons.Neuron, notify_neuron: Callable):
    """Link the fields associated with a button to its neuron.
    
    Args:
        entry_fields: A mapping of field names to instances of EntryField.
        name: …of the field being mapped to the neuron.
        neuron:
        notify_neuron:
    """
    entry_fields[name].textvariable.trace_add('write', notify_neuron)
    neuron.register_event(name)


def notify_neuron_wrapper(entry_fields: dict, name: str, neuron: neurons.Neuron) -> Callable:
    """Create the callback for an observed field.

        This will be registered as the 'trace_add' callback for an entry field.
    
    Args:
        entry_fields: A mapping of the field names to instances of EntryField.
        name: Field name.
        neuron: The neuron which will be notified of the field's state.

    Returns:
        The callback which will be called when the field is changed.
    """

    # noinspection PyUnusedLocal
    def notify_neuron(*args):
        """Call the neuron when the field changes.

        Args:
            *args: Not used. Required to match unused arguments from caller.
        """
        state = (entry_fields[name].textvariable.get()
                 != str(entry_fields[name].original_value))
        neuron(name, state)
    
    return notify_neuron


def validate_int_range(user_input: int, lowest: int = None, highest: int = None) -> bool:
    """Validate that user input is an integer within a valid range.

    Use Case: Supports field validation by Tk
    """
    
    # moviedb-#201 Refactor this method if validation can be carried out by
    #  database integrity checks >>or
    #  >>or Test this function
    lowest = user_input > lowest if lowest else True
    highest = user_input < highest if highest else True
    return lowest and highest
