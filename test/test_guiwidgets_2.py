"""Test module."""
#  Copyright (c) 2022-2023. Stephen Rigden.
#  Last modified 11/18/23, 5:50 AM by stephen.
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

from contextlib import contextmanager
from typing import Callable, Optional, Type
from unittest.mock import Mock

import pytest

import guiwidgets
import guiwidgets_2
from test.dummytk import (
    DummyTk,
    TkStringVar,
    TkToplevel,
    TtkButton,
    TtkCheckbutton,
    TtkEntry,
    TtkFrame,
    TtkLabel,
    TtkScrollbar,
    TtkTreeview,
)

Exc = Type[Optional[guiwidgets_2.exception.DatabaseSearchFoundNothing]]


# noinspection PyMissingOrEmptyDocstring
@pytest.mark.usefixtures("patch_tk")
class TestSelectMovieGUI:
    handlers_callback = Mock()
    movies = [
        guiwidgets.config.MovieUpdateDef(
            title="Select Movie Test TItle",
            year=4242,
            director="test director",
            minutes=42,
            notes="test notes",
        )
    ]

    def test_selected_movie_becomes_argument_for_callback(self):
        with self.select_movie() as cm:
            args, kwargs = cm.treeview.bind_calls[0]
            treeview_callback = kwargs["func"]
            cm.treeview.selection_set("I001")
            treeview_callback()

            expected = {
                k: v for k, v in self.movies[0].items() if k in {"title", "year"}
            }
            self.handlers_callback.assert_called_once_with(expected)

    @contextmanager
    def select_movie(self):
        # noinspection PyTypeChecker
        gui = guiwidgets.SelectMovieGUI(DummyTk(), self.movies, self.handlers_callback)
        yield gui


# noinspection PyMissingOrEmptyDocstring
@pytest.mark.usefixtures("patch_tk")
class TestFocusSet:
    def test_focus_set_calls_focus_set_on_entry(self, patch_tk):
        with self.focus_set_context() as entry:
            # noinspection PyUnresolvedReferences
            assert entry.focus_set_calls == [True]

    def test_focus_set_calls_select_range_on_entry(self, patch_tk):
        with self.focus_set_context() as entry:
            # noinspection PyUnresolvedReferences
            assert entry.select_range_calls == [(0, "end")]

    def test_focus_set_calls_icursor_on_entry(self, patch_tk):
        with self.focus_set_context() as entry:
            # noinspection PyUnresolvedReferences
            assert entry.icursor_calls == [("end",)]

    @contextmanager
    def focus_set_context(self):
        # noinspection PyTypeChecker
        entry = guiwidgets_2.ttk.Entry(DummyTk())
        guiwidgets_2._focus_set(entry)
        yield entry


