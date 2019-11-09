"""Menu handlers test module."""

#  Copyright© 2019. Stephen Rigden.
#  Last modified 11/9/19, 8:14 AM by stephen.
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
from collections import deque
from contextlib import contextmanager
from dataclasses import dataclass, field

import pytest

import handlers


# noinspection PyMissingOrEmptyDocstring
class TestAboutDialogCalled:
    
    def test_about_dialog_called(self, class_patches):
        with self.about_context() as root_window:
            dialog = root_window.children.popleft()
            assert dialog == ModalDialog(text='test program name', parent=DummyParent(),
                                         buttons={'ok': 'OK'}, sub_text='test version')
    
    @pytest.fixture
    def class_patches(self, monkeypatch):
        test_app = handlers.config.Config('test program name', 'test version')
        monkeypatch.setattr(handlers.config, 'app', test_app)
        monkeypatch.setattr(handlers.dialogs, 'ModalDialog', ModalDialog)
    
    @contextmanager
    def about_context(self):
        handlers.config.app.root_window = DummyParent()
        handlers.about_dialog()
        yield handlers.config.app.root_window


@dataclass
class DummyParent:
    """Provide a dummy for Tk root.
    
    The children are used to locate tkinter objects in the absence of python identifiers."""
    children: deque = field(default_factory=deque, init=False, repr=False, compare=False)


@dataclass
class ModalDialog:
    """Dummy for a tkinter modal dialog."""
    text: str
    parent: DummyParent
    buttons: dict
    sub_text: str
    
    def __post_init__(self):
        self.parent.children.append(self)
    
    def __call__(self, *args, **kwargs):
        pass
