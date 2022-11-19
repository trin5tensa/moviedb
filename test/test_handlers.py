"""Menu handlers test module."""

#  Copyright (c) 2022-2022. Stephen Rigden.
#  Last modified 11/19/22, 9:23 AM by stephen.
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
        hold_persistent = handlers.config.persistent
        hold_current = handlers.config.current
        
        handlers.config.persistent = handlers.config.PersistentConfig(program='Test program name',
                                                                      program_version='Test program version')
        handlers.config.current = handlers.config.CurrentConfig(tk_root=DummyParent())
        try:
            handlers.about_dialog()
            yield
        finally:
            handlers.config.persistent = hold_persistent
            handlers.config.current = hold_current

    def gui_messagebox(self, *args):
        self.messagebox_calls.append(args)


class TestPreferences:
    test_tmdb_api_key = 'test_tmdb_api_key'
    test_use_tmdb = True
    calls = []

    def test_preferences_dialog_instantiates_preferences_gui(self, monkeypatch):
        with self.preferences_context(monkeypatch):
            assert self.calls == [(DummyParent(), self.test_tmdb_api_key,
                                   self.test_use_tmdb, handlers._preferences_callback)]

    def test_preferences_callback_updates_config(self, monkeypatch):
        # NB This method uses the config set up of the context manager
        # BUT has no interest in the test instance of PreferencesGUI.
        user_api_key = 'user_api_key'
        user_use_tmdb = True
        with self.preferences_context(monkeypatch):
            handlers._preferences_callback(user_api_key, user_use_tmdb)
            assert handlers.config.persistent.tmdb_api_key == user_api_key
            assert handlers.config.persistent.use_tmdb == user_use_tmdb

    @contextmanager
    def preferences_context(self, monkeypatch):
        hold_persistent = handlers.config.persistent
        hold_current = handlers.config.current
        
        handlers.config.persistent = handlers.config.PersistentConfig('Test program name', 'Test program version')
        handlers.config.persistent.tmdb_api_key = self.test_tmdb_api_key
        handlers.config.persistent.use_tmdb = self.test_use_tmdb
        
        handlers.config.current = handlers.config.CurrentConfig(tk_root=DummyParent())
        monkeypatch.setattr(handlers.guiwidgets_2, 'PreferencesGUI',
                            lambda *args: self.calls.append(args))
        try:
            yield handlers.preferences_dialog()
        finally:
            handlers.config.persistent = hold_persistent
            handlers.config.current = hold_current
    

class TestGetTmdbGetApiKey:
    TEST_KEY = 'dummy key'
    
    @contextmanager
    def get_tmdb_key(self, monkeypatch, api_key=TEST_KEY, use_tmdb=True):
        dummy_persistent_config = handlers.config.PersistentConfig('test_prog', 'test_vers')
        dummy_persistent_config.use_tmdb = use_tmdb
        dummy_persistent_config.tmdb_api_key = api_key
        monkeypatch.setattr(handlers.config, 'persistent', dummy_persistent_config)
        # noinspection PyProtectedMember
        yield handlers._get_tmdb_api_key()
        
    def test_key_returned(self, monkeypatch):
        with self.get_tmdb_key(monkeypatch) as ctx:
            assert ctx == self.TEST_KEY
            
    def test_do_not_use_tmdb_logged(self, monkeypatch, caplog):
        caplog.set_level('DEBUG')
        with self.get_tmdb_key(monkeypatch, use_tmdb=False):
            expected = f"User declined TMDB use."
            assert caplog.messages[0] == expected

    def test_key_needs_setting_calls_preferences_dialog(self, monkeypatch):
        calls = []
        monkeypatch.setattr(handlers, 'preferences_dialog', lambda: calls.append(True))
        with self.get_tmdb_key(monkeypatch, api_key=''):
            assert calls[0]


class TestTmdbMovieSearch:
    # TODO Tests…
    pass


