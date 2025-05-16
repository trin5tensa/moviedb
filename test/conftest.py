"""pytest fixture plugin."""

#  Copyright© 2025. Stephen Rigden.
#  Last modified 5/16/25, 1:30 PM by stephen.
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

from dataclasses import dataclass, field
from unittest.mock import MagicMock

import pytest

import exception

# todo remove unused


@pytest.fixture()
def mock_fut():
    """Return an instance of the mock future class.

    The result method of this future object will return the value 42 and no
    exceptions were raised.
    """
    return _MockFuture()


@pytest.fixture()
def mock_fut_bad_key():
    """Return an instance of the mock future class.

    The result method of this future object will raise the exception TMDBAPIKeyException.
    """
    return _MockFuture(exception.TMDBAPIKeyException("Test bad key"))


@pytest.fixture()
def mock_fut_timeout():
    """Return an instance of the mock future class.

    The result method of this future object will raise the exception
    TMDBConnectionTimeout.
    """
    return _MockFuture(exception.TMDBConnectionTimeout("Test timeout exception"))


@pytest.fixture()
def mock_fut_unexpected():
    """Return an instance of the mock future class.

    The result method of this future object will raise Exception."""
    return _MockFuture(Exception("Test unexpected exception"))


# noinspection PyMissingOrEmptyDocstring
@pytest.fixture()
def mock_executor():
    return _MockThreadPoolExecutor()


@pytest.fixture()
def mock_config_current(monkeypatch):
    """Mock handlers.config.current."""
    current = MagicMock()
    monkeypatch.setattr("handlers.sundries.config.current", current)
    return current


# noinspection PyMissingOrEmptyDocstring
@dataclass
class _MockFuture:
    """An instrumented mock of a Future class."""

    exc: Exception = False
    result_called: bool = field(default=False, init=False, repr=False)
    add_done_callback_calls: list = field(default_factory=list, init=False, repr=False)

    def result(self):
        if self.exc:
            raise self.exc
        self.result_called = True
        return 42

    def add_done_callback(self, *args):
        self.add_done_callback_calls.append(args)


# noinspection PyMissingOrEmptyDocstring
@dataclass
class _MockThreadPoolExecutor:
    """An instrumented mock of a ThreadPoolExecutor class."""

    submit_calls: list = field(default_factory=list, init=False, repr=False)
    fut: _MockFuture = field(default_factory=_MockFuture, init=False, repr=False)

    def submit(self, *args):
        self.submit_calls.append(args)
        return self.fut
