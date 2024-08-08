"""Test module."""

#  Copyright© 2024. Stephen Rigden.
#  Last modified 8/8/24, 9:17 AM by stephen.
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

import pytest
from pytest_check import check

from sqlalchemy import create_engine, Engine
from sqlalchemy.exc import NoResultFound

from database_src import schema, tables
from database_src.tables import sessionmaker
from globalconstants import *

TEST_DIRECTORS = {"Donald Director"}
TEST_STARS = {"Edgar Ethelred", "Fanny Fullworthy"}
MATCH = "two"
THIRD = "three"
PREFIX = "test tag "
SOUGHT_TAG = PREFIX + MATCH
THIRD_TAG = PREFIX + THIRD
TAG_TEXTS = {
    PREFIX + "one",
    SOUGHT_TAG,
    THIRD_TAG,
}
MOVIEBAG_1 = MovieBag(
    title="First Movie",
    year=MovieInteger("4241"),
    notes="I am MOVIEBAG_1",
)
MOVIEBAG_2 = MovieBag(
    title="Transformer",
    year=MovieInteger("4242"),
    duration=MovieInteger(142),
    directors=TEST_DIRECTORS,
    stars=TEST_STARS,
    synopsis="Synopsis for test",
    notes="I am MOVIEBAG_2",
    movie_tags=TAG_TEXTS,
)
MOVIEBAG_3 = MovieBag(
    title="Third Movie",
    year=MovieInteger("4243"),
    duration=MovieInteger(242),
    notes="I am MOVIEBAG_3",
)
MOVIEBAG_4 = MovieBag(
    title="Fourth Movie",
    year=MovieInteger("4244"),
    notes="I am MOVIEBAG_4",
    stars=TEST_STARS,
)


def test_select_movie(test_database):
    movie_bag = MovieBag(
        title=MOVIEBAG_2["title"],
        year=MOVIEBAG_2["year"],
    )

    movie = tables.select_movie(movie_bag=movie_bag)

    check.equal(movie["id"], 2)
    check.is_instance(movie["created"], schema.datetime)
    check.is_instance(movie["updated"], schema.datetime)
    check.equal(movie["notes"], MOVIEBAG_2["notes"])
    check.equal(movie["title"], MOVIEBAG_2["title"])
    check.equal(int(movie["year"]), int(MOVIEBAG_2["year"]))
    check.equal(int(movie["duration"]), int(MOVIEBAG_2["duration"]))
    check.equal(movie["synopsis"], MOVIEBAG_2["synopsis"])
    check.equal(movie["stars"], MOVIEBAG_2["stars"])
    check.equal(movie["directors"], MOVIEBAG_2["directors"])
    check.equal(movie["movie_tags"], MOVIEBAG_2["movie_tags"])


def test_select_all_movies(test_database):
    movie_bags = tables.select_all_movies()

    check.equal(len(movie_bags), 4, msg="There are four movies in the test database.")
    for movie in movie_bags:
        check.between_equal(
            movie["id"],
            1,
            4,
            msg="There are four movies in the test database which should "
            "have sequential ids.",
        )
        check.equal(movie["id"], int(movie["notes"][-1:]))


def test_match_movies(test_database):
    star_substring = "full"
    year_pattern = MovieInteger("4242-4244")

    movie_bags = tables.match_movies(
        MovieBag(stars={star_substring}, year=year_pattern)
    )

    check.equal(
        len(movie_bags), 2, msg="There are just two movies starring " "Fanny Fullworthy"
    )
    for movie in movie_bags:
        check.is_in(
            "Fanny Fullworthy",
            movie["stars"],
            msg="'Fanny Fullworthy' is missing from the found movie.",
        )


def test_add_movie(test_database):
    # Arrange
    extra_star = "Gerald Golightly"
    extra_director = "Howard Hologram"
    movie_bag = MovieBag(
        title="Test Add Movie",
        year=MovieInteger(5042),
        duration=MovieInteger(159),
        synopsis="Test synopsis",
        notes="Test notes",
        movie_tags=TAG_TEXTS,
        directors=TEST_DIRECTORS | {extra_director},
        stars=TEST_STARS | {extra_star},
    )
    print()
    print("test_database tags: ", tables.select_all_tags())
    print(movie_bag)

    # Act
    # Call movie = add_movie(movie_bag=movie_bag)
    # Assert
    # todo (movie) Check eight non-relationship fields
    # todo (tags) Check tags field matches tables._select_all_tags
    # todo (people) Check extra star and director added to person table
    # todo (people) Check Movie.stars matches TEST_STARS and extra_star
    # todo (people) Check Movie.directors matches TEST_STARS and extra_director

    # Cleanup
    assert False


def test_add_movie_with_integrity_error(test_database):
    # Log and reraise IntegrityError for key mismatch.
    pass


def test_add_movie_with_constraint_failure_error(test_database):
    # Log and reraise ConstraintFailure for year outside valid range.
    pass


def test_add_movie_with_invalid_tag(test_database):
    #   Log and reraise sqlalchemy.exc.NoResultFound
    pass


def test_edit_movie(test_database):
    # todo movie
    #   Use _edit_movie
    # todo tags
    #   Use _match_tag to get Tag objects raising tables.TagNotFound exception if any not
    #   found. (new function)
    #   Add new tags to Movie.tags and delete links to old tags.
    # todo people
    #   Add Movie.stars and Movie.directors to set of orphan candidates
    #   Get people records for new stars and directors creating new if not found.
    #   Replace Movie.stars with new
    #   Replace Movie.directors with new
    #   Call _delete_orphans

    # Arrange
    # Act
    # Assert
    # Cleanup
    pass


