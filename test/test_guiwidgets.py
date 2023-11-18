"""Test module."""
#  Copyright (c) 2022-2023. Stephen Rigden.
#  Last modified 11/18/23, 5:44 AM by stephen.
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
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Callable, Sequence, Generator

import pytest

import exception
import guiwidgets
from test.dummytk import DummyTk, TkStringVar, TtkButton, TtkEntry, TtkFrame, TtkLabel


# noinspection PyMissingOrEmptyDocstring
class TestSearchMovieGUI:
    # Test Basic Initialization

    def test_parent_initialized(self, patch_tk):
        with self.movie_context() as movie_gui:
            assert movie_gui.parent == DummyTk()
            assert movie_gui.all_tags == ("test tag 1", "test tag 2")
            assert isinstance(movie_gui.callback, Callable)

    # Test create body

    def test_create_simple_body_item_called(self, patch_tk, monkeypatch):
        calls = []
        monkeypatch.setattr(
            guiwidgets.SearchMovieGUI,
            "create_body_item",
            lambda *args: calls.append(args),
        )
        monkeypatch.setattr(guiwidgets, "_focus_set", lambda *args: None)
        with self.movie_context() as movie_gui:
            assert calls == [
                (
                    movie_gui,
                    TtkFrame(
                        parent=TtkFrame(parent=DummyTk(), padding=""),
                        padding=(10, 25, 10, 0),
                    ),
                    "title",
                    "Title",
                    0,
                ),
                (
                    movie_gui,
                    TtkFrame(
                        parent=TtkFrame(parent=DummyTk(), padding=""),
                        padding=(10, 25, 10, 0),
                    ),
                    "director",
                    "Director",
                    2,
                ),
                (
                    movie_gui,
                    TtkFrame(
                        parent=TtkFrame(parent=DummyTk(), padding=""),
                        padding=(10, 25, 10, 0),
                    ),
                    "notes",
                    "Notes",
                    4,
                ),
            ]

    def test_create_min_max_body_item_called(self, patch_tk, monkeypatch):
        calls = []
        monkeypatch.setattr(
            guiwidgets.SearchMovieGUI,
            "create_min_max_body_item",
            lambda *args: calls.append(args),
        )
        with self.movie_context() as movie_gui:
            assert calls == [
                (
                    movie_gui,
                    TtkFrame(
                        parent=TtkFrame(parent=DummyTk(), padding=""),
                        padding=(10, 25, 10, 0),
                    ),
                    "year",
                    "Year",
                    1,
                ),
                (
                    movie_gui,
                    TtkFrame(
                        parent=TtkFrame(parent=DummyTk(), padding=""),
                        padding=(10, 25, 10, 0),
                    ),
                    "minutes",
                    "Length (minutes)",
                    3,
                ),
            ]

    def test_focus_set_called(self, patch_tk, monkeypatch):
        calls = []
        monkeypatch.setattr(guiwidgets, "_focus_set", lambda *args: calls.append(True))
        with self.movie_context():
            assert calls == [True]

    # noinspection DuplicatedCode
    def test_create_tag_treeview_called(self, patch_tk, patch_movie_treeview):
        with self.movie_context():
            assert treeview_call[0][1] == guiwidgets.TAG_TREEVIEW_INTERNAL_NAME
            assert treeview_call[0][2] == TtkFrame(
                parent=TtkFrame(parent=DummyTk(), padding=""), padding=(10, 25, 10, 0)
            )
            assert treeview_call[0][3] == 5
            assert treeview_call[0][4] == 0
            assert treeview_call[0][5] == "Tags"
            assert treeview_call[0][6] == ("test tag 1", "test tag 2")
            assert treeview_call[0][7]("test signal") == "test signal"

    # noinspection PyShadowingNames
    def test_treeview_observer_registered(self, patch_tk, monkeypatch):
        self.tag_treeview_observer_args = []
        monkeypatch.setattr(
            guiwidgets.MovieGUIBase.tag_treeview_observer,
            "register",
            lambda *args: self.tag_treeview_observer_args.append(args),
        )
        with self.movie_context():
            for args in self.tag_treeview_observer_args:
                assert isinstance(args[1], Callable)
        assert len(self.tag_treeview_observer_args) == 2

    # Test create body item

    def test_labels_called(self, patch_tk, check):
        with self.movie_context() as movie_gui:
            with check:
                outerframe = movie_gui.parent.children[0]
                body_frame = outerframe.children[0]

                first_label = body_frame.children[0]
                assert first_label == TtkLabel(
                    parent=TtkFrame(
                        parent=TtkFrame(parent=DummyTk(), padding=""),
                        padding=(10, 25, 10, 0),
                    ),
                    text="Title",
                    padding="",
                )

                year_label = body_frame.children[2]
                assert year_label == TtkLabel(
                    parent=TtkFrame(
                        parent=TtkFrame(parent=DummyTk(), padding=""),
                        padding=(10, 25, 10, 0),
                    ),
                    text="Year (min, max)",
                    padding="",
                )

    def test_body_item_ttk_label_gridded(self, patch_tk):
        with self.movie_context() as movie_gui:
            outerframe = movie_gui.parent.children[0]
            body_frame = outerframe.children[0]
            first_label = body_frame.children[0]
            assert first_label.grid_calls == [dict(column=0, padx=5, row=0, sticky="e")]

    def test_body_item_create_entry_called(self, patch_tk, monkeypatch):
        calls = []
        monkeypatch.setattr(
            guiwidgets.SearchMovieGUI, "create_entry", lambda *args: calls.append(args)
        )
        monkeypatch.setattr(
            guiwidgets.SearchMovieGUI, "create_min_max_body_item", lambda *args: None
        )
        monkeypatch.setattr(guiwidgets, "_focus_set", lambda *args: None)
        with self.movie_context() as movie_gui:
            assert calls == [
                (
                    movie_gui,
                    TtkFrame(
                        parent=TtkFrame(parent=DummyTk(), padding=""),
                        padding=(10, 25, 10, 0),
                    ),
                    "title",
                    1,
                    0,
                    36,
                ),
                (
                    movie_gui,
                    TtkFrame(
                        parent=TtkFrame(parent=DummyTk(), padding=""),
                        padding=(10, 25, 10, 0),
                    ),
                    "director",
                    1,
                    2,
                    36,
                ),
                (
                    movie_gui,
                    TtkFrame(
                        parent=TtkFrame(parent=DummyTk(), padding=""),
                        padding=(10, 25, 10, 0),
                    ),
                    "notes",
                    1,
                    4,
                    36,
                ),
            ]

    # Test create min-max body item

    def test_min_max_body_item_ttk_label_gridded(self, patch_tk):
        with self.movie_context() as movie_gui:
            outerframe = movie_gui.parent.children[0]
            body_frame = outerframe.children[0]
            year_label = body_frame.children[2]
            assert year_label.grid_calls == [dict(column=0, padx=5, row=1, sticky="e")]

    def test_min_max_body_item_frame_created(self, patch_tk):
        with self.movie_context() as movie_gui:
            outerframe = movie_gui.parent.children[0]
            body_frame = outerframe.children[0]
            year_max_min_frame = body_frame.children[3]
            assert year_max_min_frame == TtkFrame(
                parent=TtkFrame(
                    parent=TtkFrame(parent=DummyTk(), padding=""),
                    padding=(10, 25, 10, 0),
                ),
                padding=(2, 0),
            )

    def test_min_max_body_item_frame_gridded(self, patch_tk):
        with self.movie_context() as movie_gui:
            outerframe = movie_gui.parent.children[0]
            body_frame = outerframe.children[0]
            year_max_min_frame = body_frame.children[3]
            assert year_max_min_frame.grid_calls == [dict(column=1, row=1, sticky="w")]

    def test_min_max_body_item_entries_created_and_gridded(self, patch_tk, monkeypatch):
        with self.movie_context() as movie_gui:
            outerframe = movie_gui.parent.children[0]
            body_frame = outerframe.children[0]
            year_max_min_frame = body_frame.children[3]
            assert year_max_min_frame.children[0].grid_calls == [dict(column=0, row=0)]
            assert year_max_min_frame.children[1].grid_calls == [dict(column=1, row=0)]

    def test_validate_int_registered(self, patch_tk, monkeypatch):
        with self.movie_context() as movie_gui:
            outerframe = movie_gui.parent.children[0]
            body_frame = outerframe.children[0]
            year_max_min_frame = body_frame.children[3]
            for child in range(2):
                calls = year_max_min_frame.children[child].register_calls
                assert calls == [(movie_gui.validate_int,)]

    def test_integer_validation_configured_upon_entry(self, patch_tk, monkeypatch):
        with self.movie_context() as movie_gui:
            outerframe = movie_gui.parent.children[0]
            body_frame = outerframe.children[0]
            year_max_min_frame = body_frame.children[3]
            assert year_max_min_frame.children[0].config_calls == [
                dict(validate="key", validatecommand=("test registered_callback", "%S"))
            ]
            assert year_max_min_frame.children[1].config_calls == [
                dict(validate="key", validatecommand=("test registered_callback", "%S"))
            ]

    # Test create entry

    def test_create_entry_creates_ttk_entry(self, patch_tk):
        with self.movie_context() as movie_gui:
            trace_add_callback = movie_gui.entry_fields[
                "title"
            ].widget.textvariable.trace_add_callback
            assert movie_gui.entry_fields["title"].widget == TtkEntry(
                parent=TtkFrame(
                    parent=TtkFrame(parent=DummyTk(), padding=""),
                    padding=(10, 25, 10, 0),
                ),
                textvariable=TkStringVar(trace_add_callback=trace_add_callback),
                width=36,
            )

    def test_create_entry_grids_entry_widget(self, patch_tk):
        with self.movie_context() as movie_gui:
            assert movie_gui.entry_fields["title"].widget.grid_calls == [
                dict(column=1, row=0)
            ]

    def test_create_entry_links_neuron(self, patch_tk, monkeypatch):
        calls = []
        monkeypatch.setattr(
            guiwidgets.SearchMovieGUI, "neuron_linker", lambda *args: calls.append(args)
        )
        with self.movie_context() as movie_gui:
            assert calls[0] == (
                movie_gui,
                "title",
                movie_gui.search_button_neuron,
                movie_gui.neuron_callback,
            )

    # Test create buttonbox

    def test_buttonbox_created(self, patch_tk):
        with self.movie_context() as movie_gui:
            outerframe = movie_gui.parent.children[0]
            buttonbox = outerframe.children[1]
            assert buttonbox == TtkFrame(parent=outerframe, padding=(5, 5, 10, 10))

    def test_buttonbox_gridded(self, patch_tk):
        with self.movie_context() as movie_gui:
            outerframe = movie_gui.parent.children[0]
            buttonbox = outerframe.children[1]
            assert buttonbox.grid_calls[0] == dict(column=0, row=1, sticky="e")

    def test_search_button_created(self, patch_tk):
        with self.movie_context() as movie_gui:
            button = movie_gui.parent.children[0].children[1].children[0]
            assert button == TtkButton(
                parent=TtkFrame(
                    parent=TtkFrame(parent=DummyTk()), padding=(5, 5, 10, 10)
                ),
                text="Search",
                command=movie_gui.search,
            )

    def test_search_button_gridded(self, patch_tk):
        with self.movie_context() as movie_gui:
            button = movie_gui.parent.children[0].children[1].children[0]
            assert button.grid_calls[0] == dict(column=0, row=0)

    # noinspection DuplicatedCode
    def test_search_button_bound(self, patch_tk):
        with self.movie_context() as movie_gui:
            button = movie_gui.parent.children[0].children[1].children[0]
            assert button.bind_calls[0][0] == "<Return>"
            button.bind_calls[0][1](button)
            assert button.invoke_calls[0]

    def test_search_button_state_set(self, patch_tk):
        with self.movie_context() as movie_gui:
            button = movie_gui.parent.children[0].children[1].children[0]
            assert button.state_calls[0][0] == "disabled"

    # noinspection PyShadowingNames
    def test_neuron_register_called(self, patch_tk, monkeypatch):
        calls = []
        monkeypatch.setattr(
            guiwidgets.SearchMovieGUI,
            "button_state_callback",
            lambda movie_gui, button: calls.append(
                button,
            ),
        )
        with self.movie_context() as movie_gui:
            button = movie_gui.parent.children[0].children[1].children[0]
            assert calls[0] == button

    def test_cancel_button_created(self, patch_tk, monkeypatch):
        calls = []
        monkeypatch.setattr(
            guiwidgets.SearchMovieGUI,
            "create_cancel_button",
            (lambda *args, **kwargs: calls.append((args, kwargs))),
        )
        with self.movie_context() as movie_gui:
            outerframe = movie_gui.parent.children[0]
            buttonbox = outerframe.children[1]
            assert calls == [((movie_gui, buttonbox), dict(column=1))]

    # Test search

    # @pytest.mark.skip('Test dependency discovered')
    # def test_callback_called(self, patch_tk):
    #     with self.movie_context() as something:
    #         something.selected_tags = ['tag 1', 'tag 2']
    #         something.search()
    #         assert commit_callback_calls == [(dict(director='4242', minutes=['4242', '4242'],
    #                                                notes='4242', title='4242', year=['4242', '4242'], ),
    #                                           ['tag 1', 'tag 2'])]

    def test_callback_raises_movie_search_found_nothing(self, patch_tk, monkeypatch):
        # noinspection PyUnusedLocal
        def callback(*args):
            raise exception.DatabaseSearchFoundNothing

        messagebox_calls = []
        monkeypatch.setattr(
            guiwidgets, "gui_messagebox", lambda *args: messagebox_calls.append(args)
        )
        tags = []
        # noinspection PyTypeChecker
        movie_gui = guiwidgets.SearchMovieGUI(DummyTk(), callback, tags)
        movie_gui.search()
        assert messagebox_calls == [
            (DummyTk(), "No matches", "There are no matching movies in the database.")
        ]

    def test_destroy_called(self, patch_tk, monkeypatch):
        called = []
        monkeypatch.setattr(
            guiwidgets.MovieGUIBase, "destroy", lambda *args: called.append(True)
        )
        with self.movie_context() as movie_gui:
            movie_gui.search()
            assert called.pop()

    # noinspection PyMissingOrEmptyDocstring
    @contextmanager
    def movie_context(self):
        global treeview_call
        treeview_call = []
        tags = ("test tag 1", "test tag 2")
        # noinspection PyTypeChecker
        yield guiwidgets.SearchMovieGUI(DummyTk(), dummy_commit_callback, tags)


