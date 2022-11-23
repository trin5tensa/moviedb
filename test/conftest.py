"""pytest fixture plugin."""
#  Copyright (c) 2022-2022. Stephen Rigden.
#  Last modified 11/23/22, 8:37 AM by stephen.
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

import pytest

import exception


@pytest.fixture()
def mock_fut():
    """Return an instance of the mock future class.
    
    The result method of this future object will return the value 42 and no exceptions were raised."""
    return _MockFut()


@pytest.fixture()
def mock_fut_bad_key():
    """Return an instance of the mock future class.
    
    The result method of this future object will raise the exception TMDBAPIKeyException."""
    return _MockFut(exception.TMDBAPIKeyException('Test bad key'))


@pytest.fixture()
def mock_fut_timeout():
    """Return an instance of the mock future class.
    
    The result method of this future object will raise the exception TMDBConnectionTimeout."""
    return _MockFut(exception.TMDBConnectionTimeout('Test timeout exception'))


@pytest.fixture()
def mock_fut_unexpected():
    """Return an instance of the mock future class.
    
    The result method of this future object will raise Exception."""
    return _MockFut(Exception('Test unexpected exception'))


@dataclass
class _MockFut:
    """An instrumented mock of a Future class."""
    exc: Exception = False
    result_called: bool = field(default=False, init=False, repr=False)
    
    def result(self):
        if self.exc:
            raise self.exc
        self.result_called = True
        return 42
        