def test_delete_movie(test_database):
    # todo
    #  Call _delete_orphans for Movie.stars and Movie.directors
    #  Use _delete_movie which automatically updates all links

    # Arrange
    # Act
    # Assert
    # Cleanup
    pass


def test_select_all_tags(test_database):
    tag_texts = tables.select_all_tags()
    assert tag_texts == TAG_TEXTS


def test_add_tag_text(test_database):
    new_tag = "test new tag"

    tables.add_tag(tag_text=new_tag)

    tags = tables.select_all_tags()
    assert tags & {new_tag} == {new_tag}


def test_add_duplicate_tag_text_logs_and_raises_exception(test_database, logged):
    new_tag = "test new tag"
    tables.add_tag(tag_text=new_tag)

    with check:
        with pytest.raises(
            tables.IntegrityError,
            match="UNIQUE constraint failed: tag.text",
        ):
            tables.add_tag(tag_text=new_tag)

    check.equal(
        logged,
        [(("(sqlite3.IntegrityError) UNIQUE constraint failed: tag.text",), {})],
        msg="IntegrityError was not logged.",
    )


def test_add_tag_texts(test_database, logged):
    new_tag = "test new tag"
    tables.add_tags(tag_texts={new_tag})

    with check:
        with pytest.raises(
            tables.IntegrityError,
            match="UNIQUE constraint failed: tag.text",
        ):
            tables.add_tags(tag_texts={new_tag})

    check.equal(
        logged,
        [(("(sqlite3.IntegrityError) UNIQUE constraint failed: tag.text",), {})],
        msg="IntegrityError was not logged.",
    )


def test_edit_tag_text(test_database):
    old_tag_text = SOUGHT_TAG
    new_tag_text = "test new tag"

    tables.edit_tag(old_tag_text=old_tag_text, new_tag_text=new_tag_text)

    tags_remaining = tables.select_all_tags()
    check.equal(tags_remaining & {SOUGHT_TAG}, set())
    check.equal(tags_remaining & {new_tag_text}, {new_tag_text})


def test_edit_missing_tag_text_logs_and_raises_exception(test_database, logged):
    tag_text = "garbage"

    with check:
        with pytest.raises(tables.NoResultFound):
            tables.edit_tag(old_tag_text=tag_text, new_tag_text=tag_text)

    check.equal(
        logged,
        [(("No row was found when one was required",), {})],
        msg="NoResultFound was not logged.",
    )


def test_edit_duplicate_tag_text_logs_and_raises_exception(test_database, logged):
    old_tag_text = SOUGHT_TAG
    # Already present in another Tag object.
    new_tag_text = THIRD_TAG

    with check:
        with pytest.raises(
            tables.IntegrityError,
            match="UNIQUE constraint failed: tag.text",
        ):
            tables.edit_tag(old_tag_text=old_tag_text, new_tag_text=new_tag_text)
            pass

    check.equal(
        logged,
        [(("(sqlite3.IntegrityError) UNIQUE constraint failed: tag.text",), {})],
        msg="IntegrityError was not logged.",
    )


def test_delete_tag(test_database):
    tables.delete_tag(tag_text=SOUGHT_TAG)

    tags_remaining = tables.select_all_tags()
    assert tags_remaining & set(SOUGHT_TAG) == set()


def test_delete_missing_tag_suppresses_exception(test_database):
    tables.delete_tag(tag_text=SOUGHT_TAG)
    tables.delete_tag(tag_text=SOUGHT_TAG)


@pytest.fixture(scope="function")
def session_engine():
    """Yields an engine."""
    engine: Engine = create_engine("sqlite+pysqlite:///:memory:")
    schema.Base.metadata.create_all(engine)
    tables.session_factory = sessionmaker(engine)
    yield
    engine.dispose()


@pytest.fixture(scope="function")
def test_database(session_engine):
    with tables.session_factory() as session:
        session.add_all([schema.Tag(text=text) for text in TAG_TEXTS])

        for movie_bag in [MOVIEBAG_1, MOVIEBAG_2, MOVIEBAG_3, MOVIEBAG_4]:
            duration = movie_bag.get("duration")

            names = movie_bag.get("directors", set())
            directors = set()
            for director in names:
                # noinspection PyTypeChecker
                statement = tables.select(schema.Person).where(
                    schema.Person.name == director
                )
                try:
                    person = session.scalars(statement).one()
                except NoResultFound:
                    person = schema.Person(name=director)
                    session.add(person)
                directors.add(person)

            names = movie_bag.get("stars", set())
            stars = set()
            for star in names:
                # noinspection PyTypeChecker
                statement = tables.select(schema.Person).where(
                    schema.Person.name == star
                )
                try:
                    person = session.scalars(statement).one()
                except NoResultFound:
                    person = schema.Person(name=star)
                    session.add(person)
                stars.add(person)

            tag_texts = movie_bag.get("movie_tags", set())
            statement = tables.select(schema.Tag).where(schema.Tag.text.in_(tag_texts))
            tags = set(session.scalars(statement).all())

            movie = schema.Movie(
                title=movie_bag["title"],
                year=int(movie_bag["year"]),
                duration=int(duration) if duration else None,
                directors=directors,
                stars=stars,
                synopsis=movie_bag.get("synopsis"),
                notes=movie_bag.get("notes"),
                tags=tags,
            )
            session.add(movie)

        session.commit()


@pytest.fixture(scope="function")
def logged(monkeypatch):
    """Logs arguments of calls to logging.error."""
    calls = []
    monkeypatch.setattr(
        tables.logging,
        "error",
        lambda *args, **kwargs: calls.append((args, kwargs)),
    )
    return calls
