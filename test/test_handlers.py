"""Menu handlers test module."""

#  Copyright© 2020. Stephen Rigden.
#  Last modified 1/2/20, 8:10 AM by stephen.
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
from dataclasses import dataclass

import pytest

import handlers


# noinspection PyMissingOrEmptyDocstring
class TestAboutDialog:
    
    messagebox_calls = []

    def test_about_dialog_called(self, monkeypatch):
        monkeypatch.setattr(handlers.guiwidgets, 'gui_messagebox', self.gui_messagebox)
        with self.about_context():
            assert self.messagebox_calls == [(DummyParent(), 'Test program name',
                                              'Test program version'), ]

    @contextmanager
    def about_context(self):
        hold_app = handlers.config.app
        handlers.config.app = handlers.config.Config('Test program name', 'Test program version')
        handlers.config.app.tk_root = DummyParent()
        try:
            handlers.about_dialog()
            yield
        finally:
            handlers.config.app = hold_app

    def gui_messagebox(self, *args):
        self.messagebox_calls.append(args)


class TestAddMovie:
    movie_gui_args = []
    
    def test_movie_gui_called(self, monkeypatch):
        monkeypatch.setattr(handlers.guiwidgets, 'EditMovieGUI',
                            lambda parent, callback, tags:
                            self.movie_gui_args.append((parent, tags, callback)))
        with self.add_movie_context():
            assert self.movie_gui_args == [(DummyParent(), ['Movie night candidate'],
                                            handlers.add_movie_callback,)]
    
    # noinspection PyMissingOrEmptyDocstring
    @contextmanager
    def add_movie_context(self):
        hold_app = handlers.config.app
        handlers.config.app = handlers.config.Config('Test program name', 'Test program version')
        handlers.config.app.tk_root = DummyParent()
        try:
            yield handlers.add_movie()
        finally:
            handlers.config.app = hold_app


# noinspection PyMissingOrEmptyDocstring
class TestAddMovieCallback:
    
    def test_add_movie_called(self, class_patches):
        self.dummy_add_movie_calls = []
        with self.callback_context():
            assert self.dummy_add_movie_calls == [(dict(title='Test Title', year='2020'),)]
    
    def test_add_tag_and_links_called(self, class_patches):
        self.dummy_tag_and_links_calls = []
        with self.callback_context():
            assert self.dummy_tag_and_links_calls == [('test 1',
                                                       (dict(title='Test Title', year='2020'),),)]
    
    @pytest.fixture
    def class_patches(self, monkeypatch):
        monkeypatch.setattr(handlers.database, 'add_movie', self.dummy_add_movie)
        monkeypatch.setattr(handlers.database, 'add_tag_and_links', self.dummy_tag_and_links)
    
    @contextmanager
    def callback_context(self):
        movie = {'title': 'Test Title', 'year': '2020'}
        tags = ['test 1']
        yield handlers.add_movie_callback(movie, tags)

    dummy_add_movie_calls = []
    dummy_tag_and_links_calls = []

    def dummy_add_movie(self, *args):
        self.dummy_add_movie_calls.append(args)

    def dummy_tag_and_links(self, *args):
        self.dummy_tag_and_links_calls.append(args)


class TestEditMovie:
    search_gui_args = []

    def test_edit_gui_called(self, monkeypatch):
        monkeypatch.setattr(handlers.guiwidgets, 'SearchMovieGUI',
                            lambda parent, tags, callback:
                            self.search_gui_args.append((parent, callback, tags)))
        with self.edit_movie_context():
            assert self.search_gui_args == [(DummyParent(), ['Movie night candidate'],
                                             handlers.edit_movie_callback,)]
    
    # noinspection PyMissingOrEmptyDocstring
    @contextmanager
    def edit_movie_context(self):
        hold_app = handlers.config.app
        handlers.config.app = handlers.config.Config('Test program name', 'Test program version')
        handlers.config.app.tk_root = DummyParent()
        try:
            yield handlers.edit_movie()
        finally:
            handlers.config.app = hold_app


# noinspection PyMissingOrEmptyDocstring
class TestImportMovies:
    CSV_TEST_FN = 'csv_test_fn'
    askopenfilename_calls = []
    import_movies_calls = deque()
    messagebox_calls = []
    
    def test_get_filename_dialog_called(self, class_patches):
        with self.import_movies_context():
            assert self.askopenfilename_calls == [dict(parent=handlers.config.app.tk_root,
                                                       filetypes=(('Movie import files', '*.csv'),))]
    
    def test_import_movies_called(self, class_patches):
        with self.import_movies_context():
            assert self.import_movies_calls.popleft() == self.CSV_TEST_FN
    
    def test_import_movies_raises_invalid_data_exception(self, class_patches, monkeypatch):
        monkeypatch.setattr(handlers.impexp, 'import_movies', self.dummy_import_movies_with_exception)
        with self.import_movies_context():
            assert self.messagebox_calls == [((handlers.config.app.tk_root,),
                                              dict(message='Errors were found in the input file.',
                                                   detail='Test exception message', icon='warning'))]
    
    @pytest.fixture
    def class_patches(self, monkeypatch):
        monkeypatch.setattr(handlers.guiwidgets, 'gui_askopenfilename', self.dummy_askopenfilename)
        monkeypatch.setattr(handlers.guiwidgets, 'gui_messagebox', self.gui_messagebox)
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
    
    def gui_messagebox(self, *args, **kwargs):
        self.messagebox_calls.append((args, kwargs))


@dataclass
class DummyParent:
    """Provide a dummy for Tk root."""
    pass
