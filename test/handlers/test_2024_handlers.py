"""Menu handlers test module."""

#  Copyright© 2024. Stephen Rigden.
#  Last modified 11/12/24, 1:00 PM by stephen.
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

from unittest.mock import MagicMock, call

import pytest
from pytest_check import check

import handlers
from globalconstants import *


# noinspection PyMissingOrEmptyDocstring
class TestAddMovieCallback:
    def test_add_movie_callback(self, monkeypatch):
        test_title = "test title"
        test_year = "4242"
        tag_1 = "test tag 1"
        tag_2 = "test tag 2"
        selected_tags = [tag_1, tag_2]
        gui_movie: MovieTD = {
            TITLE: test_title,
            YEAR: test_year,
            MOVIE_TAGS: selected_tags,
        }
        db_movie: MovieTD = {TITLE: test_title, YEAR: test_year}
        monkeypatch.setattr(handlers.database, "add_movie", MagicMock())
        monkeypatch.setattr(handlers.database, "add_movie_tag_link", MagicMock())

        handlers.add_movie_callback(gui_movie)
        with check:
            # noinspection PyUnresolvedReferences
            handlers.database.add_movie.assert_called_once_with(gui_movie)
        with check:
            # noinspection PyUnresolvedReferences
            handlers.database.add_movie_tag_link.assert_has_calls(
                [
                    call(tag_1, db_movie),
                    call(tag_2, db_movie),
                ]
            )


# noinspection PyMissingOrEmptyDocstring
class TestEditMovieCallback:
    @pytest.mark.skip
    def test_edit_movie_callback(self, monkeypatch):
        test_old_title = "test old title"
        test_old_year = "1942"
        tag_old_1 = "test old tag 1"
        tag_old_2 = "test old tag 2"
        old_tags = [tag_old_1, tag_old_2]
        old_movie: MovieTD = {
            TITLE: test_old_title,
            YEAR: test_old_year,
            MOVIE_TAGS: old_tags,
        }
        test_title = "test title"
        test_year = "4242"
        tag_1 = "test tag 1"
        tag_2 = "test tag 2"
        selected_tags = [tag_1, tag_2]
        new_movie: MovieTD = {
            TITLE: test_title,
            YEAR: test_year,
            MOVIE_TAGS: selected_tags,
        }
        db_movie: MovieTD = {TITLE: test_title, YEAR: test_year}
        monkeypatch.setattr(handlers.database, "replace_movie", MagicMock())
        monkeypatch.setattr(
            handlers.database, "movie_tags", mock_movie_tags := MagicMock()
        )
        monkeypatch.setattr(
            handlers.database,
            "edit_movie_tag_links",
            mock_edit_movie_tag_links := MagicMock(),
        )
        monkeypatch.setattr(handlers.guiwidgets, "gui_messagebox", MagicMock())
        monkeypatch.setattr(handlers.config, "current", mock_current := MagicMock())

        # noinspection PyTypeChecker
        callback = handlers.edit_movie_callback(old_movie)
        callback(new_movie)

        with check:
            # noinspection PyUnresolvedReferences
            handlers.database.replace_movie.assert_called_once_with(
                old_movie, new_movie
            )
        with check:
            # noinspection PyUnresolvedReferences
            handlers.database.movie_tags.assert_called_once_with(old_movie)
        with check:
            # noinspection PyUnresolvedReferences
            handlers.database.edit_movie_tag_links.assert_called_once_with(
                db_movie,
                mock_movie_tags(),
                selected_tags,
            )

        new_movie: MovieTD = {
            TITLE: test_title,
            YEAR: test_year,
            MOVIE_TAGS: selected_tags,
        }
        mock_edit_movie_tag_links.side_effect = (
            handlers.exception.DatabaseSearchFoundNothing
        )
        callback(new_movie)
        with check:
            # noinspection PyUnresolvedReferences
            handlers.guiwidgets.gui_messagebox.assert_called_once_with(
                mock_current.tk_root,
                handlers.MISSING_MOVIE,
                f"{handlers.THE_MOVIE} {new_movie} {handlers.MOVIE_DELETED}",
            )
