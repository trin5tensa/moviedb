"""Functional pytests for database module. """
import pytest

import src.database as database


@pytest.fixture(scope='module')
def init_database_access():
    """Consolidate database access into a time saving single access for the whole module."""
    database.init_database_access(filename=':memory:')


def test_init_database_access_with_new_database(dbsession, init_database_access):
    """Create a new database and test that date_created is today."""
    # database.init_database_access(filename=':memory:')
    with database._session_scope() as dbsession:
        today = (dbsession.query(database._MetaData.value)
                 .filter(database._MetaData.name == 'date_created')
                 .one())
    assert today.value[0:10] == str(database.datetime.datetime.today())[0:10]


def test_init_database_access_with_existing_database(dbsession, tmpdir):
    """Attach to an existing database and check tha date_last_accessed is today."""
    path = tmpdir.mkdir('tmpdir').join(database.database_fn)
    database.init_database_access(filename=path)

    # Reattach to the same database
    database.init_database_access(filename=path)

    with database._session_scope() as dbsession:
        today = (dbsession.query(database._MetaData.value)
                 .filter(database._MetaData.name == 'date_last_accessed')
                 .one())
    assert today.value[0:10] == str(database.datetime.datetime.today())[0:10]
