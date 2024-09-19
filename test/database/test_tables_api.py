"""Test module."""

#  Copyright© 2024. Stephen Rigden.
#  Last modified 8/29/24, 8:27 AM by stephen.
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

    # Act
    tables.add_movie(movie_bag=movie_bag)

    # Assert
    with tables.session_factory() as session:
        movie = tables._select_movie(session, movie_bag=movie_bag)

        # Check eight non-relationship fields
        check.is_instance(movie.id, int)
        check.is_instance(movie.created, schema.datetime)
        check.is_instance(movie.updated, schema.datetime)
        check.equal(movie.title, movie_bag["title"])
        check.equal(movie.year, int(movie_bag["year"]))
        check.equal(movie.duration, int(movie_bag["duration"]))
        check.equal(movie.synopsis, movie_bag["synopsis"])
        check.equal(movie.notes, movie_bag["notes"])

        # Check relationship fields
        check.equal({tag.text for tag in movie.tags}, movie_bag["movie_tags"])
        check.equal({person.name for person in movie.directors}, movie_bag["directors"])
        check.equal({person.name for person in movie.stars}, movie_bag["stars"])

        # Check new people added to people table
        people = tables._select_people(session, names={extra_star, extra_director})
        check.equal(
            len(people),
            2,
            msg=f"Expected two names in person table: {extra_star}, {extra_director}",
        )


def test_add_movie_with_invalid_tag(test_database, log_error):
    movie_bag = MovieBag(
        title="Test Add Movie",
        year=MovieInteger(5042),
        movie_tags={"garbage"},
    )

    with check:
        with pytest.raises(
            tables.TagNotFound,
            match="garbage",
        ):
            tables.add_movie(movie_bag=movie_bag)
    check.equal(
        log_error,
        [(("No row was found when one was required", "Bad tag: {'garbage'}"), {})],
        msg="TagNotFound was not logged.",
    )


def test_add_movie_with_title_year_duplication_error(test_database, log_error):
    with check:
        with pytest.raises(
            tables.MovieExists,
            match="UNIQUE constraint failed: movie.title, movie.year",
        ):
            tables.add_movie(movie_bag=MOVIEBAG_1)
    check.equal(
        log_error,
        [
            (
                (
                    "UNIQUE constraint failed: movie.title, movie.year",
                    "Duplicate title and year: movie.title='First Movie', "
                    "movie.year=4241.",
                ),
                {},
            )
        ],
    )


def test_add_movie_with_too_early_year(test_database, log_error):
    movie_bag = MovieBag(
        title="Test Add Movie",
        year=MovieInteger(0),
    )

    with check:
        with pytest.raises(
            tables.InvalidReleaseYear,
            match="CHECK constraint failed: year>1878",
        ):
            tables.add_movie(movie_bag=movie_bag)
    check.equal(
        log_error,
        [
            (
                (
                    "CHECK constraint failed: year>1878",
                    ("(sqlite3.IntegrityError) CHECK constraint failed: year>1878",),
                ),
                {},
            )
        ],
    )


def test_add_movie_with_too_late_year(test_database, log_error):
    movie_bag = MovieBag(
        title="Test Add Movie",
        year=MovieInteger(424242),
    )

    with check:
        with pytest.raises(
            tables.InvalidReleaseYear,
            match="CHECK constraint failed: year<=10000",
        ):
            tables.add_movie(movie_bag=movie_bag)
    check.equal(
        log_error,
        [
            (
                (
                    "CHECK constraint failed: year<=10000",
                    ("(sqlite3.IntegrityError) CHECK constraint failed: year<=10000",),
                ),
                {},
            )
        ],
    )


