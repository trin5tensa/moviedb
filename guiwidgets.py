"""GUI Windows.

This module includes windows for presenting data supplied to it and returning entered data to its
callers.
"""

#  Copyright© 2025. Stephen Rigden.
#  Last modified 2/6/25, 11:33 AM by stephen.
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
import logging
import tkinter as tk
import tkinter.ttk as ttk
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Sequence

import config
from globalconstants import MovieBag, MovieInteger
import neurons
from guiwidgets_2 import (
    CANCEL_TEXT,
    TITLE,
    TITLE_TEXT,
    YEAR,
    YEAR_TEXT,
    DIRECTOR,
    DIRECTOR_TEXT,
    DURATION,
    DURATION_TEXT,
    NOTES,
    NOTES_TEXT,
    SEARCH_TEXT,
    MOVIE_TAGS_TEXT,
    focus_set,
)

TAG_TREEVIEW_INTERNAL_NAME = "tag treeview"


@dataclass
class MovieGUIBase:
    """A base class for movie input forms.

    WARNING:
        This module uses the original subclassed approach to Tkinter primary widgets. It
        is fragile and should not be used as template for future developments.
        Any proposed refactoring should consider abandoning these classes and using the newer
        composed classes of guiwidgets_2 as a model for future development.
    """

    parent: tk.Tk

    selected_tags: Sequence[str] = field(default_factory=tuple, init=False, repr=False)
    # All widgets of this class will be enclosed in this frame.
    outer_frame: ttk.Frame = field(default=None, init=False, repr=False)
    # A more convenient data structure for entry fields.
    entry_fields: Dict[str, "_EntryField"] = field(
        default_factory=dict, init=False, repr=False
    )
    # Observer of treeview selection state
    tag_treeview_observer: neurons.Observer = field(
        default=neurons.Observer, init=False
    )

    def __post_init__(self):
        self.outer_frame = ttk.Frame(self.parent)
        self.outer_frame.grid(column=0, row=0, sticky="nsew")
        self.outer_frame.columnconfigure(0, weight=1)
        self.outer_frame.rowconfigure(0, weight=1)
        self.outer_frame.rowconfigure(1, minsize=35)

        self.create_body(self.outer_frame)
        self.create_buttonbox(self.outer_frame)

    def create_body(self, outerframe: ttk.Frame) -> ttk.Frame:
        """Create a body frame.

        This has two configured columns one for labels and another for user input fields
        """

        # Initialize an internal dictionary to simplify field data management.
        self.entry_fields = _create_entry_fields(
            (TITLE, YEAR, DIRECTOR, DURATION, NOTES),
            (TITLE_TEXT, YEAR_TEXT, DIRECTOR_TEXT, DURATION_TEXT, NOTES_TEXT),
        )

        body_frame = ttk.Frame(outerframe, padding=(10, 25, 10, 0))
        body_frame.grid(column=0, row=0, sticky="n")
        body_frame.columnconfigure(0, weight=1, minsize=30)
        body_frame.columnconfigure(1, weight=1)
        return body_frame

    def create_buttonbox(self, outerframe: ttk.Frame) -> ttk.Frame:
        """Create the buttonbox."""
        buttonbox = ttk.Frame(outerframe, padding=(5, 5, 10, 10))
        buttonbox.grid(column=0, row=1, sticky="e")
        return buttonbox

    def create_cancel_button(self, buttonbox: ttk.Frame, column: int):
        """Create a cancel button

        Args:
            buttonbox:
            column:
        """
        cancel_button = ttk.Button(buttonbox, text=CANCEL_TEXT, command=self.destroy)
        cancel_button.grid(column=column, row=0)
        cancel_button.bind("<Return>", lambda event, b=cancel_button: b.invoke())

    def neuron_linker(
        self,
        internal_name: str,
        neuron: neurons.Neuron,
        neuron_callback: Callable,
        initial_state: bool = False,
    ):
        """Set a neuron callback which will be called whenever the field is changed by the user.

        Args:
            internal_name: Name of widget. The neuron will be notified whenever this widget is
            changed by the user.
            neuron:
            neuron_callback: This will be set as the trace_add method of the field's textvariable.
            initial_state:

        Returns:

        """
        self.entry_fields[internal_name].textvariable.trace_add(
            "write", neuron_callback(internal_name, neuron)
        )
        neuron.register_event(internal_name, initial_state)

    def neuron_callback(self, internal_name: str, neuron: neurons.Neuron) -> Callable:
        """Create the callback for an observed field.

        This will be registered as the 'trace_add' callback for an entry field.
        """

        # noinspection PyUnusedLocal
        def change_neuron_state(*args):
            """Call the neuron when the field changes.

            Args:
                *args: Not used. Required to match unused arguments from caller.
            """
            state = self.entry_fields[internal_name].textvariable.get() != str(
                self.entry_fields[internal_name].original_value
            )
            neuron(internal_name, state)

        return change_neuron_state

    @staticmethod
    def button_state_callback(button: ttk.Button) -> Callable:
        """Create the callback for a button.

        This will be registered with a neuron as s notifee."""

        def change_button_state(state: bool):
            """Enable or disable the commit button when the title or year field change."""
            if state:
                button.state(["!disabled"])
            else:
                button.state(["disabled"])

        return change_button_state

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
    def validate_int_range(
        user_input: int, lowest: int = None, highest: int = None
    ) -> bool:
        """Validate that user input is an integer within a valid range.

        Use Case: Supports field validation by Tk
        """

        lowest = user_input > lowest if lowest else True
        highest = user_input < highest if highest else True
        return lowest and highest

    def treeview_callback(self, reselection: Sequence[str]):
        """Update selected tags with user's changes."""
        self.selected_tags = reselection

    def destroy(self):
        """Destroy all widgets of this class."""
        self.outer_frame.destroy()