# noinspection PyMissingOrEmptyDocstring
@pytest.mark.usefixtures("patch_tk")
class TestLabelFieldWidget:
    def test_label_field_widget_created(self):
        with self.labelfield_context() as labelfield:
            assert labelfield.parent == TtkFrame(DummyTk())
            assert labelfield.col_0_width == 30
            assert labelfield.col_1_width == 36

    def test_column_0_configure_called(self):
        with self.labelfield_context() as labelfield:
            args, kwargs = labelfield.parent.columnconfigure_calls[0]
            assert args == (0,)
            assert kwargs == dict(weight=1, minsize=labelfield.col_0_width)

    def test_column_1_configure_called(self):
        with self.labelfield_context() as labelfield:
            args, kwargs = labelfield.parent.columnconfigure_calls[1]
            assert args == (1,)
            assert kwargs == dict(weight=1)

    def test_add_entry_row_calls_create_label(self, dummy_entry_field, monkeypatch):
        create_label_calls = []
        monkeypatch.setattr(
            guiwidgets_2._InputZone,
            "_create_label",
            lambda *args: create_label_calls.append(args),
        )
        with self.labelfield_context() as labelfield:
            labelfield.add_entry_row(dummy_entry_field)
            _, entry_field, row = create_label_calls[0]
            assert create_label_calls == [(labelfield, dummy_entry_field.label_text, 0)]

    @pytest.mark.skip
    def test_add_entry_row_creates_entry(self, dummy_entry_field):
        with self.labelfield_context() as labelfield:
            labelfield.add_entry_row(dummy_entry_field)
            assert dummy_entry_field.widget == TtkEntry(
                parent=TtkFrame(parent=DummyTk()),
                textvariable=TkStringVar(value="4242"),
                width=36,
            )

    def test_add_entry_row_grids_entry(self, dummy_entry_field):
        with self.labelfield_context() as labelfield:
            labelfield.add_entry_row(dummy_entry_field)
            # noinspection PyUnresolvedReferences
            assert dummy_entry_field.widget.grid_calls == [dict(column=1, row=0)]

    def test_add_entry_row_creates_checkbutton(self, dummy_entry_field):
        with self.labelfield_context() as labelfield:
            labelfield.add_checkbox_row(dummy_entry_field)
            # noinspection PyTypeChecker
            assert dummy_entry_field.widget == TtkCheckbutton(
                parent=TtkFrame(parent=DummyTk()),
                text=dummy_entry_field.label_text,
                variable=dummy_entry_field.textvariable,
                width=guiwidgets_2._InputZone.col_1_width,
            )

    def test_add_entry_row_grids_checkbutton(self, dummy_entry_field):
        with self.labelfield_context() as labelfield:
            labelfield.add_checkbox_row(dummy_entry_field)
            # noinspection PyUnresolvedReferences
            assert dummy_entry_field.widget.grid_calls == [dict(column=1, row=0)]

    def test_add_treeview_row_calls_create_label(self, monkeypatch):
        items = ["tag 1", "tag 2"]
        with self.labelfield_context() as labelfield:
            calls = []
            monkeypatch.setattr(
                guiwidgets_2._InputZone,
                "_create_label",
                lambda *args: calls.append(args),
            )
            labelfield.add_treeview_row(
                guiwidgets_2.SELECT_TAGS_TEXT, items, lambda: None
            )
            assert calls == [(labelfield, guiwidgets_2.SELECT_TAGS_TEXT, 0)]

    # noinspection PyPep8Naming
    def test_add_treeview_row_creates_MovieTagTreeview_object(self, monkeypatch):
        items = ["tag 1", "tag 2"]

        def dummy_callback():
            pass

        with self.labelfield_context() as labelfield:
            calls = []
            monkeypatch.setattr(
                guiwidgets_2, "_MovieTagTreeview", lambda *args: calls.append(args)
            )
            labelfield.add_treeview_row(
                guiwidgets_2.SELECT_TAGS_TEXT, items, dummy_callback
            )
            assert calls == [(labelfield.parent, 0, items, dummy_callback)]

    # noinspection PyPep8Naming
    def test_add_treeview_row_returns_MovieTagTreeview_object(self, monkeypatch):
        items = ["tag 1", "tag 2"]
        with self.labelfield_context() as labelfield:
            movie_tag_treeview = labelfield.add_treeview_row(
                guiwidgets_2.SELECT_TAGS_TEXT, items, lambda: None
            )
            assert isinstance(movie_tag_treeview, guiwidgets_2._MovieTagTreeview)

    def test_create_label_creates_label(self, dummy_entry_field):
        row = 0
        with self.labelfield_context() as labelfield:
            labelfield._create_label(dummy_entry_field.label_text, row)
            # noinspection PyTypeChecker
            assert labelfield.parent.children[0] == TtkLabel(
                TtkFrame(DummyTk()), dummy_entry_field.label_text
            )

    def test_create_label_grids_label(self, dummy_entry_field):
        row = 0
        with self.labelfield_context() as labelfield:
            labelfield._create_label(dummy_entry_field, row)
            assert labelfield.parent.children[0].grid_calls == [
                {
                    "column": 0,
                    "row": row,
                    "sticky": "ne",
                    "padx": 5,
                }
            ]

    @contextmanager
    def labelfield_context(self):
        parent_frame = TtkFrame(DummyTk())
        # noinspection PyTypeChecker
        yield guiwidgets_2._InputZone(parent_frame)

    @pytest.fixture()
    def dummy_entry_field(self):
        return guiwidgets_2._EntryField(
            "dummy field", original_value="dummy field value"
        )


