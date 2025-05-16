"""This module contains code for movie maintenance."""

#  Copyright© 2025. Stephen Rigden.
#  Last modified 5/16/25, 6:53 AM by stephen.
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

import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
from collections.abc import Callable, Iterator, Collection
from dataclasses import dataclass, KW_ONLY, field
import datetime
from functools import partial
from itertools import count
import logging
import queue

from moviebag import (
    MovieBag,
    MovieInteger,
    setstr_to_str,
)
from gui import common, tk_facade
from gui.constants import *


MOVIE_DELETE_MESSAGE = "Do you want to delete this movie?"
UNEXPECTED_KEY = "Unexpected key"


@dataclass
class MovieGUI:
    """This base class for movies creates a standard movies input form."""

    parent: tk.Tk
    database_callback: Callable[[MovieBag], None]

    _: KW_ONLY
    tmdb_callback: Callable[[str, queue.LifoQueue], None]
    all_tags: Collection[str]
    prepopulate: MovieBag

    entry_fields: dict[
        str,
        tk_facade.Entry | tk_facade.Text | tk_facade.Treeview,
    ] = field(default_factory=dict, init=False, repr=False, compare=False)
    outer_frame: ttk.Frame = field(default=None, init=False, repr=False, compare=False)
    tmdb_treeview: ttk.Treeview = field(default=None, init=False, repr=False)

    # TMDB Producer/consumer queue.
    tmdb_data_queue: queue.LifoQueue = field(
        default_factory=queue.Queue, init=False, repr=False
    )
    # Polling frequency for queue consumer.
    tmdb_consumer_poll: int = field(default=40, init=False, repr=False)
    # ID of consumer event used for cancellation of queue polling.
    tmdb_consumer_recall_id: str = field(default=None, init=False, repr=False)
    # Used to hold movies sent from TMDB
    tmdb_movies: dict[str, MovieBag] = field(
        default_factory=MovieBag, init=False, repr=False
    )
    # Used to pause the Internet call to TMDB while the user is still
    #  entering match data.
    match_pause: int = field(default=500, init=False, repr=False)
    match_pause_id: str = field(default="", init=False, repr=False)

    def __post_init__(self):
        self.outer_frame, body_frame, buttonbox = common.create_body_and_buttonbox(
            self.parent,
            type(self).__name__.lower(),
        )
        tmdb_frame = self.create_tmdb_frame(self.outer_frame)
        self.fill_body(body_frame)
        self.populate()
        self.fill_buttonbox(buttonbox)
        self.fill_tmdb_frame(tmdb_frame)
        common.init_button_enablements(self.entry_fields)

    @staticmethod
    def create_tmdb_frame(outer_frame: ttk.Frame) -> ttk.Frame:
        """Creates a frame which will contain movies found in TMDB.

        Args:
            outer_frame:

        Returns:
            tmdb_frame:
        """
        outer_frame.columnconfigure(1, weight=1000)
        tmdb_frame = ttk.Frame(outer_frame, padding=10)
        tmdb_frame.grid(column=1, row=0, sticky="nw")
        tmdb_frame.columnconfigure(0, weight=1, minsize=25)
        return tmdb_frame

    def fill_body(self, body_frame: ttk.Frame):
        """Creates the widgets for the entry form and the data structures for their
        support.

        The widgets are:
            title: ttk.Entry
            year: ttk.Entry
            directors: ttk.Entry
            duration: ttk.Entry
            notes: ttk.Text
            tags: ttk.Treeview

        Args:
            body_frame:
        """
        label_and_field = common.LabelAndField(body_frame)

        # Create entry rows for timestamp, title, year, director, and duration.
        for name, text in zip(
            (TITLE, YEAR, DIRECTORS, STARS, DURATION, TIMESTAMP),
            (
                TITLE_TEXT,
                YEAR_TEXT,
                DIRECTORS_TEXT,
                STARS_TEXT,
                DURATION_TEXT,
                TIMESTAMP_TEXT,
            ),
        ):
            self.entry_fields[name] = tk_facade.Entry(text, body_frame)
            label_and_field.add_entry_row(self.entry_fields[name])
        self.entry_fields[TIMESTAMP].widget.state(["disabled"])

        # Create label and text widgets.
        self.entry_fields[SYNOPSIS] = tk_facade.Text(SYNOPSIS_TEXT, body_frame)
        label_and_field.add_text_row(self.entry_fields[SYNOPSIS])
        self.entry_fields[NOTES] = tk_facade.Text(NOTES_TEXT, body_frame)
        label_and_field.add_text_row(self.entry_fields[NOTES], height=2)

        # Create a label and treeview for movie tags.
        self.entry_fields[MOVIE_TAGS] = tk_facade.Treeview(MOVIE_TAGS_TEXT, body_frame)
        label_and_field.add_treeview_row(
            self.entry_fields[MOVIE_TAGS],
            sorted(self.all_tags),
        )

        self.entry_fields[TITLE].widget.focus_set()

    def populate(self):
        """Initialises field values."""
        created = self.prepopulate.get("created")
        updated = self.prepopulate.get("updated")
        timestamp_str = self.strftime(created, updated)
        self.entry_fields[TIMESTAMP].original_value = timestamp_str

        self.entry_fields[TITLE].original_value = self.prepopulate.get("title", "")
        self.entry_fields[TITLE].widget.icursor(tk.END)
        if year := self.prepopulate.get("year"):
            self.entry_fields[YEAR].original_value = str(year)
        else:
            self.entry_fields[YEAR].original_value = ""
        self.entry_fields[DIRECTORS].original_value = setstr_to_str(
            self.prepopulate.get("directors")
        )
        self.entry_fields[STARS].original_value = setstr_to_str(
            self.prepopulate.get("stars")
        )
        if duration := self.prepopulate.get("duration"):
            self.entry_fields[DURATION].original_value = str(duration)
        else:
            self.entry_fields[DURATION].original_value = ""
        self.entry_fields[SYNOPSIS].original_value = self.prepopulate.get(
            "synopsis", ""
        )
        self.entry_fields[NOTES].original_value = self.prepopulate.get("notes", "")
        if tags := self.prepopulate.get("tags"):
            self.entry_fields[MOVIE_TAGS].original_value = sorted(list(tags))
        else:
            self.entry_fields[MOVIE_TAGS].original_value = []

    @staticmethod
    def strftime(created: datetime.datetime, updated: datetime.datetime):
        """Formats created and updated timestamps for display

        Args:
            created:
            updated:

        Returns:
            Formatted display string. For example, '12/12/25 edited 1/21/26' or
            '12/12/25' if it has not been edited.
        """
        if created:
            str_created = created.strftime("%x")
        else:
            str_created = ""
        if updated and updated != created:
            str_updated = " edited " + updated.strftime("%x")
        else:
            str_updated = ""
        return str_created + str_updated

    def as_movie_bag(self) -> MovieBag:
        """Returns the form data as a movie bag

        Returns:
            movie bag
        """
        movie_bag = MovieBag()
        for name, widget in self.entry_fields.items():
            value = widget.current_value
            # noinspection PyUnreachableCode
            match name:
                case "timestamp":
                    pass
                case "title" if value:
                    movie_bag["title"] = value
                case "year" if value:
                    movie_bag["year"] = MovieInteger(value)
                case "duration" if value:
                    movie_bag["duration"] = MovieInteger(value)
                case "directors" if value:
                    movie_bag["directors"] = set(value.split(", "))
                case "directors":
                    movie_bag["directors"] = set()
                case "stars" if value:
                    movie_bag["stars"] = set(value.split(", "))
                case "stars":
                    movie_bag["stars"] = set()
                case "synopsis":
                    movie_bag["synopsis"] = value
                case "notes":
                    movie_bag["notes"] = value
                case "tags" if value:
                    movie_bag["tags"] = {tag for tag in value}  # pragma no branch
                case "tags":
                    movie_bag["tags"] = set()
                case "title" | "year" | "duration":
                    pass
                case _:
                    logging.error(f"Unexpected key: {name}")
                    raise KeyError(f"Unexpected key: {name}")
        return movie_bag

    def fill_buttonbox(self, buttonbox: ttk.Frame):
        """Fills the buttonbox with buttons.

        This adds one default Cancel button after any buttons added by
        subclasses. It calls the abstract class method create_button which
        must be overridden by subclasses.

        Args:
            buttonbox:
        """
        column_counter = count()
        self.create_buttons(buttonbox, column_counter)

        cancel_button = common.create_button(
            buttonbox,
            CANCEL_TEXT,
            column=next(column_counter),
            command=self.destroy,
            default="active",
        )
        common.bind_key(self.parent, "<Escape>", cancel_button)
        common.bind_key(self.parent, "<Command-.>", cancel_button)

    def create_buttons(self, buttonbox: ttk.Frame, column_counter: Iterator):
        """Create buttons within the buttonbox.

        Subclasses may call create_button to place a button in the buttonbox at
        next(column_counter).

        Args:
            buttonbox:
            column_counter:
        """
        raise NotImplementedError

    def commit(self):
        """Calls the callback with movie data and destroys this widget."""
        self.parent.after(0, self.database_callback, self.as_movie_bag())
        self.destroy()

    # noinspection PyUnusedLocal
    def destroy(self, *args):
        """
        Destroy all widgets of this class.

        Args:
            *args: Not used but needed to match external caller.
        """
        # Undo bindings on Tk/Tcl root
        # Shipman says tkinter bindings can only be attached to root or toplevel
        # widgets. This seems to be borne out by observation.
        # Issue moviedb-#500 will use toplevels throughout so obviating this
        #  need to undo bindings.
        self.parent.unbind("<Escape>")
        self.parent.unbind("<Command-.>")
        self.parent.unbind("<Return>")
        self.parent.unbind("<KP_Enter>")
        self.parent.unbind("<Delete>")

        self.parent.after_cancel(self.tmdb_consumer_recall_id)
        self.outer_frame.destroy()

    def fill_tmdb_frame(self, tmdb_frame: ttk.Frame):
        """
        This creates a treeview which will display movies retrieved from TMDB. It also
        sets up the queue for the producer and consumer pattern used to retrieve the
        on-line data from TMDB.

        Args:
            tmdb_frame: The frame into which the widgets will be placed.
        """
        tview = self.tmdb_treeview = ttk.Treeview(
            tmdb_frame,
            columns=(TITLE, YEAR, DIRECTORS, SYNOPSIS),
            show=["headings"],
            height=20,
            selectmode="browse",
        )

        # Create the table columns
        tview.column(TITLE, width=250, stretch=True)
        tview.heading(TITLE, text=TITLE_TEXT, anchor="w")
        tview.column(YEAR, width=40, stretch=True)
        tview.heading(YEAR, text=YEAR_TEXT, anchor="w")
        tview.column(DIRECTORS, width=200, stretch=True)
        tview.heading(DIRECTORS, text=DIRECTORS_TEXT, anchor="w")
        tview.column(SYNOPSIS, width=400, stretch=True)
        tview.heading(SYNOPSIS, text=SYNOPSIS_TEXT, anchor="w")
        tview.grid(column=0, row=0, sticky="nsew")
        tview.bind(
            "<<TreeviewSelect>>", func=partial(self.tmdb_treeview_callback, tview)
        )

        # Start polling the consumer end of the producer and consumer queue.
        self.tmdb_consumer()

        # Register the TMDB search function with the title field's observer.
        self.entry_fields[TITLE].observer.register(self.tmdb_search)

    # noinspection PyUnusedLocal
    def tmdb_treeview_callback(self, treeview: ttk.Treeview, *args, **kwargs):
        """Populates the input form with data from the selected TMDB movie.

        Args:
            treeview: The table of TMDB movies from which the user has just selected
            one movie. If the event loop is delayed it is possible for the user to
            deselect movie in which case this method must handle an empty treeview
            selection list.
            *args: Not used but needed to match Tk/Tcl caller's arguments.
            **kwargs: Not used but needed to match Tk/Tcl caller's arguments.
        """
        try:
            item_id = treeview.selection()[0]
        except IndexError:  # pragma nocover
            # User has deselected prior
            # selection. This can 'get through' to here
            #  only if the Tk/Tcl event loop has been blocked from rapid
            #  processing.
            return

        for k, v in self.tmdb_movies[item_id].items():
            # noinspection PyUnreachableCode
            match k:
                case "title" | "year" | "duration" | "synopsis":
                    self.entry_fields[k].current_value = str(v)
                case "directors":  # pragma nocover
                    self.entry_fields[k].current_value = ", ".join(
                        [director for director in sorted(list(v))]
                    )
                case _:  # pragma nocover
                    logging.error(f"Unexpected key: {k}")
                    raise KeyError(f"Unexpected key: {k}")
        return

    # noinspection PyUnusedLocal
    def tmdb_search(self, *args, **kwargs):
        """Schedules a delayed search of TMDB for matching movie titles.

        The Internet call to TMDB will not be made until the user has finished
        entering match data.
        finished: When no new data has been entered for self.match_pause
        milliseconds.

        Args:
            *args: Unused argument supplied by tkinter.
            **kwargs: Unused argument supplied by tkinter.
        """
        if match := self.entry_fields[TITLE].current_value:  # pragma no branch
            if self.match_pause_id:
                self.parent.after_cancel(self.match_pause_id)

            # Place a new call to tmdb_search_callback.
            self.match_pause_id = self.parent.after(
                self.match_pause,
                self.tmdb_callback,
                match,
                self.tmdb_data_queue,
            )

    def tmdb_consumer(self):
        """Consumer of queued records of movies found on the TMDB website.

        Movies arriving in the work queue are placed into a treeview. Complete
        movie details are stored in a dict for later retrieval.
        """
        try:
            # Tkinter can't wait for the thread blocking `get` method…
            work_package = self.tmdb_data_queue.get_nowait()

        except queue.Empty:
            pass
            # …so an empty queue is not exceptional.

        else:
            # Process a data package.
            items = self.tmdb_treeview.get_children()
            self.tmdb_treeview.delete(*items)
            self.tmdb_movies = {}
            for movie_bag in work_package:
                title = movie_bag.get("title", "")
                year = str(movie_bag.get("year", ""))
                directors = movie_bag.get("directors", "")
                directors = ", ".join(  # pragma no branch
                    [director for director in sorted(list(directors))]
                )
                synopsis = movie_bag.get("synopsis", "")
                iid = self.tmdb_treeview.insert(
                    "",
                    "end",
                    values=(title, year, directors, synopsis),
                )
                self.tmdb_movies[iid] = movie_bag

        finally:
            # Have tkinter call this function again after the poll interval.
            # noinspection PyTypeChecker
            self.tmdb_consumer_recall_id = self.parent.after(
                self.tmdb_consumer_poll,
                self.tmdb_consumer,
            )


