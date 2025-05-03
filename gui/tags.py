"""This module contains code for movie tag maintenance."""

#  Copyright© 2025. Stephen Rigden.
#  Last modified 5/3/25, 3:01 PM by stephen.
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
from tkinter import messagebox
import tkinter.ttk as ttk
from collections.abc import Callable
from functools import partial
import itertools
from dataclasses import dataclass, field

from gui.constants import *
from gui import common
from gui.tk_facade import EntryFields, Entry


TAG_DELETE_MESSAGE = "Do you want to delete this tag?"


@dataclass
class TagGUI:
    """A base class for tag widgets"""

    parent: tk.Tk
    tag: str = ""

    # The main outer frame of this class.
    outer_frame: ttk.Frame = field(default=None, init=False, repr=False)

    # An internal dictionary to simplify field data management.
    entry_fields: EntryFields = field(
        default_factory=dict,
        init=False,
        repr=False,
    )

    def __post_init__(self):
        """Creates the tag form."""
        self.outer_frame, body_frame, buttonbox = common.create_body_and_buttonbox(
            self.parent, type(self).__name__.lower()
        )
        self.user_input_frame(body_frame)
        self.create_buttons(buttonbox)
        common.init_button_enablements(self.entry_fields)

    def user_input_frame(self, body_frame: ttk.Frame):
        """Creates the widgets which will be used to enter data and
        display data retrieved from the user's database.

        Args:
            body_frame: The frame which contains the entry fields.
        """
        input_zone = common.LabelAndField(body_frame)

        self.entry_fields[MOVIE_TAGS] = Entry(MOVIE_TAGS_TEXT, body_frame)
        self.entry_fields[MOVIE_TAGS].original_value = self.tag
        input_zone.add_entry_row(self.entry_fields[MOVIE_TAGS])
        self.entry_fields[MOVIE_TAGS].widget.focus_set()

    def create_buttons(self, buttonbox: ttk.Frame):
        """Subclasses should override to create buttons needed for
        the subclass.
        """
        raise NotImplementedError  # pragma nocover

    def destroy(self):
        """Destroys the outer frame and all the widgets it contains."""
        self.parent.unbind("<Escape>")
        self.parent.unbind("<Command-.>")
        self.parent.unbind("<Return>")
        self.parent.unbind("<KP_Enter>")
        self.parent.unbind("<Delete>")

        self.outer_frame.destroy()


# noinspection DuplicatedCode
@dataclass
class AddTagGUI(TagGUI):
    """Presents a form for adding a tag."""

    add_tag_callback: Callable[[str], None] = field(kw_only=True)

    def create_buttons(self, buttonbox: ttk.Frame):
        """Creates commit and cancel buttons.

        The enabled/disabled state of the commit button will be controlled
        by the enable_button_callback method. This callback will be
        registered with the observer for changes in the tag field.

        Args:
            buttonbox:
        """
        column_num = itertools.count()
        commit_button = common.create_button(
            buttonbox,
            COMMIT_TEXT,
            column=next(column_num),
            command=self.commit,
            default="disabled",
        )
        self.parent.bind(
            "<Return>",
            partial(common.invoke_button, commit_button),
        )
        self.parent.bind(
            "<KP_Enter>",
            partial(common.invoke_button, commit_button),
        )
        cancel_button = common.create_button(
            buttonbox,
            CANCEL_TEXT,
            column=next(column_num),
            command=self.destroy,
            default="active",
        )
        self.parent.bind(
            "<Escape>",
            partial(common.invoke_button, cancel_button),
        )
        self.parent.bind(
            "<Command-.>",
            partial(common.invoke_button, cancel_button),
        )

        tag_entry_field = self.entry_fields[MOVIE_TAGS]
        callback = partial(
            self.enable_button_callback,
            commit_button,
            tag_entry_field,
        )
        tag_entry_field.observer.register(callback)

    # noinspection PyUnusedLocal
    @staticmethod
    def enable_button_callback(
        commit_button: ttk.Button,
        tag_entry_field: Entry,
        *args,
        **kwargs,
    ):
        """Called by the observer of the tags field whenever the contents
        are changed by the user.

        Args:
            commit_button:
            tag_entry_field:
            *args: Not used but needed to match tkinter arguments
            **kwargs: Not used but needed to match tkinter arguments
        """
        common.enable_button(commit_button, state=tag_entry_field.has_data())

    def commit(self):
        """Commits the tag to the database and closes the input form."""
        tag = self.entry_fields[MOVIE_TAGS].current_value
        self.parent.after(0, self.add_tag_callback, tag)
        self.destroy()


