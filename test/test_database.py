"""Functional pytests for database module. """
from typing import Dict

import pytest

import src.database as database

@pytest.fixture(scope='function')
def connection():
    """Database access ."""
    database.init_database_access(filename=':memory:')


@pytest.fixture(scope='function')
def session():
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
                            database._Movie.year,)
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


def test_search(connection, session, hamlet):
    expected = 'Hamlet'
    database.add_movie(hamlet)
    movie = database.search(dict(title='Hamlet'))
    assert movie.title == expected


def test_search_for_substring(connection, session, solaris):
    expected = 'Tarkovsky'
    database.add_movie(solaris)
    movie = database.search(dict(director='Tark'))
    assert movie.director == expected


def test_edit_movies(connection, session, hamlet):
    expected = 2000
    database.add_movie(hamlet)
    movie = database.search(dict(title='Hamlet'))
    movie.edit(dict(year=2000))
    result = (session.query(database._Movie.year)
              .one())
    assert result == expected