class TestAddMovie:
    TAGS = ['Movie night candidate']
    
    movie_gui_args = []
    
    def test_movie_gui_called(self, monkeypatch):
        monkeypatch.setattr(handlers.database, 'all_tags', lambda *args: self.TAGS)
        monkeypatch.setattr(handlers.guiwidgets_2, 'AddMovieGUI',
                            lambda parent, commit_callback, tmdb_search_callback, all_tags:
                            self.movie_gui_args.append((parent, commit_callback, tmdb_search_callback, all_tags)))
        
        with self.add_movie_context():
            assert self.movie_gui_args == [(DummyParent(),
                                            handlers._add_movie_callback,
                                            handlers._tmdb_io_handler,
                                            self.TAGS)]
    
    # noinspection PyMissingOrEmptyDocstring
    @contextmanager
    def add_movie_context(self):
        hold_persistent = handlers.config.persistent
        hold_current = handlers.config.current
        
        handlers.config.persistent = handlers.config.PersistentConfig('Test program name', 'Test program version')
        handlers.config.current = handlers.config.CurrentConfig(tk_root=DummyParent())
        try:
            yield handlers.add_movie()
        finally:
            handlers.config.persistent = hold_persistent
            handlers.config.current = hold_current


class TestDeleteMovie:
    
    def test_delete_movie_called(self, monkeypatch):
        calls = []
        # noinspection PyTypeChecker
        movie = handlers.config.FindMovieTypedDict(title='test title', year=[2042])
        monkeypatch.setattr(handlers.database, 'del_movie', lambda *args: calls.append(args))
        handlers._delete_movie_callback(movie)
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
            assert self.search_gui_args == [(DummyParent(), handlers._search_movie_callback, self.TAGS)]
    
    # noinspection PyMissingOrEmptyDocstring
    @contextmanager
    def edit_movie_context(self):
        hold_app = handlers.config.current
        handlers.config.current = handlers.config.PersistentConfig('Test program name', 'Test program version')
        handlers.config.current.tk_root = DummyParent()
        try:
            yield handlers.edit_movie()
        finally:
            handlers.config.current = hold_app


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
            assert self.askopenfilename_calls == [dict(parent=handlers.config.current.tk_root,
                                                       filetypes=(('Movie import files', '*.csv'),))]

    def test_import_movies_called(self, class_patches):
        with self.import_movies_context():
            assert self.import_movies_calls.popleft() == self.CSV_TEST_FN
    
    def test_import_movies_raises_invalid_data_exception(self, class_patches, monkeypatch):
        monkeypatch.setattr(handlers.impexp, 'import_movies', self.dummy_import_movies_with_exception)
        with self.import_movies_context():
            assert self.messagebox_calls == [((handlers.config.current.tk_root,),
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
        hold_persistent = handlers.config.persistent
        hold_current = handlers.config.current
        
        handlers.config.persistent = handlers.config.PersistentConfig(program='test moviedb',
                                                                      program_version='test 1.0.0.dev')
        handlers.config.current = handlers.config.CurrentConfig(tk_root='tk_root')
        try:
            yield handlers.import_movies()
        finally:
            handlers.config.persistent = hold_persistent
            handlers.config.current = hold_current

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
            assert self.dummy_add_movie_calls == [(dict(title='Test Title', year=2020),)]
    
    def test_add_movie_tag_link_called(self, class_patches):
        self.dummy_add_movie_tag_link_calls = []
        with self.callback_context():
            assert self.dummy_add_movie_tag_link_calls == [('test 1',
                                                            dict(title='Test Title', year=2020),), ]
    
    @pytest.fixture
    def class_patches(self, monkeypatch):
        monkeypatch.setattr(handlers.database, 'add_movie', self.dummy_add_movie)
        monkeypatch.setattr(handlers.database, 'add_tag', self.dummy_add_tag)
        monkeypatch.setattr(handlers.database, 'add_movie_tag_link', self.dummy_add_movie_tag_link)
    
    @contextmanager
    def callback_context(self):
        movie = handlers.config.MovieTypedDict(title='Test Title', year=2020)
        tags = ['test 1']
        yield handlers._add_movie_callback(movie, tags)
    
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
            handlers._search_movie_callback(self.criteria, self.tags)
        assert self.dummy_find_movies_calls == [(clean_criteria,)]
    
    def test_no_movies_found_raises_exception(self, class_setup, monkeypatch):
        monkeypatch.setattr(handlers.database, 'find_movies', self.configure_dummy_find_movies([]))
        with pytest.raises(exception.DatabaseSearchFoundNothing) as exc:
            handlers._search_movie_callback(self.criteria, self.tags)
        assert isinstance(exc.value, exception.DatabaseSearchFoundNothing)
    
    def test_single_movie_found_calls_instantiate_edit_movie_gui(self, class_setup, monkeypatch):
        movie = dict(title='Test Movie', year='1942')
        monkeypatch.setattr(handlers.database, 'find_movies', self.configure_dummy_find_movies([movie]))
        all_tags = ['test tag']
        monkeypatch.setattr(handlers.database, 'all_tags', lambda: all_tags)
        monkeypatch.setattr(handlers.guiwidgets, 'EditMovieGUI', DummyEditMovieGUI)
        
        with self.class_context():
            handlers._search_movie_callback(self.criteria, self.tags)
            expected = (handlers.config.current.tk_root, handlers._edit_movie_callback_wrapper(self.criteria),
                        handlers._delete_movie_callback, ['commit', 'delete'], all_tags, movie)
            assert dummy_edit_movie_gui_instance[0][0] == handlers.config.current.tk_root
            assert expected[1].__name__ == 'edit_movie_callback'
            assert dummy_edit_movie_gui_instance[0][2:] == (handlers._delete_movie_callback,
                                                            ['commit', 'delete'], all_tags, movie)

    def test_multiple_movies_found_calls_select_movie_gui(self, class_setup, monkeypatch):
        movie1 = handlers.config.MovieUpdateDef(title='Test Movie 1', year=2042)
        movie2 = handlers.config.MovieUpdateDef(title='Test Movie 2', year=2042)
        monkeypatch.setattr(handlers.database, 'find_movies',
                            self.configure_dummy_find_movies([movie1, movie2]))
        monkeypatch.setattr(handlers.guiwidgets,
                            'SelectMovieGUI', DummySelectMovieGUI)
        with self.class_context():
            handlers._search_movie_callback(self.criteria, self.tags)
            expected = handlers.config.current.tk_root, [movie1, movie2], handlers._select_movie_callback
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
        hold_persistent = handlers.config.persistent
        hold_current = handlers.config.current
        handlers.config.persistent = handlers.config.PersistentConfig(program='Test program name',
                                                                      program_version='Test program version')
        handlers.config.current = handlers.config.CurrentConfig(DummyParent())
        try:
            yield
        finally:
            handlers.config.current = hold_current
            handlers.config.persistent = hold_persistent


# noinspection PyMissingOrEmptyDocstring
class TestEditMovieCallback:
    OLD_TITLE = 'Old Test Title'
    OLD_YEAR = 1942
    OLD_MOVIE = handlers.config.MovieTypedDict(title=OLD_TITLE, year=OLD_YEAR)
    OLD_TAGS = ['Tag 1', 'Tag 2']
    NEW_TITLE = 'Test Title'
    NEW_YEAR = 2042
    NEW_MOVIE = handlers.config.MovieTypedDict(title=NEW_TITLE, year=NEW_YEAR)
    NEW_TAGS = ['Tag 2', 'Tag 3']

    replace_movie_calls: List = None
    movie_tags_calls: List = None
    edit_movie_tag_link_calls: List = None
    gui_messagebox_calls: List = None
    
    def test_edit_movie_callback_returned(self):
        with self.class_context() as cm:
            assert cm.__name__ == 'edit_movie_callback'

    def test_replace_movie_called(self, patches):
        with self.class_context() as cm:
            cm(self.NEW_MOVIE, self.NEW_TAGS)
            assert self.replace_movie_calls == [(self.OLD_MOVIE, self.NEW_MOVIE)]

    def test_movie_tags_called(self, patches):
        with self.class_context() as cm:
            cm(self.NEW_MOVIE, self.NEW_TAGS)
            assert self.movie_tags_calls == [(self.OLD_MOVIE, )]

    def test_edit_movie_tag_link_called(self, patches):
        with self.class_context() as cm:
            cm(self.NEW_MOVIE, self.NEW_TAGS)
            assert self.edit_movie_tag_link_calls == [(self.NEW_MOVIE, self.OLD_TAGS, self.NEW_TAGS)]

    def test_edit_movie_tag_link_raises_found_nothing(self, patches, monkeypatch):
        with self.class_context() as cm:
            self.gui_messagebox_calls = []

            # noinspection PyUnusedLocal
            def dummy_edit_movie_tag_links(*args):
                raise handlers.exception.DatabaseSearchFoundNothing
            
            monkeypatch.setattr(handlers.database, 'edit_movie_tag_links',
                                dummy_edit_movie_tag_links)
            monkeypatch.setattr(handlers.guiwidgets, 'gui_messagebox',
                                lambda *args: self.gui_messagebox_calls.append(args))
            
            hold_persistent = handlers.config.persistent
            hold_current = handlers.config.current
            handlers.config.persistent = handlers.config.PersistentConfig('Test program name', 'Test program version')
            handlers.config.current = handlers.config.CurrentConfig(tk_root=DummyParent())

            cm(self.NEW_MOVIE, self.NEW_TAGS)
            handlers.config.persistent = hold_persistent
            
            handlers.config.current = hold_current

            assert self.gui_messagebox_calls == [(
                    DummyParent(),
                    'Missing movie',
                    f'The movie {self.NEW_MOVIE} is no longer in the database. It may have '
                    f'been deleted by another process. ')]

    def dummy_movie_tags(self, old_movie):
        self.movie_tags_calls.append((old_movie, ))
        return self.OLD_TAGS

    @pytest.fixture
    def patches(self, monkeypatch):
        self.replace_movie_calls = []
        self.movie_tags_calls = []
        self.edit_movie_tag_link_calls = []
        monkeypatch.setattr(handlers.database, 'replace_movie',
                            lambda *args: self.replace_movie_calls.append(args))
        monkeypatch.setattr(handlers.database, 'movie_tags', self.dummy_movie_tags)
        monkeypatch.setattr(handlers.database, 'edit_movie_tag_links',
                            lambda *args: self.edit_movie_tag_link_calls.append(args))
        
    @contextmanager
    def class_context(self):
        old_movie: handlers.config.MovieTypedDict = dict(title='Old Test Title', year=1942)
        yield handlers._edit_movie_callback_wrapper(old_movie)
    

# noinspection PyMissingOrEmptyDocstring
class TestSelectMovieCallback:
    TITLE = 'Test Title'
    YEAR = 2042
    MOVIE = handlers.config.MovieUpdateDef(title=TITLE, year=YEAR)
    MOVIES = [MOVIE]

    dummy_find_movies_calls = []
    dummy_edit_movie_callback_wrapper_calls = []

    def test_find_movies_called(self, class_patches):
        with self.class_context():
            assert self.dummy_find_movies_calls[0][0] == dict(title=self.TITLE, year=self.YEAR)
            assert self.dummy_find_movies_calls[0][0] == self.MOVIE

    def test_edit_movie_gui_created(self, class_patches):
        with self.class_context():
            assert dummy_edit_movie_gui_instance[0][0] == DummyParent()
            assert dummy_edit_movie_gui_instance[0][1].__name__ == 'dummy_edit_movie_callback'
            assert dummy_edit_movie_gui_instance[0][2].__name__ == '_delete_movie_callback'
            assert dummy_edit_movie_gui_instance[0][3] == ['commit', 'delete']
            assert dummy_edit_movie_gui_instance[0][4] == ['Test tag 42']
            assert dummy_edit_movie_gui_instance[0][5] == self.MOVIE

    @pytest.fixture
    def class_patches(self, monkeypatch):
        self.dummy_find_movies_calls = []
        monkeypatch.setattr(handlers.database, 'find_movies', self.dummy_find_movies)
        monkeypatch.setattr(handlers.database, 'all_tags', lambda: ['Test tag 42'])
        monkeypatch.setattr(handlers.guiwidgets, 'EditMovieGUI', DummyEditMovieGUI)
        monkeypatch.setattr(handlers, '_edit_movie_callback_wrapper',
                            self.dummy_edit_movie_callback_wrapper)

    @contextmanager
    def class_context(self):
        global dummy_edit_movie_gui_instance
        dummy_edit_movie_gui_instance = []
        hold_persistent = handlers.config.persistent
        hold_current = handlers.config.current
        
        handlers.config.persistent = handlers.config.PersistentConfig('Test program name', 'Test program version')
        handlers.config.current = handlers.config.CurrentConfig(tk_root=DummyParent())
        try:
            yield handlers._select_movie_callback(self.TITLE, self.YEAR)
        finally:
            handlers.config.persistent = hold_persistent
            handlers.config.current = hold_current

    def dummy_find_movies(self, *args):
        self.dummy_find_movies_calls.append(args)
        return self.MOVIES

    # noinspection PyUnusedLocal
    @staticmethod
    def dummy_edit_movie_callback_wrapper(old_movie: handlers.config.MovieKeyTypedDict) -> Callable:
        def dummy_edit_movie_callback():
            pass
        return dummy_edit_movie_callback


class TestAddTag:
    
    def test_add_tag(self, monkeypatch):
        tag_gui_args = []
        monkeypatch.setattr(handlers.guiwidgets_2, 'AddTagGUI',
                            lambda parent, commit_callback:
                            tag_gui_args.append((parent, commit_callback)))
        
        tk_parent = DummyParent()
        add_tag_callback = handlers._add_tag_callback
        with self.add_tag_context():
            assert tag_gui_args == [(tk_parent, add_tag_callback)]
    
    # noinspection PyMissingOrEmptyDocstring
    @contextmanager
    def add_tag_context(self):
        hold_persistent = handlers.config.persistent
        hold_current = handlers.config.current
        
        handlers.config.persistent = handlers.config.PersistentConfig(program='Test program name',
                                                                      program_version='Test program version')
        handlers.config.current = handlers.config.CurrentConfig(tk_root=DummyParent())
        try:
            yield handlers.add_tag()
        finally:
            handlers.config.persistent = hold_persistent
            handlers.config.current = hold_current


class TestEditTag:
    
    def test_edit_tag(self, monkeypatch):
        edit_tag_args = []
        monkeypatch.setattr(handlers.guiwidgets_2, 'SearchTagGUI',
                            lambda *args: edit_tag_args.append(args))
        
        tk_parent = DummyParent()
        search_tag_callback = handlers._search_tag_callback
        with self.search_tag_context():
            assert edit_tag_args == [(tk_parent, search_tag_callback)]
    
    # noinspection PyMissingOrEmptyDocstring
    @contextmanager
    def search_tag_context(self):
        hold_persistent = handlers.config.persistent
        hold_current = handlers.config.current
    
        handlers.config.persistent = handlers.config.PersistentConfig(program='Test program name',
                                                                      program_version='Test program version')
        handlers.config.current = handlers.config.CurrentConfig(tk_root=DummyParent())
    
        # handlers.config.current = handlers.config.Config('Test program name', 'Test program version')
        # handlers.config.current.tk_root = DummyParent()
        try:
            yield handlers.edit_tag()
        finally:
            handlers.config.persistent = hold_persistent
            handlers.config.current = hold_current


class TestAddTagCallback:
    
    def test_(self, monkeypatch):
        calls = []
        monkeypatch.setattr(handlers.database, 'add_tag', lambda *args: calls.append(args))
        test_tag = 'Test tag'
        handlers._add_tag_callback(test_tag)
        assert calls == [(test_tag,)]


# noinspection PyMissingOrEmptyDocstring
class TestSearchTagCallback:
    
    def test_zero_tags_found_raises_exception(self, monkeypatch):
        tags_found = []
        monkeypatch.setattr(handlers.database, 'find_tags', lambda *args: tags_found)
        tag_pattern = '42'
        with pytest.raises(exception.DatabaseSearchFoundNothing):
            with self.search_tag_context(tag_pattern):
                pass
    
    def test_one_tag_found_calls_edit_tag_gui(self, monkeypatch, class_patches):
        tags_found = ['42']
        monkeypatch.setattr(handlers.database, 'find_tags', lambda *args: tags_found)
        tag_pattern = '42'
        with self.search_tag_context(tag_pattern):
            args_ = dummy_edit_tag_gui_instance[0]
            assert args_[0] == DummyParent()
            assert args_[1] == '42'
            assert isinstance(args_[2], Callable)
            assert isinstance(args_[3], Callable)
    
    def test_multiple_tags_found_calls_select_tag_gui(self, monkeypatch, class_patches):
        tags_found = ['42', '43']
        monkeypatch.setattr(handlers.database, 'find_tags', lambda *args: tags_found)
        tag_pattern = '42'
        with self.search_tag_context(tag_pattern):
            args_ = dummy_select_tag_gui_instance[0]
            assert args_[0] == DummyParent()
            assert isinstance(args_[1], Callable)
            assert args_[2] == ['42', '43']
    
    @pytest.fixture
    def class_patches(self, monkeypatch):
        monkeypatch.setattr(handlers.guiwidgets_2, 'EditTagGUI', DummyEditTagGUI)
        monkeypatch.setattr(handlers.guiwidgets_2, 'SelectTagGUI', DummySelectTagGUI)
    
    @contextmanager
    def search_tag_context(self, tag_pattern: str):
        hold_persistent = handlers.config.persistent
        hold_current = handlers.config.current
    
        handlers.config.persistent = handlers.config.PersistentConfig(program='Test program name',
                                                                      program_version='Test program version')
        handlers.config.current = handlers.config.CurrentConfig(tk_root=DummyParent())
        
        try:
            yield handlers._search_tag_callback(tag_pattern)
        finally:
            handlers.config.persistent = hold_persistent
            handlers.config.current = hold_current


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
        hold_persistent = handlers.config.persistent
        hold_current = handlers.config.current
    
        handlers.config.persistent = handlers.config.PersistentConfig(program='Test program name',
                                                                      program_version='Test program version')
        handlers.config.current = handlers.config.CurrentConfig(tk_root=DummyParent())
        callback = handlers._edit_tag_callback_wrapper(self.old_tag)

        try:
            yield callback(self.new_tag)
        finally:
            handlers.config.persistent = hold_persistent
            handlers.config.current = hold_current


# noinspection PyMissingOrEmptyDocstring
class TestDeleteTagCallback:
    tag = 'test tag'
    
    def test_database_delete_tag_called(self, monkeypatch):
        del_tag_args = []
        monkeypatch.setattr(handlers.database, 'del_tag', lambda *args: del_tag_args.append(args))
        with self.delete_tag_callback_context():
            assert del_tag_args == [(self.tag,)]
    
    def test_database_search_found_nothing_ignored(self, monkeypatch):
        # noinspection PyUnusedLocal
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
        callback = handlers._delete_tag_callback_wrapper(self.tag)
        yield callback()


# noinspection PyMissingOrEmptyDocstring
class TestSearchTagCallbackWrapper:
    tag = 'Test tag'
    
    def test_select_tag_callback_calls_edit_tag_gui(self, monkeypatch):
        monkeypatch.setattr(handlers.guiwidgets_2, 'EditTagGUI', DummyEditTagGUI)
        
        with self.callback_context():
            args = dummy_edit_tag_gui_instance[0]
            assert args[0] == DummyParent()
            assert args[1] == self.tag
            assert args[2].__code__.co_name == 'delete_tag_callback'
            assert args[3].__code__.co_name == 'edit_tag_callback'
    
    @contextmanager
    def callback_context(self):
        global dummy_edit_tag_gui_instance
        dummy_edit_tag_gui_instance = []
        hold_persistent = handlers.config.persistent
        hold_current = handlers.config.current

        handlers.config.persistent = handlers.config.PersistentConfig(program='Test program name',
                                                                      program_version='Test program version')
        handlers.config.current = handlers.config.CurrentConfig(tk_root=DummyParent())
        try:
            yield handlers._select_tag_callback(self.tag)
        finally:
            handlers.config.persistent = hold_persistent
            handlers.config.current = hold_current
            dummy_edit_tag_gui_instance = []


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


dummy_edit_tag_gui_instance = []


# noinspection PyMissingOrEmptyDocstring
@dataclass
class DummyEditTagGUI:
    parent: DummyParent
    tag: str
    delete_tag_callback: Callable[[str], None]
    edit_tag_callback: Callable[[str], None]
    
    def __post_init__(self):
        dummy_edit_tag_gui_instance.append((self.parent, self.tag, self.delete_tag_callback,
                                            self.edit_tag_callback))


dummy_select_tag_gui_instance = []


# noinspection PyMissingOrEmptyDocstring
@dataclass
class DummySelectTagGUI:
    parent: DummyParent
    select_tag_callback: Callable[[str], None]
    tags_to_show: Sequence[str]
    
    def __post_init__(self):
        dummy_select_tag_gui_instance.append((self.parent, self.select_tag_callback, self.tags_to_show))


dummy_gui_messagebox_calls = []


# noinspection PyMissingOrEmptyDocstring
def dummy_gui_messagebox(*args, **kwargs):
    dummy_gui_messagebox_calls.append((args, kwargs))
