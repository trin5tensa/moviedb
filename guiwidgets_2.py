"""GUI Windows.

This module includes windows for presenting data supplied to it and returning entered data to its
callers.
"""
#  Copyright (c) 2022-2023. Stephen Rigden.
#  Last modified 1/19/23, 8:56 AM by stephen.
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
import queue
import tkinter as tk
import tkinter.ttk as ttk
from dataclasses import dataclass, field
from tkinter import filedialog, messagebox
from typing import Callable, Dict, Iterable, Iterator, Mapping, Sequence, Tuple, TypeVar

import config
import exception
import neurons

MOVIE_FIELD_NAMES = ('title', 'year', 'director', 'minutes', 'notes',)
MOVIE_FIELD_TEXTS = ('Title', 'Year', 'Director', 'Length (minutes)', 'Notes',)
TAG_FIELD_NAMES = ('tag',)
TAG_FIELD_TEXTS = ('Tag',)
SELECT_TAGS_TEXT = 'Select tags'
SEARCH_TEXT = 'Search'
COMMIT_TEXT = 'Commit'
SAVE_TEXT = 'Save'
DELETE_TEXT = 'Delete'
CANCEL_TEXT = 'Cancel'

ParentType = TypeVar('ParentType', tk.Tk, tk.Toplevel, ttk.Frame)


