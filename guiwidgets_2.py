"""GUI Windows.

This module includes windows for presenting data and returning entered data to its callers.
"""

#  Copyright© 2025. Stephen Rigden.
#  Last modified 3/3/25, 1:43 PM by stephen.
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
import queue
from functools import partial

from tkinter import filedialog, messagebox

# noinspection PyUnresolvedReferences
from dataclasses import dataclass, field
from typing import (
    Callable,
    Dict,
    Iterable,
    Literal,
    Optional,
    Union,
    Sequence,
)

import config
from gui import tk_facade, common
from globalconstants import *

# noinspection DuplicatedCode
TITLE_TEXT = "Title"
YEAR_TEXT = "Year"
DIRECTORS_TEXT = "Directors"
DURATION_TEXT = "Runtime"
NOTES_TEXT = "Notes"
MOVIE_TAGS_TEXT = "Tags"
SEARCH_TEXT = "Search"
COMMIT_TEXT = "Commit"
SAVE_TEXT = "Save"
DELETE_TEXT = "Delete"
CANCEL_TEXT = "Cancel"

MOVIE_DELETE_MESSAGE = "Do you want to delete this movie?"
TAG_DELETE_MESSAGE = "Do you want to delete this tag?"
NO_MATCH_MESSAGE = "No matches"
NO_MATCH_DETAIL = "There are no matching tags in the database."
UNEXPECTED_KEY = "Unexpected key"

DefaultLiteral = Literal["normal", "active", "disabled"]
StateFlags = Optional[list[Literal["active", "normal", "disabled", "!disabled"]]]


