"""Menu handlers for movies."""

#  Copyright© 2025. Stephen Rigden.
#  Last modified 4/5/25, 1:52 PM by stephen.
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

from unittest.mock import MagicMock

import pytest
from pytest_check import check

from handlers import sundries


def test_tmdb_search_exception_callback_calls_future(monkeypatch):
    # Arrange
    fut = MagicMock(name="fut", autospec=True)
    monkeypatch.setattr(sundries.concurrent.futures, "Future", fut)

    # Act
    sundries._tmdb_search_exception_callback(fut)

    # Assert
    fut.result.assert_called_once_with()


# noinspection PyPep8Naming
def test_tmdb_search_exception_callback_raises_TMDBConnectionTimeout(
    config_current, monkeypatch, messagebox
):
    # Arrange
    messagebox = MagicMock(name="messagebox", autospec=True)
    monkeypatch.setattr(sundries, "messagebox", messagebox)
    fut = MagicMock(name="fut", autospec=True)
    fut.result.side_effect = sundries.tmdb.exception.TMDBConnectionTimeout
    monkeypatch.setattr(sundries.concurrent.futures, "Future", fut)

    # Act
    sundries._tmdb_search_exception_callback(fut)

    # Assert
    messagebox.showinfo.assert_called_once_with(
        sundries.config.current.tk_root,
        sundries.TMDB_UNREACHABLE,
    )


def test_tmdb_search_exception_with_settings_update(
    config_current, monkeypatch, caplog, messagebox
):
    # Arrange
    fut = MagicMock(name="fut", autospec=True)
    log_msg = "42"
    fut.result.side_effect = sundries.tmdb.exception.TMDBAPIKeyException(log_msg)
    monkeypatch.setattr(sundries.concurrent.futures, "Future", fut)
    settings_dialog = MagicMock(name="settings_dialog", autospec=True)
    monkeypatch.setattr(sundries, "settings_dialog", settings_dialog)
    messagebox.askyesno.return_value = True

    # Act
    sundries._tmdb_search_exception_callback(fut)

    # Assert
    check.equal(caplog.messages, [log_msg])
    with check:
        messagebox.askyesno.assert_called_once_with(
            sundries.config.current.tk_root,
            sundries.INVALID_API_KEY,
            detail=sundries.SET_API_KEY,
            icon="question",
            default="no",
        )
    with check:
        settings_dialog.assert_called_once_with()


def test_tmdb_search_exception_with_settings_update_declined(
    monkeypatch,
    messagebox,
):
    # Arrange
    fut = MagicMock(name="fut", autospec=True)
    settings_dialog = MagicMock(name="settings_dialog", autospec=True)
    monkeypatch.setattr(sundries, "settings_dialog", settings_dialog)
    messagebox.askyesno.return_value = False

    # Act
    sundries._tmdb_search_exception_callback(fut)

    # Assert
    with check:
        settings_dialog.assert_not_called()


@pytest.fixture(scope="function")
def config_current(monkeypatch):
    """This fixture patches a call to current.tk_root to suppress
    initiation of tk/tcl.

    Args:
        monkeypatch:
    """
    current = MagicMock(name="current", autospec=True)
    monkeypatch.setattr(sundries.config, "current", current)


# todo Temporary Tk/Tcl code is in the wrong place
@pytest.fixture(scope="function")
def messagebox(monkeypatch) -> MagicMock:
    """Stops Tk from starting."""
    messagebox = MagicMock(name="messagebox", autospec=True)
    monkeypatch.setattr(sundries, "messagebox", messagebox)
    return messagebox
