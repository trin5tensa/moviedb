"""Test Module."""

#  Copyright© 2025. Stephen Rigden.
#  Last modified 4/19/25, 1:55 PM by stephen.
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

from gui import tags


# noinspection PyMissingOrEmptyDocstring
class TestTagGUI:
    def test_post_init(self, tk, ttk, monkeypatch):
        """Test that TagGUI.__post_init__ correctly initializes the GUI.

        This test verifies that the __post_init__ method:
        1. Creates the body and buttonbox using create_body_and_buttonbox
        2. Sets the outer_frame attribute
        3. Calls the user_input_frame method to create input widgets
        4. Calls the create_buttons method to create buttons
        5. Initializes button enablements using init_button_enablements

        Args:
            tk: Mock for tkinter module
            ttk: Mock for tkinter.ttk module
            monkeypatch: Pytest fixture for patching dependencies
        """
        # Arrange
        name = tags.TagGUI.__name__.lower()
        create_body_and_buttonbox = MagicMock(
            name="create_body_and_buttonbox",
            autospec=True,
        )
        outer_frame = MagicMock(name="outer_frame", autospec=True)
        body_frame = MagicMock(name="body_frame", autospec=True)
        buttonbox = MagicMock(name="buttonbox", autospec=True)
        create_body_and_buttonbox.return_value = (
            outer_frame,
            body_frame,
            buttonbox,
        )
        monkeypatch.setattr(
            tags.common,
            "create_body_and_buttonbox",
            create_body_and_buttonbox,
        )
        user_input_frame = MagicMock(name="user_input_frame", autospec=True)
        monkeypatch.setattr(tags.TagGUI, "user_input_frame", user_input_frame)
        create_buttons = MagicMock(name="create_buttons", autospec=True)
        monkeypatch.setattr(tags.TagGUI, "create_buttons", create_buttons)
        init_button_enablements = MagicMock(
            name="init_button_enablements",
            autospec=True,
        )
        monkeypatch.setattr(
            tags.common, "init_button_enablements", init_button_enablements
        )

        # Act
        tag_gui = tags.TagGUI(tk)

        # Assert
        with check:
            create_body_and_buttonbox.assert_called_once_with(tk, name)
        check.equal(tag_gui.outer_frame, outer_frame)
        with check:
            user_input_frame.assert_called_once_with(body_frame)
        with check:
            create_buttons.assert_called_once_with(buttonbox)
        with check:
            init_button_enablements.assert_called_once_with(tag_gui.entry_fields)

    def test_user_input_frame(self, tk, ttk, taggui_post_init, monkeypatch):
        # Arrange
        tag = "tag for test_user_input_frame"
        tag_gui = tags.TagGUI(tk, tag)

        body_frame = MagicMock(name="body_frame", autospec=True)
        label_and_field = MagicMock(name="label_and_field", autospec=True)
        monkeypatch.setattr(tags.common, "LabelAndField", label_and_field)
        entry = MagicMock(name="entry", autospec=True)
        monkeypatch.setattr(tags, "Entry", entry)

        # Act
        tag_gui.user_input_frame(body_frame)

        # Assert
        with check:
            label_and_field.assert_called_once_with(body_frame)
        with check:
            entry.assert_called_once_with(tags.MOVIE_TAGS_TEXT, body_frame)
        check.equal(tag_gui.entry_fields[tags.MOVIE_TAGS], entry())
        check.equal(
            tag_gui.entry_fields[tags.MOVIE_TAGS].original_value,
            tag,
        )
        with check:
            label_and_field().add_entry_row.assert_called_once_with(
                tag_gui.entry_fields[tags.MOVIE_TAGS]
            )
        with check:
            # noinspection PyUnresolvedReferences
            tag_gui.entry_fields[
                tags.MOVIE_TAGS
            ].widget.focus_set.assert_called_once_with()

    def test_create_buttons(self, tk, ttk, taggui_post_init, monkeypatch):
        # Arrange
        tag = "tag for test_user_input_frame"
        tag_gui = tags.TagGUI(tk, tag)
        body_frame = MagicMock(name="body_frame", autospec=True)

        # Act
        with check.raises(NotImplementedError):
            tag_gui.create_buttons(body_frame)

    def test_destroy(self, tk, ttk, taggui_post_init, monkeypatch):
        # Arrange
        tag = "tag for test_destroy"
        tag_gui = tags.TagGUI(tk, tag)
        outer_frame = MagicMock(name="outer_frame", autospec=True)
        monkeypatch.setattr(tag_gui, "outer_frame", outer_frame)

        # Act
        tag_gui.destroy()

        # Assert
        with check:
            # noinspection PyUnresolvedReferences
            tag_gui.outer_frame.destroy.assert_called_once_with()


