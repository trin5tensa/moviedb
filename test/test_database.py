"""Functional pytests for database module. """
from typing import Dict

import pytest
import sqlalchemy.orm.exc

import src.database as database


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
    return dict(title='Hamlet', director='Branagh', minutes=242, year=1996)


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


@pytest.fixture(scope='class')
def loaded_database(hamlet, solaris, dreams, revanche):
    """Provide a loaded database."""
    database.connect_to_database(filename=':memory:')
    # noinspection PyProtectedMember
    movies = [database._Movie(**movie) for movie in (hamlet, solaris, dreams, revanche)]
    # noinspection PyProtectedMember,PyProtectedMember
    with database._session_scope() as session:
        session.add_all(movies)


def test_session_rollback(connection):
    with pytest.raises(ZeroDivisionError):
        with database._session_scope() as session:
            database._build_movie_query(session, dict(minutes=[169]))
            # noinspection PyStatementEffect
            42 / 0


def test_init_database_access_with_new_database(connection):
    """Create a new database and test that date_created is today."""
    with database._session_scope() as session:
        today = (session.query(database._MoviesMetaData.value)
                 .filter(database._MoviesMetaData.name == 'date_created')
                 .one())
    assert today.value[0:10] == str(database.datetime.datetime.today())[0:10]


def test_init_database_access_with_existing_database(tmpdir):
    """Attach to an existing database and check tha date_last_accessed is today."""
    path = tmpdir.mkdir('tmpdir').join(database.database_fn)
    database.connect_to_database(filename=path)

    # Reattach to the same database
    database.connect_to_database(filename=path)

    with database._session_scope() as session:
        current = (session.query(database._MoviesMetaData.value)
                   .filter(database._MoviesMetaData.name == 'date_last_accessed')
                   .one())
        previous = (session.query(database._MoviesMetaData.value)
                    .filter(database._MoviesMetaData.name == 'date_created')
                    .one())
    assert current != previous


def test_add_movie(connection, session, hamlet):
    expected = tuple(hamlet.values())
    database.add_movie(hamlet)
    result = (session.query(database._Movie.title,
                            database._Movie.director,
                            database._Movie.minutes,
                            database._Movie.year, )
              .one())
    assert result == expected


def test_add_movie_with_notes(connection, session, revanche):
    expected = tuple(revanche.values())
    database.add_movie(revanche)
    result = (session.query(database._Movie.title,
                            database._Movie.director,
                            database._Movie.minutes,
                            database._Movie.year,
                            database._Movie.notes, )
              .one())
    assert result == expected


@pytest.mark.usefixtures('loaded_database')
class TestQueryMovie:
    def test_search_movie_year(self):
        expected = ['Hamlet']
        title = [movie.title for movie in database._search_movies(dict(year=[1996]))]
        assert title == expected

    def test_search_movie_id(self):
        expected = ['Hamlet']
        title = [movie.title for movie in database._search_movies(dict(id=1))]
        assert title == expected

    def test_search_movie_title(self):
        expected = ['Hamlet']
        title = [movie.title for movie in database._search_movies(dict(title='Ham'))]
        assert title == expected

    def test_search_movie_director(self):
        expected = ['Tarkovsky']
        director = [movie.director for movie in database._search_movies(dict(director='Tark'))]
        assert director == expected

    def test_search_movie_notes(self):
        expected = ['Revanche']
        title = [movie.title for movie in database._search_movies(dict(notes='Oscar'))]
        assert title == expected

    def test_search_movie_with_range_of_minutes(self):
        expected = [169]
        minutes = [movie.minutes for movie in database._search_movies(dict(minutes=[170, 160]))]
        assert minutes == expected

    def test_search_movie_with_range_of_minutes_2(self):
        expected = [119, 122, 169]
        run_times = [movie.minutes for movie in database._search_movies(dict(minutes=[170, 100]))]
        assert sorted(run_times) == expected

    def test_search_movie_with_minute(self):
        expected = [169]
        minutes = [movie.minutes for movie in database._search_movies(dict(minutes=[169]))]
        assert minutes == expected

    def test_value_error_is_raised(self):
        valid_set = {'id', 'title', 'director', 'minutes', 'year', 'notes'}
        expected = f"Key(s) '{{'months'}}' not in valid set '{valid_set}'.",
        with pytest.raises(ValueError) as exception:
            for _ in database._search_movies(dict(months=[169])):
                pass
        assert exception.type is ValueError
        assert exception.value.args == expected


@pytest.mark.usefixtures('loaded_database')
class TestEditMovie:
    def test_edit_movie(self):
        new_note = 'Science Fiction'
        database.edit_movie(dict(title='Solaris'), dict(notes=new_note))

        for movie in database._search_movies(dict(title='Solaris')):
            assert movie.notes == new_note


@pytest.mark.usefixtures('loaded_database')
class TestDeleteMovie:
    def test_delete_movie(self):
        database.del_movie(dict(title='Solaris'))
        movies = [movie for movie in database._search_movies(dict(title='Solaris'))]
        assert not movies


@pytest.mark.usefixtures('loaded_database')
class TestTagOperations:
    def test_add_new_tag(self, session):
        tag = 'Movie night candidate'
        database.add_tag_and_links(tag)

        count = (session.query(database._Tag)
                 .filter(database._Tag.tag == 'Movie night candidate')
                 .count())
        assert count == 1

    def test_add_existing_tag_ignored(self, session):
        tag = 'Movie night candidate'
        database.add_tag_and_links(tag)
        database.add_tag_and_links(tag)

        count = (session.query(database._Tag)
                 .filter(database._Tag.tag == 'Movie night candidate')
                 .count())
        assert count == 1

    def test_add_links_to_movies(self, session):
        expected = {'Solaris', "Akira Kurosawa's Dreams"}
        test_tag = 'Foreign'
        movies = [('Solaris', 1972), ("Akira Kurosawa's Dreams", 1972)]
        database.add_tag_and_links(test_tag, movies)

        movies = (session.query(database._Movie.title)
                  .filter(database._Movie.tags.any(tag=test_tag)))
        result = {movie.title for movie in movies}
        assert result == expected

    def test_edit_tag(self, session):
        old_tag = 'old test tag'
        movies = [('Solaris', 1972)]
        database.add_tag_and_links(old_tag, movies)
        old_tag_id, tag = (session.query(database._Tag.id, database._Tag.tag)
                           .filter(database._Tag.tag == 'old test tag')
                           .one())

        new_tag = 'new test tag'
        database.edit_tag(old_tag, new_tag)
        new_tag_id, tag = (session.query(database._Tag.id, database._Tag.tag)
                           .filter(database._Tag.tag == 'new test tag')
                           .one())

        assert old_tag_id == new_tag_id

    def test_del_tag(self, session):
        # Add a tag and links
        test_tag = 'Going soon'
        movies = [('Solaris', 1972), ('Hamlet', 1996)]
        database.add_tag_and_links(test_tag, movies)

        # Delete the tag
        database.del_tag(test_tag)

        # Is the tag still there?
        with pytest.raises(sqlalchemy.orm.exc.NoResultFound):
            session.query(database._Tag).filter(database._Tag.tag == test_tag).one()

        # Do any movies still have the tag?
        assert (session.query(database._Movie)
                .filter(database._Movie.tags.any(tag=test_tag))
                .all()) == []
