"""GUI Windows.

This module includes windows for presenting data and returning entered data to its callers.
"""

#  Copyright (c) 2022-2024. Stephen Rigden.
#  Last modified 3/19/24, 8:23 AM by stephen.
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

# This tkinter import method supports accurate test mocking of tk and ttk.
import tkinter as tk
import tkinter.ttk as ttk

from tkinter import filedialog, messagebox
from dataclasses import dataclass, field
from typing import (
    Callable,
    Dict,
    Iterable,
    Iterator,
    Tuple,
    Literal,
    Optional,
    Union,
)

import config
import exception
import tk_facade
from tk_facade import TkParentType
from globalconstants import *


# todo Turn on PyCharm's duplicate inspection

TITLE_TEXT = "Title"
YEAR_TEXT = "Year"
DIRECTOR_TEXT = "Director"
DURATION_TEXT = "Length (minutes)"
NOTES_TEXT = "Notes"
MOVIE_TAG_TEXT = "Tag"
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
        self.fill_buttonbox(buttonbox)
        self.tmdb_results_frame(tmdb_frame)

        # Set the enabled state of the buttons
        # todo Move to separate method - See TagGUI for model.
        # todo unittest next line
        for v in self.entry_fields.values():
            v.observer.notify()

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
        # todo new issue: escape key should be a tuple of self.id and name for correct deletion of
        #  multiple windows with same name.
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
        This creates the widgets which will be used to enter data an display data
        retrieved from the user's database.

        Args:
            body_frame:The frame into which the widgets will be placed.
        """

        input_zone = InputZone(body_frame)

        # Create entry rows for title, year, director, and duration.
        for name, text in zip(
            (TITLE, YEAR, DIRECTOR, DURATION),
            (TITLE_TEXT, YEAR_TEXT, DIRECTOR_TEXT, DURATION_TEXT),
        ):
            self.entry_fields[name] = tk_facade.Entry(text, body_frame)
            input_zone.add_entry_row(self.entry_fields[name])
        focus_set(self.entry_fields[TITLE].widget)

        # Create label and text widget.
        self.entry_fields[NOTES] = tk_facade.Text(NOTES_TEXT, body_frame)
        input_zone.add_text_row(self.entry_fields[NOTES])

        # Create a label and treeview for movie tags.
        self.entry_fields[MOVIE_TAGS] = tk_facade.Treeview(MOVIE_TAGS_TEXT, body_frame)
        input_zone.add_treeview_row(self.entry_fields[MOVIE_TAGS], self.all_tags)

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
            columns=("title", "year", "director"),
            show=["headings"],
            height=20,
            selectmode="browse",
        )
        self.tmdb_treeview.column("title", width=300, stretch=True)
        self.tmdb_treeview.heading("title", text="Title", anchor="w")
        self.tmdb_treeview.column("year", width=40, stretch=True)
        self.tmdb_treeview.heading("year", text="Year", anchor="w")
        self.tmdb_treeview.column("director", width=200, stretch=True)
        self.tmdb_treeview.heading("director", text="Director", anchor="w")
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
        create_button(
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
            if self.last_text_event_id:
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
            for movie in work_package:
                movie["director"] = ", ".join(movie["director"])
                item_id = self.tmdb_treeview.insert(
                    "", "end", values=(movie["title"], movie["year"], movie["director"])
                )
                self.tmdb_movies[item_id] = movie

        finally:
            # Have tkinter call this function again after the poll interval.
            self.recall_id = self.parent.after(self.work_queue_poll, self.tmdb_consumer)

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

        for k, v in self.tmdb_movies[item_id].items():
            self.entry_fields[k].current_value = v

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

    add_movie_callback: Callable[[MovieTD], None] = field(default=None, kw_only=True)

    def _create_buttons(self, buttonbox: ttk.Frame, column_num: Iterator):
        commit_button = create_button(
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
            enable_button(commit_button, title.has_data() and year.has_data())

        return func

    def commit(self):
        """Commit a new movie to the database."""
        self.return_fields = {
            name: entry_field.current_value
            for name, entry_field in self.entry_fields.items()
        }
        try:
            self.add_movie_callback(self.return_fields)

        # Alert user to title and year constraint failure.
        except exception.MovieDBConstraintFailure:
            exc = exception.MovieDBConstraintFailure
            messagebox.showinfo(parent=self.parent, message=exc.msg, detail=exc.detail)

        # Alert user to invalid year (not YYYY within range).
        except exception.MovieYearConstraintFailure as exc:
            msg = exc.args[0]
            messagebox.showinfo(parent=self.parent, message=msg)

        # Clear fields ready for next entry.
        else:
            for v in self.entry_fields.values():
                v.clear_current_value()
            items = self.tmdb_treeview.get_children()
            self.tmdb_treeview.delete(*items)


@dataclass
class EditMovieGUI(MovieGUI):
    """Create and manage a GUI form for editing an existing movie."""

    old_movie: config.MovieUpdateDef = field(default=None, kw_only=True)
    edit_movie_callback: Callable[[config.FindMovieTypedDict], None] = field(
        default=None, kw_only=True
    )
    delete_movie_callback: Callable[[config.FindMovieTypedDict], None] = field(
        default=None, kw_only=True
    )

    def __post_init__(self):
        super().__post_init__()
        for k in self.entry_fields.keys():
            # noinspection PyTypedDict
            self.entry_fields[k].original_value = self.old_movie[k]

    def _create_buttons(self, buttonbox: ttk.Frame, column_num: Iterator):
        commit_button = create_button(
            buttonbox,
            COMMIT_TEXT,
            column=next(column_num),
            command=self.commit,
            default="disabled",
        )
        delete_button = create_button(
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
            changes = any(
                [entry_field.changed() for entry_field in self.entry_fields.values()]
            )
            db_keys_present = all(
                [self.entry_fields[k].has_data() for k in (TITLE, YEAR)]
            )
            enable_button(commit_button, changes and db_keys_present)
            enable_button(delete_button, not changes)

        return func

    def commit(self):
        """Commit an edited movie to the database."""
        self.return_fields = {
            name: entry_field.current_value  # pragma no cover
            for name, entry_field in self.entry_fields.items()
        }

        try:
            # noinspection PyArgumentList
            self.edit_movie_callback(self.return_fields)

        # Alert user to title and year constraint failure.
        except exception.MovieDBConstraintFailure:
            exc = exception.MovieDBConstraintFailure
            messagebox.showinfo(parent=self.parent, message=exc.msg, detail=exc.detail)

        # Alert user to invalid year (not YYYY within range).
        except exception.MovieYearConstraintFailure as exc:
            msg = exc.args[0]
            messagebox.showinfo(parent=self.parent, message=msg)

        else:
            self.destroy()

    def delete(self):
        """The user clicked the 'Delete' button."""
        if gui_askyesno(
            message=MOVIE_DELETE_MESSAGE, icon="question", parent=self.parent
        ):
            movie = config.FindMovieTypedDict(
                title=self.entry_fields[TITLE].original_value,
                year=[self.entry_fields[YEAR].original_value],
            )
            self.delete_movie_callback(movie)
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
        self.outer_frame, body_frame, buttonbox = create_input_form_framing(
            self.parent, type(self).__name__.lower(), self.destroy
        )
        self.user_input_frame(body_frame)
        self.create_buttons(buttonbox)
        self.init_button_enablements()

    def user_input_frame(self, body_frame: tk.Frame):
        """
        This creates the widgets which will be used to enter data an display data
        retrieved from the user's database.

        Args:
            body_frame:The frame into which the widgets will be placed.
        """
        input_zone = InputZone(body_frame)

        # Tag field
        self.entry_fields[MOVIE_TAG] = tk_facade.Entry(MOVIE_TAG_TEXT, body_frame)
        self.entry_fields[MOVIE_TAG].original_value = self.tag
        input_zone.add_entry_row(self.entry_fields[MOVIE_TAG])
        focus_set(self.entry_fields[MOVIE_TAG].widget)

    def create_buttons(self, body_frame: tk.Frame):
        """Creates the buttons for this widget."""
        raise NotImplementedError  # pragma nocover

    def init_button_enablements(self):
        """Set the initial enabled state of the buttons"""
        for v in self.entry_fields.values():
            v.observer.notify()

    def destroy(self):
        """Destroy this instance's widgets."""
        self.outer_frame.destroy()


