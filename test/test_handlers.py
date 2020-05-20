"""Menu handlers test module."""

#  Copyright© 2020. Stephen Rigden.
#  Last modified 5/20/20, 8:54 AM by stephen.
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
from typing import Callable, List, Literal, Sequence

import pytest

import exception
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
    TAGS = ['Movie night candidate']
    
    movie_gui_args = []
    
    def test_movie_gui_called(self, monkeypatch):
        monkeypatch.setattr(handlers.database, 'all_tags', lambda *args: self.TAGS)
        monkeypatch.setattr(handlers.guiwidgets, 'AddMovieGUI',
                            lambda parent, commit_callback, delete_callback, buttons_to_show, all_tags:
                            self.movie_gui_args.append((parent, commit_callback, delete_callback,
                                                        buttons_to_show,
                                                        all_tags)))
        with self.add_movie_context():
            assert self.movie_gui_args == [(DummyParent(),
                                            handlers.add_movie_callback,
                                            handlers.delete_movie_callback,
                                            ['commit'], self.TAGS)]
    
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


class TestDeleteMovie:
    
    def test_delete_movie_called(self, monkeypatch):
        calls = []
        movie = handlers.config.FindMovieDef(title='test title', year=[2042])
        monkeypatch.setattr(handlers.database, 'del_movie', lambda *args: calls.append(args))
        handlers.delete_movie_callback(movie)
        assert calls == [(movie,)]


class TestEditMovie:
    TAGS = ['Movie night candidate']
    
    search_gui_args = []
    
    def test_edit_gui_called(self, monkeypatch):
        monkeypatch.setattr(handlers.database, 'all_tags', lambda *args: self.TAGS)
        monkeypatch.setattr(handlers.guiwidgets, 'SearchMovieGUI',
                            lambda parent, callback, tags:
                            self.search_gui_args.append((parent, callback, tags)))
        with self.edit_movie_context():
            assert self.search_gui_args == [(DummyParent(), handlers.search_movie_callback, self.TAGS)]
    
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
    askopenfilename_calls = None
    import_movies_calls = None
    messagebox_calls = None

    def test_user_cancellation_of_askopenfilename_dialog(self, class_patches, monkeypatch):
        monkeypatch.setattr(handlers.guiwidgets_2, 'gui_askopenfilename', lambda **kwargs: '')
        with self.import_movies_context():
            assert self.import_movies_calls == deque([])

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
        monkeypatch.setattr(handlers.guiwidgets_2, 'gui_askopenfilename', self.dummy_askopenfilename)
        monkeypatch.setattr(handlers.guiwidgets, 'gui_messagebox', self.gui_messagebox)
        monkeypatch.setattr(handlers.impexp, 'import_movies', self.dummy_import_movies)

    @contextmanager
    def import_movies_context(self):
        self.askopenfilename_calls = []
        self.import_movies_calls = deque()
        self.messagebox_calls = []
        hold_app = handlers.config.app
        handlers.config.app = handlers.config.Config(name='test moviedb', version='test 1.0.0.dev')
        handlers.config.app.tk_root = 'tk_root'
        try:
            yield handlers.import_movies()
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


# noinspection PyMissingOrEmptyDocstring
class TestAddMovieCallback:
    
    def test_add_movie_called(self, class_patches):
        self.dummy_add_movie_calls = []
        with self.callback_context():
            assert self.dummy_add_movie_calls == [(dict(title='Test Title', year='2020'),)]
    
    def test_add_movie_tag_link_called(self, class_patches):
        self.dummy_add_movie_tag_link_calls = []
        with self.callback_context():
            assert self.dummy_add_movie_tag_link_calls == [('test 1',
                                                            dict(title='Test Title', year='2020'),), ]
    
    @pytest.fixture
    def class_patches(self, monkeypatch):
        monkeypatch.setattr(handlers.database, 'add_movie', self.dummy_add_movie)
        monkeypatch.setattr(handlers.database, 'add_tag', self.dummy_add_tag)
        monkeypatch.setattr(handlers.database, 'add_movie_tag_link', self.dummy_add_movie_tag_link)
    
    @contextmanager
    def callback_context(self):
        movie = {'title': 'Test Title', 'year': '2020'}
        tags = ['test 1']
        yield handlers.add_movie_callback(movie, tags)
    
    dummy_add_movie_calls = []
    dummy_add_tag_calls = []
    dummy_add_movie_tag_link_calls = []
    
    def dummy_add_movie(self, *args):
        self.dummy_add_movie_calls.append(args)
    
    def dummy_add_tag(self, *args):
        self.dummy_add_tag_calls.append(args)
    
    def dummy_add_movie_tag_link(self, *args):
        self.dummy_add_movie_tag_link_calls.append(args)