@dataclass
class MovieGUI:
    # noinspection GrazieInspection
    """Create and manage a Tk input form for movies."""
    parent: tk.Tk
    tmdb_search_callback: Callable[[str, queue.LifoQueue], None]
    # This is a complete list of the tags in the database
    all_tags: Sequence[str]

    prepopulate: MovieBag | None = field(default=None, kw_only=True)

    # All widgets created by this class will be enclosed in this frame.
    outer_frame: ttk.Frame = field(default=None, init=False, repr=False)
    # A more convenient data structure for entry fields.
    entry_fields: Dict[
        str,
        Union[
            tk_facade.Entry,
            tk_facade.Text,
            tk_facade.Treeview,
        ],
    ] = field(default_factory=dict, init=False, repr=False)

    # Treeview for TMDB
    tmdb_treeview: ttk.Treeview = field(default=None, init=False, repr=False)

    # These variables are used for the consumer end of the TMDB producer/consumer pattern.
    tmdb_work_queue: queue.LifoQueue = field(
        default_factory=queue.Queue, init=False, repr=False
    )
    work_queue_poll: int = field(default=40, init=False, repr=False)
    recall_id: str = field(default=None, init=False, repr=False, compare=False)
    tmdb_movies: dict[str, dict] = field(default_factory=dict, init=False, repr=False)

    # These variables help to decide if the user has finished entering the title.
    last_text_queue_timer: int = field(default=500, init=False, repr=False)
    last_text_event_id: str = field(default="", init=False, repr=False)

    # Local variables exposed for testing
    return_fields: dict = field(default=None, init=False, repr=False)

    def __post_init__(self):
        self.outer_frame, body_frame, buttonbox, tmdb_frame = self.framing(self.parent)
        self.user_input_frame(body_frame)
        if self.prepopulate:
            self.populate()
        self.fill_buttonbox(buttonbox)
        self.tmdb_results_frame(tmdb_frame)
        common.init_button_enablements(self.entry_fields)

    def framing(
        self, parent: TkParentType
    ) -> tuple[ttk.Frame, ttk.Frame, ttk.Frame, ttk.Frame]:
        """Create framing.

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
        name = type(self).__name__.lower()
        outer_frame = ttk.Frame(parent, padding=10, name=name)
        outer_frame.grid(column=0, row=0, sticky="nsew")
        outer_frame.columnconfigure(0, weight=1)
        outer_frame.columnconfigure(1, weight=1000)
        outer_frame.rowconfigure(0)
        config.current.escape_key_dict[name] = self.destroy

        input_zone = ttk.Frame(outer_frame, padding=10)
        input_zone.grid(column=0, row=0, sticky="nw")
        input_zone.columnconfigure(0, weight=1, minsize=25)

        internet_zone = ttk.Frame(outer_frame, padding=10)
        internet_zone.grid(column=1, row=0, sticky="nw")
        internet_zone.columnconfigure(0, weight=1, minsize=25)

        input_form = ttk.Frame(input_zone, padding=10)
        input_form.grid(column=0, row=0, sticky="new")

        buttonbox = ttk.Frame(input_zone, padding=(5, 5, 10, 10))
        buttonbox.grid(column=0, row=1, sticky="ne")

        return outer_frame, input_form, buttonbox, internet_zone

    def user_input_frame(self, body_frame: tk.Frame):
        """
        This creates the widgets which will be used to enter data and display data
        retrieved from the user's database.

        Args:
            body_frame:The frame into which the widgets will be placed.
        """
        # todo The test suite for this method needs to be rewritten to current standards

        input_zone = common.LabelAndField(body_frame)

        # Create entry rows for title, year, director, and duration.
        for name, text in zip(
            (TITLE, YEAR, DIRECTORS, DURATION),
            (TITLE_TEXT, YEAR_TEXT, DIRECTORS_TEXT, DURATION_TEXT),
        ):
            self.entry_fields[name] = tk_facade.Entry(text, body_frame)
            input_zone.add_entry_row(self.entry_fields[name])
        self.entry_fields[TITLE].widget.focus_set()

        # Create label and text widget.
        self.entry_fields[NOTES] = tk_facade.Text(NOTES_TEXT, body_frame)
        input_zone.add_text_row(self.entry_fields[NOTES])

        # Create a label and treeview for movie tags.
        self.entry_fields[MOVIE_TAGS] = tk_facade.Treeview(MOVIE_TAGS_TEXT, body_frame)
        input_zone.add_treeview_row(self.entry_fields[MOVIE_TAGS], self.all_tags)

    def populate(self):
        """Initialises field values."""
        self.entry_fields[TITLE].original_value = self.prepopulate[TITLE]
        self.entry_fields[YEAR].original_value = int(self.prepopulate[YEAR])
        self.entry_fields[DIRECTORS].original_value = ", ".join(
            director for director in self.prepopulate.get(DIRECTORS, "")
        )
        self.entry_fields[DURATION].original_value = (
            int(self.prepopulate[DURATION]) if (self.prepopulate.get(DURATION)) else ""
        )
        self.entry_fields[NOTES].original_value = self.prepopulate.get(NOTES, "")
        self.entry_fields[MOVIE_TAGS].original_value = list(
            self.prepopulate.get(MOVIE_TAGS, "")
        )

    def tmdb_results_frame(self, tmdb_frame: tk.Frame):
        """
        This creates a treeview which will display movies retrieved from TMDB. It also sets up
        the queue for the producer and consumer pattern used to retrieve the on-line data from
        TMDB.

        Args:
            tmdb_frame: The frame into which the widgets will be placed.
        """
        self.tmdb_treeview = ttk.Treeview(
            tmdb_frame,
            # columns=("title", "year", "director"),
            columns=(TITLE, YEAR, DIRECTORS),
            show=["headings"],
            height=20,
            selectmode="browse",
        )
        self.tmdb_treeview.column(TITLE, width=300, stretch=True)
        self.tmdb_treeview.heading(TITLE, text=TITLE_TEXT, anchor="w")
        self.tmdb_treeview.column(YEAR, width=40, stretch=True)
        self.tmdb_treeview.heading(YEAR, text=YEAR_TEXT, anchor="w")
        self.tmdb_treeview.column(DIRECTORS, width=200, stretch=True)
        self.tmdb_treeview.heading(DIRECTORS, text=DIRECTORS_TEXT, anchor="w")
        self.tmdb_treeview.grid(column=0, row=0, sticky="nsew")
        self.tmdb_treeview.bind("<<TreeviewSelect>>", func=self.tmdb_treeview_callback)

        # TMDB Producer and consumer queue
        self.tmdb_consumer()
        self.entry_fields[TITLE].observer.register(self.tmdb_search)

    def fill_buttonbox(self, buttonbox: tk.Frame):
        """
        This adds one default Cancel button after any buttons added by subclasses. It calls
        the abstract class method create_button which must be overridden by subclasses.

        Args:
            buttonbox: The frame into which the widgets will be placed.

        Returns:

        """
        column_num = itertools.count()
        self._create_buttons(buttonbox, column_num)
        common.create_button(
            buttonbox,
            CANCEL_TEXT,
            column=next(column_num),
            command=self.destroy,
            default="active",
        )

    def _create_buttons(self, buttonbox: ttk.Frame, column_num: Iterator):
        """Create buttons within the buttonbox.

        Subclasses may call create_button to place a button in the buttonbox at
        next(column_num).

        Args:
            buttonbox:
            column_num:
        """
        raise NotImplementedError

    # noinspection PyUnusedLocal
    def tmdb_search(self, *args, **kwargs):
        """
        Search TMDB for matching movies titles.

        A delayed search event is placed in the Tk/Tcl event queue. An earlier call awaiting
        execution will be removed.

        Args:
            *args: Unused argument supplied by tkinter.
            **kwargs: Unused argument supplied by tkinter.
        """
        substring = self.entry_fields[TITLE].current_value
        if substring:  # pragma no branch
            if self.last_text_event_id:  # pragma no branch
                self.parent.after_cancel(self.last_text_event_id)

            # Place a new call to tmdb_search_callback.
            self.last_text_event_id = self.parent.after(
                self.last_text_queue_timer,
                self.tmdb_search_callback,
                substring,
                self.tmdb_work_queue,
            )

    def tmdb_consumer(self):
        """Consumer of queued records of movies found on the TMDB website.

        Movies arriving in the work queue are placed into a treeview. Complete movie
        details are stored in a dict for later retrieval should the user select a
        treeview entry.
        """
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
            for movie_bag in work_package:
                item_id = self.tmdb_treeview.insert(
                    "",
                    "end",
                    values=(
                        movie_bag.get("title", ""),
                        movie_bag.get("year", ""),
                        ", ".join(movie_bag.get("directors", "")),
                    ),
                )
                self.tmdb_movies[item_id] = movie_bag

        finally:
            # Have tkinter call this function again after the poll interval.
            # noinspection PyTypeChecker
            self.recall_id = self.parent.after(
                self.work_queue_poll,
                self.tmdb_consumer,
            )

    # noinspection PyUnusedLocal
    def tmdb_treeview_callback(self, *args, **kwargs):
        """Populate the input form with data from the selected TMDB movie.

        Args:
            *args: Not used but may be provided by caller.
            **kwargs: Not used but may be provided by caller.
        """
        if self.tmdb_treeview.selection():
            item_id = self.tmdb_treeview.selection()[0]
        # Else user has deselected prior selection.
        else:  # pragma nocover
            return

        for name, widget in self.tmdb_movies[item_id].items():
            match name:
                case "title" | "year" | "duration" | "notes":
                    self.entry_fields[name].current_value = widget
                case "directors":  # pragma nocover
                    self.entry_fields[name].current_value = ", ".join(
                        [director for director in widget]
                    )
                case _:  # pragma nocover
                    logging.error(f"Unexpected key: {name}")  # pragma no branch
                    raise KeyError(f"Unexpected key: {name}")  # pragma no branch

    def as_movie_bag(self) -> MovieBag:
        """Returns the form data as a movie bag

        Returns:
            movie bag
        """
        movie_bag = MovieBag()
        for name, widget in self.entry_fields.items():
            if widget.current_value:
                match name:
                    case "title":
                        movie_bag["title"] = widget.current_value
                    case "year":
                        movie_bag["year"] = MovieInteger(widget.current_value)
                    case "duration":
                        movie_bag["duration"] = MovieInteger(widget.current_value)
                    case "directors":
                        movie_bag["directors"] = set(widget.current_value.split(", "))
                    case "notes":
                        movie_bag["notes"] = widget.current_value
                    case "tags":
                        movie_bag["tags"] = {  # pragma no branch
                            tag for tag in widget.current_value
                        }
                    case _:
                        logging.error(f"Unexpected key: {name}")
                        raise KeyError(f"Unexpected key: {name}")
        return movie_bag

    # noinspection PyUnusedLocal
    def destroy(self, *args):
        """
        Destroy all widgets of this class.

        Args:
            *args: Not used but needed to match external caller.
        """
        self.parent.after_cancel(self.recall_id)
        self.outer_frame.destroy()


@dataclass
class AddMovieGUI(MovieGUI):
    """Create and manage a GUI form for entering a new movie."""

    add_movie_callback: Callable[[MovieBag], None] = field(default=None, kw_only=True)

    def _create_buttons(self, buttonbox: ttk.Frame, column_num: Iterator):
        commit_button = common.create_button(
            buttonbox,
            COMMIT_TEXT,
            column=next(column_num),
            command=self.commit,
            default="normal",
        )

        # Commit button registration with title and year field observers
        title_entry_field = self.entry_fields[TITLE]
        year_entry_field = self.entry_fields[YEAR]
        title_entry_field.observer.register(
            self.enable_commit_button(
                commit_button, title_entry_field, year_entry_field
            )
        )
        year_entry_field.observer.register(
            self.enable_commit_button(
                commit_button, title_entry_field, year_entry_field
            )
        )

    @staticmethod
    def enable_commit_button(
        commit_button: ttk.Button,
        title: tk_facade.Entry,
        year: tk_facade.Entry,
    ) -> Callable:
        """
        The returned function may be registered with any observer of widgets that need to
        affect the enabled or disabled state of the commit button.

        Args:
            commit_button:
            title:
            year:

        Returns:
            A callable which will be invoked by tkinter whenever the observed fields
            are changed by the user.
        """

        # noinspection PyUnusedLocal
        def func(*args, **kwargs):
            """The commit button will be enabled if the title and the year fields contain data.

            Args:
                *args: Sent by tkinter but not used.
                **kwargs: Sent by tkinter but not used.
            """
            common.enable_button(
                commit_button, state=title.has_data() and year.has_data()
            )

        return func

    def commit(self):
        """Commits a new movie to the database.

        The form is cleared of entries so the user can enter and commit
        another movie.
        """
        self.add_movie_callback(self.as_movie_bag())

        for v in self.entry_fields.values():
            v.clear_current_value()
        items = self.tmdb_treeview.get_children()
        self.tmdb_treeview.delete(*items)


@dataclass
class EditMovieGUI(MovieGUI):
    """Create and manage a GUI form for editing an existing movie."""

    edit_movie_callback: Callable[[MovieBag], None] = field(default=None, kw_only=True)
    delete_movie_callback: Callable = field(default=None, kw_only=True)

    def _create_buttons(self, buttonbox: ttk.Frame, column_num: Iterator):
        commit_button = common.create_button(
            buttonbox,
            COMMIT_TEXT,
            column=next(column_num),
            command=self.commit,
            default="disabled",
        )
        delete_button = common.create_button(
            buttonbox,
            DELETE_TEXT,
            column=next(column_num),
            command=self.delete,
            default="active",
        )

        # Commit button registration with fields' observer.
        for entry_field in self.entry_fields.values():
            entry_field.observer.register(
                self.enable_buttons(commit_button, delete_button)
            )

    def enable_buttons(
        self, commit_button: ttk.Button, delete_button: ttk.Button
    ) -> Callable:
        """The returned function may be registered with any observer of widgets that need to
        affect the enabled or disabled state of the commit button.

        Args:
            commit_button:
            delete_button:

        Returns:
            A callable which will be invoked by tkinter whenever registered fields
            are changed by the user.,
        """

        # noinspection PyUnusedLocal
        def func(*args, **kwargs):
            """The enabled or disabled state of the commit button will be changed depending on
            whether any observed fields have changed.

            Note: The database key fields of title and year may not be empty. The commit button
            will be disabled if the current value of either is an empty string.

                Args:
                    *args: Sent by tkinter callback but not used.
                    **kwargs: Sent by tkinter callback but not used.
            """
            changes = any(  # pragma no branch
                [entry_field.changed() for entry_field in self.entry_fields.values()]
            )
            db_keys_present = all(  # pragma no branch
                [self.entry_fields[k].has_data() for k in (TITLE, YEAR)]
            )
            common.enable_button(commit_button, state=changes and db_keys_present)
            common.enable_button(delete_button, state=not changes)

        return func

    def commit(self):
        """Commit an edited movie to the database."""
        self.parent.after(0, self.edit_movie_callback, self.as_movie_bag())
        self.destroy()

    def delete(self):
        """The user clicked the 'Delete' button."""
        if gui_askyesno(
            message=MOVIE_DELETE_MESSAGE, icon="question", parent=self.parent
        ):
            # noinspection PyTypeChecker
            self.parent.after(0, self.delete_movie_callback)
            self.destroy()


@dataclass
class TagGUI:
    """A base class for tag widgets"""

    parent: tk.Tk
    tag: str = ""

    # The main outer frame of this class.
    outer_frame: ttk.Frame = field(default=None, init=False, repr=False)

    # An internal dictionary to simplify field data management.
    entry_fields: Dict[str, tk_facade.Entry] = field(
        default_factory=dict, init=False, repr=False
    )

    # noinspection DuplicatedCode
    def __post_init__(self):
        """Create the Tk widget."""
        # Create outer frames to hold fields and buttons.
        self.outer_frame, body_frame, buttonbox = common.create_body_and_buttonbox(
            self.parent, type(self).__name__.lower(), self.destroy
        )
        self.user_input_frame(body_frame)
        self.create_buttons(buttonbox)
        common.init_button_enablements(self.entry_fields)

    def user_input_frame(self, body_frame: tk.Frame):
        """
        This creates the widgets which will be used to enter data and display data
        retrieved from the user's database.

        Args:
            body_frame:The frame into which the widgets will be placed.
        """
        # todo The test suite for this method needs to be rewritten to current standards

        input_zone = common.LabelAndField(body_frame)

        # Tag field
        self.entry_fields[MOVIE_TAGS] = tk_facade.Entry(MOVIE_TAGS_TEXT, body_frame)
        self.entry_fields[MOVIE_TAGS].original_value = self.tag
        input_zone.add_entry_row(self.entry_fields[MOVIE_TAGS])
        self.entry_fields[MOVIE_TAGS].widget.focus_set()

    def create_buttons(self, body_frame: tk.Frame):
        """Creates the buttons for this widget."""
        raise NotImplementedError  # pragma nocover

    def destroy(self):
        """Destroy this instance's widgets."""
        self.outer_frame.destroy()