@dataclass
class SearchMovieGUI(MovieGUIBase):
    """A form for searching for a movie.

    WARNING:
        This module uses the original subclassed approach to Tkinter primary widgets. It
        is fragile and should not be used as template for future developments.
        Any proposed refactoring should consider abandoning these classes and using the newer
        composed classes of guiwidgets_2 as a model for future development.
    """

    # On exit this callback will be called with a dictionary of fields and user entered values.
    callback: Callable[[MovieBag], None]
    # Tags list
    all_tags: Sequence[str]

    selected_tags: Sequence[str] = field(default_factory=tuple, init=False)
    # Neuron controlling enabled state of Search button
    search_button_neuron: neurons.OrNeuron = field(
        default_factory=neurons.OrNeuron, init=False
    )

    def create_body(self, outerframe: ttk.Frame):
        """Create the body of the form."""
        body_frame = super().create_body(outerframe)
        row = itertools.count()

        self.create_body_item(body_frame, "title", "Title", next(row))
        self.create_min_max_body_item(body_frame, "year", "Year", next(row))
        self.create_body_item(body_frame, "director", "Director", next(row))
        self.create_min_max_body_item(
            body_frame, "minutes", "Length (minutes)", next(row)
        )
        self.create_body_item(body_frame, "notes", "Notes", next(row))

        # Create treeview for tag selection.
        self.tag_treeview_observer = MovieTreeview(
            TAG_TREEVIEW_INTERNAL_NAME,
            body_frame,
            row=next(row),
            column=0,
            label_text=MOVIE_TAGS_TEXT,
            items=self.all_tags,
            user_callback=self.treeview_callback,
        )()
        self.tag_treeview_observer.register(self.search_button_neuron)

        focus_set(self.entry_fields["title"].widget)

    def create_body_item(
        self, body_frame: ttk.Frame, internal_name: str, text: str, row: int
    ):
        """Create a ttk label and ttk entry.

        Args:
            body_frame: The frame enclosing the label and entry.
            internal_name: of the entry.
            text: The text of the label that is seen by the user.
            row: The tk grid row of the item within the frame's grid.
        """
        label = ttk.Label(body_frame, text=text)
        label.grid(column=0, row=row, sticky="e", padx=5)
        self.create_entry(body_frame, internal_name, 1, row, 36)

    def create_min_max_body_item(
        self, body_frame: ttk.Frame, internal_name: str, text: str, row: int
    ):
        """Create a ttk label and ttk entry.

        Args:
            body_frame: The frame enclosing the label and entry.
            internal_name: of the entry.
            text: The text of the label that is seen by the user.
            row: The tk grid row of the item within the frame's grid.
        """
        # Create label
        label = ttk.Label(body_frame, text=f"{text} (min, max)")
        label.grid(column=0, row=row, sticky="e", padx=5)

        # Create entry frame with a max entry and a min entry
        entry_frame = ttk.Frame(body_frame, padding=(2, 0))
        entry_frame.grid(column=1, row=row, sticky="w")
        self.create_entry(
            entry_frame, (min_field_name := f"{internal_name}_min"), 0, 0, 6
        )
        self.create_entry(
            entry_frame, (max_field_name := f"{internal_name}_max"), 1, 0, 6
        )

        # Place integer field validation on both fields
        for field_name in (min_field_name, max_field_name):
            entry_field = self.entry_fields[field_name]
            registered_callback = entry_field.widget.register(self.validate_int)
            entry_field.widget.config(
                validate="key", validatecommand=(registered_callback, "%S")
            )

    def create_entry(
        self,
        body_frame: ttk.Frame,
        internal_name: str,
        column: int,
        row: int,
        width: int,
    ):
        """Create a ttk entry

        Args:
            body_frame: The frame enclosing the entry.
            internal_name: of the entry
            column: The tk grid column of the item within the frame's grid.
            row: The tk grid row of the item within the frame's grid.
            width: The tk character width of the entry widget.
        """
        entry_field = self.entry_fields[internal_name] = _EntryField("", "")
        entry = ttk.Entry(
            body_frame, textvariable=entry_field.textvariable, width=width
        )
        entry.grid(column=column, row=row)
        entry_field.widget = entry
        self.neuron_linker(
            internal_name, self.search_button_neuron, self.neuron_callback
        )

    # noinspection DuplicatedCode
    def create_buttonbox(self, outerframe: ttk.Frame):
        """Create the buttons."""
        buttonbox = super().create_buttonbox(outerframe)
        column_num = itertools.count()

        # Search button
        search = ttk.Button(buttonbox, text=SEARCH_TEXT, command=self.search)
        search.grid(column=next(column_num), row=0)
        search.bind("<Return>", lambda event, b=search: b.invoke())
        search.state(["disabled"])
        self.search_button_neuron.register(self.button_state_callback(search))

        # Cancel button
        self.create_cancel_button(buttonbox, column=next(column_num))

    def search(self):
        """The user clicked the search button."""
        return_fields = {
            internal_name: movie_field.textvariable.get()
            for internal_name, movie_field in self.entry_fields.items()
        }
        movie_bag = self.as_movie_bag(return_fields)
        self.callback(movie_bag)
        self.destroy()

    def as_movie_bag(self, return_fields: dict[str, ...]) -> MovieBag:
        """Returns the entered data as a movie bag.

        Args:
            return_fields:

        Returns:
            movie bag
        """
        movie_bag = MovieBag()
        for k, v in return_fields.items():
            if v:
                match k:
                    case "title":
                        movie_bag["title"] = v
                    case "year_min" | "year_max":
                        movie_bag["year"] = self._range_converter(
                            [
                                return_fields["year_min"],
                                return_fields["year_max"],
                            ]
                        )
                    case "director":
                        movie_bag["directors"] = set(v.split(", "))
                    case "notes":
                        movie_bag["notes"] = v
                    case "minutes_min" | "minutes_max":
                        movie_bag["duration"] = self._range_converter(
                            [
                                return_fields["minutes_min"],
                                return_fields["minutes_max"],
                            ]
                        )
                    case "year" | "minutes":
                        # Both keys are present but with no values.
                        # Probably cruft.
                        pass
                    case _:
                        logging.error(f"Unexpected key: {k}")
                        raise KeyError(f"Unexpected key: {k}")
        movie_bag["tags"] = set(self.selected_tags)
        return movie_bag

    @staticmethod
    def _range_converter(value: Sequence[str]) -> MovieInteger:
        """Converts a 'range' string into a MovieInteger object.

        Args:
            value: The year and minutes item in the old style FindMovieTypedDict
            contained a sequence of strings. The intended use was for either
            a single numeric string or a pair of numeric strings.
            For example: [1960] or [1960, 1965].

        Returns:
            A MovieInt object.
        """
        match len(value):
            case 1:
                duration_range = f"{value[0]}"
            case 2:
                duration_range = f"{value[0]}-{value[1]}"
            case _:
                raise ValueError(
                    f"Length of value must be 1 or 2 not" f" {len(value)}. {value=}"
                )
        return MovieInteger(duration_range)