@dataclass
class AddTagGUI(TagGUI):
    """Present a form for adding a tag to the user."""

    add_tag_callback: Callable[[str], None] = None

    # noinspection DuplicatedCode
    def create_buttons(self, buttonbox: ttk.Frame):
        """
        Creates the commit and cancel buttons.

        Args:
            buttonbox:
        """
        # noinspection DuplicatedCode
        column_num = itertools.count()

        commit_button = create_button(
            buttonbox,
            COMMIT_TEXT,
            column=next(column_num),
            command=self.commit,
            default="disabled",
        )
        create_button(
            buttonbox,
            CANCEL_TEXT,
            column=next(column_num),
            command=self.destroy,
            default="active",
        )

        # Commit button registration with tag field observer
        tag_entry_field = self.entry_fields[MOVIE_TAG]
        tag_entry_field.observer.register(
            self.enable_commit_button(commit_button, tag_entry_field)
        )

    @staticmethod
    def enable_commit_button(
        commit_button: ttk.Button, tag_field: tk_facade.Entry
    ) -> Callable:
        """
        The returned function may be registered with any observer of widgets that need to
        affect the enabled or disabled state of the commit button.

        Args:
            commit_button:
            tag_field:

        Returns:
            A callable which will be invoked by tkinter whenever the observed field
            is changed by the user.
        """

        # noinspection PyUnusedLocal
        def func(*args, **kwargs):
            """The commit button will be enabled if the tag field has data.

            Args:
                *args: Sent by tkinter but not used.
                **kwargs: Sent by tkinter but not used.
            """
            enable_button(commit_button, tag_field.has_data())

        return func

    def commit(self):
        """The user has clicked the 'Commit' button. The tag is returned to the caller and the
        window is deleted."""
        tag = self.entry_fields[MOVIE_TAG].current_value
        self.add_tag_callback(tag)
        self.destroy()


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
        search_button = create_button(
            buttonbox,
            SEARCH_TEXT,
            column=next(column_num),
            command=self.search,
            default="disabled",
        )
        create_button(
            buttonbox,
            CANCEL_TEXT,
            column=next(column_num),
            command=self.destroy,
            default="active",
        )

        # Commit button registration with tag field observer
        tag_entry_field = self.entry_fields[MOVIE_TAG]
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
            enable_button(search_button, tag_field.has_data())

        return func

    def search(self):
        """Respond to the user's click of the 'Search' button."""
        search_pattern = self.entry_fields[MOVIE_TAG].current_value
        try:
            self.search_tag_callback(search_pattern)
        except exception.DatabaseSearchFoundNothing:
            # Warn user and give user the opportunity to reenter the search criteria.
            gui_messagebox(self.parent, NO_MATCH_MESSAGE, NO_MATCH_DETAIL)
        else:
            self.destroy()