@dataclass
class SearchTagGUI(TagGUI):
    """Present a form for creating a search pattern which may be used to search the
    database for matching tags.
    """

    search_tag_callback: Callable[[str], None] = None

    # noinspection DuplicatedCode
    def create_buttons(self, buttonbox: ttk.Frame):
        """
        Creates the commit and cancel buttons.

        Args:
            buttonbox:
        """
        # noinspection DuplicatedCode
        column_num = itertools.count()
        search_button = common.create_button(
            buttonbox,
            SEARCH_TEXT,
            column=next(column_num),
            command=self.search,
            default="disabled",
        )
        common.create_button(
            buttonbox,
            CANCEL_TEXT,
            column=next(column_num),
            command=self.destroy,
            default="active",
        )

        # Commit button registration with tag field observer
        tag_entry_field = self.entry_fields[MOVIE_TAGS]
        tag_entry_field.observer.register(
            self.enable_search_button(search_button, tag_entry_field)
        )

    @staticmethod
    def enable_search_button(
        search_button: ttk.Button, tag_field: tk_facade.Entry
    ) -> Callable:
        """
        The returned function may be registered with any observer of widgets that need to
        affect the enabled or disabled state of the search button.

        Args:
            search_button:
            tag_field:

        Returns:
            A callable which will be invoked by tkinter whenever the observed field
            is changed by the user.
        """

        # noinspection PyUnusedLocal
        def func(*args, **kwargs):
            """The search button will be enabled if the tag field has data.

            Args:
                *args: Sent by tkinter but not used.
                **kwargs: Sent by tkinter but not used.
            """
            common.enable_button(search_button, state=tag_field.has_data())

        return func

    def search(self):
        """Respond to the user's click of the 'Search' button."""
        search_pattern = self.entry_fields[MOVIE_TAGS].current_value
        self.search_tag_callback(search_pattern)
        self.destroy()


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
        frames = common.create_body_and_buttonbox(
            self.parent, type(self).__name__.lower(), self.destroy
        )
        self.outer_frame, body_frame, buttonbox = frames

        # Create and grid treeview
        tree = ttk.Treeview(body_frame, columns=[], height=10, selectmode="browse")
        tree.grid(column=0, row=0, sticky="w")

        # Specify column width and title
        tree.column("#0", width=350)
        tree.heading("#0", text=MOVIE_TAGS_TEXT)

        # Populate the treeview rows
        for tag in self.tags_to_show:
            tree.insert(
                "", "end", iid=tag, text=tag, values=[], tags=MOVIE_TAGS, open=True
            )

        # Bind the treeview callback
        tree.bind("<<TreeviewSelect>>", func=self.selection_callback(tree))

        # Create the button
        column_num = 0
        common.create_button(
            buttonbox, CANCEL_TEXT, column_num, self.destroy, default="active"
        )

    def selection_callback(self, tree: ttk.Treeview) -> Callable:
        """Call the callback provided by the caller and destroy all Tk widgets
        associated with this class.

        Args:
            tree:

        Returns:
            The callback.
        """

        # noinspection PyUnusedLocal
        def func(*args):
            """Save the newly changed user selection.

            Args:
                *args: Not used. Needed for compatibility with Tk:Tcl caller.
            """
            tag = tree.selection()[0]
            self.destroy()
            self.select_tag_callback(tag)

        return func

    def destroy(self):
        """Destroy all Tk widgets associated with this class."""
        self.outer_frame.destroy()