def test_edit_movie(test_database):
    old_movie_bag = MovieBag(
        title="Test Edit Movie",
        year=MovieInteger(5042),
        duration=MovieInteger(159),
        synopsis="Test synopsis",
        notes="Test notes",
        movie_tags=TAG_TEXTS,
        directors={"Yolanda Ypsilanti"},
        stars={"O Star 10", "O Star 11"},
    )
    tables.add_movie(movie_bag=old_movie_bag)
    new_movie_bag = MovieBag(
        title="Son of Test Edit Movie",
        year=MovieInteger(6042),
        duration=MovieInteger(242),
        synopsis="Test synopsis sequel",
        notes="Test notes sequel",
        movie_tags={SOUGHT_TAG},
        directors={"Zach Zimmermann"},
        stars={"O Star 10", "N Star 20"},
    )

    tables.edit_movie(old_movie_bag=old_movie_bag, new_movie_bag=new_movie_bag)

    with tables.session_factory() as session:
        movie = tables._select_movie(session, movie_bag=new_movie_bag)

        # Check eight non-relationship fields
        check.is_instance(movie.id, int)
        check.is_instance(movie.created, schema.datetime)
        check.is_instance(movie.updated, schema.datetime)
        check.equal(movie.title, new_movie_bag["title"])
        check.equal(movie.year, int(new_movie_bag["year"]))
        check.equal(movie.duration, int(new_movie_bag["duration"]))
        check.equal(movie.synopsis, new_movie_bag["synopsis"])
        check.equal(movie.notes, new_movie_bag["notes"])

        # Check relationship fields
        check.equal({tag.text for tag in movie.tags}, new_movie_bag["movie_tags"])
        check.equal(
            {person.name for person in movie.directors}, new_movie_bag["directors"]
        )
        check.equal({person.name for person in movie.stars}, new_movie_bag["stars"])

        # Check new people added to people table
        people = tables._select_people(
            session,
            names=old_movie_bag["directors"]
            | old_movie_bag["stars"]
            | new_movie_bag["directors"]
            | new_movie_bag["stars"],
        )
        check.equal(
            {person.name for person in people},
            new_movie_bag["directors"] | new_movie_bag["stars"],
            msg=f"Either new people not added to person table or orphans not removed.",
        )


def test_edit_movie_with_invalid_tag(test_database, log_error):
    old_movie_bag = MovieBag(
        title="Test Edit Movie",
        year=MovieInteger(5042),
    )
    tables.add_movie(movie_bag=old_movie_bag)
    new_movie_bag = MovieBag(
        movie_tags={"garbage"},
    )

    with check:
        with pytest.raises(
            tables.TagNotFound,
            match="garbage",
        ):
            tables.edit_movie(
                old_movie_bag=old_movie_bag,
                new_movie_bag=new_movie_bag,
            )
    check.equal(
        log_error,
        [(("No row was found when one was required", "Bad tag: {'garbage'}"), {})],
        msg="TagNotFound was not logged.",
    )


def test_edit_movie_with_title_year_duplication_error(test_database, log_error):
    old_movie_bag = MovieBag(
        title="Test Edit Movie",
        year=MovieInteger(5042),
    )
    tables.add_movie(movie_bag=old_movie_bag)

    with check:
        with pytest.raises(
            tables.MovieExists,
            match="UNIQUE constraint failed: movie.title, movie.year",
        ):
            tables.edit_movie(old_movie_bag=old_movie_bag, new_movie_bag=MOVIEBAG_1)
    check.equal(
        log_error,
        [
            (
                (
                    "UNIQUE constraint failed: movie.title, movie.year",
                    "Duplicate title and year.",
                ),
                {},
            )
        ],
    )


def test_edit_movie_with_too_early_year(test_database, log_error):
    old_movie_bag = MovieBag(
        title="Test Edit Movie",
        year=MovieInteger(5042),
    )
    tables.add_movie(movie_bag=old_movie_bag)
    new_movie_bag = MovieBag(
        year=MovieInteger(0),
    )

    with check:
        with pytest.raises(
            tables.InvalidReleaseYear,
            match="CHECK constraint failed: year>1878",
        ):
            tables.edit_movie(old_movie_bag=old_movie_bag, new_movie_bag=new_movie_bag)
    check.equal(
        log_error,
        [
            (
                (
                    "CHECK constraint failed: year>1878",
                    ("(sqlite3.IntegrityError) CHECK constraint failed: year>1878",),
                ),
                {},
            )
        ],
    )


