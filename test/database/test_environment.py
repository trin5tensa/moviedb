"""Test module."""

#  Copyright© 2025. Stephen Rigden.
#  Last modified 1/17/25, 7:27 AM by stephen.
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
from sqlalchemy import create_engine

from database import update, environment


def test_start_engine(monkeypatch, tmp_path, log_info):
    def mock_getcreate_directories(
        getcreate_directories_calls_, data_dir_path_, database_dir_path_
    ):
        """..."""

        def func(*args, **kwargs):
            """..."""
            getcreate_directories_calls_.append((args, kwargs))
            return data_dir_path_, database_dir_path_

        return func

    def mock_getcreate_metadata(get_create_metadata_calls_, saved_version_):
        """..."""

        def func(*args, **kwargs):
            """..."""
            get_create_metadata_calls_.append((args, kwargs))
            return saved_version_

        return func

    # Arrange
    data_dir_name = environment.DATA_DIR_NAME
    data_dir_path = tmp_path
    database_dir_name = environment.DATABASE_STEM + environment.schema.VERSION
    database_dir_path = data_dir_path / database_dir_name
    saved_version = environment.schema.VERSION

    getcreate_directories_calls = []
    monkeypatch.setattr(
        environment,
        "_getcreate_directories",
        mock_getcreate_directories(
            getcreate_directories_calls, data_dir_path, database_dir_path
        ),
    )

    get_create_metadata_calls = []
    monkeypatch.setattr(
        environment,
        "_getcreate_metadata",
        mock_getcreate_metadata(get_create_metadata_calls, saved_version),
    )

    register_session_factory_calls = []
    monkeypatch.setattr(
        environment,
        "_register_session_factory",
        lambda *args, **kwargs: register_session_factory_calls.append((args, kwargs)),
    )

    # Act
    environment.start_engine()

    # Assert
    check.equal(getcreate_directories_calls, [((data_dir_name, database_dir_name), {})])
    check.equal(get_create_metadata_calls, [((data_dir_path,), {})])
    check.equal(register_session_factory_calls, [((database_dir_path,), {})])
    check.equal(
        log_info,
        (
            [
                ((environment.DATABASE_REOPENED_MSG + environment.schema.VERSION,), {}),
            ]
        ),
    )


def test_start_engine_with_update(monkeypatch, tmp_path):
    def mock_getcreate_directories(data_dir_path_, database_dir_path_):
        """..."""

        # noinspection PyUnusedLocal,PyMissingOrEmptyDocstring
        def func(*args, **kwargs):
            return data_dir_path_, database_dir_path_

        return func

    def mock_getcreate_metadata(saved_version_):
        """..."""

        # noinspection PyMissingOrEmptyDocstring,PyUnusedLocal
        def func(*args, **kwargs):
            return saved_version_

        return func

    # Arrange
    data_dir_path = tmp_path
    database_dir_name = environment.DATABASE_STEM + environment.schema.VERSION
    database_dir_path = data_dir_path / database_dir_name
    saved_version = "DBv42"

    monkeypatch.setattr(
        environment,
        "_getcreate_directories",
        mock_getcreate_directories(data_dir_path, database_dir_path),
    )

    monkeypatch.setattr(
        environment,
        "_getcreate_metadata",
        mock_getcreate_metadata(saved_version),
    )

    monkeypatch.setattr(
        environment, "_register_session_factory", lambda *args, **kwargs: None
    )

    update_database_calls = []
    monkeypatch.setattr(
        environment,
        "_update_database",
        lambda *args, **kwargs: update_database_calls.append((args, kwargs)),
    )

    # Act
    environment.start_engine()

    # Assert
    assert update_database_calls == [((saved_version, data_dir_path), {})]


def test__get_create_directories(monkeypatch):
    data_dir_name = "Movie Data Test"
    database_dir_name = "Movie Database Test"
    program_path = environment.Path(__file__)
    expected_data_dir_path = program_path.parents[3] / data_dir_name
    expected_database_dir_path = expected_data_dir_path / database_dir_name
    mkdir_calls = []
    monkeypatch.setattr(
        environment.Path,
        "mkdir",
        lambda *args, **kwargs: mkdir_calls.append((args, kwargs)),
    )

    data_dir_path, database_dir_path = environment._getcreate_directories(
        data_dir_name, database_dir_name
    )

    check.equal(
        mkdir_calls,
        [
            (
                (environment.Path("/Users/stephen/Documents/Coding/Movie Data Test"),),
                {"exist_ok": True},
            ),
            (
                (
                    environment.Path(
                        "/Users/stephen/Documents/Coding/Movie Data Test/Movie Database Test"
                    ),
                ),
                {"exist_ok": True},
            ),
        ],
    )
    check.equal(data_dir_path, expected_data_dir_path)
    check.equal(database_dir_path, expected_database_dir_path)


def test__get_create_directories_with_missing_directories(monkeypatch, log_info):
    data_dir_name = "Movie Data Test"
    database_dir_name = "Movie Database Test"
    monkeypatch.setattr(environment.Path, "mkdir", lambda *args, **kwargs: None)

    environment._getcreate_directories(data_dir_name, database_dir_name)

    assert log_info == [
        ((environment.NO_MOVIE_DATA_DIRECTORY_MSG,), {}),
        ((environment.NO_DATABASE_DIRECTORY_MSG,), {}),
    ]