@dataclass
class EditTagGUI(TagGUI):
    """Present a form for editing or deleting a tag to the user."""

    delete_tag_callback: Callable[[], None] = None
    edit_tag_callback: Callable[[str], None] = None

    # noinspection DuplicatedCode
    def create_buttons(self, buttonbox: ttk.Frame):
        """
        Creates the commit and cancel buttons.

        Args:
            buttonbox:
        """
        column_num = itertools.count()
        commit_button = create_button(
            buttonbox,
            COMMIT_TEXT,
            column=next(column_num),
            command=self.commit,
            default="disabled",
        )
        delete_button = create_button(
            buttonbox,
            DELETE_TEXT,
            column=next(column_num),
            command=self.delete,
            default="active",
        )
        create_button(
            buttonbox,
            CANCEL_TEXT,
            column=next(column_num),
            command=self.destroy,
            default="active",
        )

        # Commit button registration
        tag_entry_field = self.entry_fields[MOVIE_TAG]
        tag_entry_field.observer.register(
            self.enable_buttons(commit_button, delete_button, tag_entry_field)
        )

    @staticmethod
    def enable_buttons(
        commit_button: ttk.Button, delete_button: ttk.Button, tag_field: tk_facade.Entry
    ) -> Callable:
        """
        The returned function may be registered with any observer of widgets that need to
        affect the enabled or disabled state of the commit button.

        Args:
            commit_button:
            delete_button:
            tag_field:

        Returns:
            A callable which will be invoked by tkinter whenever the observed field
            is changed by the user.
        """

        # noinspection PyUnusedLocal
        def func(*args, **kwargs):
            """The commit button will be enabled if the tag field has data and has been
            changed from its original value.

            Args:
                *args: Sent by tkinter but not used.
                **kwargs: Sent by tkinter but not used.
            """
            enable_button(commit_button, tag_field.has_data() and tag_field.changed())
            enable_button(
                delete_button, tag_field.has_data() and not tag_field.changed()
            )

        return func

    def commit(self):
        """The user clicked the 'Commit' button."""
        tag = self.entry_fields[MOVIE_TAG].current_value
        self.edit_tag_callback(tag)
        self.destroy()

    def delete(self):
        """The user clicked the 'Delete' button.

        Get the user's confirmation of deletion with a dialog window. Either exit the
        method or call the registered deletion callback."""
        if gui_askyesno(
            message=f"{TAG_DELETE_MESSAGE}",
            icon="question",
            default="no",
            parent=self.parent,
        ):
            self.delete_tag_callback()
            self.destroy()
        else:
            self.entry_fields[MOVIE_TAG].original_value = self.tag
            focus_set(self.entry_fields[MOVIE_TAG].widget)


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
        frames = create_input_form_framing(
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
        create_button(
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
        frames = create_input_form_framing(
            self.toplevel, type(self).__name__.lower(), self.destroy
        )
        self.outer_frame, body_frame, buttonbox = frames
        input_zone = InputZone(body_frame)

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
        save_button = create_button(
            buttonbox,
            SAVE_TEXT,
            column=next(column_num),
            command=self.save,
            default="disabled",
        )
        create_button(
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
            state = any(
                [entry_field.changed() for entry_field in self.entry_fields.values()]
            )
            enable_button(save_button, state)

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


def gui_askopenfilename(
    parent: TkParentType,
    filetypes: Iterable[tuple[str, str | list[str] | tuple[str, ...]]] | None,
):
    """Present a Tk askopenfilename."""
    return filedialog.askopenfilename(parent=parent, filetypes=filetypes)


@dataclass
class InputZone:
    """Configure the parent frame with two columns to contain labels and widgets for
    user input.

    Widgets are added by calling the various methods `add_<widget>_row`, for example,
    add_entry_row. Each call will grid the row as the last row in the zone and will
    align the labels and the widget.
    """

    parent: TkParentType
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
        # Create a column for scrollbars.
        self.parent.columnconfigure(2, weight=1)

    def add_entry_row(self, entry_field: tk_facade.Entry):
        """
        Add label and entry widgets as the bottom row.

        Args:
            entry_field:
        """
        row_ix = next(self.row)
        self._create_label(entry_field.label_text, row_ix)
        entry_field.widget.configure(width=self.col_1_width)
        entry_field.widget.grid(column=1, row=row_ix)

    def add_text_row(self, entry_field: tk_facade.Text):
        """
        Add label and text widgets as the bottom row.

        Args:
            entry_field:

        Returns:
            text widget
        """
        row_ix = next(self.row)
        self._create_label(entry_field.label_text, row_ix)

        entry_field.widget.configure(
            width=self.col_1_width - 2,
            height=8,
            wrap="word",
            font="TkTextFont",
            padx=15,
            pady=10,
        )
        entry_field.widget.grid(column=1, row=row_ix, sticky="e")

        scrollbar = ttk.Scrollbar(
            self.parent, orient="vertical", command=entry_field.widget.yview
        )
        entry_field.widget.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(column=2, row=row_ix, sticky="ns")

    def add_checkbox_row(self, entry_field: tk_facade.Checkbutton):
        """
        Add a label and a checkbox as the bottom row.

        Checkbutton has a 'command' parameter used for callbacks.
        For consistency with other widgets this method will use the text variable via
        link_field_to_neuron. This link is set up by the caller.

        Args:
            entry_field:
        """
        row_ix = next(self.row)
        entry_field.widget.configure(
            text=entry_field.label_text, width=self.col_1_width
        )
        entry_field.widget.grid(column=1, row=row_ix)

    def add_treeview_row(
        self, entry_field: tk_facade.Treeview, all_tags: Sequence[str]
    ):
        """
        Add a label and a treeview as the bottom row.

        Args:
            entry_field:
            all_tags
        """
        row_ix = next(self.row)
        self._create_label(entry_field.label_text, row_ix)

        entry_field.widget.configure(
            columns=("tags",),
            height=7,
            selectmode="extended",
            show="tree",
            padding=5,
        )
        entry_field.widget.column("tags", width=127)
        for item in all_tags:
            if item:
                entry_field.widget.insert("", "end", item, text=item, tags="tags")
        entry_field.widget.grid(column=1, row=row_ix, sticky="e")

        scrollbar = ttk.Scrollbar(
            self.parent, orient="vertical", command=entry_field.widget.yview
        )
        entry_field.widget.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(column=2, row=row_ix, sticky="ns")

    def _create_label(self, text: str, row_ix: int):
        """Create a label for the current row.

        Args:
            text:
            row_ix: The row into which the label will be placed.
        """

        label = ttk.Label(self.parent, text=text)
        label.grid(column=0, row=row_ix, sticky="ne", padx=5)


def create_body_and_button_frames(
    parent: TkParentType, name: str, destroy: Callable
) -> Tuple[ttk.Frame, ttk.Frame, ttk.Frame]:
    """
    Create the outer frames for an input form.

    This consists of an upper body and a lower buttonbox frame.

    Note: Do not call this function if the input form has label and entry widgets. Use the higher
    level function create_input_form_framing.

    Args:
        parent: The Tk parent frame.
        name: Name which identifies which moviedb class has the destroy method.
        destroy:

    Returns:
        Outer frame which contains the body and buttonbox frames.
        Body frame
        Buttonbox frame
    """

    outer_frame = ttk.Frame(parent, name=name)
    outer_frame.grid(column=0, row=0, sticky="nsew")
    outer_frame.columnconfigure(0, weight=1)
    config.current.escape_key_dict[name] = destroy

    body_frame = ttk.Frame(outer_frame, padding=(10, 25, 10, 0))
    body_frame.grid(column=0, row=0, sticky="n")

    buttonbox = ttk.Frame(outer_frame, padding=(5, 5, 10, 10))
    buttonbox.grid(column=0, row=1, sticky="e")

    return outer_frame, body_frame, buttonbox


def create_input_form_framing(
    parent: TkParentType, name: str, destroy: Callable
) -> Tuple[ttk.Frame, ttk.Frame, ttk.Frame]:
    """Create the outer frames for an input form.

    An input body frame has two columns, one for the field labels and one for the
    entry fields.

    Note: For a plain form without columns call the lower level function
    create_body_and_button_frames.

    Args:
        parent: The Tk parent frame.
        name: Name which identifies which moviedb class has the destroy method.
        destroy:

    Returns:
        Outer frame which contains the body and buttonbox frames.
        Body frame
        Buttonbox frame
    """
    outer_frame, body_frame, buttonbox = create_body_and_button_frames(
        parent, name, destroy
    )
    outer_frame.rowconfigure(0, weight=1)
    outer_frame.rowconfigure(1, minsize=35)
    return outer_frame, body_frame, buttonbox


def create_button(
    buttonbox: ttk.Frame,
    text: str,
    column: int,
    command: Callable,
    default: DefaultLiteral,
) -> ttk.Button:
    """Create a button

    Args:
        buttonbox: The enclosing buttonbox.
        text: The enclosing buttonbox.
        column: The index of the button in the buttonbox. '0' is leftmost position.
        command: The command to be executed when the button is clicked.
        default: 'normal', 'active', or 'disabled. See 'The Command Callback' in the
            'Button' section of TkDocs. https://tkdocs.com/tutorial/widgets.html#button

    Returns:
        The button
    """
    button = ttk.Button(buttonbox, text=text, default=default, command=command)
    button.grid(column=column, row=0)
    button.bind("<Return>", lambda event, b=button: b.invoke())  # pragma nocover
    return button


def enable_button(button: ttk.Button, state: bool):
    """
    Enable or disable a button.

    Args:
        button:
        state:
    """
    if state:
        # Enable the button
        button.state(["!disabled"])
        # Highlight the button to show it is enabled
        button.configure(default="active")
    else:
        # Disable the button
        button.state(["disabled"])
        # Remove the button highlight
        button.configure(default="disabled")


def focus_set(entry: ttk.Entry):
    """Set initial focus for this class."""
    entry.focus_set()
    entry.select_range(0, tk.END)
    entry.icursor(tk.END)