@dataclass
class SelectMovieGUI(MovieGUIBase):
    """A form for selecting a movie.

    WARNING:
        This module uses the original subclassed approach to Tkinter primary widgets. It
        is fragile and should not be used as template for future developments.
        Any proposed refactoring should consider abandoning these classes and using the newer
        composed classes of guiwidgets_2 as a model for future development.
    """

    # Movie records retrieved from the database.
    movies: List[MovieBag]
    # On exit this callback will be called with a dictionary of fields and user entered values.
    callback: Callable
    # Attributes for managing the treeview
    treeview: ttk.Treeview = field(default=None, init=False, repr=False)
    treeview_items: dict[str : config.MovieKeyTypedDict] = field(
        default_factory=MovieBag, init=False, repr=False
    )

    def create_body(self, outerframe: ttk.Frame):
        """Create the body of the form."""
        body_frame = super().create_body(outerframe)

        # Create and grid treeview
        self.treeview = ttk.Treeview(
            body_frame,
            columns=[YEAR, DIRECTOR, DURATION, NOTES],
            height=25,
            selectmode="browse",
        )
        self.treeview.grid(column=0, row=0, sticky="w")

        # Set up column widths and titles
        column_widths = (350, 50, 100, 50, 350)
        for column_ix, internal_name in enumerate(
            (TITLE, YEAR, DIRECTOR, DURATION, NOTES)
        ):
            if column_ix == 0:
                internal_name = "#0"
            self.treeview.column(internal_name, width=column_widths[column_ix])
            self.treeview.heading(
                internal_name,
                text=(TITLE_TEXT, YEAR_TEXT, DIRECTOR_TEXT, DURATION_TEXT, NOTES_TEXT)[
                    column_ix
                ],
            )

        # Populate rows with movies and build a lookup dictionary.
        for movie in self.movies:
            item_id = self.treeview.insert(
                "",
                "end",
                text=movie["title"],
                values=(
                    movie["year"],
                    movie.get("directors", ""),
                    movie.get("duration", ""),
                    movie.get("notes", ""),
                ),
                tags="title",
            )
            self.treeview_items[item_id] = movie
        self.treeview.bind(
            "<<TreeviewSelect>>", func=self.treeview_callback(self.treeview)
        )

    def treeview_callback(self, tree: ttk.Treeview):
        """Create a callback which will be called when the user makes a selection.

        Args:
            tree:

        Returns: The callback.
        """

        # noinspection PyUnusedLocal
        def func(*args):
            """Save the newly changed user selection.

            Args:
                *args: Not used. Needed for compatibility with Tk:Tcl caller.
            """
            (item_id,) = tree.selection()
            # Return control to Tk/Tcl and delete this dialog *before*
            #   running the callback.
            self.parent.after(0, self.callback, self.treeview_items[item_id])
            self.destroy()

        return func

    def create_buttonbox(self, outerframe: ttk.Frame):
        """Create the buttons."""
        buttonbox = super().create_buttonbox(outerframe)

        # Cancel button
        self.create_cancel_button(buttonbox, column=0)


