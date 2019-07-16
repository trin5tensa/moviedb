"""Functional pytests for database module. """
from typing import Dict

import pytest

import src.database as database


@pytest.fixture()
def connection():
    """Database access ."""
    database.init_database_access(filename=':memory:')


@pytest.fixture()
def session():
    """Provide a session scope."""
    # noinspection PyProtectedMember
    with database._session_scope() as session:
        yield session


@pytest.fixture(scope='module')
def hamlet() -> Dict:
    """Provide test data for 'Hamlet'."""
    return dict(title='Hamlet', director='Branagh', minutes=242, year=1996)


@pytest.fixture(scope='module')
def solaris() -> Dict:
    """Provide test data for 'Solaris'."""
    return dict(title='Solaris', director='Tarkovsky', minutes=169, year=1972)


@pytest.fixture(scope='module')
def dreams() -> Dict:
    """Provide test data for "Akira Kurosawa's Dreams"."""
    return dict(title="Akira Kurosawa's Dreams", director='Kurosawa', minutes=119, year=1972)


@pytest.fixture(scope='class')
def loaded_database(hamlet, solaris, dreams):
    """Provide a loaded database."""
    database.init_database_access(filename=':memory:')
    # noinspection PyProtectedMember
    movies = [database._Movie(**movie) for movie in (hamlet, solaris, dreams)]
    # noinspection PyProtectedMember,PyProtectedMember
    with database._session_scope() as session:
        session.add_all(movies)


def test_init_database_access_with_new_database(connection):
    """Create a new database and test that date_created is today."""
    with database._session_scope() as session:
        today = (session.query(database._MetaData.value)
                 .filter(database._MetaData.name == 'date_created')
                 .one())
    assert today.value[0:10] == str(database.datetime.datetime.today())[0:10]


def test_init_database_access_with_existing_database(tmpdir):
    """Attach to an existing database and check tha date_last_accessed is today."""
    path = tmpdir.mkdir('tmpdir').join(database.database_fn)
    database.init_database_access(filename=path)

    # Reattach to the same database
    database.init_database_access(filename=path)

    with database._session_scope() as session:
        today = (session.query(database._MetaData.value)
                 .filter(database._MetaData.name == 'date_last_accessed')
                 .one())
    assert today.value[0:10] == str(database.datetime.datetime.today())[0:10]


def test_add_movie(connection, session, hamlet):
    expected = tuple(hamlet.values())
    database.add_movie(hamlet)
    result = (session.query(database._Movie.title,
                            database._Movie.director,
                            database._Movie.minutes,
                            database._Movie.year, )
              .one())
    assert result == expected


def test_add_movies(connection, session, hamlet, solaris):
    expected = [tuple(hamlet.values()), tuple(solaris.values())]
    database.add_movies(iter((hamlet, solaris)))
    result = (session.query(database._Movie.title,
                            database._Movie.director,
                            database._Movie.minutes,
                            database._Movie.year, )
              .all())
    assert result == expected


@pytest.mark.usefixtures('loaded_database')
class TestsNeedingLoadedDatabase:
    def test_search_movie(self):
        expected = 'Hamlet'
        movies = database._search_movie(dict(year=[1996]))
        assert movies.one().title == expected

    def test_search_movie_with_substring(self):
        expected = 'Tarkovsky'
        movies = database._search_movie(dict(director='Tark'))
        assert movies.one().director == expected

    def test_search_movie_with_minute_range(self):
        expected = 169
        movies = database._search_movie(dict(minutes=[170, 160]))
        assert movies.one().minutes == expected

    def test_search_movie_with_minute_range_2(self):
        expected = 169
        movies = database._search_movie(dict(minutes=[169]))
        assert movies.one().minutes == expected

    def test_search_movie_with_minute_range_3(self):
        with pytest.raises(TypeError) as exception:
            database._search_movie(dict(minutes=169))
        assert exception.type is TypeError
        assert exception.value.args == ("'int' object is not iterable",)

    def test_value_error_is_raised(self):
        with pytest.raises(ValueError) as exception:
            database._search_movie(dict(months=[169]))
        assert exception.type is ValueError

    def test_search_movie_all(self):
        expected = [119, 169]
        movies = database.search_movie_all(dict(minutes=[170, 100]))
        run_times = [database._Movie.minutes for database._Movie in movies]
        assert run_times == expected
