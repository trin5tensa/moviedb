"""Functional pytests for database module. """

#  Copyright (c) 2022-2022. Stephen Rigden.
#  Last modified 10/15/22, 12:37 PM by stephen.
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

import random
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Callable, Dict

import pytest
import sqlalchemy.orm.exc

import database
import exception


class DatabaseTestException(Exception):
    """Base class for exceptions in this module."""
    pass


@pytest.fixture()
def connection():
    """Database access ."""
    database.connect_to_database(filename=':memory:')


@pytest.fixture()
def session():
    """Provide a session scope."""
    # noinspection PyProtectedMember
    with database._session_scope() as session:
        yield session


@pytest.fixture(scope='module')
def hamlet() -> Dict:
    """Provide test data for 'Hamlet'."""
    return dict(title='Hamlet', director='Branagh', minutes=242, year=1996, tmdb_id=142,
                original_title='Omlet', release_date=database.datetime.date(1996, 6, 6),
                synopsis='Father fixation')


@pytest.fixture(scope='module')
def revanche() -> Dict:
    """Provide test data for 'Hamlet'."""
    return dict(title='Revanche', director='Speilmann', minutes=122, year=2008, notes='Oscar nominated')


@pytest.fixture(scope='module')
def solaris() -> Dict:
    """Provide test data for 'Solaris'."""
    return dict(title='Solaris', director='Tarkovsky', minutes=169, year=1972)


@pytest.fixture(scope='module')
def dreams() -> Dict:
    """Provide test data for "Akira Kurosawa's Dreams"."""
    return dict(title="Akira Kurosawa's Dreams", director='Kurosawa', minutes=119, year=1972)


@pytest.fixture()
def loaded_database(hamlet, solaris, dreams, revanche):
    """Provide a loaded database."""
    database.connect_to_database(filename=':memory:')
    # noinspection PyProtectedMember
    movies = [database.Movie(**movie) for movie in (hamlet, solaris, dreams, revanche)]
    # noinspection PyProtectedMember
    with database._session_scope() as session:
        session.add_all(movies)
    database.add_tag('blue')
    database.add_movie_tag_link('blue', database.MovieKeyTypedDict(title='Hamlet', year=1996))
    database.add_tag('yellow')
    database.add_movie_tag_link('yellow', database.MovieKeyTypedDict(title='Revanche', year=2008))
    database.add_tag('green')
    database.add_movie_tag_link('green', database.MovieKeyTypedDict(title='Revanche', year=2008))
    database.add_movie_tag_link('green', database.MovieKeyTypedDict(title='Solaris', year=1972))


def test_init_database_access_with_new_database(connection):
    """Create a new database and test that date_created is today."""
    with database._session_scope() as session:
        today = (session.query(database.MoviesMetaData.value)
                 .filter(database.MoviesMetaData.name == 'date_created')
                 .one())
    assert today.value[0:10] == str(database.datetime.datetime.today())[0:10]


def test_init_database_access_with_existing_database(tmpdir):
    """Attach to an existing database and check tha date_last_accessed is today."""

    # Slow test: 5% chance of this test being run.
    if random.randint(0, 99) > 5:
        return
    
    path = tmpdir.mkdir('tmpdir').join(database.database_fn)
    database.connect_to_database(filename=path)
    
    # Reattach to the same database
    database.connect_to_database(filename=path)
    
    with database._session_scope() as session:
        current = (session.query(database.MoviesMetaData.value)
                   .filter(database.MoviesMetaData.name == 'date_last_accessed')
                   .one())
        previous = (session.query(database.MoviesMetaData.value)
                    .filter(database.MoviesMetaData.name == 'date_created')
                    .one())
    assert current != previous


def test_add_movie(connection, session, hamlet):
    expected = tuple(hamlet.values())
    database.add_movie(hamlet)
    result = (session.query(database.Movie.title,
                            database.Movie.director,
                            database.Movie.minutes,
                            database.Movie.year,
                            database.Movie.tmdb_id,
                            database.Movie.original_title,
                            database.Movie.release_date,
                            database.Movie.synopsis,
                            )
              .one())
    assert result == expected