# noinspection PyMissingOrEmptyDocstring, DuplicatedCode
class TestAddTagGUI:
    def test_create_buttons(self, tk, ttk, taggui_post_init, monkeypatch):
        # Arrange
        tag = "tag for test_create_buttons"
        add_tag_callback = MagicMock(name="add_tag_callback", autospec=True)
        add_tag = tags.AddTagGUI(tk, tag, add_tag_callback=add_tag_callback)

        create_button = MagicMock(name="create_button", autospec=True)
        commit_button = "commit button"
        create_button.return_value = commit_button
        monkeypatch.setattr(tags.common, "create_button", create_button)

        buttonbox = MagicMock(name="buttonbox", autospec=True)
        monkeypatch.setattr(tags.ttk, "Frame", buttonbox)
        column_num = tags.itertools.count()
        partial = MagicMock(name="partial", autospec=True)
        monkeypatch.setattr(tags, "partial", partial)
        tag_entry_field = MagicMock(name="tag_entry_field", autospec=True)
        add_tag.entry_fields[tags.MOVIE_TAGS] = tag_entry_field

        # Act
        add_tag.create_buttons(buttonbox)

        # Assert
        with check:
            create_button.assert_has_calls(
                [
                    call(
                        buttonbox,
                        tags.COMMIT_TEXT,
                        column=next(column_num),
                        command=add_tag.commit,
                        default="disabled",
                    ),
                    call(
                        buttonbox,
                        tags.CANCEL_TEXT,
                        column=next(column_num),
                        command=add_tag.destroy,
                        default="active",
                    ),
                ]
            )
        with check:
            partial.assert_called_once_with(
                add_tag.enable_button_callback,
                commit_button,
                tag_entry_field,
            )
        with check:
            tag_entry_field.observer.register.assert_called_once_with(
                partial(),
            )

    def test_enable_button_callback(self, tk, ttk, taggui_post_init, monkeypatch):
        # Arrange
        tag = "tag for test_enable_button_callback"
        add_tag_callback = MagicMock(name="add_tag_callback", autospec=True)
        add_tag = tags.AddTagGUI(tk, tag, add_tag_callback=add_tag_callback)
        enable_button = MagicMock(name="enable_button", autospec=True)
        monkeypatch.setattr(tags.common, "enable_button", enable_button)
        commit_button = MagicMock(name="commit_button", autospec=True)
        tag_entry_field = MagicMock(name="tag_entry_field", autospec=True)
        add_tag.entry_fields[tags.MOVIE_TAGS] = tag_entry_field

        # Act
        add_tag.enable_button_callback(commit_button, tag_entry_field)

        # Assert
        with check:
            enable_button.assert_called_once_with(
                commit_button, state=tag_entry_field.has_data()
            )

    def test_commit(self, tk, ttk, taggui_post_init, monkeypatch):
        # Arrange
        tag = "tag for test_commit"
        add_tag_callback = MagicMock(name="add_tag_callback", autospec=True)
        add_tag = tags.AddTagGUI(tk, tag, add_tag_callback=add_tag_callback)
        tag_entry_field = MagicMock(name="tag_entry_field", autospec=True)
        tag_entry_field.current_value = tag
        add_tag.entry_fields[tags.MOVIE_TAGS] = tag_entry_field
        destroy = MagicMock(name="destroy", autospec=True)
        monkeypatch.setattr(add_tag, "destroy", destroy)

        # Act
        add_tag.commit()

        # Assert
        with check:
            tk.after.assert_called_once_with(0, add_tag_callback, tag)
        with check:
            # noinspection PyUnresolvedReferences
            add_tag.destroy.assert_called_once_with()


