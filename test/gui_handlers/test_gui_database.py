"""Menu handlers test module."""

#  Copyright© 2024. Stephen Rigden.
#  Last modified 9/27/24, 7:20 AM by stephen.
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

from gui_handlers import guidatabase


def test_add_movie(monkeypatch):
    mock_name = test_add_movie.__name__
    monkeypatch.setattr(guidatabase.config, "current", MagicMock(name=mock_name))
    test_tags = {"tag 1", "tag 2", "tag 3"}
    mock_select_tags = MagicMock(name=mock_name, return_value=test_tags)
    monkeypatch.setattr(guidatabase.tables, "select_all_tags", mock_select_tags)
    mock_add_movie_gui = MagicMock(name=mock_name)
    monkeypatch.setattr(guidatabase.guiwidgets_2, "AddMovieGUI", mock_add_movie_gui)

    guidatabase.add_movie()

    mock_add_movie_gui.assert_called_once_with(
        guidatabase.config.current.tk_root,
        guidatabase._tmdb_io_handler,
        list(test_tags),
        add_movie_callback=guidatabase.add_movie_callback,
    )


def test_edit_movie(monkeypatch):
    mock_name = test_add_movie.__name__
    monkeypatch.setattr(guidatabase.config, "current", MagicMock(name=mock_name))
    test_tags = {"tag 1", "tag 2", "tag 3"}
    mock_select_tags = MagicMock(name=mock_name, return_value=test_tags)
    monkeypatch.setattr(guidatabase.tables, "select_all_tags", mock_select_tags)
    mock_search_movie_gui = MagicMock(name=mock_name)
    monkeypatch.setattr(guidatabase.guiwidgets, "SearchMovieGUI", mock_search_movie_gui)

    guidatabase.edit_movie()

    mock_search_movie_gui.assert_called_once_with(
        guidatabase.config.current.tk_root,
        guidatabase._search_movie_callback,
        list(test_tags),
    )