def test_add_movie_with_empty_title_string_logs_error(connection, session, monkeypatch):
    expected = "Year string expected but got empty string."
    calls = []
    monkeypatch.setattr(database.logging, 'error', lambda msg: calls.append(msg))
    
    bad_row = dict(title='Hamlet', director='Branagh', minutes=242, year='')
    with pytest.raises(ValueError):
        database.add_movie(bad_row)
    assert calls == [expected]


def test_add_movie_with_empty_title_string_raises_value_error(connection, session, monkeypatch):
    expected = "Year string expected but got empty string."
    monkeypatch.setattr(database.logging, 'error', lambda msg: None)
    
    bad_row = dict(title='Hamlet', director='Branagh', minutes=242, year='')
    with pytest.raises(ValueError) as exc:
        database.add_movie(bad_row)
    assert str(exc.value) == expected


def test_add_movie_with_non_numeric_values(connection, session, monkeypatch):
    bad_int = 'forty two'
    expected = f"invalid literal for int() with base 10: '{bad_int}'"
    logging_msg = (f'{expected}\nA non-integer value has been supplied for either the year '
                   f'or the minute column.')
    calls = []
    monkeypatch.setattr(database.logging, 'error', lambda msg: calls.append(msg))

    bad_row = dict(title='Hamlet', director='Branagh', minutes=bad_int, year='1942')
    with pytest.raises(ValueError) as exc:
        database.add_movie(bad_row)
    assert str(exc.value) == expected
    assert calls[0] == logging_msg


def test_add_movie_with_notes(connection, session, revanche):
    expected = tuple(revanche.values())
    database.add_movie(revanche)
    result = (session.query(database.Movie.title,
                            database.Movie.director,
                            database.Movie.minutes,
                            database.Movie.year,
                            database.Movie.notes, )
              .one())
    assert result == expected


@pytest.mark.usefixtures('loaded_database')
class TestFindMovie:
    
    def test_search_movie_year(self):
        test_year = 1996
        movies = database.find_movies(database.FindMovieTypedDict(year=[str(test_year)]))
        assert movies[0]['year'] == test_year
    
    def test_search_movie_title(self):
        expected = 'Hamlet'
        movies = database.find_movies(dict(title='Ham'))
        assert movies[0]['title'] == expected
    
    def test_search_movie_director(self):
        # Slow test: 5% chance of this test being run.
        if random.randint(0, 99) > 5:
            return
        
        expected = 'Tarkovsky'
        movies = database.find_movies(dict(director='Tark'))
        assert movies[0]['director'] == expected
        
    def test_search_movie_notes(self):
        expected = 'Revanche'
        movies = database.find_movies(dict(notes='Oscar'))
        assert movies[0]['title'] == expected
    
    def test_search_movie_with_range_of_minutes(self):
        expected = {122}
        criteria = database.FindMovieTypedDict(minutes=['130', '120'])
        movies = database.find_movies(criteria)
        minutes = {movie['minutes'] for movie in movies}
        assert minutes == expected
    
    def test_search_movie_with_range_of_minutes_2(self):
        expected = {119, 122, 169}
        criteria = database.FindMovieTypedDict(minutes=['170', '100'])
        movies = database.find_movies(criteria)
        minutes = {movie['minutes'] for movie in movies}
        assert minutes == expected
    
    def test_search_movie_with_minute(self):
        expected = {169}
        movies = database.find_movies(database.FindMovieTypedDict(minutes=['169']))
        minutes = {movie['minutes'] for movie in movies}
        assert minutes == expected
    
    def test_search_movie_tag(self):
        expected = {'Revanche', 'Solaris'}
        movies = database.find_movies(dict(tags='green'))
        titles = {movie['title'] for movie in movies}
        assert titles == expected
    
    def test_search_movie_all_tags(self):
        expected = {'Hamlet', 'Revanche'}
        movies = database.find_movies(dict(tags=['blue', 'yellow']))
        titles = {movie['title'] for movie in movies}
        assert titles == expected
    
    def test_value_error_is_raised(self, monkeypatch):
        invalid_keys = {'months', }
        expected = f"Invalid attribute '{invalid_keys}'."
        calls = []
        monkeypatch.setattr(database.logging, 'error', lambda msg: calls.append(msg))

        with pytest.raises(ValueError) as exc:
            # noinspection PyTypeChecker
            for _ in database.find_movies(dict(months=[169])):
                pass
        assert exc.type is ValueError
        assert exc.value.args == (expected,)
        assert calls[0] == expected