@dataclass
class AddMovieGUI:
    """Create and manage a Tk input form which allows a user to supply the data needed to
    add a movie."""

    parent: tk.Tk
    # When the user clicks the commit button this will be called with a dictionary of fields and user entered values.
    commit_callback: Callable[[config.MovieTypedDict, Sequence[str]], None]
    # When the user changes the title field this will ba called with the field's text.
    tmdb_search_callback: Callable[[str, queue.LifoQueue], None]
    # This is a complete list of all the tags in the database
    all_tags: Sequence[str]

    # All widgets created by this class will be enclosed in this frame.
    outer_frame: ttk.Frame = field(default=None, init=False, repr=False)
    # A more convenient data structure for entry fields.
    entry_fields: Dict[str, '_EntryField'] = field(default_factory=dict, init=False, repr=False)
    title: str = field(default=None, init=False, repr=False)

    # Treeview for tags.
    treeview: '_MovieTagTreeview' = field(default=None, init=False, repr=False)
    selected_tags: Sequence[str] = field(default_factory=tuple, init=False, repr=False)

    # Treeview for IMDB.
    tmdb_treeview: ttk.Treeview = field(default=None, init=False, repr=False)

    # These variables are used for the consumer end of the TMDB producer/consumer pattern.
    tmdb_work_queue: queue.LifoQueue = field(default_factory=queue.Queue, init=False, repr=False)
    work_queue_poll: int = 40
    recall_id: str = field(default=None, init=False, repr=False, compare=False)
    tmdb_movies: dict[str, dict] = field(default_factory=dict, init=False, repr=False)

    # These variables help to decide if the user has finished entering the title.
    last_text_queue_timer: int = 1000
    last_text_event_id: str = ''

    def __post_init__(self):
        # Initialize an internal dictionary to simplify field data management.
        self.entry_fields = _create_entry_fields(MOVIE_FIELD_NAMES, MOVIE_FIELD_TEXTS)
        self.title = MOVIE_FIELD_NAMES[0]
        year = MOVIE_FIELD_NAMES[1]

        # Create frames to hold fields and buttons.
        self.outer_frame, body_frame, buttonbox, internet_frame = self.framing(self.parent)

        # Create labels and fields.
        label_field = _LabelFieldWidget(body_frame)
        for movie_field_name in MOVIE_FIELD_NAMES:
            label_field.add_entry_row(self.entry_fields[movie_field_name])
        _focus_set(self.entry_fields[self.title].widget)

        # Create a treeview for movie tags.
        self.treeview = label_field.add_treeview_row(SELECT_TAGS_TEXT, items=self.all_tags,
                                                     callers_callback=self.treeview_callback)

        # Create a treeview for movies retrieved from tmdb.
        self.tmdb_treeview = ttk.Treeview(internet_frame,
                                     columns=('title', 'year', 'director'),
                                     show=['headings'],
                                     height=20,
                                     selectmode='browse')
        self.tmdb_treeview.column('title', width=300, stretch=True)
        self.tmdb_treeview.heading('title', text='Title', anchor='w')
        self.tmdb_treeview.column('year', width=40, stretch=True)
        self.tmdb_treeview.heading('year', text='Year', anchor='w')
        self.tmdb_treeview.column('director', width=200, stretch=True)
        self.tmdb_treeview.heading('director', text='Director', anchor='w')
        self.tmdb_treeview.grid(column=0, row=0, sticky='nsew')
        self.tmdb_treeview.bind('<<TreeviewSelect>>',
                                func=self.tmdb_treeview_callback)

        # Populate buttonbox with commit and cancel buttons.
        column_num = itertools.count()
        commit_button = _create_button(buttonbox, COMMIT_TEXT, column=next(column_num),
                                       command=self.commit, enabled=False)
        _create_button(buttonbox, CANCEL_TEXT, column=next(column_num),
                       command=self.destroy, enabled=True)

        # Link commit neuron to commit button.
        commit_button_enabler = _enable_button(commit_button)
        commit_neuron = _create_buttons_andneuron(commit_button_enabler)

        # Link commit neuron to year field.
        observer = _create_the_fields_observer(self.entry_fields, year, commit_neuron)
        self.entry_fields[year].observer = observer
        _link_field_to_neuron(self.entry_fields, year, commit_neuron, observer)

        # Link a new observer to the title field.
        observer = neurons.Observer()
        self.entry_fields[self.title].observer = observer
        observer.register(self.call_title_notifees(commit_neuron))
        _link_field_to_neuron(self.entry_fields, self.title, commit_neuron, observer.notify)

        # Start the tmdb_work_queue polling
        self.tmdb_consumer()

    def call_title_notifees(self, commit_neuron: neurons.AndNeuron) -> Callable:
        """
        This function creates the notifee for the title field observer which will be called whenever
        the user changes the title.
        
        Args:
            commit_neuron: The neuron which enable and disables the commit button.

        Returns:
            The notifee function
        """

        # noinspection PyUnusedLocal
        def func(*args):
            """
            This function organizes the actions which respond to the user's changes to the title field.
            
            Args:
                *args: Not used. This is required to match unused arguments from caller.
            """
            text = self.entry_fields[self.title].textvariable.get()

            # Invoke a database search
            self.tmdb_search(text)

            # Notify the commit button neuron
            commit_neuron(self.title, bool(text))

        return func

    def tmdb_search(self, substring: str):
        """
        Initiate a TMDB search for matching movies titles when the user has finished typing.
        
        Args:
            substring: The current content of the title field.
        """
        # Valid strings for search are > zero length.
        if substring:

            # Delete the previous call to tmdb_search_callback if it still in the event queue. It will only be in the
            # event queue if it is still waiting to be executed.
            if self.last_text_event_id:
                self.parent.after_cancel(self.last_text_event_id)

            # Place a new call to tmdb_search_callback.
            self.last_text_event_id = self.parent.after(self.last_text_queue_timer, self.tmdb_search_callback,
                                                        substring, self.tmdb_work_queue)

    def tmdb_consumer(self):
        """Consumer of queued records of movies found on the TMDB website."""

        try:
            # Tkinter can't wait for the thread blocking `get` method…
            work_package = self.tmdb_work_queue.get_nowait()

        except queue.Empty:
            # …so an empty queue is not exceptional.
            pass

        else:
            # Process a work package.
            items = self.tmdb_treeview.get_children()
            self.tmdb_treeview.delete(*items)
            self.tmdb_movies = {}
            for ix, movie in enumerate(work_package):
                movie['director'] = ', '.join(movie['director'])
                item_id = self.tmdb_treeview.insert('', 'end', values=(
                    movie['title'],
                    movie['year'],
                    movie['director']))
                self.tmdb_movies[item_id] = movie

        finally:
            # Have tkinter call this function again after the poll interval.
            self.recall_id = self.parent.after(self.work_queue_poll, self.tmdb_consumer)

    def treeview_callback(self, reselection: Sequence[str]):
        """Update selected tags with the user's changes."""
        self.selected_tags = reselection

    def tmdb_treeview_callback(self, *args, **kwargs):
        # todo docs
        # todo test this method
        if self.tmdb_treeview.selection():
            item_id = self.tmdb_treeview.selection()[0]
        else:
            return

        for k, v in self.tmdb_movies[item_id].items():
            self.entry_fields[k].textvariable.set(v)


    def commit(self):
        """The user clicked the 'Commit' button."""
        return_fields = {internal_name: movie_field.textvariable.get()
                         for internal_name, movie_field in self.entry_fields.items()}

        # Commit and exit
        try:
            self.commit_callback(return_fields, self.selected_tags)

        # Alert user to title and year constraint failure.
        except exception.MovieDBConstraintFailure:
            msg = 'Database constraint failure.'
            detail = 'A movie with this title and year is already present in the database.'
            messagebox.showinfo(parent=self.parent, message=msg, detail=detail)

        # Alert user to invalid year.
        except exception.MovieYearConstraintFailure as exc:
            msg = exc.args[0]
            messagebox.showinfo(parent=self.parent, message=msg)

        # Clear fields ready for next entry.
        else:
            _clear_input_form_fields(self.entry_fields)
            self.treeview.clear_selection()
            items = self.tmdb_treeview.get_children()
            self.tmdb_treeview.delete(*items)

    def destroy(self):
        """Destroy all widgets of this class."""
        self.parent.after_cancel(self.recall_id)
        self.outer_frame.destroy()

    @staticmethod
    def framing(parent: ParentType) -> tuple[ttk.Frame, ttk.Frame, ttk.Frame, ttk.Frame]:
        """ Create framing.

        Structure:
            outer_frame: Frame
                input_zone: Frame
                    input_form: Frame
                    buttonbox: Frame
                internet_zone: Frame

        Args:
            parent:

        Returns:
            outer_frame, fields, buttonbox, internet
        """
        outer_frame = ttk.Frame(parent, padding=10)
        outer_frame.grid(column=0, row=0, sticky='nsew')
        outer_frame.columnconfigure(0, weight=1)
        outer_frame.columnconfigure(1, weight=1000)
        outer_frame.rowconfigure(0)

        input_zone = ttk.Frame(outer_frame, padding=10)
        input_zone.grid(column=0, row=0, sticky='nw')
        input_zone.columnconfigure(0, weight=1, minsize=25)

        internet_zone = ttk.Frame(outer_frame, padding=10)
        internet_zone.grid(column=1, row=0, sticky='nw')
        internet_zone.columnconfigure(0, weight=1, minsize=25)

        input_form = ttk.Frame(input_zone, padding=10)
        input_form.grid(column=0, row=0, sticky='new')

        buttonbox = ttk.Frame(input_zone, padding=(5, 5, 10, 10))
        buttonbox.grid(column=0, row=1, sticky='ne')

        return outer_frame, input_form, buttonbox, internet_zone


