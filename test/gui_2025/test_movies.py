"""Test Module."""

#  Copyright© 2025. Stephen Rigden.
#  Last modified 3/20/25, 11:56 AM by stephen.
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

    tmdb_callback = MagicMock(name="tmdb_callback", autospec=True)
    all_tags = []

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
        fill_tmdb_frame = MagicMock(name="fill_tmdb_frame", autospec=True)
        monkeypatch.setattr(movies.MovieGUI, "fill_tmdb_frame", fill_tmdb_frame)
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
            fill_tmdb_frame.assert_called_once_with(tmdb_frame)
        with check:
            init_button_enablements.assert_called_once_with(movies_gui.entry_fields)

    def test_create_tmdb_frame(self, ttk, movie_gui_obj, monkeypatch):
        # Arrange
        monkeypatch.setattr(movies, "ttk", ttk)

        # Act
        movie_gui_obj.create_tmdb_frame(ttk.Frame)

        # Assert
        with check:
            ttk.Frame.columnconfigure.assert_called_once_with(1, weight=1000)
        with check:
            ttk.Frame.assert_called_once_with(ttk.Frame, padding=10)
        with check:
            ttk.Frame().grid.assert_called_once_with(column=1, row=0, sticky="nw")
        with check:
            ttk.Frame().columnconfigure.assert_called_once_with(0, weight=1, minsize=25)

    def test_fill_body(self, ttk, movie_gui_obj, monkeypatch):
        # Arrange
        body_frame = ttk.Frame()
        label_and_field = MagicMock(name="label_and_field", autospec=True)
        monkeypatch.setattr(movies.common, "LabelAndField", label_and_field)
        # todo Fix or accept ALL 'noinspection DuplicatedCode' pragmas.
        # noinspection DuplicatedCode
        tk_facade_entry = MagicMock(name="tk_facade_entry", autospec=True)
        monkeypatch.setattr(movies.tk_facade, "Entry", tk_facade_entry)
        tk_facade_text = MagicMock(name="tk_facade_text", autospec=True)
        monkeypatch.setattr(movies.tk_facade, "Text", tk_facade_text)
        tk_facade_treeview = MagicMock(name="tk_facade_treeview", autospec=True)
        monkeypatch.setattr(movies.tk_facade, "Treeview", tk_facade_treeview)

        # Act
        movie_gui_obj.fill_body(body_frame)

        # Assert
        with check:
            label_and_field.assert_called_once_with(body_frame)
        with check:
            assert movie_gui_obj.entry_fields == {
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
                    call(movie_gui_obj.entry_fields[movies.TITLE]),
                    call(movie_gui_obj.entry_fields[movies.YEAR]),
                    call(movie_gui_obj.entry_fields[movies.DIRECTORS]),
                    call(movie_gui_obj.entry_fields[movies.DURATION]),
                ]
            )
        with check:
            label_and_field().add_text_row.assert_called_once_with(
                movie_gui_obj.entry_fields[movies.NOTES]
            )
        with check:
            label_and_field().add_treeview_row.assert_called_once_with(
                movie_gui_obj.entry_fields[movies.MOVIE_TAGS], movie_gui_obj.all_tags
            )
        with check:
            tk_facade_entry().widget.focus_set.assert_called_once_with()

    def test_populate(self, movie_gui_obj, monkeypatch):
        # Arrange
        for field_name in [
            movies.TITLE,
            movies.YEAR,
            movies.DIRECTORS,
            movies.DURATION,
            movies.NOTES,
            movies.MOVIE_TAGS,
        ]:
            movie_gui_obj.entry_fields[field_name] = MagicMock(
                name=f"tk_facade_{field_name}", autospec=True
            )
        movie_bag: movies.MovieBag = {
            "title": "Populate Title",
            "year": movies.MovieInteger(4042),
            "directors": {"Tina Tangle", "Sam Smith"},
            "duration": movies.MovieInteger(142),
            "notes": "A populate note",
            "tags": {"Tag Y", "Tag X"},
        }
        movie_gui_obj.prepopulate = movie_bag

        # Act
        # noinspection DuplicatedCode
        movie_gui_obj.populate()

        # Assert
        check.equal(
            movie_gui_obj.entry_fields[movies.TITLE].original_value,
            "Populate Title",
        )
        check.equal(
            movie_gui_obj.entry_fields[movies.YEAR].original_value,
            "4042",
        )
        check.equal(
            movie_gui_obj.entry_fields[movies.DIRECTORS].original_value,
            "Sam Smith, Tina Tangle",
        )
        check.equal(
            movie_gui_obj.entry_fields[movies.DURATION].original_value,
            "142",
        )
        check.equal(
            movie_gui_obj.entry_fields[movies.NOTES].original_value,
            "A populate note",
        )
        check.equal(
            movie_gui_obj.entry_fields[movies.MOVIE_TAGS].original_value,
            ["Tag X", "Tag Y"],
        )

    def test_populate_with_empty_prepopulate(self, movie_gui_obj, monkeypatch):
        # Arrange
        for field_name in [
            movies.TITLE,
            movies.YEAR,
            movies.DIRECTORS,
            movies.DURATION,
            movies.NOTES,
            movies.MOVIE_TAGS,
        ]:
            mock = MagicMock(name=f"tk_facade_{field_name}", autospec=True)
            mock.__str__.return_value = ""
            movie_gui_obj.entry_fields[field_name] = mock

        # Act
        # noinspection DuplicatedCode
        movie_gui_obj.populate()

        # Assert
        check.equal(
            movie_gui_obj.entry_fields[movies.TITLE].original_value,
            "",
        )
        check.equal(
            movie_gui_obj.entry_fields[movies.YEAR].original_value,
            "",
        )
        check.equal(
            movie_gui_obj.entry_fields[movies.DIRECTORS].original_value,
            "",
        )
        check.equal(
            movie_gui_obj.entry_fields[movies.DURATION].original_value,
            "",
        )
        check.equal(
            movie_gui_obj.entry_fields[movies.NOTES].original_value,
            "",
        )
        check.equal(
            movie_gui_obj.entry_fields[movies.MOVIE_TAGS].original_value,
            [],
        )

    # noinspection DuplicatedCode
    def test_as_movie_bag(self, movie_gui_obj, monkeypatch):
        # Arrange
        ef_title = "AMB Title"
        ef_year = "4242"
        ef_director = "Sidney Stoneheart, Tina Tatum"
        ef_duration = "42"
        ef_notes = "AMB Notes"
        ef_tags = {"Alpha", "Beta"}
        for k, v in [
            (movies.TITLE, ef_title),
            (movies.YEAR, ef_year),
            (movies.DIRECTORS, ef_director),
            (movies.DURATION, ef_duration),
            (movies.NOTES, ef_notes),
            (movies.MOVIE_TAGS, ef_tags),
        ]:
            widget = MagicMock(name=k)
            widget.current_value = v
            monkeypatch.setitem(movie_gui_obj.entry_fields, k, widget)

        mb_year = movies.MovieInteger("4242")
        mb_director = {"Sidney Stoneheart", "Tina Tatum"}
        mb_duration = movies.MovieInteger("42")
        expected_movie_bag = movies.MovieBag(
            title=ef_title,
            year=mb_year,
            duration=mb_duration,
            directors=mb_director,
            notes=ef_notes,
            tags=ef_tags,
        )

        # Act
        movie_bag = movie_gui_obj.as_movie_bag()

        assert movie_bag == expected_movie_bag

    # noinspection DuplicatedCode
    def test_as_movie_bag_with_bad_key(self, movie_gui_obj, monkeypatch, caplog):
        bad_key = "garbage"
        monkeypatch.setattr(movies.MovieGUI, "__post_init__", lambda *args: None)
        widget = MagicMock(name=bad_key)
        widget.current_value = "Has a current_value"
        monkeypatch.setitem(movie_gui_obj.entry_fields, bad_key, widget)
        exc_notes = f"{movies.UNEXPECTED_KEY}: {bad_key}"

        with check:
            with pytest.raises(KeyError, match=exc_notes):
                movie_gui_obj.as_movie_bag()
        check.equal(caplog.messages, [exc_notes])

    # noinspection DuplicatedCode
    def test_as_movie_bag_with_blank_input_field(self, movie_gui_obj, monkeypatch):
        ef_title = "AMB Title"
        for k, v in [("title", ef_title), ("notes", "")]:
            widget = MagicMock(name=k)
            widget.current_value = v
            monkeypatch.setitem(movie_gui_obj.entry_fields, k, widget)

        expected_movie_bag = movies.MovieBag(
            title=ef_title,
        )

        movie_bag = movie_gui_obj.as_movie_bag()

        assert movie_bag == expected_movie_bag

    def test_fill_buttonbox(self, ttk, movie_gui_obj, monkeypatch):
        # Arrange
        buttonbox = ttk.Frame()
        count = MagicMock(name="count", autospec=True)
        monkeypatch.setattr(movies, "count", count)
        create_buttons = MagicMock(name="create_buttons", autospec=True)
        monkeypatch.setattr(movie_gui_obj, "_create_buttons", create_buttons)
        create_button = MagicMock(name="create_button", autospec=True)
        monkeypatch.setattr(movies.common, "create_button", create_button)

        # Act
        movie_gui_obj.fill_buttonbox(buttonbox)

        # Assert
        with check:
            create_buttons.assert_called_once_with(buttonbox, count())
        with check:
            create_button.assert_called_once_with(
                buttonbox,
                movies.common.CANCEL_TEXT,
                column=next(count()),
                command=movie_gui_obj.destroy,
                default="active",
            )

    def test_create_buttons(self, ttk, movie_gui_obj, monkeypatch):
        # Arrange
        buttonbox = ttk.Frame()
        count = MagicMock(name="count", autospec=True)
        monkeypatch.setattr(movies, "count", count)
        column_counter = count()

        # Act and Assert
        with check.raises(NotImplementedError):
            movie_gui_obj._create_buttons(buttonbox, column_counter)

    def test_destroy(self, tk, ttk, movie_gui_obj, monkeypatch):
        # Arrange
        movie_gui_obj.tmdb_poller = "tmdb_poller"
        outer_frame = MagicMock(name="outer_frame", autospec=True)
        monkeypatch.setattr(movies.MovieGUI, "outer_frame", outer_frame)
        movie_gui_obj.outer_frame = outer_frame

        # Act
        movie_gui_obj.destroy()

        # Assert
        with check:
            tk.Tk().after_cancel.assert_called_once_with(movie_gui_obj.tmdb_poller)
        with check:
            outer_frame.destroy.assert_called_once_with()

    def test_fill_tmdb_frame(self, ttk, movie_gui_obj, monkeypatch):
        # Arrange
        # noinspection DuplicatedCode
        ttk = MagicMock(name="ttk", autospec=True)
        monkeypatch.setattr(movies, "ttk", ttk)
        tmdb_frame = MagicMock(name="tmdb_frame", autospec=True)
        monkeypatch.setattr(movies.ttk, "Frame", tmdb_frame)
        tview = MagicMock(name="tview", autospec=True)
        monkeypatch.setattr(movies.ttk, "Treeview", tview)
        # noinspection DuplicatedCode
        partial = MagicMock(name="partial", autospec=True)
        monkeypatch.setattr(movies, "partial", partial)
        tmdb_consumer = MagicMock(name="tmdb_consumer", autospec=True)
        monkeypatch.setattr(movies.MovieGUI, "tmdb_consumer", tmdb_consumer)
        entry = MagicMock(name="entry", autospec=True)
        monkeypatch.setattr(movies.tk_facade, "Entry", entry)
        monkeypatch.setitem(movie_gui_obj.entry_fields, movies.TITLE, entry)

        # Act
        movie_gui_obj.fill_tmdb_frame(tmdb_frame)

        # Assert
        with check:
            tview.assert_called_once_with(
                ttk.Frame,
                columns=(movies.TITLE, movies.YEAR, movies.DIRECTORS),
                show=["headings"],
                height=20,
                selectmode="browse",
            )
        with check:
            tview().column.assert_has_calls(
                [
                    call(movies.TITLE, width=300, stretch=True),
                    call(movies.YEAR, width=40, stretch=True),
                    call(movies.DIRECTORS, width=200, stretch=True),
                ]
            )
        with check:
            tview().heading.assert_has_calls(
                [
                    call(movies.TITLE, text=movies.TITLE_TEXT, anchor="w"),
                    call(movies.YEAR, text=movies.YEAR_TEXT, anchor="w"),
                    call(movies.DIRECTORS, text=movies.DIRECTORS_TEXT, anchor="w"),
                ],
            )
        with check:
            tview().grid.assert_called_once_with(column=0, row=0, sticky="nsew")
        with check:
            tview().bind.assert_called_once_with(
                "<<TreeviewSelect>>",
                func=movies.partial(movie_gui_obj.tmdb_treeview_callback, tview()),
            )
        with check:
            tmdb_consumer.assert_called_once_with()
        with check:
            entry.observer.register.assert_called_once_with(movie_gui_obj.tmdb_search)

    def test_tmdb_treeview_callback(self, movie_gui_obj, monkeypatch):
        # Arrange the partial callable with its preset part set to the treeview.
        item_id = "42"
        treeview = MagicMock(name="treeview", autospec=True)
        treeview.selection.return_value = [item_id]
        callback = movies.partial(movie_gui_obj.tmdb_treeview_callback, treeview)

        # Arrange the tmdb_movies item which contains the twst movie selection
        movie_bag = movies.MovieBag(
            title="Test TMDB Callback",
            year=movies.MovieInteger(4242),
            duration=movies.MovieInteger(942),
            directors={"Simon Simple", "Rachel River"},
            notes="Notes for 'Test TMDB Callback'",
        )
        movie_gui_obj.tmdb_movies[item_id] = movie_bag

        # Arrange entry_fields with mocked tk_facade.TkinterFacade for each field name.
        movie_gui_obj.entry_fields = {
            k: MagicMock(name=k, autospec=True) for k in movie_bag.keys()
        }

        # Rearrange the movie_bag fields into their displayed formats.
        expected = dict(
            title="Test TMDB Callback",
            year="4242",
            duration="942",
            directors="Rachel River, Simon Simple",
            notes="Notes for 'Test TMDB Callback'",
        )

        # Act
        callback()

        # Assert
        for k, v in expected.items():
            check.equal(movie_gui_obj.entry_fields[k].current_value, v)

    @pytest.fixture(scope="function")
    def movie_gui_obj(self, tk, moviegui_post_init, monkeypatch):
        """Creates a MovieGUI object without running the __post_init__ method."""
        return movies.MovieGUI(
            tk.Tk(), tmdb_callback=self.tmdb_callback, all_tags=self.all_tags
        )


@pytest.fixture(scope="function")
def moviegui_post_init(monkeypatch):
    """Stops the MovieGUI.__post_init__ method from running."""
    monkeypatch.setattr(
        movies.MovieGUI,
        "__post_init__",
        lambda *args, **kwargs: None,
    )