# noinspection PyMissingOrEmptyDocstring
class TestEditTagGUI:
    def test_create_buttons(self, tk, ttk, taggui_post_init, monkeypatch):
        # Arrange
        tag = "edit tag for test_create_buttons"
        edit_tag_callback = MagicMock(
            name="edit_tag_callback",
            autospec=True,
        )
        delete_tag_callback = MagicMock(
            name="delete_tag_callback",
            autospec=True,
        )
        edit_tag = tags.EditTagGUI(
            tk,
            tag,
            edit_tag_callback=edit_tag_callback,
            delete_tag_callback=delete_tag_callback,
        )

        create_button = MagicMock(name="create_button", autospec=True)
        commit_button = MagicMock(name="commit_button", autospec=True)
        delete_button = MagicMock(name="delete_button", autospec=True)
        create_button.side_effect = [commit_button, delete_button, "unused"]
        # noinspection DuplicatedCode
        monkeypatch.setattr(tags.common, "create_button", create_button)

        buttonbox = MagicMock(name="buttonbox", autospec=True)
        monkeypatch.setattr(tags.ttk, "Frame", buttonbox)
        column_num = tags.itertools.count()
        partial = MagicMock(name="partial", autospec=True)
        monkeypatch.setattr(tags, "partial", partial)
        tag_entry_field = MagicMock(name="tag_entry_field", autospec=True)
        edit_tag.entry_fields[tags.MOVIE_TAGS] = tag_entry_field

        # Act
        edit_tag.create_buttons(buttonbox)

        # Assert
        with check:
            create_button.assert_has_calls(
                [
                    call(
                        buttonbox,
                        tags.COMMIT_TEXT,
                        column=next(column_num),
                        command=edit_tag.commit,
                        default="disabled",
                    ),
                    call(
                        buttonbox,
                        tags.DELETE_TEXT,
                        column=next(column_num),
                        command=edit_tag.delete,
                        default="active",
                    ),
                    call(
                        buttonbox,
                        tags.CANCEL_TEXT,
                        column=next(column_num),
                        command=edit_tag.destroy,
                        default="active",
                    ),
                ]
            )
        with check:
            partial.assert_called_once_with(
                edit_tag.enable_button_callback,
                commit_button,
                delete_button,
                tag_entry_field,
            )
        with check:
            tag_entry_field.observer.register.assert_called_once_with(
                partial(),
            )

    def test_enable_button_callback(self, tk, ttk, taggui_post_init, monkeypatch):
        # Arrange
        tag = "edit tag for test_enable_button_callback"
        edit_tag_callback = MagicMock(
            name="edit_tag_callback",
            autospec=True,
        )
        delete_tag_callback = MagicMock(
            name="delete_tag_callback",
            autospec=True,
        )
        edit_tag = tags.EditTagGUI(
            tk,
            tag,
            edit_tag_callback=edit_tag_callback,
            delete_tag_callback=delete_tag_callback,
        )
        enable_button = MagicMock(name="enable_button", autospec=True)
        monkeypatch.setattr(tags.common, "enable_button", enable_button)
        commit_button = MagicMock(name="commit_button", autospec=True)
        delete_button = MagicMock(name="delete_button", autospec=True)
        tag_entry_field = MagicMock(name="tag_entry_field", autospec=True)
        edit_tag.entry_fields[tags.MOVIE_TAGS] = tag_entry_field

        # Act
        edit_tag.enable_button_callback(
            commit_button,
            delete_button,
            tag_entry_field,
        )

        # Assert
        with check:
            enable_button.assert_has_calls(
                [
                    call(commit_button, state=tag_entry_field.has_data()),
                    call(delete_button, state=tag_entry_field.has_data()),
                ]
            )

    def test_commit(self, tk, ttk, taggui_post_init, monkeypatch):
        # Arrange
        tag = "edit tag for test_commit"
        edit_tag_callback = MagicMock(name="edit_tag_callback", autospec=True)
        delete_tag_callback = MagicMock(name="delete_tag_callback", autospec=True)
        edit_tag = tags.EditTagGUI(
            tk,
            tag,
            edit_tag_callback=edit_tag_callback,
            delete_tag_callback=delete_tag_callback,
        )
        tag_entry_field = MagicMock(name="tag_entry_field", autospec=True)
        tag_entry_field.current_value = tag
        edit_tag.entry_fields[tags.MOVIE_TAGS] = tag_entry_field
        destroy = MagicMock(name="destroy", autospec=True)
        monkeypatch.setattr(edit_tag, "destroy", destroy)

        # Act
        edit_tag.commit()

        # Assert
        with check:
            tk.after.assert_called_once_with(0, edit_tag.edit_tag_callback, tag)
        with check:
            # noinspection PyUnresolvedReferences
            edit_tag.destroy.assert_called_once_with()

    def test_user_confirms_delete(self, tk, ttk, taggui_post_init, monkeypatch):
        # Arrange
        tag = "edit tag for test_commit"
        edit_tag_callback = MagicMock(name="edit_tag_callback", autospec=True)
        delete_tag_callback = MagicMock(name="delete_tag_callback", autospec=True)
        edit_tag = tags.EditTagGUI(
            tk,
            tag,
            edit_tag_callback=edit_tag_callback,
            delete_tag_callback=delete_tag_callback,
        )
        messagebox = MagicMock(name="messagebox", autospec=True)
        monkeypatch.setattr(tags, "messagebox", messagebox)
        destroy = MagicMock(name="destroy", autospec=True)
        monkeypatch.setattr(edit_tag, "destroy", destroy)

        # Act
        edit_tag.delete()

        # Assert
        with check:
            messagebox.askyesno.assert_called_once_with(
                message=f"{tags.TAG_DELETE_MESSAGE}",
                icon="question",
                default="no",
                parent=edit_tag.parent,
            )
        with check:
            tk.after.assert_called_once_with(0, edit_tag.delete_tag_callback)
        with check:
            # noinspection PyUnresolvedReferences
            edit_tag.destroy.assert_called_once_with()

    def test_user_declines_delete(self, tk, ttk, taggui_post_init, monkeypatch):
        # Arrange
        tag = "edit tag for test_commit"
        edit_tag_callback = MagicMock(name="edit_tag_callback", autospec=True)
        delete_tag_callback = MagicMock(name="delete_tag_callback", autospec=True)
        edit_tag = tags.EditTagGUI(
            tk,
            tag,
            edit_tag_callback=edit_tag_callback,
            delete_tag_callback=delete_tag_callback,
        )
        messagebox = MagicMock(name="messagebox", autospec=True)
        messagebox.askyesno.return_value = False
        monkeypatch.setattr(tags, "messagebox", messagebox)
        tag_entry_field = MagicMock(name="tag_entry_field", autospec=True)
        tag_entry_field.current_value = tag
        edit_tag.entry_fields[tags.MOVIE_TAGS] = tag_entry_field

        # Act
        edit_tag.delete()

        # Assert
        check.equal(
            edit_tag.entry_fields[tags.MOVIE_TAGS].original_value,
            edit_tag.tag,
        )
        with check:
            tag_entry_field.widget.focus_set.assert_called_once_with()