# noinspection PyMissingOrEmptyDocstring
class TestSearchMovieCallback:
    
    def test_criteria_correctly_cleaned_up(self, class_setup, monkeypatch):
        monkeypatch.setattr(handlers.database, 'find_movies', self.configure_dummy_find_movies([]))
        clean_criteria = dict(title='Pot', year=[2000, 2010], tags=('blue', 'red'))
        with pytest.raises(exception.DatabaseSearchFoundNothing):
            handlers.search_movie_callback(self.criteria, self.tags)
        assert self.dummy_find_movies_calls == [(clean_criteria,)]
    
    def test_no_movies_found_raises_exception(self, class_setup, monkeypatch):
        monkeypatch.setattr(handlers.database, 'find_movies', self.configure_dummy_find_movies([]))
        with pytest.raises(exception.DatabaseSearchFoundNothing) as exc:
            handlers.search_movie_callback(self.criteria, self.tags)
        assert isinstance(exc.value, exception.DatabaseSearchFoundNothing)
    
    def test_single_movie_found_calls_instantiate_edit_movie_gui(self, class_setup, monkeypatch):
        movie = handlers.config.MovieUpdateDef(title='Test Movie')
        monkeypatch.setattr(handlers.database, 'find_movies', self.configure_dummy_find_movies([movie]))
        all_tags = ['test tag']
        monkeypatch.setattr(handlers.database, 'all_tags', lambda: all_tags)
        monkeypatch.setattr(handlers.guiwidgets, 'EditMovieGUI', DummyEditMovieGUI)
        with self.class_context():
            handlers.search_movie_callback(self.criteria, self.tags)
            expected = (handlers.config.app.tk_root, handlers.edit_movie_callback,
                        handlers.delete_movie_callback, ['commit', 'delete'], all_tags, movie)
        assert dummy_edit_movie_gui_instance[0] == expected

    def test_multiple_movies_found_calls_select_movie_gui(self, class_setup, monkeypatch):
        movie1 = handlers.config.MovieUpdateDef(title='Test Movie 1')
        movie2 = handlers.config.MovieUpdateDef(title='Test Movie 2')
        monkeypatch.setattr(handlers.database, 'find_movies',
                            self.configure_dummy_find_movies([movie1, movie2]))
        monkeypatch.setattr(handlers.guiwidgets,
                            'SelectMovieGUI', DummySelectMovieGUI)
        with self.class_context():
            handlers.search_movie_callback(self.criteria, self.tags)
            expected = handlers.config.app.tk_root, [movie1, movie2], handlers.select_movie_callback
        assert dummy_select_movie_gui_instance[0] == expected
    
    dummy_find_movies_calls = None
    
    def configure_dummy_find_movies(self, movies: list = None,
                                    exception_: exception.DatabaseException = False):
        def dummy_find_movies(*args):
            self.dummy_find_movies_calls.append(args)
            if exception_:
                raise exception_
            return movies
        
        return dummy_find_movies
    
    @pytest.fixture
    def class_setup(self):
        self.dummy_find_movies_calls = []
        self.dummy_select_movie_gui_instance = []
        self.criteria = {internal_names: ''
                         for internal_names in handlers.guiwidgets.MOVIE_FIELD_NAMES}
        self.criteria['title'] = 'Pot'
        self.criteria['year'] = [2000, 2010]
        self.criteria['director'] = []
        self.criteria['minutes'] = ['', '']
        self.criteria['notes'] = ''
        self.tags = ('blue', 'red')
    
    @contextmanager
    def class_context(self):
        hold_app = handlers.config.app
        handlers.config.app = handlers.config.Config('Test program name', 'Test program version')
        handlers.config.app.tk_root = DummyParent()
        try:
            yield
        finally:
            handlers.config.app = hold_app