@dataclass
class MovieTreeview:
    """Create and manage a treeview and a descriptive label."""

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
    initial_selection: List[str] = field(default_factory=list)
    observer: neurons.Observer = field(default_factory=neurons.Observer, init=False)

    # noinspection DuplicatedCode
    def __call__(self) -> neurons.Observer:
        # Create the label
        label = ttk.Label(self.body_frame, text=self.label_text, padding=(0, 2))
        label.grid(column=self.column, row=self.row, sticky="ne", padx=5)

        # Create a frame for the treeview and its scrollbar
        treeview_frame = ttk.Frame(self.body_frame, padding=5)
        treeview_frame.grid(column=self.column + 1, row=self.row, sticky="w")

        # Create the treeview
        tree = ttk.Treeview(
            treeview_frame,
            columns=("tags",),
            height=10,
            selectmode="extended",
            show="tree",
            padding=5,
        )
        tree.grid(column=0, row=0, sticky="w")
        tree.column("tags", width=100)
        tree.bind(
            "<<TreeviewSelect>>", func=self.treeview_callback(tree, self.user_callback)
        )

        # Create the scrollbar
        scrollbar = ttk.Scrollbar(
            treeview_frame, orient=tk.VERTICAL, command=tree.yview
        )
        scrollbar.grid(column=1, row=0)
        tree.configure(yscrollcommand=scrollbar.set)

        # Populate the treeview
        for item in self.items:
            if item:
                tree.insert("", "end", item, text=item, tags="tags")
        tree.selection_add(self.initial_selection)

        return self.observer

    def treeview_callback(
        self, tree: ttk.Treeview, callback: Callable[[Sequence[str]], None]
    ):
        """Create a callback which will be called whenever the user selection is changed.

        Args:
            tree:
            callback:

        Returns: The callback.
        """

        # noinspection PyUnusedLocal
        def update_tag_selection(*args):
            """Notify MovieTreeview's caller and observer's notifees.

            Args:
                *args: Not used. Needed for compatibility with Tk:Tcl caller.
            """
            current_selection = tree.selection()
            callback(current_selection)
            self.observer.notify(
                self.internal_name,
                set(current_selection) != set(self.initial_selection),
            )

        return update_tag_selection