@dataclass
class AddMovieGUI(MovieGUI):
    """Create and manage a GUI form for entering a new movie."""

    def create_buttons(self, buttonbox: ttk.Frame, column_num: Iterator):
        """Adds a commit button and registers its enabler function with
        the observers of the title and year fields.

        Args:
            buttonbox:
            column_num:
        """
        commit_button = common.create_button(
            buttonbox,
            COMMIT_TEXT,
            column=next(column_num),
            command=self.commit,
            default="normal",
        )
        common.bind_key(self.parent, "<Return>", commit_button)
        common.bind_key(self.parent, "<KP_Enter>", commit_button)

        self.entry_fields[TITLE].observer.register(
            partial(
                self.enable_commit_button,
                commit_button,
                self.entry_fields[TITLE],
                self.entry_fields[YEAR],
            )
        )
        self.entry_fields[YEAR].observer.register(
            partial(
                self.enable_commit_button,
                commit_button,
                self.entry_fields[TITLE],
                self.entry_fields[YEAR],
            )
        )

    # noinspection PyUnusedLocal
    @staticmethod
    def enable_commit_button(
        commit_button: ttk.Button,
        title: tk_facade.Entry,
        year: tk_facade.Entry,
        *args,
        **kwargs,
    ):
        """Enables the Commit button if either the title or the year field
        has data.

        This function will be registered with the observers for the title
        and year fields. It should be created as a partial function.

        Args:
            commit_button: Partial argument.
            title: Partial argument.
            year: Partial argument.
            *args: Unused but needed to match caller's arguments
            **kwargs: Unused but needed to match caller's arguments
        """
        common.enable_button(
            commit_button,
            state=title.has_data() and year.has_data(),
        )


