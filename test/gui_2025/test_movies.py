"""Test Module."""

#  Copyright© 2025. Stephen Rigden.
#  Last modified 4/19/25, 11:48 AM by stephen.
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

from moviebag import MovieBag
from gui import movies


# noinspection DuplicatedCode
class TestMovieGUI:
    """Tests for the MovieGUI class."""

    tmdb_callback = MagicMock(name="tmdb_callback", autospec=True)
    all_tags = set()
    prepopulate = MovieBag()

    def test_post_init(self, tk, ttk, monkeypatch):
        """Test that MovieGUI.__post_init__ correctly initializes the GUI.

        This test verifies that the __post_init__ method:
        1. Creates the body and buttonbox using create_body_and_buttonbox
        2. Creates the TMDB frame using create_tmdb_frame
        3. Fills the body with widgets using fill_body
        4. Populates the fields with initial values using populate
        5. Fills the buttonbox with buttons using fill_buttonbox
        6. Fills the TMDB frame with widgets using fill_tmdb_frame
        7. Initializes button enablements using init_button_enablements

        Args:
            tk: Mock for tkinter module
            ttk: Mock for tkinter.ttk module
            monkeypatch: Pytest fixture for patching dependencies
        """
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
        all_tags = set()

        # Act
        movies_gui = movies.MovieGUI(
            tk.Tk,
            tmdb_callback=tmdb_callback,
            all_tags=all_tags,
            prepopulate=self.prepopulate,
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
                movie_gui_obj.entry_fields[movies.MOVIE_TAGS],
                sorted(movie_gui_obj.all_tags),
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
        monkeypatch.setattr(movie_gui_obj, "create_buttons", create_buttons)
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
                movies.CANCEL_TEXT,
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
            movie_gui_obj.create_buttons(buttonbox, column_counter)

    def test_destroy(self, tk, ttk, movie_gui_obj, monkeypatch):
        # Arrange
        movie_gui_obj.tmdb_consumer_poll = 42
        outer_frame = MagicMock(name="outer_frame", autospec=True)
        monkeypatch.setattr(movies.MovieGUI, "outer_frame", outer_frame)
        movie_gui_obj.outer_frame = outer_frame

        # Act
        movie_gui_obj.destroy()

        # Assert
        with check:
            tk.Tk().after_cancel.assert_called_once_with(
                movie_gui_obj.tmdb_consumer_recall_id
            )
        with check:
            outer_frame.destroy.assert_called_once_with()

    def test_fill_tmdb_frame(self, ttk, movie_gui_obj, monkeypatch):
        # Arrange
        ttk = MagicMock(name="ttk", autospec=True)
        monkeypatch.setattr(movies, "ttk", ttk)
        tmdb_frame = MagicMock(name="tmdb_frame", autospec=True)
        monkeypatch.setattr(movies.ttk, "Frame", tmdb_frame)
        tview = MagicMock(name="tview", autospec=True)
        monkeypatch.setattr(movies.ttk, "Treeview", tview)
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
                columns=(movies.TITLE, movies.YEAR, movies.DIRECTORS, movies.NOTES),
                show=["headings"],
                height=20,
                selectmode="browse",
            )
        with check:
            tview().column.assert_has_calls(
                [
                    call(movies.TITLE, width=250, stretch=True),
                    call(movies.YEAR, width=40, stretch=True),
                    call(movies.DIRECTORS, width=200, stretch=True),
                    call(movies.NOTES, width=400, stretch=True),
                ]
            )
        with check:
            tview().heading.assert_has_calls(
                [
                    call(movies.TITLE, text=movies.TITLE_TEXT, anchor="w"),
                    call(movies.YEAR, text=movies.YEAR_TEXT, anchor="w"),
                    call(movies.DIRECTORS, text=movies.DIRECTORS_TEXT, anchor="w"),
                    call(movies.NOTES, text=movies.NOTES_TEXT, anchor="w"),
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

    def test_initialize_tmdb_search(self, movie_gui_obj, monkeypatch):
        # Arrange
        match = "test_tmdb_search match"
        after = MagicMock(name="after", autospec=True)
        monkeypatch.setattr(movie_gui_obj.parent, "after", after)
        after_cancel = MagicMock(name="after_cancel", autospec=True)
        monkeypatch.setattr(movie_gui_obj.parent, "after_cancel", after_cancel)
        entry = MagicMock(name="entry", autospec=True)
        monkeypatch.setattr(movies.tk_facade, "Entry", entry)
        movie_gui_obj.entry_fields[movies.TITLE] = entry
        entry.current_value = match

        # Act
        movie_gui_obj.tmdb_search()

        # Assert
        with check:
            after_cancel.assert_not_called()
        with check:
            after.assert_called_once_with(
                movie_gui_obj.match_pause,
                movie_gui_obj.tmdb_callback,
                match,
                movie_gui_obj.tmdb_data_queue,
            )

    def test_subsequent_tmdb_search(self, movie_gui_obj, monkeypatch):
        # Arrange
        event_id = "42"
        movie_gui_obj.match_pause_id = event_id
        after_cancel = MagicMock(name="after_cancel", autospec=True)
        monkeypatch.setattr(movie_gui_obj.parent, "after_cancel", after_cancel)
        entry = MagicMock(name="entry", autospec=True)
        monkeypatch.setattr(movies.tk_facade, "Entry", entry)
        movie_gui_obj.entry_fields[movies.TITLE] = entry

        # Act
        movie_gui_obj.tmdb_search()

        # Assert
        with check:
            after_cancel.assert_called_once_with(event_id)

    def test_tmdb_consumer_with_empty_data_queue(self, movie_gui_obj, monkeypatch):
        # Arrange
        data_queue = MagicMock(name="data_queue", autospec=True)
        monkeypatch.setattr(movie_gui_obj, "tmdb_data_queue", data_queue)
        tview = MagicMock(name="tview", autospec=True)
        monkeypatch.setattr(movie_gui_obj, "tmdb_treeview", tview)
        after = MagicMock(name="after", autospec=True)
        monkeypatch.setattr(movie_gui_obj.parent, "after", after)
        movie_gui_obj.tmdb_data_queue.get_nowait.side_effect = movies.queue.Empty

        # Act
        movie_gui_obj.tmdb_consumer()

        # Assert
        with check:
            data_queue.get_nowait.assert_called_once_with()
        with check:
            tview.get_children.assert_not_called()
        with check:
            after.assert_called_once_with(
                movie_gui_obj.tmdb_consumer_poll, movie_gui_obj.tmdb_consumer
            )

    def test_tmdb_consumer_with_filled_data_queue(self, movie_gui_obj, monkeypatch):
        # Arrange
        title = "Test of test_tmdb_consumer_with_filled_data_queue"
        year = 4242
        directors_in = {"II", "GG", "HH"}
        directors_out = "GG, HH, II"
        notes = "A note"
        movie_bag = movies.MovieBag(
            title=title,
            year=movies.MovieInteger(year),
            directors=directors_in,
            notes=notes,
        )
        iid = "item id"
        expected = {iid: movie_bag}

        data_queue = MagicMock(name="data_queue", autospec=True)
        monkeypatch.setattr(movie_gui_obj, "tmdb_data_queue", data_queue)
        get_nowait = MagicMock(name="get_nowait", autospec=True)
        monkeypatch.setattr(movie_gui_obj.tmdb_data_queue, "get_nowait", get_nowait)
        get_nowait.return_value = [movie_bag]

        tview = MagicMock(name="tview", autospec=True)
        tview_content = ["Old title", "Old year", "Old directors"]
        tview.get_children.return_value = tview_content
        tview.insert.return_value = iid
        monkeypatch.setattr(movie_gui_obj, "tmdb_treeview", tview)
        after = MagicMock(name="after", autospec=True)
        monkeypatch.setattr(movie_gui_obj.parent, "after", after)
        movie_gui_obj.tmdb_movies["cuckoo"] = movies.MovieBag()

        # Act
        movie_gui_obj.tmdb_consumer()

        # Assert
        with check:
            data_queue.get_nowait.assert_called_once_with()
        with check:
            tview.get_children.assert_called_with()
        with check:
            tview.delete.assert_called_with(*tview_content)
        with check:
            tview.insert.assert_called_with(
                "",
                "end",
                values=(title, str(year), directors_out, notes),
            )
        check.equal(movie_gui_obj.tmdb_movies, expected)
        with check:
            after.assert_called_once_with(
                movie_gui_obj.tmdb_consumer_poll, movie_gui_obj.tmdb_consumer
            )

    @pytest.fixture(scope="function")
    def movie_gui_obj(self, tk, moviegui_post_init, monkeypatch):
        """Creates a MovieGUI object without running the __post_init__ method."""
        return movies.MovieGUI(
            tk.Tk(),
            tmdb_callback=self.tmdb_callback,
            all_tags=self.all_tags,
            prepopulate=self.prepopulate,
        )


# noinspection DuplicatedCode
class TestAddMovieGUI:
    """Tests for the AddMovieGUI class."""

    add_movie_callback = MagicMock(name="add_movie_callback", autospec=True)
    tmdb_callback = MagicMock(name="tmdb_callback", autospec=True)
    all_tags = set()
    prepopulate = MovieBag()

    def test_create_buttons(self, add_movie_obj, monkeypatch, ttk):
        # Arrange create_button
        create_button = MagicMock(name="create_button", autospec=True)
        monkeypatch.setattr(movies.common, "create_button", create_button)

        # Arrange buttonbox and commit button
        buttonbox = MagicMock(name="buttonbox", autospec=True)
        monkeypatch.setattr(ttk.Frame, "buttonbox", buttonbox)
        commit_button = MagicMock(name="commit_button", autospec=True)
        monkeypatch.setattr(movies.ttk, "Button", commit_button)
        create_button.return_value = commit_button

        # Arrange entry_fields for title and year
        title_entry_field = MagicMock(name="title_entry_field", autospec=True)
        monkeypatch.setattr(movies.tk_facade, "Entry", title_entry_field)
        add_movie_obj.entry_fields[movies.TITLE] = title_entry_field
        year_entry_field = MagicMock(name="year_entry_field", autospec=True)
        monkeypatch.setattr(movies.tk_facade, "Entry", year_entry_field)
        add_movie_obj.entry_fields[movies.YEAR] = year_entry_field

        # Arrange partial
        partial = MagicMock(name="partial", autospec=True)
        monkeypatch.setattr(movies, "partial", partial)

        # Arrange column number
        column_num = movies.count(42)

        # Act
        add_movie_obj.create_buttons(buttonbox, column_num)

        # Assert
        with check:
            create_button.assert_called_once_with(
                buttonbox,
                movies.COMMIT_TEXT,
                column=42,
                command=add_movie_obj.commit,
                default="normal",
            )
        with check:
            title_entry_field.observer.register.assert_called_once_with(
                partial(
                    add_movie_obj.enable_commit_button,
                    commit_button,
                    title_entry_field,
                    year_entry_field,
                )
            )
        with check:
            year_entry_field.observer.register.assert_called_once_with(
                partial(
                    add_movie_obj.enable_commit_button,
                    commit_button,
                    title_entry_field,
                    year_entry_field,
                )
            )

    def test_enable_commit_button(self, add_movie_obj, monkeypatch):
        # Arrange
        entry = MagicMock(name="entry", autospec=True)
        entry.title.has_data.return_value = True
        entry.year.has_data.return_value = False
        monkeypatch.setattr(movies.tk_facade, "Entry", entry)
        commit_button = MagicMock(name="commit_button", autospec=True)
        monkeypatch.setattr(movies.ttk, "Button", commit_button)
        enable_button = MagicMock(name="enable_button", autospec=True)
        monkeypatch.setattr(movies.common, "enable_button", enable_button)

        # Act
        add_movie_obj.enable_commit_button(commit_button, entry.title, entry.year)

        # Assert
        enable_button.assert_called_once_with(
            commit_button,
            state=entry.title.has_data() and entry.year.has_data(),
        )

    def test_commit(self, add_movie_obj, monkeypatch, tk):
        # Arrange clear_current_value
        entry = MagicMock(name="entry", autospec=True)
        monkeypatch.setattr(movies.tk_facade, "Entry", entry)
        add_movie_obj.entry_fields["title"] = entry

        # Arrange as_movie_bag
        as_movie_bag = MagicMock(name="as_movie_bag", autospec=True)
        as_movie_bag.return_value = movies.MovieBag(title=entry.current_value)
        monkeypatch.setattr(as_movie_bag, "as_movie_bag", as_movie_bag)

        # Arrange tview
        tview_content = ["Old title", "Old year", "Old directors"]
        tview = MagicMock(name="tview", autospec=True)
        tview.get_children.return_value = tview_content
        monkeypatch.setattr(movies.ttk, "Treeview", tview)
        add_movie_obj.tmdb_treeview = tview

        # Act
        add_movie_obj.commit()

        # Assert
        with check:
            self.add_movie_callback.assert_called_once_with(
                add_movie_obj.as_movie_bag()
            )
        with check:
            entry.clear_current_value.assert_called_once_with()
        with check:
            tview.get_children.assert_called_once_with()
        with check:
            tview.delete.assert_called_once_with(*tview_content)

    @pytest.fixture(scope="function")
    def add_movie_obj(self, tk, moviegui_post_init, monkeypatch):
        """Creates an AddMovieGUI object without running the __post_init__
        method.
        """
        return movies.AddMovieGUI(
            tk.Tk(),
            add_movie_callback=self.add_movie_callback,
            tmdb_callback=self.tmdb_callback,
            all_tags=self.all_tags,
            prepopulate=self.prepopulate,
        )


# noinspection DuplicatedCode
class TestEditMovieGUI:
    """Tests for the AddMovieGUI class."""

    edit_movie_callback = MagicMock(name="edit_movie_callback", autospec=True)
    delete_movie_callback = MagicMock(name="delete_movie_callback", autospec=True)
    tmdb_callback = MagicMock(name="tmdb_callback", autospec=True)
    all_tags = set()
    prepopulate = MovieBag()

    def test_create_buttons(self, edit_movie_obj, monkeypatch):
        # Arrange button box and buttons
        buttonbox = MagicMock(name="buttonbox", autospec=True)
        monkeypatch.setattr(movies.ttk, "Frame", buttonbox)
        button = MagicMock(name="button", autospec=True)
        monkeypatch.setattr(movies.ttk, "Button", button)
        create_button = MagicMock(name="create_button", autospec=True)
        create_button.return_value = button
        monkeypatch.setattr(movies.common, "create_button", create_button)
        column_num = movies.count()

        # Arrange entry_fields.
        entry = MagicMock(name="entry", autospec=True)
        monkeypatch.setattr(movies.tk_facade, "Entry", entry)
        monkeypatch.setitem(edit_movie_obj.entry_fields, movies.TITLE, entry)

        # Arrange enable_buttons and its partial call
        enable_buttons = MagicMock(name="enable_buttons", autospec=True)
        monkeypatch.setattr(edit_movie_obj, "enable_buttons", enable_buttons)
        partial = MagicMock(name="partial", autospec=True)
        monkeypatch.setattr(movies, "partial", partial)

        # Act
        edit_movie_obj.create_buttons(buttonbox, column_num)

        # Assert
        check.equal(
            create_button.call_args_list,
            [
                call(
                    buttonbox,
                    movies.COMMIT_TEXT,
                    column=0,
                    command=edit_movie_obj.commit,
                    default="disabled",
                ),
                call(
                    buttonbox,
                    movies.DELETE_TEXT,
                    column=1,
                    command=edit_movie_obj.delete,
                    default="active",
                ),
            ],
        )
        with check:
            partial.assert_called_once_with(enable_buttons, button, button)
        with check:
            entry.observer.register.assert_called_once_with(
                partial(enable_buttons, button, button)
            )

    def test_enable_buttons(self, edit_movie_obj, monkeypatch):
        # Arrange
        button = MagicMock(name="commit_button", autospec=True)
        monkeypatch.setattr(movies.ttk, "Button", button)

        enable_button = MagicMock(name="enable_button", autospec=True)
        monkeypatch.setattr(movies.common, "enable_button", enable_button)
        entry = MagicMock(name="entry", autospec=True)
        entry.has_data.return_value = True
        entry.changed.return_value = True
        monkeypatch.setattr(movies.tk_facade, "Entry", entry)
        edit_movie_obj.entry_fields[movies.TITLE] = entry
        edit_movie_obj.entry_fields[movies.YEAR] = entry

        # Act
        edit_movie_obj.enable_buttons(button, button)

        # Assert
        with check:
            enable_button.assert_has_calls(
                [
                    call(
                        button,
                        state=True,
                    ),
                    call(
                        button,
                        state=False,
                    ),
                ]
            )

    def test_commit(self, edit_movie_obj, monkeypatch):
        # Arrange
        after = MagicMock(name="after", autospec=True)
        monkeypatch.setattr(edit_movie_obj.parent, "after", after)
        destroy = MagicMock(name="destroy", autospec=True)
        monkeypatch.setattr(edit_movie_obj, "destroy", destroy)

        # Act
        edit_movie_obj.commit()

        # Assert
        with check:
            after.assert_called_once_with(
                0, self.edit_movie_callback, edit_movie_obj.as_movie_bag()
            )
        with check:
            destroy.assert_called_once_with()

    def test_delete(self, edit_movie_obj, monkeypatch):
        # Arrange
        after = MagicMock(name="after", autospec=True)
        monkeypatch.setattr(edit_movie_obj.parent, "after", after)
        destroy = MagicMock(name="destroy", autospec=True)
        monkeypatch.setattr(edit_movie_obj, "destroy", destroy)
        ask_yes_no = MagicMock(name="askyesno", autospec=True)
        monkeypatch.setattr(movies.messagebox, "askyesno", ask_yes_no)

        # Act
        edit_movie_obj.delete()

        # Assert
        with check:
            ask_yes_no.assert_called_once_with(
                message=movies.MOVIE_DELETE_MESSAGE,
                icon="question",
                parent=edit_movie_obj.parent,
            )
        with check:
            after.assert_called_once_with(0, self.delete_movie_callback)
        with check:
            destroy.assert_called_once_with()

    def test_delete_denied(self, edit_movie_obj, monkeypatch):
        # Arrange
        destroy = MagicMock(name="destroy", autospec=True)
        monkeypatch.setattr(edit_movie_obj, "destroy", destroy)
        ask_yes_no = MagicMock(name="askyesno", autospec=True)
        ask_yes_no.return_value = False
        monkeypatch.setattr(movies.messagebox, "askyesno", ask_yes_no)

        # Act
        edit_movie_obj.delete()

        # Assert
        with check:
            ask_yes_no.assert_called_once_with(
                message=movies.MOVIE_DELETE_MESSAGE,
                icon="question",
                parent=edit_movie_obj.parent,
            )
        with check:
            destroy.assert_not_called()

    @pytest.fixture(scope="function")
    def edit_movie_obj(self, tk, moviegui_post_init, monkeypatch):
        """Creates a MovieGUI object without running the __post_init__ method."""
        return movies.EditMovieGUI(
            tk.Tk(),
            edit_movie_callback=self.edit_movie_callback,
            delete_movie_callback=self.delete_movie_callback,
            tmdb_callback=self.tmdb_callback,
            all_tags=self.all_tags,
            prepopulate=self.prepopulate,
        )


# noinspection DuplicatedCode
class TestSearchMovieGUI:
    """Tests for the SearchMovieGUI class."""

    match_movie_callback = MagicMock(name="match_movie_callback", autospec=True)
    tmdb_callback = MagicMock(name="tmdb_callback", autospec=True)
    all_tags = set()
    prepopulate = MovieBag()

    def test_create_buttons(self, search_movie_obj, monkeypatch, ttk):
        # Arrange create_button
        create_button = MagicMock(name="create_button", autospec=True)
        monkeypatch.setattr(movies.common, "create_button", create_button)

        # Arrange buttonbox and commit button
        buttonbox = MagicMock(name="buttonbox", autospec=True)
        monkeypatch.setattr(ttk.Frame, "buttonbox", buttonbox)
        search_button = MagicMock(name="search_button", autospec=True)
        monkeypatch.setattr(movies.ttk, "Button", search_button)
        create_button.return_value = search_button

        # Arrange entry_fields for title and year
        entry_field = MagicMock(name="entry_field", autospec=True)
        monkeypatch.setattr(movies.tk_facade, "Entry", entry_field)
        search_movie_obj.entry_fields["dummy field name"] = entry_field

        # Arrange partial
        partial = MagicMock(name="partial", autospec=True)
        monkeypatch.setattr(movies, "partial", partial)

        # Arrange column number
        column_num = movies.count(42)

        # Act
        search_movie_obj.create_buttons(buttonbox, column_num)

        # Assert
        with check:
            create_button.assert_called_once_with(
                buttonbox,
                movies.SEARCH_TEXT,
                column=42,
                command=search_movie_obj.search,
                default="normal",
            )
        with check:
            entry_field.observer.register.assert_called_once_with(
                partial(
                    search_movie_obj.enable_search_button,
                    search_button,
                )
            )

    @pytest.mark.parametrize(
        "data_present, state",
        [
            (True, True),
            (False, False),
        ],
    )
    def test_enable_search_button(
        self, data_present, state, search_movie_obj, monkeypatch
    ):
        # Arrange data_present
        entry = MagicMock(name="entry", autospec=True)
        entry.changed.return_value = data_present
        monkeypatch.setattr(movies.tk_facade, "Entry", entry)
        search_movie_obj.entry_fields[movies.TITLE] = entry

        # Arrange search button
        search_button = MagicMock(name="search_button", autospec=True)
        monkeypatch.setattr(movies.ttk, "Button", search_button)

        # Arrange enable button
        enable_button = MagicMock(name="enable_button", autospec=True)
        monkeypatch.setattr(movies.common, "enable_button", enable_button)

        # Act
        search_movie_obj.enable_search_button(search_button)

        # Assert
        enable_button.assert_called_once_with(
            search_button,
            state=state,
        )

    def test_search(self, search_movie_obj, monkeypatch, tk):
        # Arrange
        after = MagicMock(name="after", autospec=True)
        monkeypatch.setattr(search_movie_obj.parent, "after", after)
        destroy = MagicMock(name="destroy", autospec=True)
        monkeypatch.setattr(search_movie_obj, "destroy", destroy)

        # Act
        search_movie_obj.search()

        # Assert
        with check:
            after.assert_called_once_with(
                0, self.match_movie_callback, search_movie_obj.as_movie_bag()
            )
        with check:
            destroy.assert_called_once_with()

    @pytest.fixture(scope="function")
    def search_movie_obj(self, tk, moviegui_post_init, monkeypatch):
        """Creates a SearchMovieGUI object without running the __post_init__
        method.
        """
        return movies.SearchMovieGUI(
            tk.Tk(),
            match_movie_callback=self.match_movie_callback,
            tmdb_callback=self.tmdb_callback,
            all_tags=self.all_tags,
            prepopulate=self.prepopulate,
        )


@pytest.fixture(scope="function")
def moviegui_post_init(monkeypatch):
    """Stops the MovieGUI.__post_init__ method from running."""
    monkeypatch.setattr(
        movies.MovieGUI,
        "__post_init__",
        lambda *args, **kwargs: None,
    )