# noinspection PyMissingOrEmptyDocstring, DuplicatedCode
class TestSearchTagGUI:
    def test_create_buttons(self, tk, ttk, taggui_post_init, monkeypatch):
        # Arrange
        tag = "search tag for test_create_buttons"
        search_tag_callback = MagicMock(name="search_tag_callback", autospec=True)
        search_tag = tags.SearchTagGUI(tk, tag, search_tag_callback=search_tag_callback)

        create_button = MagicMock(name="create_button", autospec=True)
        search_button = "search button"
        create_button.return_value = search_button
        monkeypatch.setattr(tags.common, "create_button", create_button)

        buttonbox = MagicMock(name="buttonbox", autospec=True)
        monkeypatch.setattr(tags.ttk, "Frame", buttonbox)
        column_num = tags.itertools.count()
        partial = MagicMock(name="partial", autospec=True)
        monkeypatch.setattr(tags, "partial", partial)
        tag_entry_field = MagicMock(name="tag_entry_field", autospec=True)
        search_tag.entry_fields[tags.MOVIE_TAGS] = tag_entry_field

        # Act
        search_tag.create_buttons(buttonbox)

        # Assert
        with check:
            create_button.assert_has_calls(
                [
                    call(
                        buttonbox,
                        tags.SEARCH_TEXT,
                        column=next(column_num),
                        command=search_tag.search,
                        default="disabled",
                    ),
                    call(
                        buttonbox,
                        tags.CANCEL_TEXT,
                        column=next(column_num),
                        command=search_tag.destroy,
                        default="active",
                    ),
                ]
            )
        with check:
            partial.assert_called_once_with(
                search_tag.enable_button_callback,
                search_button,
                tag_entry_field,
            )
        with check:
            tag_entry_field.observer.register.assert_called_once_with(
                partial(),
            )

    def test_enable_button_callback(self, tk, ttk, taggui_post_init, monkeypatch):
        # Arrange
        tag = "tag for test_enable_button_callback"
        search_tag_callback = MagicMock(name="search_tag_callback", autospec=True)
        search_tag = tags.SearchTagGUI(tk, tag, search_tag_callback=search_tag_callback)
        enable_button = MagicMock(name="enable_button", autospec=True)
        monkeypatch.setattr(tags.common, "enable_button", enable_button)
        search_button = MagicMock(name="search_button", autospec=True)
        tag_entry_field = MagicMock(name="tag_entry_field", autospec=True)
        search_tag.entry_fields[tags.MOVIE_TAGS] = tag_entry_field

        # Act
        search_tag.enable_button_callback(search_button, tag_entry_field)

        # Assert
        with check:
            enable_button.assert_called_once_with(
                search_button, state=tag_entry_field.has_data()
            )

    def test_commit(self, tk, ttk, taggui_post_init, monkeypatch):
        # Arrange
        tag = "search tag for test_commit"
        search_tag_callback = MagicMock(name="search_tag_callback", autospec=True)
        search_tag = tags.SearchTagGUI(tk, tag, search_tag_callback=search_tag_callback)
        tag_entry_field = MagicMock(name="tag_entry_field", autospec=True)
        tag_entry_field.current_value = tag
        search_tag.entry_fields[tags.MOVIE_TAGS] = tag_entry_field
        destroy = MagicMock(name="destroy", autospec=True)
        monkeypatch.setattr(search_tag, "destroy", destroy)

        # Act
        search_tag.search()

        # Assert
        with check:
            tk.after.assert_called_once_with(0, search_tag_callback, tag)
        with check:
            # noinspection PyUnresolvedReferences
            search_tag.destroy.assert_called_once_with()


@pytest.fixture(scope="function")
def taggui_post_init(monkeypatch):
    """Stops the TagGUI.__post_init__ from running."""
    monkeypatch.setattr(
        tags.TagGUI,
        "__post_init__",
        lambda *args, **kwargs: None,
    )