@dataclass
class AddTagGUI:
    """ Present a form for adding a tag to the user."""
    parent: tk.Tk
    add_tag_callback: Callable[[str], None]

    # The main outer frame of this class.
    outer_frame: ttk.Frame = field(default=None, init=False, repr=False)

    # An internal dictionary to simplify field data management.
    entry_fields: Dict[str, '_EntryField'] = field(default_factory=dict, init=False, repr=False)

    # noinspection DuplicatedCode
    def __post_init__(self):
        # Initialize an internal dictionary to simplify field data management.
        self.entry_fields = _create_entry_fields(TAG_FIELD_NAMES, TAG_FIELD_TEXTS)

        # Create outer frames to hold fields and buttons.
        self.outer_frame, body_frame, buttonbox = _create_input_form_framing(self.parent)

        # Create label and field
        label_field = _LabelFieldWidget(body_frame)
        for movie_field_name in TAG_FIELD_NAMES:
            label_field.add_entry_row(self.entry_fields[movie_field_name])

        # Populate buttonbox with commit and cancel buttons
        column_num = itertools.count()
        commit_button = _create_button(buttonbox, COMMIT_TEXT, column=next(column_num),
                                       command=self.commit, enabled=False)
        _create_button(buttonbox, CANCEL_TEXT, column=next(column_num),
                       command=self.destroy).focus_set()

        # Link commit button to tag field
        button_enabler = _enable_button(commit_button)
        neuron = _create_button_orneuron(button_enabler)
        _link_field_to_neuron(self.entry_fields, TAG_FIELD_NAMES[0], neuron,
                              _create_the_fields_observer(self.entry_fields, TAG_FIELD_NAMES[0], neuron))
        self.entry_fields[TAG_FIELD_NAMES[0]].observer = neuron

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
    entry_fields: Dict[str, '_EntryField'] = field(default_factory=dict, init=False, repr=False)

    # noinspection DuplicatedCode,DuplicatedCode
    def __post_init__(self):
        """Create the Tk widget."""

        # Initialize an internal dictionary to simplify field data management.
        self.entry_fields = _create_entry_fields(TAG_FIELD_NAMES, TAG_FIELD_TEXTS)

        # Create the outer frames to hold fields and buttons.
        self.outer_frame, body_frame, buttonbox = _create_input_form_framing(self.parent)

        # Create the field label and field entry widgets.
        label_field = _LabelFieldWidget(body_frame)
        for movie_field_name in TAG_FIELD_NAMES:
            label_field.add_entry_row(self.entry_fields[movie_field_name])

        # Populate buttonbox with the search and cancel buttons.
        column_num = itertools.count()
        search_button = _create_button(buttonbox, SEARCH_TEXT, column=next(column_num),
                                       command=self.search, enabled=False)
        _create_button(buttonbox, CANCEL_TEXT, column=next(column_num),
                       command=self.destroy).focus_set()

        # Link the search button to the tag field.
        button_enabler = _enable_button(search_button)
        neuron = _create_button_orneuron(button_enabler)
        notify_neuron = _create_the_fields_observer(self.entry_fields, TAG_FIELD_NAMES[0], neuron)
        _link_field_to_neuron(self.entry_fields, TAG_FIELD_NAMES[0], neuron, notify_neuron)
        self.entry_fields[TAG_FIELD_NAMES[0]].observer = neuron

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
    entry_fields: Dict[str, '_EntryField'] = field(default_factory=dict, init=False, repr=False)

    # noinspection DuplicatedCode
    def __post_init__(self):
        # Initialize an internal dictionary to simplify field data management.
        self.entry_fields = _create_entry_fields(TAG_FIELD_NAMES, TAG_FIELD_TEXTS)
        self.entry_fields[TAG_FIELD_NAMES[0]].original_value = self.tag

        # Create outer frames to hold fields and buttons.
        self.outer_frame, body_frame, buttonbox = _create_input_form_framing(self.parent)

        # Create field label and field entry widgets.
        label_field = _LabelFieldWidget(body_frame)
        for movie_field_name in TAG_FIELD_NAMES:
            label_field.add_entry_row(self.entry_fields[movie_field_name])

        # Populate buttonbox with commit, delete, and cancel buttons
        column_num = itertools.count()
        commit_button = _create_button(buttonbox, COMMIT_TEXT, column=next(column_num),
                                       command=self.commit, enabled=False)
        _create_button(buttonbox, DELETE_TEXT, column=next(column_num), command=self.delete)
        _create_button(buttonbox, CANCEL_TEXT, column=next(column_num),
                       command=self.destroy).focus_set()

        # Link commit button to tag field
        button_enabler = _enable_button(commit_button)
        neuron = _create_button_orneuron(button_enabler)
        notify_neuron = _create_the_fields_observer(self.entry_fields, TAG_FIELD_NAMES[0], neuron)
        _link_field_to_neuron(self.entry_fields, TAG_FIELD_NAMES[0], neuron, notify_neuron)
        self.entry_fields[TAG_FIELD_NAMES[0]].observer = neuron

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
        self.outer_frame, body_frame, buttonbox = _create_body_and_button_frames(self.parent)

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
        _create_button(buttonbox, CANCEL_TEXT, column_num, self.destroy)

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