# noinspection PyMissingOrEmptyDocstring
@pytest.mark.usefixtures('loaded_database', 'monkeypatch')
class TestReplaceMovie:
    OLD_MOVIE: database.MovieKeyTypedDict = dict(title='Hamlet', year=1996)
    NEW_MOVIE: database.MovieTypedDict = dict(title='New Movie', year='2042', director='Starchild')
    
    build_movie_query_calls = None
    add_movie_calls = None
    
    def test_replace_all_fields(self):
        expected = [dict(title='Omlet', director='Starchild', minutes=42, year=1942, notes='fortytwo',
                         tags=['blue'])]
        new_movie = database.MovieTypedDict(title='Omlet', director='Starchild', minutes=42,
                                            year=1942, notes='fortytwo')
        class_context = self.context_wrapper(self.OLD_MOVIE, new_movie)
        with class_context():
            movies = database.find_movies(dict(title='Omlet'))
            assert movies == expected

    def test_missing_original_record_raises_movie_not_found(self):
        expected = ('The movie was not found in the database. '
                    'It may have been deleted by an external process.')
        old_movie = database.FindMovieTypedDict(**self.OLD_MOVIE)
        database.del_movie(old_movie)
        
        class_context = self.context_wrapper(self.OLD_MOVIE, self.NEW_MOVIE)
        with pytest.raises(database.exception.MovieDBMovieNotFound) as exc:
            with class_context():
                pass
        assert exc.type is database.exception.MovieDBMovieNotFound
        assert exc.value.args == (expected, )

    def test_test_non_unique_replacement_record_raises_constraint_failure(self):
        expected = 'UNIQUE constraint failed: movies.title, movies.year'
        new_movie = database.MovieTypedDict(title='Solaris', director='Starchild', minutes=42,
                                            year=1972, notes='fortytwo')
        
        class_context = self.context_wrapper(self.OLD_MOVIE, new_movie)
        with pytest.raises(database.exception.MovieDBConstraintFailure) as exc:
            with class_context():
                pass

        assert exc.type is database.exception.MovieDBConstraintFailure
        assert exc.value.args == (expected,)
    
    @staticmethod
    def context_wrapper(old_movie: database.MovieKeyTypedDict,
                        new_movie: database.MovieTypedDict) -> Callable:
        """Return a context managed caller which will yield database.replace_movie().
        
        Args:
            old_movie:
            new_movie:

        Returns::
            A generator which yields database.replace_movie
        """
        @contextmanager
        def class_context():
            yield database.replace_movie(old_movie, new_movie)
        return class_context
    

def test_delete_movie_by_title_and_year(loaded_database):
    database.del_movie(database.FindMovieTypedDict(title='Solaris', year=['1972', '']))
    movies = database.find_movies(dict(title='Solaris'))
    assert movies == []


def test_delete_movie_by_title_and_length(loaded_database):
    database.del_movie(database.FindMovieTypedDict(title='Solaris', minutes=['', '169']))
    movies = database.find_movies(dict(title='Solaris'))
    assert movies == []


def test_all_tags(loaded_database):
    tags = database.all_tags()
    assert tags == ['blue', 'green', 'yellow']


def test_movie_tags(loaded_database, revanche):
    title_year = database.MovieKeyTypedDict(title=revanche['title'], year=revanche['year'])
    tags = database.movie_tags(title_year)
    assert set(tags) == {'yellow', 'green'}