@dataclass
class EditMovieGUI(MovieGUI):
    """Create and manage a GUI form for viewing, editing, or deleting a movie."""

    delete_movie_callback: Callable

    def create_buttons(self, buttonbox: ttk.Frame, column_num: Iterator):
        """Create commit and delete buttons.

        Args:
            buttonbox:
            column_num:
        """
        # noinspection DuplicatedCode
        commit_button = common.create_button(
            buttonbox,
            COMMIT_TEXT,
            column=next(column_num),
            command=self.commit,
            default="disabled",
        )
        common.bind_key(self.parent, "<Return>", commit_button)
        common.bind_key(self.parent, "<KP_Enter>", commit_button)

        delete_button = common.create_button(
            buttonbox,
            DELETE_TEXT,
            column=next(column_num),
            command=self.delete,
            default="active",
        )
        common.bind_key(self.parent, "<Delete>", delete_button)

        # Register buttons with the fields' observers.
        for entry_field in self.entry_fields.values():
            entry_field.observer.register(
                partial(self.enable_buttons, commit_button, delete_button)
            )

    # noinspection PyUnusedLocal
    def enable_buttons(
        self, commit_button: ttk.Button, delete_button: ttk.Button, *args, **kwargs
    ):
        """Enables the Commit and Delete buttons depending on the state of the
        entered data.

        This function will be registered with the observers for all fields.
        It should be created as a partial function.

        Args:
            commit_button:
            delete_button:
            *args: Unused but needed to match caller's arguments
            **kwargs: Unused but needed to match caller's arguments
        """
        changes = any(  # pragma no branch
            [entry_field.changed() for entry_field in self.entry_fields.values()]
        )
        db_keys_present = all(  # pragma no branch
            [self.entry_fields[k].has_data() for k in (TITLE, YEAR)]
        )
        common.enable_button(commit_button, state=changes and db_keys_present)
        common.enable_button(delete_button, state=not changes)

    def delete(self):
        """Delete a movie from the database.

        Ask the user for permission to delete the movie and, if given,
        delete it.
        """
        if messagebox.askyesno(
            message=MOVIE_DELETE_MESSAGE,
            icon="question",
            parent=self.parent,
        ):
            # noinspection PyTypeChecker
            self.parent.after(0, self.delete_movie_callback)
            self.destroy()


@dataclass
class SearchMovieGUI(MovieGUI):
    """Create and manage a GUI form to search movies in the database."""

    def create_buttons(self, buttonbox: ttk.Frame, column_num: Iterator):
        """Adds a search button and registers its enabler function with
        all field observers.

        Args:
            buttonbox:
            column_num:
        """
        search_button = common.create_button(
            buttonbox,
            SEARCH_TEXT,
            column=next(column_num),
            command=self.commit,
            default="normal",
        )
        common.bind_key(self.parent, "<Return>", search_button)
        common.bind_key(self.parent, "<KP_Enter>", search_button)

        for widget in self.entry_fields.values():
            widget.observer.register(
                partial(
                    self.enable_search_button,
                    search_button,
                )
            )

    # noinspection PyUnusedLocal
    def enable_search_button(self, search_button, *args, **kwargs):
        """Enables the Search button depending on the state of the entered data.

        This function will be registered with the observers for all fields.
        It should be created as a partial function.

        Args:
            search_button:
            *args: Unused but needed to match caller's arguments
            **kwargs: Unused but needed to match caller's arguments
        """
        changes = any(  # pragma no branch
            [entry_field.changed() for entry_field in self.entry_fields.values()]
        )
        common.enable_button(search_button, state=changes)
