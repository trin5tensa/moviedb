"""Menu handlers test module."""

#  Copyright© 2019. Stephen Rigden.
#  Last modified 11/18/19, 7:56 AM by stephen.
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
class TestAboutDialog:
    
    def test_about_dialog_called(self, class_patches):
        with self.about_context() as tk_root:
            dialog = tk_root.children.popleft()
            assert dialog == ModalDialog(text='test program name', parent=DummyParent(),
                                         buttons={'ok': 'OK'}, sub_text='test version')
    
    @pytest.fixture
    def class_patches(self, monkeypatch):
        test_app = handlers.config.Config('test program name', 'test version')
        monkeypatch.setattr(handlers.config, 'app', test_app)
        monkeypatch.setattr(handlers.dialogs, 'ModalDialog', ModalDialog)

    @contextmanager
    def about_context(self):
        hold_app = handlers.config.app
        handlers.config.app.tk_root = DummyParent()
        handlers.about_dialog()
        try:
            yield handlers.config.app.tk_root
        finally:
            handlers.config.app = hold_app


# noinspection PyMissingOrEmptyDocstring
class TestImportMovies:
    CSV_TEST_FN = 'csv_test_fn'
    askopenfilename_calls = deque()
    import_movies_calls = deque()
    show_info_calls = deque()
    
    def test_get_filename_dialog_called(self, class_patches):
        with self.import_movies_context():
            expected = dict(parent=handlers.config.app.tk_root,
                            filetypes=(('Movie import files', '*.csv'),))
            assert self.askopenfilename_calls.popleft() == expected
    
    def test_import_movies_called(self, class_patches):
        with self.import_movies_context():
            assert self.import_movies_calls.popleft() == self.CSV_TEST_FN
    
    def test_import_movies_raises_invalid_data_exception(self, class_patches, monkeypatch):
        monkeypatch.setattr(handlers.impexp, 'import_movies', self.dummy_import_movies_with_exception)
        with self.import_movies_context():
            expected = dict(parent=handlers.config.app.tk_root,
                            message='Errors were found in the input file.',
                            detail='Test exception message', icon='warning')
            assert self.show_info_calls.popleft() == expected
    
    @pytest.fixture
    def class_patches(self, monkeypatch):
        monkeypatch.setattr(handlers.filedialog, 'askopenfilename', self.dummy_askopenfilename)
        monkeypatch.setattr(handlers.messagebox, 'showinfo', self.dummy_show_info)
        monkeypatch.setattr(handlers.impexp, 'import_movies', self.dummy_import_movies)
    
    @contextmanager
    def import_movies_context(self):
        hold_app = handlers.config.app
        handlers.config.app = handlers.config.Config(name='test moviedb', version='test 1.0.0.dev')
        handlers.config.app.tk_root = 'tk_root'
        try:
            handlers.import_movies()
            yield
        finally:
            handlers.config.app = hold_app
    
    def dummy_askopenfilename(self, **kwargs):
        self.askopenfilename_calls.append(kwargs)
        return self.CSV_TEST_FN
    
    def dummy_import_movies(self, csv_fn):
        self.import_movies_calls.append(csv_fn)
    
    def dummy_import_movies_with_exception(self, csv_fn):
        raise handlers.impexp.MoviedbInvalidImportData('Test exception message')
    
    def dummy_show_info(self, **kwargs):
        self.show_info_calls.append(kwargs)


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