# noinspection PyMissingOrEmptyDocstring
class TestEditMovieCallback:
    OLD_TAGS = ['old test tag']
    
    def test_edit_movie_called(self, class_patches):
        with self.class_context() as (updates, _, _):
            movie = dict(title=(updates['title']), year=[(updates['year'])])
            assert self.edit_movie_calls == [(movie, updates)]
    
    def raise_movie_not_found(self, *args):
        raise handlers.exception.DatabaseSearchFoundNothing
    
    def test_edit_movie_shows_movie_not_found_gui_alert(self, class_patches, monkeypatch):
        monkeypatch.setattr(handlers.database, 'edit_movie', self.raise_movie_not_found)
        msg_args = []
        monkeypatch.setattr(handlers.guiwidgets, 'gui_messagebox',
                            lambda *args: msg_args.append(args))
        with self.class_context():
            assert msg_args == [(DummyParent(), 'Missing movie',
                                 "The movie {'title': 'Test Title', 'year': [4242]} is no longer "
                                 "available. "
                                 "It may have been deleted by another process.")]

    def test_edit_movie_tags_shows_movie_not_found_gui_alert(self, class_patches, monkeypatch):
        monkeypatch.setattr(handlers.database, 'edit_movies_tag', self.raise_movie_not_found)
        msg_args = []
        monkeypatch.setattr(handlers.guiwidgets, 'gui_messagebox',
                            lambda *args: msg_args.append(args))
        with self.class_context():
            assert msg_args == [(DummyParent(), 'Missing movie',
                                 "The movie {'title': 'Test Title', 'year': [4242]} is no longer "
                                 "available. "
                                 "It may have been deleted by another process.")]
    
    def test_movie_tags_called(self, class_patches):
        with self.class_context() as (updates, _, _):
            movie = dict(title=(updates['title']), year=(updates['year']))
            assert self.movie_tags_calls == [movie]
    
    def test_edit_movies_tag_called(self, class_patches):
        with self.class_context() as (updates, old_tags, selected_tags):
            movie = dict(title=(updates['title']), year=(updates['year']))
            assert self.edit_movies_tag_calls == [(movie, old_tags, selected_tags)]
    
    @pytest.fixture
    def class_patches(self, monkeypatch):
        self.edit_movie_calls = []
        self.movie_tags_calls = []
        self.edit_movies_tag_calls = []
        monkeypatch.setattr(handlers.database, 'edit_movie',
                            lambda movie, updates: self.edit_movie_calls.append((movie, updates)))
        monkeypatch.setattr(handlers.database, 'movie_tags', self.movie_tags)
        monkeypatch.setattr(handlers.database, 'edit_movies_tag',
                            lambda *args: self.edit_movies_tag_calls.append(args))
    
    def movie_tags(self, movie):
        self.movie_tags_calls.append(movie)
        return self.OLD_TAGS
    
    @contextmanager
    def class_context(self):
        updates = handlers.config.MovieUpdateDef(title='Test Title', year=4242, notes='Test note')
        selected_tags = ['test tag']
        hold_app = handlers.config.app
        handlers.config.app = handlers.config.Config('Test program name', 'Test program version')
        handlers.config.app.tk_root = DummyParent()
        handlers.edit_movie_callback(updates, selected_tags)
        try:
            yield updates, self.OLD_TAGS, selected_tags
        finally:
            handlers.config.app = hold_app


# noinspection PyMissingOrEmptyDocstring
class TestSelectMovieCallback:
    TITLE = 'Test Title'
    YEAR = 2042
    MOVIE = ['Test Movie']

    dummy_find_movies_calls = []
    dummy_edit_movie_callback = []

    def test_find_movies_called(self, class_patches):
        with self.class_context():
            assert self.dummy_find_movies_calls[0][0] == dict(title=self.TITLE, year=self.YEAR)

    def test_edit_movie_gui_created(self, class_patches):
        sentinel_1 = object()
        sentinel_2 = object()
        with self.class_context():
            assert dummy_edit_movie_gui_instance[0][0] == DummyParent()
            assert dummy_edit_movie_gui_instance[0][3] == ['commit', 'delete']
            assert dummy_edit_movie_gui_instance[0][4] == ['Test tag 42']
            assert dummy_edit_movie_gui_instance[0][5] == 'Test Movie'
            dummy_edit_movie_gui_instance[0][1](sentinel_1, sentinel_2)
            assert self.dummy_edit_movie_callback == [(sentinel_1, sentinel_2)]

    @pytest.fixture
    def class_patches(self, monkeypatch):
        self.dummy_find_movies_calls = []
        monkeypatch.setattr(handlers.database, 'find_movies', self.dummy_find_movies)
        monkeypatch.setattr(handlers.database, 'all_tags', lambda: ['Test tag 42'])
        monkeypatch.setattr(handlers.guiwidgets, 'EditMovieGUI', DummyEditMovieGUI)
        monkeypatch.setattr(handlers, 'edit_movie_callback',
                            (lambda updates, selected_tags:
                             self.dummy_edit_movie_callback.append((updates, selected_tags))))

    @contextmanager
    def class_context(self):
        global dummy_edit_movie_gui_instance
        dummy_edit_movie_gui_instance = []
        hold_app = handlers.config.app
        handlers.config.app = handlers.config.Config('Test program name', 'Test program version')
        handlers.config.app.tk_root = DummyParent()
        try:
            yield handlers.select_movie_callback(self.TITLE, self.YEAR)
        finally:
            handlers.config.app = hold_app

    def dummy_find_movies(self, *args):
        self.dummy_find_movies_calls.append(args)
        return self.MOVIE