# noinspection PyMissingOrEmptyDocstring,DuplicatedCode
@dataclass
class TtkTreeview:
    parent: TtkFrame
    columns: Sequence[str]
    height: int
    selectmode: str

    show: str = field(default="tree headings")
    padding: int = field(default=0)
    item_id: Generator = itertools.count(1)

    grid_calls: list = field(
        default_factory=list, init=False, repr=False, compare=False
    )
    column_calls: list = field(
        default_factory=list, init=False, repr=False, compare=False
    )
    heading_calls: list = field(
        default_factory=list, init=False, repr=False, compare=False
    )
    insert_calls: list = field(
        default_factory=list, init=False, repr=False, compare=False
    )
    bind_calls: list = field(
        default_factory=list, init=False, repr=False, compare=False
    )
    yview_calls: list = field(
        default_factory=list, init=False, repr=False, compare=False
    )
    configure_calls: list = field(
        default_factory=list, init=False, repr=False, compare=False
    )
    selection_add_calls: list = field(
        default_factory=list, init=False, repr=False, compare=False
    )

    def __post_init__(self):
        self.parent.children.append(self)

    def grid(self, **kwargs):
        self.grid_calls.append(
            kwargs,
        )

    def column(self, *args, **kwargs):
        self.column_calls.append((args, kwargs))

    def heading(self, *args, **kwargs):
        self.heading_calls.append((args, kwargs))

    def insert(self, *args, **kwargs):
        self.insert_calls.append((args, kwargs))
        return f"I{next(self.item_id):03}"

    def bind(self, *args, **kwargs):
        self.bind_calls.append((args, kwargs))

    def yview(self, *args, **kwargs):
        self.yview_calls.append((args, kwargs))

    def selection_add(self, *args):
        self.selection_add_calls.append(args)

    def configure(self, **kwargs):
        self.configure_calls.append(kwargs)

    @staticmethod
    def selection():
        return ["test tag 1", "test tag 2"]