@pytest.mark.usefixtures("patch_tk")
class TestMovieTagTreeview:
    def test_treeview_created(self):
        with self.movie_tag_treeview_context() as cm:
            treeview = cm.parent.children[0]
            assert treeview == TtkTreeview(
                parent=TtkFrame(parent=DummyTk()),
                columns=("tags",),
                height=7,
                show="tree",
                padding=5,
            )

    def test_treeview_gridded(self):
        with self.movie_tag_treeview_context() as cm:
            treeview = cm.parent.children[0]
            assert treeview.grid_calls == [dict(column=1, row=5, sticky="e")]

    def test_treeview_column_width_set(self):
        with self.movie_tag_treeview_context() as cm:
            treeview = cm.parent.children[0]
            assert treeview.column_calls == [(("tags",), dict(width=127))]

    def test_treeview_bind_called(self, monkeypatch):
        calls = []
        monkeypatch.setattr(
            guiwidgets_2._MovieTagTreeview,
            "selection_callback_wrapper",
            lambda *args: calls.append(args),
        )
        with self.movie_tag_treeview_context() as cm:
            treeview = cm.parent.children[0]
            assert treeview.bind_calls[0][0] == ("<<TreeviewSelect>>",)
            assert calls == [(cm, cm.treeview, cm.callers_callback)]

    def test_scrollbar_created(self):
        with self.movie_tag_treeview_context() as cm:
            treeview, scrollbar = cm.parent.children
            assert scrollbar == TtkScrollbar(cm.parent, "vertical", treeview.yview)

    def test_scrollbar_gridded(self):
        with self.movie_tag_treeview_context() as cm:
            _, scrollbar = cm.parent.children
            assert scrollbar.grid_calls == [dict(column=2, row=5, sticky="ns")]

    def test_treeview_configured_with_scrollbar(self):
        with self.movie_tag_treeview_context() as cm:
            treeview, scrollbar = cm.parent.children
            assert treeview.configure_calls == [dict(yscrollcommand=scrollbar.set)]

    def test_treeview_populated_with_items(self):
        with self.movie_tag_treeview_context() as cm:
            treeview, scrollbar = cm.parent.children
            assert treeview.insert_calls == [
                (("", "end", "tag 1"), dict(text="tag 1", tags="tags")),
                (("", "end", "tag 2"), dict(text="tag 2", tags="tags")),
            ]

    def test_set_initial_selection(self):
        with self.movie_tag_treeview_context() as cm:
            treeview, scrollbar = cm.parent.children
            assert treeview.selection_add_calls == [(cm.initial_selection,)]

    def test_callback_called_with_current_user_selection(self):
        tree = TtkTreeview(TtkFrame(DummyTk()))
        calls = []
        tree.selection_set(("test tag", "ignored tag"))
        with self.movie_tag_treeview_context() as cm:
            selection_callback = cm.selection_callback_wrapper(
                tree, lambda *args: calls.append(args)
            )
            selection_callback()
            assert calls == [((("test tag", "ignored tag"),),)]

    def test_observer_notify_called_with_changed_selection(self, monkeypatch):
        tree = TtkTreeview(TtkFrame(DummyTk()))
        calls = []
        with self.movie_tag_treeview_context() as cm:
            monkeypatch.setattr(cm.observer, "notify", lambda *args: calls.append(args))
            selection_callback = cm.selection_callback_wrapper(tree, lambda *args: None)
            selection_callback()
            assert calls == [(True,)]

    def test_observer_notify_called_with_unchanged_selection(self, monkeypatch):
        tree = TtkTreeview(TtkFrame(DummyTk()))
        calls = []
        tree.selection_set(("test tag", "ignored tag"))
        with self.movie_tag_treeview_context() as cm:
            monkeypatch.setattr(cm.observer, "notify", lambda *args: calls.append(args))
            selection_callback = cm.selection_callback_wrapper(tree, lambda *args: None)
            cm.initial_selection = (("test tag", "ignored tag"),)
            selection_callback()
            assert calls == [(False,)]

    def test_clear_selection_calls_selection_set(self):
        with self.movie_tag_treeview_context() as cm:
            cm.clear_selection()
            assert cm.treeview.selection_set_calls == [()]

    def test_selection_set_calls_selection_set(self):
        new_selection = ["choice 1", "choice 2"]
        with self.movie_tag_treeview_context() as cm:
            cm.selection_set(new_selection)
            assert cm.treeview.selection_set_calls == [(new_selection,)]

    # noinspection PyMissingOrEmptyDocstring
    @contextmanager
    def movie_tag_treeview_context(self):
        # noinspection PyTypeChecker
        parent = guiwidgets_2.ttk.Frame(DummyTk())
        row = 5
        items = ["tag 1", "tag 2"]
        initial_selection = [
            "tag 1",
        ]
        yield guiwidgets_2._MovieTagTreeview(
            parent, row, items, lambda *args: None, initial_selection
        )