@dataclass
class PreferencesGUI:
    """Create and manage a Tk input form which allows the user to update program preferences."""
    parent: tk.Tk

    # Preference fields
    api_key: str
    do_not_ask: bool

    # On commit this callback will be called with the updated preferences.
    save_callback: Callable[[str, bool], None]

    # Internal field names and associated GUI texts.
    api_key_name = 'api_key'
    api_key_text = 'TMDB API key'
    use_tmdb_name = 'use_tmdb'
    use_tmdb_text = 'Use TMDB (The Movie Database)'

    toplevel: tk.Toplevel = None
    # A more convenient data structure for entry fields.
    entry_fields: Dict[str, '_EntryField'] = field(default_factory=dict, init=False, repr=False)

    def __post_init__(self):
        """Create the widgets and closures required for their operation."""
        # Create a toplevel window
        self.toplevel = tk.Toplevel(self.parent)

        # Create outer frames to hold fields and buttons.
        self.outer_frame, body_frame, buttonbox = _create_input_form_framing(self.toplevel)

        # Initialize an internal dictionary to simplify field data management.
        self.entry_fields = _create_entry_fields((self.api_key_name, self.use_tmdb_name),
                                                 (self.api_key_text, self.use_tmdb_text))
        original_values = {self.api_key_name: self.api_key, self.use_tmdb_name: self.do_not_ask}
        _set_original_value(self.entry_fields, original_values)

        # Create labels and fields
        label_field = _LabelFieldWidget(body_frame)
        label_field.add_entry_row(self.entry_fields[self.api_key_name])
        label_field.add_checkbox_row(self.entry_fields[self.use_tmdb_name])
        _focus_set(self.entry_fields[self.api_key_name].widget)

        # Create buttons
        column_num = itertools.count()
        save_button = _create_button(buttonbox, SAVE_TEXT, column=next(column_num),
                                     command=self.save, enabled=False)
        _create_button(buttonbox, CANCEL_TEXT, column=next(column_num),
                       command=self.destroy, enabled=True)

        # moviedb-#257 Create an XORNeuron
        #   Neuron linking tmdb_api_key and use_tmdb should be an XorNeuron.
        #   because user should either provide a key or state that she doesn't want to use TMDB.
        #   This needs a new Neuron sub class and a new _link_xor_neuron_to_button function
        # Link save button to save neuron
        save_button_enabler = _enable_button(save_button)
        save_neuron = _create_button_orneuron(save_button_enabler)

        # Link api key field to save neuron
        self.entry_fields[self.api_key_name].observer = _create_the_fields_observer(
            self.entry_fields, self.api_key_name, save_neuron)
        _link_field_to_neuron(self.entry_fields, self.api_key_name, save_neuron,
                              self.entry_fields[self.api_key_name].observer)

        # Link tmdb don't ask field to save neuron
        self.entry_fields[self.use_tmdb_name].observer = _create_the_fields_observer(
            self.entry_fields, self.use_tmdb_name, save_neuron)
        _link_field_to_neuron(self.entry_fields, self.use_tmdb_name, save_neuron,
                              self.entry_fields[self.use_tmdb_name].observer)

        # moviedb-#251 Center dialog on topmost window of moviedb

    def save(self):
        """Save the edited preference values to the config file."""
        tmdb_api_key: str = self.entry_fields[self.api_key_name].textvariable.get()
        tmdb_do_not_ask_again: bool = self.entry_fields[self.use_tmdb_name].textvariable.get() == '1'
        self.save_callback(tmdb_api_key, tmdb_do_not_ask_again)
        self.destroy()

    def destroy(self):
        """Destroy all widgets of this class."""
        self.toplevel.destroy()


