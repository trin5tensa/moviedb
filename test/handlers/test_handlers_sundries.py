"""Menu handlers for movies."""

#  Copyright© 2025. Stephen Rigden.
#  Last modified 4/9/25, 9:26 AM by stephen.
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
    monkeypatch,
):
    # Arrange
    showinfo = MagicMock(name="showinfo", autospec=True)
    monkeypatch.setattr(sundries.common, "showinfo", showinfo)
    fut = MagicMock(name="fut", autospec=True)
    fut.result.side_effect = sundries.tmdb.exception.TMDBConnectionTimeout
    monkeypatch.setattr(sundries.concurrent.futures, "Future", fut)

    # Act
    sundries._tmdb_search_exception_callback(fut)

    # Assert
    showinfo.assert_called_once_with(
        sundries.TMDB_UNREACHABLE,
    )


def test_tmdb_search_exception_with_settings_update(
    monkeypatch,
    caplog,
):
    # Arrange
    fut = MagicMock(name="fut", autospec=True)
    log_msg = "42"
    fut.result.side_effect = sundries.tmdb.exception.TMDBAPIKeyException(log_msg)
    monkeypatch.setattr(sundries.concurrent.futures, "Future", fut)
    settings_dialog = MagicMock(name="settings_dialog", autospec=True)
    monkeypatch.setattr(sundries, "settings_dialog", settings_dialog)
    askyesno = MagicMock(name="askyesno", autospec=True)
    askyesno.return_value = True
    monkeypatch.setattr(sundries.common, "askyesno", askyesno)

    # Act
    sundries._tmdb_search_exception_callback(fut)

    # Assert
    check.equal(caplog.messages, [log_msg])
    with check:
        askyesno.assert_called_once_with(
            sundries.INVALID_API_KEY,
            detail=sundries.SET_API_KEY,
        )
    with check:
        settings_dialog.assert_called_once_with()


def test_tmdb_search_exception_with_settings_update_declined(
    monkeypatch,
):
    # Arrange
    fut = MagicMock(name="fut", autospec=True)
    settings_dialog = MagicMock(name="settings_dialog", autospec=True)
    monkeypatch.setattr(sundries, "settings_dialog", settings_dialog)
    askyesno = MagicMock(name="askyesno", autospec=True)
    askyesno.return_value = True
    monkeypatch.setattr(sundries.common, "askyesno", askyesno)

    # Act
    sundries._tmdb_search_exception_callback(fut)

    # Assert
    with check:
        settings_dialog.assert_not_called()
