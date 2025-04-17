"""Test module"""

#  Copyright© 2025. Stephen Rigden.
#  Last modified 4/17/25, 12:51 PM by stephen.
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
from unittest.mock import MagicMock, call

import pytest
from pytest_check import check

from gui import tk_facade, types


# noinspection PyMissingOrEmptyDocstring
class TestObserver:
    def test_observer(self):
        foo1_calls = []
        foo2_calls = []
        argus = ("arg1", "arg2")
        kwargus = {"kwarg1": "kwarg1", "kwarg2": "kwarg2"}

        def foo1(*args, **kwargs):
            foo1_calls.append((args, kwargs))

        def foo2(*args, **kwargs):
            foo2_calls.append((args, kwargs))

        observer = tk_facade.Observer()
        observer.register(foo1)
        observer.register(foo2)

        observer.notify(*argus, **kwargus)
        observer.deregister(foo2)
        observer.notify(*argus, **kwargus)

        #  Test correct registration and notification.
        check.equal(
            foo1_calls,
            [
                (("arg1", "arg2"), {"kwarg1": "kwarg1", "kwarg2": "kwarg2"}),
                (("arg1", "arg2"), {"kwarg1": "kwarg1", "kwarg2": "kwarg2"}),
            ],
        )
        #  Test correct deregistration.
        check.equal(
            foo2_calls,
            [(("arg1", "arg2"), {"kwarg1": "kwarg1", "kwarg2": "kwarg2"})],
        )


# noinspection PyMissingOrEmptyDocstring
class TestEntry:
    label_text = "dummy label"
    empty_value = ""
    test_value = "test value"

    def test_all_init(self, tk, ttk, tk_parent_type):
        with self.entry(tk) as cut:
            # noinspection DuplicatedCode
            check.equal(cut.label_text, self.label_text)
            check.equal(cut.parent, tk)
            check.is_instance(cut.observer, tk_facade.Observer)
            check.equal(cut.widget, ttk.Entry())
            check.equal(cut._textvariable, tk.StringVar())
            check.equal(cut._original_value, "")
            with check:
                # noinspection PyUnresolvedReferences
                cut.widget.configure.assert_called_once_with(
                    textvariable=tk.StringVar()
                )
            with check:
                # noinspection PyUnresolvedReferences
                cut._textvariable.trace_add.assert_called_once_with(
                    "write", cut.observer.notify
                )

    def test_original_value(self, tk, ttk):
        with self.entry(tk) as cut:
            cut.original_value = self.test_value
            check.equal(cut.original_value, self.test_value)
            with check:
                # noinspection PyUnresolvedReferences
                cut._textvariable.set.assert_has_calls(
                    [
                        call(""),
                        call(self.test_value),
                    ]
                )

    def test_current_value(self, tk, ttk):
        with self.entry(tk) as cut:
            test_value = "test current value"
            cut.current_value = test_value
            with check:
                # noinspection PyUnresolvedReferences
                cut._textvariable.set.assert_called_with(test_value)

            result = cut.current_value
            check.equal(result, cut._textvariable.get())

            cut.clear_current_value()
            with check:
                # noinspection PyUnresolvedReferences
                cut._textvariable.set.assert_called_with("")

    def test_has_data(self, tk, ttk):
        with self.entry(tk) as cut:
            cut._textvariable.get.return_value = self.test_value
            check.equal(cut.has_data(), True)

            cut._textvariable.get.return_value = self.empty_value
            check.equal(cut.has_data(), False)

    def test_changed(self, tk, ttk):
        with self.entry(tk) as cut:
            cut._textvariable.get.return_value = self.test_value
            cut._original_value = self.test_value
            check.equal(cut.changed(), False)
            cut._original_value = "garbage"
            check.equal(cut.changed(), True)

    @contextmanager
    def entry(self, tk):
        # noinspection PyTypeChecker
        cut = tk_facade.Entry(self.label_text, tk)
        yield cut


# noinspection PyMissingOrEmptyDocstring
class TestText:
    label_text = "dummy label"
    empty_value = ""
    test_value = "test True"

    def test_all_init(self, tk, ttk, tk_parent_type, monkeypatch):
        monkeypatch.setattr(tk_facade.Text, "modified", mock_modified := MagicMock())
        with self.text(tk) as cut:
            check.equal(cut.label_text, self.label_text)
            check.equal(cut.parent, tk)
            check.is_instance(cut.observer, tk_facade.Observer)
            check.equal(cut.widget, tk.Text())
            check.equal(cut._original_value, "")
            with check:
                # noinspection PyUnresolvedReferences
                cut.widget.bind.assert_called_once_with("<<Modified>>", mock_modified())
            with check:
                # noinspection PyUnresolvedReferences
                cut.widget.replace.assert_called_once_with("1.0", "end", "")

    def test_original_value(self, tk, ttk):
        with self.text(tk) as cut:
            test_value = "test original value"
            cut.original_value = test_value
            check.equal(cut.original_value, test_value)
            with check:
                # noinspection PyUnresolvedReferences
                cut.widget.replace.assert_has_calls(
                    [call("1.0", "end", ""), call("1.0", "end", test_value)]
                )

    def test_current_value(self, tk, ttk):
        with self.text(tk) as cut:
            test_value = "test current value"
            cut.current_value = test_value
            with check:
                # noinspection PyUnresolvedReferences
                cut.widget.replace.assert_called_with("1.0", "end", test_value)

            result = cut.current_value
            # noinspection PyArgumentList
            check.equal(result, cut.widget.get())

            cut.clear_current_value()
            with check:
                # noinspection PyUnresolvedReferences
                cut.widget.replace.assert_called_with("1.0", "end", "")

    def test_modified(self, tk, ttk, monkeypatch):
        with self.text(tk) as cut:
            monkeypatch.setattr(cut.observer, "notify", MagicMock())
            cut.modified()()
            with check:
                # noinspection PyUnresolvedReferences
                cut.widget.edit_modified.assert_called_once_with(False)
            with check:
                # noinspection PyUnresolvedReferences
                cut.observer.notify.assert_called_once_with()

    def test_has_data(self, tk, ttk):
        with self.text(tk) as cut:
            cut.widget.get.return_value = self.test_value
            check.equal(cut.has_data(), True)

            cut.widget.get.return_value = self.empty_value
            check.equal(cut.has_data(), False)

    @contextmanager
    def text(self, tk):
        # noinspection PyTypeChecker
        cut = tk_facade.Text(self.label_text, tk)
        yield cut


