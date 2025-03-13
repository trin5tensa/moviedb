"""Test Module."""

#  Copyright© 2025. Stephen Rigden.
#  Last modified 3/13/25, 12:53 PM by stephen.
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
from unittest.mock import MagicMock, call

from gui import movies


class TestMovieGUI:
    """Tests for the MovieGUI class."""

    def test_post_init(self, tk, ttk, monkeypatch):
        # Arrange
        name = movies.MovieGUI.__name__.lower()
        destroy = MagicMock(name="destroy", autospec=True)
        monkeypatch.setattr(movies.MovieGUI, "destroy", destroy)
        create_body_and_buttonbox = MagicMock(
            name="create_body_and_buttonbox", autospec=True
        )
        outer_frame = ttk.Frame()
        body_frame = ttk.Frame()
        buttonbox = ttk.Frame()
        create_body_and_buttonbox.return_value = outer_frame, body_frame, buttonbox
        monkeypatch.setattr(
            movies.common, "create_body_and_buttonbox", create_body_and_buttonbox
        )
        create_tmdb_frame = MagicMock(name="create_tmdb_frame", autospec=True)
        tmdb_frame = ttk.Frame
        create_tmdb_frame.return_value = tmdb_frame
        monkeypatch.setattr(movies.MovieGUI, "create_tmdb_frame", create_tmdb_frame)
        fill_body = MagicMock(name="fill_body", autospec=True)
        monkeypatch.setattr(movies.MovieGUI, "fill_body", fill_body)
        # noinspection DuplicatedCode
        populate = MagicMock(name="populate", autospec=True)
        monkeypatch.setattr(movies.MovieGUI, "populate", populate)
        fill_buttonbox = MagicMock(name="fill_buttonbox", autospec=True)
        monkeypatch.setattr(movies.MovieGUI, "fill_buttonbox", fill_buttonbox)
        fill_tmdb = MagicMock(name="fill_tmdb", autospec=True)
        monkeypatch.setattr(movies.MovieGUI, "fill_tmdb", fill_tmdb)
        init_button_enablements = MagicMock(
            name="init_button_enablements", autospec=True
        )
        monkeypatch.setattr(
            movies.common, "init_button_enablements", init_button_enablements
        )
        tmdb_callback = MagicMock(name="tmdb_callback")
        all_tags = []

        # Act
        movies_gui = movies.MovieGUI(
            tk.Tk, tmdb_callback=tmdb_callback, all_tags=all_tags
        )

        # Assert
        with check:
            create_body_and_buttonbox.assert_called_once_with(tk.Tk, name, destroy)
        with check:
            create_tmdb_frame.assert_called_once_with(outer_frame)
        with check:
            fill_body.assert_called_once_with(body_frame)
        with check:
            populate.assert_called_once_with()
        with check:
            fill_buttonbox.assert_called_once_with(buttonbox)
        with check:
            fill_tmdb.assert_called_once_with(tmdb_frame)
        with check:
            init_button_enablements.assert_called_once_with(movies_gui.entry_fields)

    def test_create_tmdb_frame(self, tk, ttk, moviegui_post_init, monkeypatch):
        # Arrange
        monkeypatch.setattr(movies, "ttk", ttk)
        tmdb_callback = MagicMock(name="tmdb_callback", autospec=True)
        all_tags = []
        movie_gui = movies.MovieGUI(
            tk.Tk(), tmdb_callback=tmdb_callback, all_tags=all_tags
        )

        # Act
        movie_gui.create_tmdb_frame(ttk.Frame)

        # Assert
        with check:
            ttk.Frame.columnconfigure.assert_called_once_with(1, weight=1000)
        with check:
            ttk.Frame.assert_called_once_with(ttk.Frame, padding=10)
        with check:
            ttk.Frame().grid.assert_called_once_with(column=1, row=0, sticky="nw")
        with check:
            ttk.Frame().columnconfigure.assert_called_once_with(0, weight=1, minsize=25)

    def test_fill_body(self, tk, ttk, moviegui_post_init, monkeypatch):
        # Arrange
        body_frame = ttk.Frame()
        label_and_field = MagicMock(name="label_and_field", autospec=True)
        monkeypatch.setattr(movies.common, "LabelAndField", label_and_field)
        # noinspection DuplicatedCode
        tk_facade_entry = MagicMock(name="tk_facade_entry", autospec=True)
        monkeypatch.setattr(movies.tk_facade, "Entry", tk_facade_entry)
        tk_facade_text = MagicMock(name="tk_facade_text", autospec=True)
        monkeypatch.setattr(movies.tk_facade, "Text", tk_facade_text)
        tk_facade_treeview = MagicMock(name="tk_facade_treeview", autospec=True)
        monkeypatch.setattr(movies.tk_facade, "Treeview", tk_facade_treeview)
        tmdb_callback = MagicMock(name="tmdb_callback", autospec=True)
        all_tags = []
        movie_gui = movies.MovieGUI(
            tk.Tk(), tmdb_callback=tmdb_callback, all_tags=all_tags
        )

        # Act
        movie_gui.fill_body(body_frame)

        # Assert
        with check:
            label_and_field.assert_called_once_with(body_frame)
        with check:
            assert movie_gui.entry_fields == {
                movies.TITLE: tk_facade_entry(),
                movies.YEAR: tk_facade_entry(),
                movies.DIRECTORS: tk_facade_entry(),
                movies.DURATION: tk_facade_entry(),
                movies.NOTES: tk_facade_text(),
                movies.MOVIE_TAGS: tk_facade_treeview(),
            }
        with check:
            label_and_field().add_entry_row.assert_has_calls(
                [
                    call(movie_gui.entry_fields[movies.TITLE]),
                    call(movie_gui.entry_fields[movies.YEAR]),
                    call(movie_gui.entry_fields[movies.DIRECTORS]),
                    call(movie_gui.entry_fields[movies.DURATION]),
                ]
            )
        with check:
            label_and_field().add_text_row.assert_called_once_with(
                movie_gui.entry_fields[movies.NOTES]
            )
        with check:
            label_and_field().add_treeview_row.assert_called_once_with(
                movie_gui.entry_fields[movies.MOVIE_TAGS], movie_gui.all_tags
            )
        with check:
            tk_facade_entry().widget.focus_set.assert_called_once_with()


@pytest.fixture(scope="function")
def moviegui_post_init(monkeypatch):
    """Stops the MovieGUI.__post_init__ method from running."""
    monkeypatch.setattr(
        movies.MovieGUI,
        "__post_init__",
        lambda *args, **kwargs: None,
    )