def gui_messagebox(parent: ParentType, message: str, detail: str = '', icon: str = 'info'):
    """Present a Tk messagebox."""
    messagebox.showinfo(parent, message, detail=detail, icon=icon)


def gui_askyesno(parent: ParentType, message: str, detail: str = '') -> bool:
    """
    Present a Tk askyesno dialog.
    
    Args:
        parent:
        message:
        detail:

    Returns:
        True if user clicks 'Yes', False if user clicks 'No'
    """
    # moviedb-#247 Test this function
    return messagebox.askyesno(parent, message, detail=detail)


def gui_askopenfilename(parent: ParentType, filetypes: Iterable[tuple[str, str | list[str] | tuple[str, ...]]] | None):
    """Present a Tk askopenfilename."""
    return filedialog.askopenfilename(parent=parent, filetypes=filetypes)


@dataclass
class _MovieTagTreeview:
    """Create and manage a treeview and a descriptive label.
    
    The user callback will be called whenever the user has changes the selection. The observer will
    also be notified with a boolean message stating if the current selection differs from the original
    selection.
    """

    # The frame which contains the treeview.
    body_frame: ttk.Frame
    # The tk grid row of the label and treeview within the frame's grid.
    row: int
    # A list of all the items which will be displayed in the treeview.
    items: Sequence[str]
    # Caller's callback for notification of reselection.
    callers_callback: Callable[[Sequence[str]], None]
    # Items to be selected on opening.
    initial_selection: Sequence[str] = field(default_factory=list)

    treeview: ttk.Treeview = field(default=None, init=False, repr=False)
    observer: neurons.Neuron = field(default_factory=neurons.Neuron, init=False, repr=False)

    # noinspection DuplicatedCode
    def __post_init__(self):
        # Create a frame for the treeview and its scrollbar
        treeview_frame = ttk.Frame(self.body_frame, padding=5)
        treeview_frame.grid(column=1, row=self.row, sticky='w')

        # Create the treeview
        self.treeview = ttk.Treeview(treeview_frame, columns=('tags',), height=10, selectmode='extended',
                                     show='tree', padding=5)
        self.treeview.grid(column=0, row=0, sticky='w')
        self.treeview.column('tags', width=100)
        self.treeview.bind('<<TreeviewSelect>>',
                           func=self.selection_callback_wrapper(self.treeview, self.callers_callback))

        # Create the scrollbar
        scrollbar = ttk.Scrollbar(treeview_frame, orient=tk.VERTICAL, command=self.treeview.yview)
        scrollbar.grid(column=1, row=0)
        self.treeview.configure(yscrollcommand=scrollbar.set)

        # Populate the treeview
        for item in self.items:
            self.treeview.insert('', 'end', item, text=item, tags='tags')
        # noinspection PyTypeChecker
        self.treeview.selection_add(self.initial_selection)

    def selection_callback_wrapper(self, treeview: ttk.Treeview,
                                   user_callback: Callable[[Sequence[str]], None]) -> Callable:
        """Create a callback which will be called whenever the user selection is changed.

        Args:
            treeview:
            user_callback:

        Returns: The callback.
        """

        # noinspection PyUnusedLocal
        def selection_callback(*args):
            """Notify MovieTreeview's caller and observer's notifees.

            Args:
                *args: Not used. Needed for compatibility with Tk:Tcl caller.
            """
            current_selection = treeview.selection()
            user_callback(current_selection)
            self.observer.notify(set(current_selection) != set(self.initial_selection))

        return selection_callback

    def clear_selection(self):
        """Clear the current selection.
        
        Use Case:
            When the user enters a record the input form is reused. The treeview selection
            needs to be cleared ready for the next record entry.
        """
        # noinspection PyArgumentList
        self.treeview.selection_set()