# noinspection PyMissingOrEmptyDocstring
class TestTreeview:
    label_text = "dummy label"
    test_value = {"test original value"}
    empty_value = []

    def test_all_init(self, tk, ttk, tk_parent_type, monkeypatch):
        with self.treeview(tk) as cut:
            check.equal(cut.label_text, self.label_text)
            check.equal(cut.parent, tk)
            check.is_instance(cut.observer, tk_facade.Observer)
            check.equal(cut.widget, ttk.Treeview())
            with check:
                # This has a lambda parameter
                # noinspection PyUnresolvedReferences
                cut.widget.bind.assert_called()
            check.equal(cut._original_value, set())

    def test_original_value(self, tk, ttk):
        with self.treeview(tk) as cut:
            cut.original_value = self.test_value
            check.equal(cut.original_value, self.test_value)
            with check:
                # noinspection PyUnresolvedReferences
                cut.widget.selection_set.assert_has_calls(
                    [call(self.empty_value), call(self.test_value)]
                )

    def test_current_value(self, tk, ttk):
        with self.treeview(tk) as cut:
            # Test setter and clearer.
            cut.current_value = self.test_value
            cut.clear_current_value()
            with check:
                # noinspection PyUnresolvedReferences
                cut.widget.selection_set.assert_has_calls(
                    [
                        call(self.empty_value),  # Initialization
                        call(self.test_value),  # Setter
                        call(self.empty_value),  # Clearer
                    ]
                )

            # Test getter
            cut.widget.selection.return_value = self.test_value
            result = cut.current_value
            check.equal(result, cut.widget.selection())

    def test_has_data(self, tk, ttk):
        with self.treeview(tk) as cut:
            cut.widget.selection.return_value = self.test_value
            check.equal(cut.has_data(), True)

            cut.widget.selection.return_value = self.empty_value
            check.equal(cut.has_data(), False)

    @contextmanager
    def treeview(self, tk):
        # noinspection PyTypeChecker
        cut = tk_facade.Treeview(self.label_text, tk)
        yield cut


# noinspection PyMissingOrEmptyDocstring
class TestCheckbutton:
    label_text = "dummy label"
    initial_value = False
    test_value = True
    clear_value = False

    def test_all_init(self, tk, ttk, tk_parent_type):
        with self.checkbutton(tk) as cut:
            # noinspection DuplicatedCode
            check.equal(cut.label_text, self.label_text)
            check.equal(cut.parent, tk)
            check.is_instance(cut.observer, tk_facade.Observer)
            check.equal(cut.widget, ttk.Checkbutton())
            check.equal(cut._variable, tk.IntVar())
            check.equal(cut._original_value, self.initial_value)
            with check:
                # noinspection PyUnresolvedReferences
                cut.widget.configure.assert_called_once_with(variable=cut._variable)
            with check:
                # noinspection PyUnresolvedReferences
                cut._variable.trace_add.assert_called_once_with(
                    "write", cut.observer.notify
                )

    def test_original_value(self, tk, ttk):
        with self.checkbutton(tk) as cut:
            cut.original_value = self.initial_value
            check.equal(cut.original_value, self.initial_value)
            with check:
                # noinspection PyUnresolvedReferences
                cut._variable.set.assert_has_calls(
                    [
                        call(self.initial_value),
                        call(self.initial_value),
                    ]
                )

    def test_current_value(self, tk, ttk):
        with self.checkbutton(tk) as cut:
            # Test setter
            cut.current_value = self.test_value
            with check:
                # noinspection PyUnresolvedReferences
                cut._variable.set.assert_called_with(self.test_value)

            # Test getter
            cut._variable.get.return_value = self.test_value
            result = cut.current_value
            check.equal(result, cut._variable.get())

            # Test clearer
            cut.clear_current_value()
            with check:
                # noinspection PyUnresolvedReferences
                cut._variable.set.assert_called_with(self.clear_value)

    @contextmanager
    def checkbutton(self, tk):
        # noinspection PyTypeChecker
        cut = tk_facade.Checkbutton(self.label_text, tk)
        yield cut


# noinspection PyMissingOrEmptyDocstring,DuplicatedCode
@pytest.fixture
def tk(monkeypatch):
    monkeypatch.setattr(tk_facade, "tk", tk := MagicMock())
    return tk


# noinspection PyMissingOrEmptyDocstring
@pytest.fixture
def ttk(monkeypatch):
    monkeypatch.setattr(tk_facade, "ttk", ttk := MagicMock())
    return ttk


# noinspection PyMissingOrEmptyDocstring
@pytest.fixture
def tk_parent_type(monkeypatch):
    monkeypatch.setattr(types, "TkParentType", tk_parent_type := MagicMock)
    return tk_parent_type