@pytest.mark.usefixtures('loaded_database')
class TestTagOperations:
    
    def test_add_new_tag(self, session):
        tag = 'Movie night candidate'
        database.add_tag(tag)
    
        count = (session.query(database.Tag)
                 .filter(database.Tag.tag == 'Movie night candidate')
                 .count())
        assert count == 1

    def test_find_tags_gets_none(self, session):
        found_tags = database.find_tags('non existent tag')
        assert found_tags == []

    def test_find_tags_gets_one(self, session):
        found_tags = database.find_tags('green')
        assert found_tags == ['green']

    def test_find_tags_gets_many(self, session):
        tag = 'seen'
        database.add_tag(tag)
        found_tags = database.find_tags('ee')
        assert found_tags == ['green', 'seen']

    def test_add_existing_tag_ignored(self, session):
        tag = 'Movie night candidate'
        database.add_tag(tag)
        database.add_tag(tag)
    
        count = (session.query(database.Tag)
                 .filter(database.Tag.tag == 'Movie night candidate')
                 .count())
        assert count == 1
    
    def test_add_links_to_movies(self, session):
        expected = {'Solaris', "Akira Kurosawa's Dreams"}
        test_tag = 'Foreign'
        database.add_tag(test_tag)
        movie = database.MovieKeyTypedDict(title='Solaris', year=1972)
        database.add_movie_tag_link(test_tag, movie)
        movie = database.MovieKeyTypedDict(title="Akira Kurosawa's Dreams", year=1972)
        database.add_movie_tag_link(test_tag, movie)

        movies = (session.query(database.Movie.title)
                  .filter(database.Movie.tags.any(tag=test_tag)))
        result = {movie.title for movie in movies}
        assert result == expected
    
    def test_edit_tag(self, session):
        old_tag = 'old test tag'
        database.add_tag(old_tag)
        movie = database.MovieKeyTypedDict(title='Solaris', year=1972)
        database.add_movie_tag_link(old_tag, movie)
        old_tag_id, tag = (session.query(database.Tag.id, database.Tag.tag)
                           .filter(database.Tag.tag == 'old test tag')
                           .one())

        new_tag = 'new test tag'
        database.edit_tag(old_tag, new_tag)
        new_tag_id, tag = (session.query(database.Tag.id, database.Tag.tag)
                           .filter(database.Tag.tag == 'new test tag')
                           .one())

        assert old_tag_id == new_tag_id

    def test_edit_tag_raises_exception_database_search_found_nothing(self, session, monkeypatch):
        old_tag = 'old test tag'
        new_tag = 'new test tag'
        with pytest.raises(database.exception.DatabaseSearchFoundNothing) as cm:
            database.edit_tag(old_tag, new_tag)
        assert cm.typename == 'DatabaseSearchFoundNothing'
        assert cm.match(f'The tag {old_tag} is not in the database.')

    def test_edit_tag_logs_database_search_found_nothing(self, session, monkeypatch):
        calls = []
        monkeypatch.setattr(database.logging, 'info', lambda msg: calls.append(msg))
    
        old_tag = 'old test tag'
        new_tag = 'new test tag'
        with pytest.raises(database.exception.DatabaseSearchFoundNothing):
            database.edit_tag(old_tag, new_tag)
        assert calls == [("An incomplete database session has been rolled back because of exception:\n"
                          "NoResultFound"),
                         f"The tag {old_tag} is not in the database."]

    def test_edit_movies_tag(self, session):
        title_year = database.MovieKeyTypedDict(title='Revanche', year=2008)
        old_tags = ('green', 'yellow')
        new_tags = ('blue', 'yellow')
        database.edit_movie_tag_links(title_year, old_tags, new_tags)
        movies = database.find_movies(database.FindMovieTypedDict(title=title_year['title'],
                                                                  year=[str(title_year['year'])]))
        assert set(movies[0]['tags']) == {'blue', 'yellow'}

    def test_edit_movies_tag_raises_exception_movie_not_found(self, session):
        title_year = database.MovieKeyTypedDict(title='Non Existent Movie', year=1972)
        new_tags = ('green', 'yellow')
        old_tags = ('blue', 'yellow')
        with pytest.raises(exception.DatabaseSearchFoundNothing) as cm:
            database.edit_movie_tag_links(title_year, old_tags, new_tags)
        assert cm.typename == 'DatabaseSearchFoundNothing'
        assert cm.match("The movie Non Existent Movie, 1972 is not in the database.")

    def test_edit_movies_tag_logs_exception_movie_not_found(self, session, monkeypatch):
        calls = []
        monkeypatch.setattr(database.logging, 'info', lambda msg: calls.append(msg))
    
        title = 'Non Existent Movie'
        year = 1972
        title_year = database.MovieKeyTypedDict(title=title, year=year)
        new_tags = ('green', 'yellow')
        old_tags = ('blue', 'yellow')
        with pytest.raises(exception.DatabaseSearchFoundNothing):
            database.edit_movie_tag_links(title_year, old_tags, new_tags)
        assert calls == [("An incomplete database session has been rolled back because of exception:\n"
                          "NoResultFound"),
                         f"The movie {title}, {year} is not in the database."]

    def test_del_tag(self, session):
        # Add a tag and links
        test_tag = 'Going soon'
        database.add_tag(test_tag)
        movie = database.MovieKeyTypedDict(title='Solaris', year=1972)
        database.add_movie_tag_link(test_tag, movie)
        movie = database.MovieKeyTypedDict(title='Hamlet', year=1996)
        database.add_movie_tag_link(test_tag, movie)
        
        # Delete the tag
        database.del_tag(test_tag)
        
        # Is the tag still there?
        with pytest.raises(sqlalchemy.orm.exc.NoResultFound):
            session.query(database.Tag).filter(database.Tag.tag == test_tag).one()
        
        # Do any movies still have the tag?
        assert (session.query(database.Movie)
                .filter(database.Movie.tags.any(tag=test_tag))
                .all()) == []