def test_edit_movie_with_too_late_year(test_database, log_error):
    old_movie_bag = MovieBag(
        title="Test Edit Movie",
        year=MovieInteger(5042),
    )
    tables.add_movie(movie_bag=old_movie_bag)
    new_movie_bag = MovieBag(
        year=MovieInteger(14242),
    )

    with check:
        with pytest.raises(
            tables.InvalidReleaseYear,
            match="CHECK constraint failed: year<=10000",
        ):
            tables.edit_movie(old_movie_bag=old_movie_bag, new_movie_bag=new_movie_bag)
    check.equal(
        log_error,
        [
            (
                (
                    "CHECK constraint failed: year<=10000",
                    ("(sqlite3.IntegrityError) CHECK constraint failed: year<=10000",),
                ),
                {},
            )
        ],
    )


def test_delete_movie(test_database):
    movie_bag = MovieBag(
        title="Test Delete Movie",
        year=MovieInteger(5042),
        stars={"Sylvia Star", "Sidney Star"},
    )
    tables.add_movie(movie_bag=movie_bag)

    tables.delete_movie(movie_bag=movie_bag)

    with tables.session_factory() as session:
        movies = tables._match_movies(
            session,
            match=movie_bag,
        )
        check.equal(len(movies), 0, "The movie was not deleted.")

        people = tables._select_people(session, names=movie_bag["stars"])
        check.equal(len(people), 0, msg=f"People not removed from people table.")


def test_previously_deleted_movie(test_database):
    """This tests the scenario where the movie has been deleted by another
    process.Orphan deletion must still be executed."""
    movie_bag = MovieBag(
        title="Test Previously Deleted Movie",
        year=MovieInteger(5042),
        stars={"Sylvia Star", "Sidney Star"},
    )
    with tables.session_factory() as session:
        for person_name in movie_bag["stars"]:
            tables._add_person(session, name=person_name)
        session.commit()

    tables.delete_movie(movie_bag=movie_bag)

    with tables.session_factory() as session:
        movies = tables._match_movies(
            session,
            match=movie_bag,
        )
        check.equal(len(movies), 0, "The movie was not deleted.")

        people = tables._select_people(session, names=movie_bag["stars"])
        check.equal(len(people), 0, msg=f"People not removed from people table.")


def test_select_all_tags(test_database):
    tag_texts = tables.select_all_tags()
    assert tag_texts == TAG_TEXTS


def test_add_tag_text(test_database):
    new_tag = "test new tag"

    tables.add_tag(tag_text=new_tag)

    tags = tables.select_all_tags()
    assert tags & {new_tag} == {new_tag}


def test_add_duplicate_tag_logs_and_raises_exception(test_database, log_error):
    new_tag = "test new tag"
    tables.add_tag(tag_text=new_tag)

    with check:
        with pytest.raises(
            tables.TagExists,
            match="UNIQUE constraint failed: tag.text",
        ):
            tables.add_tag(tag_text=new_tag)

    check.equal(
        log_error,
        [(("(sqlite3.IntegrityError) UNIQUE constraint failed: tag.text",), {})],
        msg="IntegrityError was not logged.",
    )


def test_add_tags(test_database, log_error):
    new_tag = "test new tag"
    tables.add_tags(tag_texts={new_tag})

    with check:
        with pytest.raises(
            tables.TagExists,
            match="UNIQUE constraint failed: tag.text",
        ):
            tables.add_tags(tag_texts={new_tag})
    check.equal(
        log_error,
        [(("(sqlite3.IntegrityError) UNIQUE constraint failed: tag.text",), {})],
        msg="IntegrityError was not logged.",
    )