# noinspection PyMissingOrEmptyDocstring
@pytest.mark.usefixtures("patch_tk")
class TestCreateButton:
    def test_create_button_grid(self):
        with self.button_context() as button:
            assert button.grid_calls == [dict(column=0, row=0)]

    def test_create_button_bind(self):
        with self.button_context() as button:
            assert button.bind_calls[0][0] == "<Return>"
            assert isinstance(button.bind_calls[0][1], Callable)

    def test_disable_at_initialization(self):
        with self.button_context(default="disabled") as button:
            assert button.default == "disabled"

    @contextmanager
    def button_context(self, default: guiwidgets_2.DefaultLiteral = None):
        buttonbox = TtkFrame(DummyTk())
        text = "Dummy Button"
        column = 0
        # noinspection PyTypeChecker
        yield guiwidgets_2._create_button(
            buttonbox, text, column, lambda: None, default=default
        )


def test_gui_messagebox(monkeypatch):
    calls = []
    monkeypatch.setattr(
        guiwidgets_2.messagebox,
        "showinfo",
        lambda *args, **kwargs: calls.append((args, kwargs)),
    )
    parent = DummyTk()
    message = "test message"
    detail = "test detail"
    # noinspection PyTypeChecker
    guiwidgets_2.gui_messagebox(parent, message, detail)
    assert calls == [((parent, message), dict(detail=detail, icon="info"))]


def test_gui_askopenfilename(monkeypatch):
    calls = []
    monkeypatch.setattr(
        guiwidgets_2.filedialog,
        "askopenfilename",
        lambda **kwargs: calls.append(kwargs),
    )
    parent = DummyTk()
    filetypes = (("test filetypes",),)
    # noinspection PyTypeChecker
    guiwidgets_2.gui_askopenfilename(parent, filetypes)
    assert calls == [(dict(parent=parent, filetypes=filetypes))]


@pytest.mark.usefixtures("patch_tk")
def test_clear_input_form_fields_calls_textvariable_set():
    textvariable = guiwidgets_2.tk.StringVar()
    # noinspection PyTypeChecker
    entry_field = guiwidgets_2._EntryField(
        "label", "original value", textvariable=textvariable
    )
    entry_fields = dict(test_entry=entry_field)
    guiwidgets_2.clear_textvariables(entry_fields)
    # noinspection PyUnresolvedReferences
    assert entry_fields["test_entry"].textvariable.set_calls == [
        ("original value",),
        ("",),
    ]


def test_set_original_value(patch_tk):
    entry = "test entry"
    test_label_text = "test label text"
    test_original_value = "test original value"

    entry_field = guiwidgets_2._EntryField(test_label_text)
    entry_fields = {entry: entry_field}
    original_values = {entry: test_original_value}
    guiwidgets_2._set_original_value(entry_fields, original_values)
    assert entry_field.original_value == test_original_value
    # noinspection PyUnresolvedReferences
    assert entry_field.textvariable.set_calls == [("",), (test_original_value,)]


def test_enable_button_wrapper(patch_tk):
    # noinspection PyTypeChecker
    button = TtkButton(DummyTk(), "Dummy Button")
    # noinspection PyTypeChecker
    enable_button = guiwidgets_2._enable_button(button)
    enable_button(True)
    assert button.state_calls == [["!disabled"]]