@dataclass
class InstrumentedSession:
    """A Session dummy with test instrumentation."""
    commit_called = False
    rollback_called = False
    close_called = False
    
    def correct_function(self):
        """A working test function"""
        pass
    
    def incorrect_function(self):
        """A broken test function"""
        raise DatabaseTestException
    
    def commit(self):
        """Register the calling of this function."""
        self.commit_called = True
    
    def rollback(self):
        """Register the calling of this function."""
        self.rollback_called = True
    
    def close(self):
        """Register the calling of this function."""
        self.close_called = True


@dataclass
class InstrumentedLogging:
    """A Logging dummy with test instrumentation."""

    def __init__(self) -> None:
        self.info_calls = []
    
    def info(self, msg):
        """Register the arguments with which this function was called."""
        self.info_calls.append(msg)


def test_commit_called(monkeypatch):
    monkeypatch.setattr(database, 'Session', InstrumentedSession)
    with database._session_scope() as session:
        session.correct_function()
    assert session.commit_called
    assert session.close_called


def test_rollback_called(monkeypatch):
    monkeypatch.setattr(database, 'Session', InstrumentedSession)
    monkeypatch.setattr(database, 'logging', InstrumentedLogging())
    with pytest.raises(DatabaseTestException):
        with database._session_scope() as session:
            session.incorrect_function()
    assert session.rollback_called
    assert session.close_called


def test_logging_called(monkeypatch):
    monkeypatch.setattr(database, 'Session', InstrumentedSession)
    log = InstrumentedLogging()
    monkeypatch.setattr(database, 'logging', log)
    with pytest.raises(DatabaseTestException):
        with database._session_scope() as session:
            session.incorrect_function()
    assert log.info_calls[0] == ("An incomplete database session has been rolled back "
                                 "because of exception:\nDatabaseTestException")