@dataclass
class PreferencesGUI:
    """Create and manage a Tk input form which allows the user to update
    program preferences."""

    parent: tk.Tk

    # Preference fields
    api_key: str
    do_not_ask: bool

    # On commit this callback will be called with the updated preferences.
    save_callback: Callable[[str, bool], None]

    # Internal field names and associated GUI texts.
    api_key_name = "api_key"
    api_key_text = "TMDB API key"
    use_tmdb_name = "use_tmdb"
    use_tmdb_text = "Use TMDB (The Movie Database)"

    toplevel: tk.Toplevel = None
    # A more convenient data structure for entry fields.
    entry_fields: Dict[str, Union[tk_facade.Entry, tk_facade.Checkbutton]] = field(
        default_factory=dict, init=False, repr=False
    )

    # noinspection DuplicatedCode
    def __post_init__(self):
        """Create the widgets and closures required for their operation."""
        # Create a toplevel window
        self.toplevel = tk.Toplevel(self.parent)

        # Create outer frames to hold fields and buttons.
        frames = common.create_body_and_buttonbox(
            self.toplevel, type(self).__name__.lower(), self.destroy
        )
        self.outer_frame, body_frame, buttonbox = frames
        input_zone = common.LabelAndField(body_frame)

        # TMDB API key field
        self.entry_fields[self.api_key_name] = tk_facade.Entry(
            self.api_key_text, body_frame
        )
        self.entry_fields[self.api_key_name].original_value = self.api_key
        input_zone.add_entry_row(self.entry_fields[self.api_key_name])

        # 'Use TMDB' checkbutton
        self.entry_fields[self.use_tmdb_name] = tk_facade.Checkbutton(
            self.use_tmdb_text, body_frame
        )
        self.entry_fields[self.use_tmdb_name].original_value = self.do_not_ask
        input_zone.add_checkbox_row(self.entry_fields[self.use_tmdb_name])

        # Create buttons
        column_num = itertools.count()
        save_button = common.create_button(
            buttonbox,
            SAVE_TEXT,
            column=next(column_num),
            command=self.save,
            default="disabled",
        )
        common.create_button(
            buttonbox,
            CANCEL_TEXT,
            column=next(column_num),
            command=self.destroy,
            default="active",
        )

        # Register the save button callback with its many observers.
        for entry_field in self.entry_fields.values():
            entry_field.observer.register(
                self.enable_save_button(save_button),
            )

    def enable_save_button(self, save_button: ttk.Button) -> Callable:
        """Manages the enabled or disabled state of the save button.

        Args:
            save_button:

        Returns:
            A callable which will be invoked by tkinter whenever the api_key or
            use_tmdb field contents are changed by the user,
        """

        # noinspection PyUnusedLocal
        def func(*args, **kwargs):
            """This function enables or disables the save button depending on the
            state of fields compared to their original values.

            Args:
                *args: Sent by tkinter callback but not used.
                **kwargs: Sent by tkinter callback but not used.
            """
            state = any(  # pragma no branch
                [entry_field.changed() for entry_field in self.entry_fields.values()]
            )
            common.enable_button(save_button, state=state)

        return func

    def save(self):
        """Save the edited preference values to the config file."""
        tmdb_api_key: str = self.entry_fields[self.api_key_name].current_value
        # noinspection PyTypeChecker
        tmdb_do_not_ask_again: bool = self.entry_fields[
            self.use_tmdb_name
        ].current_value
        self.save_callback(tmdb_api_key, tmdb_do_not_ask_again)
        self.destroy()

    def destroy(self):
        """Destroy all widgets of this class."""
        self.toplevel.destroy()


def gui_messagebox(
    parent: TkParentType, message: str, detail: str = "", icon: str = "info"
):
    """Present a Tk messagebox."""
    # noinspection PyTypeChecker
    messagebox.showinfo(parent, message, detail=detail, icon=icon)


def gui_askyesno(
    parent: TkParentType,
    message: str,
    detail: str = "",
    icon: str = "question",
    default="no",
) -> bool:
    """
    Present a Tk askyesno dialog.

    Args:
        default:
        parent:
        message:
        detail:
        icon:

    Returns:
        True if user clicks 'Yes', False if user clicks 'No'
    """
    # noinspection PyTypeChecker
    return messagebox.askyesno(
        parent, message, detail=detail, icon=icon, default=default
    )


# todo remove this unused function
def gui_askopenfilename(
    parent: TkParentType,
    filetypes: Iterable[tuple[str, str | list[str] | tuple[str, ...]]] | None,
):
    """Present a Tk askopenfilename."""
    return filedialog.askopenfilename(parent=parent, filetypes=filetypes)