class TestAddTag:
    
    def test_add_tag(self, monkeypatch):
        tag_gui_args = []
        monkeypatch.setattr(handlers.guiwidgets_2, 'AddTagGUI',
                            lambda parent, commit_callback:
                            tag_gui_args.append((parent, commit_callback)))
        
        tk_parent = DummyParent()
        add_tag_callback = handlers.add_tag_callback
        with self.add_tag_context():
            assert tag_gui_args == [(tk_parent, add_tag_callback)]
    
    # noinspection PyMissingOrEmptyDocstring
    @contextmanager
    def add_tag_context(self):
        hold_app = handlers.config.app
        handlers.config.app = handlers.config.Config('Test program name', 'Test program version')
        handlers.config.app.tk_root = DummyParent()
        try:
            yield handlers.add_tag()
        finally:
            handlers.config.app = hold_app


class TestAddTagCallback:
    
    def test_(self, monkeypatch):
        calls = []
        monkeypatch.setattr(handlers.database, 'add_tag', lambda *args: calls.append(args))
        test_tag = 'Test tag'
        handlers.add_tag_callback(test_tag)
        assert calls == [(test_tag,)]


class TestEditTagCallback:
    old_tag = 'test old tag'
    new_tag = 'test new tag'
    
    def test_database_edit_tag_called(self, monkeypatch):
        edit_tags_args = []
        monkeypatch.setattr(handlers.database, 'edit_tag', lambda *args: edit_tags_args.append(args))
        with self.add_tag_callback_context():
            assert edit_tags_args == [(self.old_tag, self.new_tag)]
    
    def test_database_search_found_nothing_raised(self, monkeypatch):
        # noinspection PyMissingOrEmptyDocstring,PyUnusedLocal
        def raise_exception(*args): raise handlers.database.exception.DatabaseSearchFoundNothing
        
        message_args = []
        
        monkeypatch.setattr(handlers.database, 'edit_tag', raise_exception)
        monkeypatch.setattr(handlers.guiwidgets, 'gui_messagebox',
                            lambda *args: message_args.append(args))
        with self.add_tag_callback_context():
            assert message_args == [(DummyParent(), 'Missing tag',
                                     'The tag test old tag is no longer available. '
                                     'It may have been deleted by another process.')]
    
    # noinspection PyMissingOrEmptyDocstring
    @contextmanager
    def add_tag_callback_context(self):
        hold_app = handlers.config.app
        handlers.config.app = handlers.config.Config('Test program name', 'Test program version')
        handlers.config.app.tk_root = DummyParent()

        callback = handlers.edit_tag_callback_wrapper(self.old_tag)

        try:
            yield callback(self.new_tag)
        finally:
            handlers.config.app = hold_app


class TestDeleteTagCallback:
    tag = 'test tag'
    
    def test_databasse_delete_tag_called(self, monkeypatch):
        del_tag_args = []
        monkeypatch.setattr(handlers.database, 'del_tag', lambda *args: del_tag_args.append(args))
        with self.delete_tag_callback_context():
            assert del_tag_args == [(self.tag,)]
    
    def test_database_search_found_nothing_ignored(self, monkeypatch):
        def raise_exception(*args):
            raise handlers.database.exception.DatabaseSearchFoundNothing
        
        monkeypatch.setattr(handlers.database, 'del_tag', raise_exception)
        try:
            with self.delete_tag_callback_context():
                pass
        except handlers.database.exception.DatabaseSearchFoundNothing:
            assert False, ("Exception 'handlers.database.exception.DatabaseSearchFoundNothing'"
                           " was not suppressed.")
    
    @contextmanager
    def delete_tag_callback_context(self):
        callback = handlers.delete_tag_callback_wrapper(self.tag)
        yield callback()


@dataclass
class DummyParent:
    """Provide a dummy for Tk root."""
    pass


dummy_edit_movie_gui_instance = []


# noinspection PyMissingOrEmptyDocstring
@dataclass
class DummyEditMovieGUI:
    parent: DummyParent
    commit_callback: Callable[[handlers.config.MovieUpdateDef, Sequence[str]], None]
    delete_callback: Callable[..., None]
    buttons_to_show: List[Literal['commit', 'delete']]
    all_tag_names: Sequence[str]
    movie: handlers.config.MovieUpdateDef
    
    def __post_init__(self):
        dummy_edit_movie_gui_instance.append((self.parent, self.commit_callback, self.delete_callback,
                                              self.buttons_to_show, self.all_tag_names, self.movie))


dummy_select_movie_gui_instance = []


# noinspection PyMissingOrEmptyDocstring
@dataclass
class DummySelectMovieGUI:
    parent: DummyParent
    movies: List[handlers.config.MovieUpdateDef]
    callback: Callable[[handlers.config.MovieUpdateDef, Sequence[str]], None]
    
    def __post_init__(self):
        dummy_select_movie_gui_instance.append((self.parent, self.movies, self.callback))


dummy_gui_messagebox_calls = []


# noinspection PyMissingOrEmptyDocstring
def dummy_gui_messagebox(*args, **kwargs):
    dummy_gui_messagebox_calls.append((args, kwargs))