def test__getcreate_metadata(tmp_path):
    expected_version = "DBv42"
    saved_version_fn = tmp_path / (environment.SAVED_VERSION + ".json")
    data = {environment.SAVED_VERSION: expected_version}
    with open(saved_version_fn, "w") as fp:
        # noinspection PyTypeChecker
        environment.json.dump(data, fp)

    saved_version = environment._getcreate_metadata(tmp_path)

    assert saved_version == expected_version


def test__getcreate_metadata_with_missing_metadata_file(tmp_path):
    saved_version = environment._getcreate_metadata(tmp_path)

    assert saved_version == environment.schema.VERSION


def test__register_session_factory(tmp_path, monkeypatch):
    def mock_create_engine(expected_engine_, create_engine_calls_):
        """..."""

        def func(*args, **kwargs):
            """..."""
            create_engine_calls_.append((args, kwargs))
            return expected_engine_

        return func

    def mock_sessionmaker(expected_factory_, sessionmaker_calls_):
        """..."""

        def func(*args, **kwargs):
            """..."""
            sessionmaker_calls_.append((args, kwargs))
            return expected_factory_

        return func

    hold_session_factory = environment.tables.session_factory
    database_name = environment.DATABASE_STEM + environment.schema.VERSION + ".sqlite3"
    database_fn = tmp_path / database_name
    expected_engine = "expected_engine"
    create_engine_calls = []
    monkeypatch.setattr(
        environment,
        "create_engine",
        mock_create_engine(expected_engine, create_engine_calls),
    )
    sessionmaker_calls = []
    expected_factory = "expected_factory"
    monkeypatch.setattr(
        environment,
        "sessionmaker",
        mock_sessionmaker(expected_factory, sessionmaker_calls),
    )
    create_all_calls = []
    monkeypatch.setattr(
        environment.schema.Base.metadata,
        "create_all",
        lambda *args, **kwargs: create_all_calls.append((args, kwargs)),
    )

    environment._register_session_factory(tmp_path)

    check.equal(
        create_engine_calls, [((f"sqlite+pysqlite:///{database_fn}",), {"echo": False})]
    )
    check.equal(environment.tables.session_factory, expected_factory)
    check.equal(create_all_calls, [((expected_engine,), {})])

    environment.tables.session_factory = hold_session_factory


def test__update_database(monkeypatch, tmp_path, log_info):
    def mock_update_old_database(update_old_database_calls_, movies_, tags_):
        """..."""

        def func(*args, **kwargs):
            """..."""
            update_old_database_calls_.append((args, kwargs))
            return movies_, tags_

        return func

    # Arrange
    old_version = "DBv42"
    stem_version = environment.DATABASE_STEM + old_version
    old_version_name = stem_version + ".sqlite3"
    old_version_fn = tmp_path / stem_version / old_version_name
    movies = ["movie 1", "movie 2", "movie 3"]
    tags = {"tag 1", "tag 2", "tag 3"}
    update_old_database_calls = []
    monkeypatch.setattr(
        environment.update,
        "update_old_database",
        mock_update_old_database(update_old_database_calls, movies, tags),
    )
    add_tags_calls = []
    monkeypatch.setattr(
        environment.tables,
        "add_tags",
        lambda *args, **kwargs: add_tags_calls.append((args, kwargs)),
    )
    add_movies_calls = []
    monkeypatch.setattr(
        environment.tables,
        "add_movie",
        lambda *args, **kwargs: add_movies_calls.append((args, kwargs)),
    )

    saved_version_fn = tmp_path / (environment.SAVED_VERSION + ".json")
    data = {environment.SAVED_VERSION: old_version}
    with open(saved_version_fn, "w") as fp:
        # noinspection PyTypeChecker
        environment.json.dump(data, fp)

    # Act
    environment._update_database(old_version, tmp_path)

    # Assert update_old_database
    check.equal(update_old_database_calls, [((old_version, old_version_fn), {})])

    # Assert movies added
    check.equal(
        add_movies_calls,
        [
            ((), {"movie_bag": "movie 1"}),
            ((), {"movie_bag": "movie 2"}),
            ((), {"movie_bag": "movie 3"}),
        ],
    )

    # Assert tags added
    check.equal(add_tags_calls, [((), {"tag_texts": tags})])

    # Assert metafile updated
    with open(saved_version_fn) as fp:
        data = environment.json.load(fp)
    msg = "The saved version file was not correctly updated."
    check.equal(data[environment.SAVED_VERSION], environment.schema.VERSION, msg)

    # Assert update logged
    msg = environment.UPDATE_SUCCESSFUL_MSG + environment.schema.VERSION
    assert log_info == [
        ((msg,), {}),
    ]


@pytest.fixture(scope="function")
def session_engine():
    """Yields an engine."""
    update.engine = create_engine("sqlite+pysqlite:///:memory:")
    yield update.engine


@pytest.fixture(scope="function")
def log_info(monkeypatch):
    """Logs arguments of calls to logging.error."""
    calls = []
    monkeypatch.setattr(
        update.logging, "info", lambda *args, **kwargs: calls.append((args, kwargs))
    )
    return calls