@dataclass
class _EntryField:
    """
    A support class for the attributes of a GUI entry field.

    This is typically used for an input form with static data using
    _create_entry_fields and dynamic data using _set_original_value.
    _create_entry_fields creates a dictionary of EntryField objects using lists of internal names and
    label texts. These values are usually derived from static text.
    _set_original_value adds the original value of fields if not blank. This dynamic data is usually
    supplied by the external caller.
    """
    label_text: str
    original_value: str = ''
    widget: ttk.Entry = None
    # There is an uninvestigated problem with pytest's monkey patching of tk.StringVar if
    #   textvariable is initialized as:
    #   textvariable: tk.StringVar = field(default_factory=tk.StringVar, init=False, repr=False)
    textvariable: tk.StringVar = None
    # The observer attribute is *not* needed for normal operation. If initialized when the observer is
    # first created it will permit external testing of the chain of neurons.
    observer: Callable = field(default=None, init=False, repr=False)

    def __post_init__(self):
        self.textvariable = tk.StringVar()
        self.textvariable.set(self.original_value)


@dataclass
class _LabelFieldWidget:
    """
    Create a two column frame for labels and widgets. Call specific methods such as add_entry_row
    to add specific widgets.
    """

    parent: tk.Frame
    row: Iterator = field(default=None, init=False, repr=False)

    col_0_width: int = 30
    col_1_width: int = 36

    def __post_init__(self):
        """Create two columns within the parent frame."""
        self.row = itertools.count()

        # Create a column for the labels.
        self.parent.columnconfigure(0, weight=1, minsize=self.col_0_width)
        # Create a column for the fields.
        self.parent.columnconfigure(1, weight=1)

    def add_entry_row(self, entry_field: _EntryField):
        """
        Add a label and an entry as the bottom row.
        
        Args:
            entry_field:
        """
        row_ix = next(self.row)
        self._create_label(entry_field.label_text, row_ix)
        # todo add multiline to notes field.
        entry_field.widget = ttk.Entry(self.parent, textvariable=entry_field.textvariable,
                                       width=self.col_1_width)
        entry_field.widget.grid(column=1, row=row_ix)

    def add_checkbox_row(self, entry_field: _EntryField):
        """
        Add a label and a checkbox as the bottom row.
 
        Checkbutton has a 'command' parameter used for callbacks.
        For consistency with other widgets this method will use the text variable via
        link_field_to_neuron. This link is set up by the caller.
        
        Args:
            entry_field:
        """
        row_ix = next(self.row)
        entry_field.widget = ttk.Checkbutton(self.parent, text=entry_field.label_text,
                                             variable=entry_field.textvariable, width=self.col_1_width)
        entry_field.widget.grid(column=1, row=row_ix)

    def add_treeview_row(self, label_text, items, callers_callback) -> _MovieTagTreeview:
        """
        Add a label and a treeview as the bottom row.

        Args:
            label_text:
            items: A list of all the items which will be displayed in the treeview.
            callers_callback: Caller's callback for notification of reselection.
        """

        row_ix = next(self.row)
        self._create_label(label_text, row_ix)
        return _MovieTagTreeview(self.parent, row_ix, items, callers_callback)

    def _create_label(self, text: str, row_ix: int):
        """ Create a label for the current row.
    
        Args:
            text:
            row_ix: The row into which the label will be placed.
        """

        label = ttk.Label(self.parent, text=text)
        label.grid(column=0, row=row_ix, sticky='e', padx=5)


