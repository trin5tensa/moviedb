"""Functional pytests for database module. """
import src.database as database

def test_init_database_access_with_new_database(dbsession):
    """Create a new database and test that date_created is today."""
    database.init_database_access(database_fn=':memory:')
    with database._session_scope() as dbsession:
        today = (dbsession.query(database._MetaData.value)
                 .filter(database._MetaData.name == 'date_created')
                 .one())
    assert today.value[0:10] == str(database.datetime.datetime.today())[0:10]

def test_init_database_access_with_existing_database(dbsession):
    """Attach to an existing database and check tha date_last_accessed is today."""
    database.init_database_access(database_fn=':memory:')
    # Reattach to the same database
    database.init_database_access(database_fn=':memory:')

    with database._session_scope() as dbsession:
        today = (dbsession.query(database._MetaData.value)
                 .filter(database._MetaData.name == 'date_last_accessed')
                 .one())
    assert today.value[0:10] == str(database.datetime.datetime.today())[0:10]

# DayBreak
#  Move access call to module scoped fixture. NB Current timings 21-27 ms
#  coverage, todo's