@dataclass
class EditTagGUI(TagGUI):
    """Presents a form for editing a tag."""

    edit_tag_callback: Callable[[str], None] = field(kw_only=True)
    delete_tag_callback: Callable[[], None] = field(kw_only=True)

    def create_buttons(self, buttonbox: ttk.Frame):
        """Creates commit, delete, and cancel buttons.

        The enabled/disabled state of the commit and delete buttons will
        be controlled by the enable_button_callback method. This callback
        will be registered with the observer for changes in the tag field.

        Args:
            buttonbox:
        """

        column_num = itertools.count()
        commit_button = common.create_button(
            buttonbox,
            COMMIT_TEXT,
            column=next(column_num),
            command=self.commit,
            default="disabled",
        )
        self.parent.bind(
            "<Return>",
            partial(common.invoke_button, commit_button),
        )
        self.parent.bind(
            "<KP_Enter>",
            partial(common.invoke_button, commit_button),
        )
        delete_button = common.create_button(
            buttonbox,
            DELETE_TEXT,
            column=next(column_num),
            command=self.delete,
            default="active",
        )
        self.parent.bind(
            "<Delete>",
            partial(common.invoke_button, delete_button),
        )
        cancel_button = common.create_button(
            buttonbox,
            CANCEL_TEXT,
            column=next(column_num),
            command=self.destroy,
            default="active",
        )
        self.parent.bind(
            "<Escape>",
            partial(common.invoke_button, cancel_button),
        )
        self.parent.bind(
            "<Command-.>",
            partial(common.invoke_button, cancel_button),
        )

        tag_entry_field = self.entry_fields[MOVIE_TAGS]
        callback = partial(
            self.enable_button_callback,
            commit_button,
            delete_button,
            tag_entry_field,
        )
        tag_entry_field.observer.register(callback)

    # noinspection PyUnusedLocal
    @staticmethod
    def enable_button_callback(
        commit_button: ttk.Button,
        delete_button: ttk.Button,
        tag_entry_field: Entry,
        *args,
        **kwargs,
    ):
        """Called by the observer of the tags field whenever the contents
        are changed by the user.

        Args:
            commit_button:
            delete_button:
            tag_entry_field:
            *args: Not used but needed to match tkinter arguments
            **kwargs: Not used but needed to match tkinter arguments
        """
        common.enable_button(commit_button, state=tag_entry_field.has_data())
        common.enable_button(delete_button, state=tag_entry_field.has_data())

    def commit(self):
        """Commits the tag to the database and closes the input form."""
        tag = self.entry_fields[MOVIE_TAGS].current_value
        self.parent.after(0, self.edit_tag_callback, tag)
        self.destroy()

    def delete(self):
        """Deletes the tag from the database and closes the input form.

        If the user declines the alert asking for confirmation the form
        is re-initialized.
        """
        if messagebox.askyesno(
            message=f"{TAG_DELETE_MESSAGE}",
            icon="question",
            default="no",
            parent=self.parent,
        ):
            # noinspection PyTypeChecker
            self.parent.after(0, self.delete_tag_callback)
            self.destroy()
        else:
            self.entry_fields[MOVIE_TAGS].original_value = self.tag
            self.entry_fields[MOVIE_TAGS].widget.focus_set()


# noinspection DuplicatedCode
@dataclass
class SearchTagGUI(TagGUI):
    """Presents a form for searching for a tag."""

    search_tag_callback: Callable[[str], None] = field(kw_only=True)

    def create_buttons(self, buttonbox: ttk.Frame):
        """Creates search and cancel buttons.

        The enabled/disabled state of the search button will be controlled
        by the enable_button_callback method. This callback will be
        registered with the observer for changes in the tag field.

        Args:
            buttonbox:
        """
        column_num = itertools.count()
        search_button = common.create_button(
            buttonbox,
            SEARCH_TEXT,
            column=next(column_num),
            command=self.search,
            default="disabled",
        )
        self.parent.bind(
            "<Return>",
            partial(common.invoke_button, search_button),
        )
        self.parent.bind(
            "<KP_Enter>",
            partial(common.invoke_button, search_button),
        )
        cancel_button = common.create_button(
            buttonbox,
            CANCEL_TEXT,
            column=next(column_num),
            command=self.destroy,
            default="active",
        )
        self.parent.bind(
            "<Escape>",
            partial(common.invoke_button, cancel_button),
        )
        self.parent.bind(
            "<Command-.>",
            partial(common.invoke_button, cancel_button),
        )

        tag_entry_field = self.entry_fields[MOVIE_TAGS]
        callback = partial(
            self.enable_button_callback,
            search_button,
            tag_entry_field,
        )
        tag_entry_field.observer.register(callback)

    # noinspection PyUnusedLocal
    @staticmethod
    def enable_button_callback(
        search_button: ttk.Button,
        tag_entry_field: Entry,
        *args,
        **kwargs,
    ):
        """Called by the observer of the tags field whenever the contents
        are changed by the user.

        Args:
            search_button:
            tag_entry_field:
            *args: Not used but needed to match tkinter arguments
            **kwargs: Not used but needed to match tkinter arguments
        """
        common.enable_button(search_button, state=tag_entry_field.has_data())

    def search(self):
        """Commits the tag to the database and closes the input form."""
        tag = self.entry_fields[MOVIE_TAGS].current_value
        self.parent.after(0, self.search_tag_callback, tag)
        self.destroy()