# noinspection PyMissingOrEmptyDocstring,DuplicatedCode
@dataclass
class TtkScrollbar:
    parent: TtkFrame
    orient: str
    command: Callable

    set_calls: list = field(default_factory=list, init=False, repr=False, compare=False)
    grid_calls: list = field(
        default_factory=list, init=False, repr=False, compare=False
    )

    def __post_init__(self):
        self.parent.children.append(self)

    def set(self, *args, **kwargs):
        self.set_calls.append((args, kwargs))

    def grid(self, **kwargs):
        self.grid_calls.append(kwargs)


# noinspection PyMissingOrEmptyDocstring,DuplicatedCode
@pytest.fixture()
def patch_tk(monkeypatch):
    monkeypatch.setattr(guiwidgets.tk, "Tk", DummyTk)
    monkeypatch.setattr(guiwidgets.tk, "StringVar", TkStringVar)
    monkeypatch.setattr(guiwidgets.ttk, "Frame", TtkFrame)
    monkeypatch.setattr(guiwidgets.ttk, "Label", TtkLabel)
    monkeypatch.setattr(guiwidgets.ttk, "Entry", TtkEntry)
    monkeypatch.setattr(guiwidgets.ttk, "Button", TtkButton)
    monkeypatch.setattr(guiwidgets.ttk, "Treeview", TtkTreeview)
    monkeypatch.setattr(guiwidgets.ttk, "Scrollbar", TtkScrollbar)


treeview_call = []


# noinspection PyMissingOrEmptyDocstring
@dataclass
class DummyTreeview:
    internal_name: str
    body_frame: TtkFrame
    row: int
    column: int
    label_text: str
    items: Sequence[str]
    user_callback: Callable

    initial_selection: Sequence[str] = field(default_factory=tuple)

    def __call__(self):
        self.user_callback = self.treeview_callback()
        treeview_call.append(
            (
                self,
                self.internal_name,
                self.body_frame,
                self.row,
                self.column,
                self.label_text,
                self.items,
                self.user_callback,
            )
        )
        return guiwidgets.neurons.Observer()

    @staticmethod
    def treeview_callback():
        def update_tag_selection(test_token):
            return test_token

        return update_tag_selection


# noinspection PyMissingOrEmptyDocstring
@pytest.fixture()
def patch_movie_treeview(monkeypatch):
    monkeypatch.setattr(guiwidgets, "MovieTreeview", DummyTreeview)


commit_callback_calls = []


# noinspection PyUnusedLocal,PyMissingOrEmptyDocstring
def dummy_commit_callback(
    movie_dict: guiwidgets.config.MovieTypedDict, tags: Sequence[str]
):
    commit_callback_calls.append((movie_dict, tags))