@dataclass
class _EntryField:
    """
    A support class for the attributes of a GUI entry field.

    This is typically used for an input form with static data using
    _create_entry_fields and dynamic data using _set_original_value.
    _create_entry_fields creates a dictionary of EntryField objects using lists of
    internal names and label texts. These values are usually derived from static text.
    _set_original_value adds the original value of fields if not blank. This dynamic
    data is usually supplied by the external caller.
    """

    label_text: str
    original_value: str = ""
    widget: ttk.Entry | ttk.Checkbutton | tk.Text = None
    # tkinter offers StringVar, IntVar, and DoubleVar. Only StringVar is used here to enable
    #   code generalization.
    # There is an uninvestigated problem with pytest's monkey patching of tk.StringVar if
    #   textvariable is initialized as:
    #   textvariable: tk.StringVar = field(default_factory=tk.StringVar, init=False, repr=False)
    textvariable: tk.StringVar = None
    observer: neurons.Observer = field(
        default_factory=neurons.Observer, init=False, repr=False
    )

    def __post_init__(self):
        self.textvariable = tk.StringVar()
        self.textvariable.set(self.original_value)
        self.textvariable.trace_add("write", self.observer.notify)


def _create_entry_fields(
    internal_names: Sequence[str],
    label_texts: Sequence[str],
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

    return {
        internal_name: _EntryField(
            label_text
        )  # pragma no cover (coverage cannot handle this code)
        for internal_name, label_text in zip(internal_names, label_texts)
    }
