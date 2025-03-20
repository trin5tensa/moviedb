"""This module contains code for movie maintenance."""

#  Copyright© 2025. Stephen Rigden.
#  Last modified 3/20/25, 11:56 AM by stephen.
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

# This tkinter import method supports accurate test mocking of tk and ttk.
import tkinter as tk
import tkinter.ttk as ttk
from collections.abc import Callable, Sequence, Iterator
from dataclasses import dataclass, KW_ONLY, field
from functools import partial
from itertools import count
import logging
import queue

from globalconstants import (
    MovieBag,
    MovieInteger,
    setstr_to_str,
    TITLE,
    YEAR,
    DIRECTORS,
    DURATION,
    NOTES,
    MOVIE_TAGS,
)
from gui import common, tk_facade

TITLE_TEXT = "Title"
YEAR_TEXT = "Year"
DIRECTORS_TEXT = "Directors"
DURATION_TEXT = "Runtime"
NOTES_TEXT = "Notes"
MOVIE_TAGS_TEXT = "Tags"

UNEXPECTED_KEY = "Unexpected key"


@dataclass
class MovieGUI:
    """This base class for movies creates a standard movies input form."""

    parent: tk.Tk

    _: KW_ONLY
    tmdb_callback: Callable[[str, queue.LifoQueue], None]
    all_tags: Sequence[str]

    prepopulate: MovieBag = field(
        default_factory=MovieBag, init=False, repr=False, compare=False
    )
    entry_fields: dict[
        str,
        tk_facade.Entry | tk_facade.Text | tk_facade.Treeview,
    ] = field(default_factory=dict, init=False, repr=False, compare=False)
    outer_frame: ttk.Frame = field(default=None, init=False, repr=False, compare=False)

    # These variables are used for the consumer end of the TMDB
    # producer/consumer pattern.
    tmdb_poller: str = field(default=None, init=False, repr=False, compare=False)
    tmdb_movies: dict[str, MovieBag] = field(
        default_factory=MovieBag, init=False, repr=False
    )

    def __post_init__(self):
        self.outer_frame, body_frame, buttonbox = common.create_body_and_buttonbox(
            self.parent, type(self).__name__.lower(), self.destroy
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
        # noinspection DuplicatedCode
        label_and_field = common.LabelAndField(body_frame)

        # Create entry rows for title, year, director, and duration.
        for name, text in zip(
            (TITLE, YEAR, DIRECTORS, DURATION),
            (TITLE_TEXT, YEAR_TEXT, DIRECTORS_TEXT, DURATION_TEXT),
        ):
            self.entry_fields[name] = tk_facade.Entry(text, body_frame)
            label_and_field.add_entry_row(self.entry_fields[name])

        # Create label and text widget.
        self.entry_fields[NOTES] = tk_facade.Text(NOTES_TEXT, body_frame)
        label_and_field.add_text_row(self.entry_fields[NOTES])

        # Create a label and treeview for movie tags.
        self.entry_fields[MOVIE_TAGS] = tk_facade.Treeview(MOVIE_TAGS_TEXT, body_frame)
        label_and_field.add_treeview_row(self.entry_fields[MOVIE_TAGS], self.all_tags)

        self.entry_fields[TITLE].widget.focus_set()

    def populate(self):
        """Initialises field values."""
        self.entry_fields[TITLE].original_value = self.prepopulate.get("title", "")
        if year := self.prepopulate.get("year"):
            self.entry_fields[YEAR].original_value = str(year)
        else:
            self.entry_fields[YEAR].original_value = ""
        self.entry_fields[DIRECTORS].original_value = setstr_to_str(
            self.prepopulate.get("directors")
        )
        if duration := self.prepopulate.get("duration"):
            self.entry_fields[DURATION].original_value = str(duration)
        else:
            self.entry_fields[DURATION].original_value = ""
        self.entry_fields[NOTES].original_value = self.prepopulate.get("notes", "")
        if tags := self.prepopulate.get("tags"):
            self.entry_fields[MOVIE_TAGS].original_value = sorted(list(tags))
        else:
            self.entry_fields[MOVIE_TAGS].original_value = []

    # noinspection DuplicatedCode
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

    def fill_buttonbox(self, buttonbox: ttk.Frame):
        """Fills the buttonbox with buttons.

        This adds one default Cancel button after any buttons added by
        subclasses. It calls the abstract class method create_button which
        must be overridden by subclasses.

        Args:
            buttonbox:
        """
        column_counter = count()
        self._create_buttons(buttonbox, column_counter)
        common.create_button(
            buttonbox,
            common.CANCEL_TEXT,
            column=next(column_counter),
            command=self.destroy,
            default="active",
        )

    def _create_buttons(self, buttonbox: ttk.Frame, column_counter: Iterator):
        """Create buttons within the buttonbox.

        Subclasses may call create_button to place a button in the buttonbox at
        next(column_counter).

        Args:
            buttonbox:
            column_counter:
        """
        raise NotImplementedError

    # noinspection PyUnusedLocal
    def destroy(self, *args):
        """
        Destroy all widgets of this class.

        Args:
            *args: Not used but needed to match external caller.
        """
        self.parent.after_cancel(self.tmdb_poller)
        self.outer_frame.destroy()

    def fill_tmdb_frame(self, tmdb_frame: ttk.Frame):
        """
        This creates a treeview which will display movies retrieved from TMDB. It also
        sets up the queue for the producer and consumer pattern used to retrieve the
        on-line data from TMDB.

        Args:
            tmdb_frame: The frame into which the widgets will be placed.
        """
        tview = ttk.Treeview(
            tmdb_frame,
            columns=(TITLE, YEAR, DIRECTORS),
            show=["headings"],
            height=20,
            selectmode="browse",
        )

        # Create the table columns
        # todo could 'Notes' be added? Needs to be done during integration
        #  testing to check widths and stretching.
        tview.column(TITLE, width=300, stretch=True)
        tview.heading(TITLE, text=TITLE_TEXT, anchor="w")
        tview.column(YEAR, width=40, stretch=True)
        tview.heading(YEAR, text=YEAR_TEXT, anchor="w")
        tview.column(DIRECTORS, width=200, stretch=True)
        tview.heading(DIRECTORS, text=DIRECTORS_TEXT, anchor="w")
        tview.grid(column=0, row=0, sticky="nsew")
        tview.bind(
            "<<TreeviewSelect>>", func=partial(self.tmdb_treeview_callback, tview)
        )

        # Start polling the consumer queue
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
            match k:
                case "title" | "year" | "duration" | "notes":
                    self.entry_fields[k].current_value = str(v)
                case "directors":  # pragma nocover
                    self.entry_fields[k].current_value = ", ".join(
                        [director for director in sorted(list(v))]
                    )
                case _:  # pragma nocover
                    logging.error(f"Unexpected key: {k}")
                    raise KeyError(f"Unexpected key: {k}")
        return

    def tmdb_consumer(self):
        """Stub method."""
        pass

    def tmdb_search(self, *args, **kwargs):
        """Stub method."""
        pass

    # todo
    #  tmdb_search
    #  tmdb_consumer
    #  tmdb_treeview_callback