def test_link_or_neuron_to_button():
    # noinspection PyMissingOrEmptyDocstring
    def change_button_state():
        pass

    neuron = guiwidgets_2._create_button_orneuron(change_button_state)
    assert isinstance(neuron, guiwidgets_2.neurons.OrNeuron)
    assert neuron.notifees == [change_button_state]


def test_link_and_neuron_to_button():
    # noinspection PyMissingOrEmptyDocstring
    def change_button_state():
        pass

    neuron = guiwidgets_2._create_buttons_andneuron(change_button_state)
    assert isinstance(neuron, guiwidgets_2.neurons.AndNeuron)
    assert neuron.notifees == [change_button_state]


@pytest.mark.skip
def test_link_field_to_neuron_trace_add_called(patch_tk, dummy_entry_fields):
    name = "tag"
    neuron = guiwidgets_2.neurons.OrNeuron()
    notify_neuron = guiwidgets_2._create_the_fields_observer(
        dummy_entry_fields, name, neuron
    )
    guiwidgets_2._link_field_to_neuron(dummy_entry_fields, name, neuron, notify_neuron)
    # noinspection PyUnresolvedReferences
    assert dummy_entry_fields["tag"].textvariable.trace_add_calls == [
        ("write", notify_neuron)
    ]


def test_link_field_to_neuron_register_event_called(patch_tk, dummy_entry_fields):
    name = "tag"
    neuron = guiwidgets_2.neurons.OrNeuron()
    notifee = DummyActivateButton()
    neuron.register(notifee)
    notify_neuron = guiwidgets_2._create_the_fields_observer(
        dummy_entry_fields, name, neuron
    )
    guiwidgets_2._link_field_to_neuron(dummy_entry_fields, name, neuron, notify_neuron)
    assert not notifee.state
    notify_neuron()
    assert notifee.state


def test_notify_neuron_wrapper(patch_tk, dummy_entry_fields):
    name = "tag"
    neuron = guiwidgets_2.neurons.OrNeuron()
    notifee = DummyActivateButton()
    neuron.register(notifee)
    notify_neuron = guiwidgets_2._create_the_fields_observer(
        dummy_entry_fields, name, neuron
    )

    # Match tag field contents to original value thus 'activating' the button.
    notify_neuron()
    assert notifee.state

    # Change original value so 'new' value of '4242' appears to be no change thus 'deactivating'
    # the button.
    dummy_entry_fields["tag"].original_value = "4242"
    notify_neuron()
    assert not notifee.state


# noinspection PyMissingOrEmptyDocstring
@pytest.fixture
def dummy_entry_fields():
    # noinspection PyProtectedMember
    return dict(tag=guiwidgets_2._EntryField("Tag", ""))


# noinspection PyMissingOrEmptyDocstring
class DummyActivateButton:
    state = None

    def __call__(self, state):
        self.state = state


# noinspection PyMissingOrEmptyDocstring,DuplicatedCode
@pytest.fixture()
def patch_tk(monkeypatch):
    monkeypatch.setattr(guiwidgets_2.tk, "Tk", DummyTk)
    monkeypatch.setattr(guiwidgets_2.tk, "Toplevel", TkToplevel)
    monkeypatch.setattr(guiwidgets_2.tk, "StringVar", TkStringVar)
    monkeypatch.setattr(guiwidgets_2.ttk, "Frame", TtkFrame)
    monkeypatch.setattr(guiwidgets_2.ttk, "Label", TtkLabel)
    monkeypatch.setattr(guiwidgets_2.ttk, "Entry", TtkEntry)
    monkeypatch.setattr(guiwidgets_2.ttk, "Checkbutton", TtkCheckbutton)
    monkeypatch.setattr(guiwidgets_2.ttk, "Button", TtkButton)
    monkeypatch.setattr(guiwidgets_2.ttk, "Treeview", TtkTreeview)
    monkeypatch.setattr(guiwidgets_2.ttk, "Scrollbar", TtkScrollbar)