def _create_entry_fields(internal_names: Sequence[str], label_texts: Sequence[str]
                         ) -> Dict[str, _EntryField]:
    """
    Create an internal dictionary to simplify field data management. See usage note in the
    associated EntryField docs.

    Args:
        internal_names: A sequence of internal_names of the fields
        label_texts: A sequence of internal internal_names, label text, original values

    Returns:
        key: The internal name of the field.
        value: An EntryField instance.
    """
    return {internal_name: _EntryField(label_text)
            for internal_name, label_text in zip(internal_names, label_texts)}


def _set_original_value(entry_fields: Dict[str, _EntryField], original_values: Dict[str, str]) -> None:
    """
    Update entry fields with original values. See usage note in the associated EntryField docs.

    Args:
        entry_fields: A dictionary of input fields.
        original_values: A dictionary of the original values of none or more of the fields.
            key: internal name
            value: original value
    """
    for internal_name, original_value in original_values.items():
        entry_fields[internal_name].original_value = original_value
        entry_fields[internal_name].textvariable.set(original_value)


def _create_body_and_button_frames(parent: ParentType) -> Tuple[ttk.Frame, ttk.Frame, ttk.Frame]:
    """Create the outer frames for an input form.

    This consists of an upper body and a lower buttonbox frame.

    Note: Do not call this function if the input form has label and entry widgets. Use the higher
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


def _create_input_form_framing(parent: ParentType) -> Tuple[ttk.Frame, ttk.Frame, ttk.Frame]:
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
    outer_frame, body_frame, buttonbox = _create_body_and_button_frames(parent)
    outer_frame.rowconfigure(0, weight=1)
    outer_frame.rowconfigure(1, minsize=35)
    return outer_frame, body_frame, buttonbox


def _clear_input_form_fields(entry_fields: Mapping[str, '_EntryField']):
    """Clear entry fields ready for fresh user input.

    Args:
        entry_fields:
    """

    for entry_field in entry_fields.values():
        entry_field.textvariable.set('')


def _create_button(buttonbox: ttk.Frame, text: str, column: int, command: Callable,
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


def _enable_button(button: ttk.Button) -> Callable:
    """Create a callback which can enable or disable a button.

    Args:
        button:

    Returns:
        A callable which will set the enabled state of the button.

    Use case:
        This callback is intended for use as the notifee of a neuron. For example, if an observed
        field is changed from its original value the neuron is notified with a 'True' argument. If it
        is changed back to its original value the neuron is notified with a 'False' argument. All
        registered notifees will then be called with the argument given to the neuron.
    """

    def func(state: bool):
        """Enable or disable the button.

        Args:
            state:
        """
        if state:
            button.state(['!disabled'])
        else:
            button.state(['disabled'])

    return func


def _focus_set(entry: ttk.Entry):
    """Set initial focus for this class."""
    entry.focus_set()
    entry.select_range(0, tk.END)
    entry.icursor(tk.END)


def _create_button_orneuron(change_button_state: Callable) -> neurons.OrNeuron:
    """Create an 'Or' neuron and link it to a button.
    
    Args:
        change_button_state:

    Returns:
        Neuron
    """
    neuron = neurons.OrNeuron()
    neuron.register(change_button_state)
    return neuron


def _create_buttons_andneuron(change_button_state: Callable) -> neurons.AndNeuron:
    """Create an 'Or' neuron and link it to a button.
    
    Args:
        change_button_state:

    Returns:
        Neuron
    """
    neuron = neurons.AndNeuron()
    neuron.register(change_button_state)
    return neuron


def _link_field_to_neuron(entry_fields: dict, name: str, neuron: neurons.Neuron,
                          notify_neuron: Callable):
    """Link the fields associated with a button to its neuron.
    
    Args:
        entry_fields: A mapping of field names to instances of EntryField.
        name: …of the field being mapped to the neuron.
        neuron:
        notify_neuron:
    """
    entry_fields[name].textvariable.trace_add('write', notify_neuron)
    neuron.register_event(name)


def _create_the_fields_observer(entry_fields: dict, name: str, neuron: neurons.Neuron) -> Callable:
    """Creates the callback for an observed field.

        The returned function will ba called whenever the field content is changed by the user.
    
    Args:
        entry_fields: A mapping of the field names to instances of EntryField.
        name: Field name.
        neuron: The neuron which will be notified of the field's state.

    Returns:
        object: The callback which will be called when the field is changed.
    """

    # TODO Consider whether this callback is exclusively for the AndNeuron class. If so change the name and docs to
    #  reflect that fact.
    # noinspection PyUnusedLocal
    def func(*args):
        """Calls the neuron when the field changes.

        Args:
            *args: Not used. Required to match unused arguments from caller.
        """
        state = (entry_fields[name].textvariable.get()
                 != entry_fields[name].original_value)
        neuron(name, state)

    return func