def test_edit_tag(test_database):
    old_tag_text = SOUGHT_TAG
    new_tag_text = "test new tag"

    tables.edit_tag(old_tag_text=old_tag_text, new_tag_text=new_tag_text)

    tags_remaining = tables.select_all_tags()
    check.equal(tags_remaining & {SOUGHT_TAG}, set())
    check.equal(tags_remaining & {new_tag_text}, {new_tag_text})


def test_edit_missing_tag_logs_and_raises_exception(test_database, log_error):
    tag_text = "garbage"

    with check:
        with pytest.raises(tables.TagNotFound):
            tables.edit_tag(old_tag_text=tag_text, new_tag_text=tag_text)
    check.equal(
        log_error,
        [(("No row was found when one was required",), {})],
        msg="NoResultFound was not logged.",
    )


def test_edit_duplicate_tag_text_logs_and_raises_exception(test_database, log_error):
    old_tag_text = SOUGHT_TAG
    # Already present in another Tag object.
    new_tag_text = THIRD_TAG

    with check:
        with pytest.raises(
            tables.TagExists,
            match="UNIQUE constraint failed: tag.text",
        ):
            tables.edit_tag(old_tag_text=old_tag_text, new_tag_text=new_tag_text)
            pass
    check.equal(
        log_error,
        [(("(sqlite3.IntegrityError) UNIQUE constraint failed: tag.text",), {})],
        msg="IntegrityError was not logged.",
    )


def test_delete_tag(test_database):
    tables.delete_tag(tag_text=SOUGHT_TAG)

    tags_remaining = tables.select_all_tags()
    assert tags_remaining & set(SOUGHT_TAG) == set()


def test_delete_missing_tag_suppresses_exception(test_database, log_error):
    tables.delete_tag(tag_text=SOUGHT_TAG)
    tables.delete_tag(tag_text=SOUGHT_TAG)


def test_delete_all_orphans(test_database, log_info):
    names = {"Mona Marimba", "Nigel Nicholby"}
    with tables.session_factory() as session:
        for name in names:
            tables._add_person(session, name=name)
        session.commit()

    tables.delete_all_orphans()

    with tables.session_factory() as session:
        people = tables._select_people(session, names=names)
        check.equal(people, set())
        check.equal(
            log_info,
            [
                (
                    (
                        "1 Orphan(s) were removed. They should have been removed before now.",
                    ),
                    {},
                )
            ],
        )


def test_invalid_movie_regression(test_database):
    """This is a regression test for #261 Invalid movie returned from search selection."""
    movie_one = MovieBag(title="Spit it Out", year=MovieInteger(2000))
    tables.add_movie(movie_bag=movie_one)
    movie_two = MovieBag(title="t", year=MovieInteger(2000))
    tables.add_movie(movie_bag=movie_two)
    movie_three = MovieBag(title="Tea for three", year=MovieInteger(2000))
    tables.add_movie(movie_bag=movie_three)

    # Only the correct movie is selected otherwise an exception would be generated.
    select_bag = MovieBag(title="t", year=MovieInteger(2000))
    tables.select_movie(movie_bag=select_bag)


@pytest.fixture(scope="function")
def session_engine():
    """Creates an engine."""
    engine: Engine = create_engine("sqlite+pysqlite:///:memory:")
    schema.Base.metadata.create_all(engine)
    tables.session_factory = sessionmaker(engine)


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
def log_error(monkeypatch):
    """Logs arguments of calls to logging.error."""
    calls = []
    monkeypatch.setattr(
        tables.logging,
        "error",
        lambda *args, **kwargs: calls.append((args, kwargs)),
    )
    return calls


@pytest.fixture(scope="function")
def log_info(monkeypatch):
    """Logs arguments of calls to logging.info."""
    calls = []
    monkeypatch.setattr(
        tables.logging,
        "info",
        lambda *args, **kwargs: calls.append((args, kwargs)),
    )
    return calls
