"""Test Module."""

#  Copyright© 2025. Stephen Rigden.
#  Last modified 5/3/25, 12:51 PM by stephen.
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

from collections.abc import Callable
import pytest
from pytest_check import check
from unittest.mock import MagicMock, call

from gui import settings


# noinspection DuplicatedCode
class TestSettings:
    """Tests for the Settings class."""

    tmdb_api_key: str = "test tmdb_api_key"
    use_tmdb: bool = False
    save_callback: Callable = MagicMock(name="save_callback")

    def test_post_init(self, monkeypatch):
        """Test Settings.__post_init__ correctly initializes the GUI.

        This test verifies that the __post_init__ method:
        1. Creates a Toplevel window
        2. Sets the window title
        3. Creates the body and buttonbox using create_body_and_buttonbox
        4. Calls the create_fields method to create input fields
        5. Calls the create_buttons method to create buttons

        Args:
            monkeypatch: Pytest fixture for patching dependencies
        """
        # Arrange Toplevel
        parent = MagicMock(name="parent", autospec=True)
        monkeypatch.setattr(settings.tk, "Tk", parent)
        toplevel = MagicMock(name="toplevel", autospec=True)
        monkeypatch.setattr(settings.tk, "Toplevel", toplevel)

        # Arrange create_body_and_buttonbox
        create_body_and_buttonbox = MagicMock(
            name="create_body_and_buttonbox", autospec=True
        )
        outer_frame = MagicMock(name="outer_frame")
        body_frame = MagicMock(name="body_frame", autospec=True)
        monkeypatch.setattr(settings.ttk, "Frame", body_frame)
        buttonbox = MagicMock(name="buttonbox", autospec=True)
        monkeypatch.setattr(settings.ttk, "Frame", buttonbox)
        create_body_and_buttonbox.return_value = (outer_frame, body_frame, buttonbox)
        monkeypatch.setattr(
            settings.common, "create_body_and_buttonbox", create_body_and_buttonbox
        )

        # Arrange fields and buttons
        create_fields = MagicMock(name="create_fields", autospec=True)
        monkeypatch.setattr(settings.Settings, "create_fields", create_fields)
        create_buttons = MagicMock(name="create_buttons", autospec=True)
        monkeypatch.setattr(settings.Settings, "create_buttons", create_buttons)

        # Act
        settings.Settings(
            parent,
            tmdb_api_key=self.tmdb_api_key,
            use_tmdb=self.use_tmdb,
            save_callback=self.save_callback,
        )

        # Assert
        with check:
            toplevel.assert_called_once_with(parent)
        with check:
            toplevel().title.assert_called_once_with(settings.WINDOW_TITLE)
        with check:
            create_body_and_buttonbox.assert_called_once_with(
                toplevel(),
                settings.Settings.__name__.lower(),
            )
        with check:
            create_fields.assert_called_once_with(body_frame)
        with check:
            create_buttons.assert_called_once_with(buttonbox)

    def test_create_fields(self, settings_obj, monkeypatch):
        # Arrange
        body_frame = MagicMock(name="body_frame", autospec=True)
        monkeypatch.setattr(settings.ttk, "Frame", body_frame)
        label_and_field = MagicMock(name="label_and_field", autospec=True)
        monkeypatch.setattr(settings.common, "LabelAndField", label_and_field)
        entry = MagicMock(name="entry", autospec=True)
        monkeypatch.setattr(settings.tk_facade, "Entry", entry)
        checkbutton = MagicMock(name="checkbutton", autospec=True)
        monkeypatch.setattr(settings.tk_facade, "Checkbutton", checkbutton)

        # Act
        settings_obj.create_fields(body_frame)

        # Assert input zone
        with check:
            label_and_field.assert_called_once_with(body_frame)

        # Assert TMDB API key field
        with check:
            entry.assert_called_once_with(settings.API_KEY_TEXT, body_frame)
        check.equal(
            settings_obj.entry_fields[settings.API_KEY_NAME].original_value,
            self.tmdb_api_key,
        )
        with check:
            label_and_field().add_entry_row.assert_called_once_with(
                settings_obj.entry_fields[settings.API_KEY_NAME]
            )

        # Assert 'Use TMDB' checkbutton
        with check:
            checkbutton.assert_called_once_with(settings.USE_TMDB_TEXT, body_frame)
        check.equal(
            settings_obj.entry_fields[settings.USE_TMDB_NAME].original_value,
            self.use_tmdb,
        )
        with check:
            label_and_field().add_checkbox_row.assert_called_once_with(
                settings_obj.entry_fields[settings.USE_TMDB_NAME]
            )

    def test_create_buttons(self, settings_obj, monkeypatch):
        # Arrange buttons
        buttonbox = MagicMock(name="buttonbox", autospec=True)
        monkeypatch.setattr(settings.ttk, "Frame", buttonbox)
        create_button = MagicMock(name="create_button", autospec=True)
        save_button = MagicMock(name="save_button", autospec=True)
        create_button.return_value = save_button
        monkeypatch.setattr(settings.common, "create_button", create_button)

        # Arrange entry fields
        widget = MagicMock(name="widget", autospec=True)
        monkeypatch.setattr(settings.tk_facade, "Entry", widget)
        monkeypatch.setitem(
            settings_obj.entry_fields,
            settings.SAVE_TEXT,
            widget,
        )
        monkeypatch.setitem(
            settings_obj.entry_fields,
            settings.CANCEL_TEXT,
            widget,
        )

        # Arrange partial, invoke, and bind.
        partial = MagicMock(name="partial", autospec=True)
        monkeypatch.setattr(settings, "partial", partial)
        invoke_button = MagicMock(name="invoke_button", autospec=True)
        monkeypatch.setattr(settings.common, "invoke_button", invoke_button)
        settings_obj.toplevel = toplevel = MagicMock(name="toplevel", autospec=True)
        monkeypatch.setattr(settings.tk, "Toplevel", toplevel)

        # Act
        settings_obj.create_buttons(buttonbox)

        # Assert
        check.equal(
            create_button.call_args_list,
            [
                call(
                    buttonbox,
                    settings.SAVE_TEXT,
                    column=0,
                    command=settings_obj.save,
                    default="disabled",
                ),
                call(
                    buttonbox,
                    settings.CANCEL_TEXT,
                    column=1,
                    command=settings_obj.destroy,
                    default="active",
                ),
            ],
        )
        check.equal(
            partial.call_args_list,
            [
                call(invoke_button, create_button()),
                call(invoke_button, create_button()),
                call(invoke_button, create_button()),
                call(invoke_button, create_button()),
                call(settings_obj.enable_save_button, save_button),
                call(settings_obj.enable_save_button, save_button),
            ],
        )
        check.equal(
            toplevel.bind.call_args_list,
            [
                call("<Return>", partial()),
                call("<KP_Enter>", partial()),
                call("<Escape>", partial()),
                call("<Command-.>", partial()),
            ],
        )
        check.equal(
            widget.observer.register.call_args_list,
            [call(partial()), call(partial())],
        )

    def test_enable_save_button(self, settings_obj, monkeypatch):
        # Arrange
        save_button = MagicMock(name="save_button", autospec=True)
        monkeypatch.setattr(settings.ttk, "Button", save_button)
        state = False

        # Arrange entry fields
        entry_field = MagicMock(name="entry_field", autospec=True)
        entry_field.changed.return_value = state
        monkeypatch.setattr(settings.tk_facade, "Entry", entry_field)
        monkeypatch.setitem(
            settings_obj.entry_fields,
            "test dummy",
            entry_field,
        )

        # Arrange enable_button
        enable_button = MagicMock(name="enable_button", autospec=True)
        monkeypatch.setattr(settings.common, "enable_button", enable_button)

        # Act
        settings_obj.enable_save_button(save_button)

        # Assert
        with check:
            entry_field.changed.assert_called_once_with()
        with check:
            enable_button.assert_called_once_with(save_button, state=state)

    def test_save(self, settings_obj, monkeypatch):
        # Arrange
        save_callback = MagicMock(name="save_callback", autospec=True)
        monkeypatch.setattr(settings_obj, "save_callback", save_callback)
        destroy = MagicMock(name="destroy", autospec=True)
        monkeypatch.setattr(settings_obj, "destroy", destroy)

        # Arrange entry fields
        api_key = MagicMock(name="api_key_name", autospec=True)
        monkeypatch.setattr(settings.tk_facade, "Entry", api_key)
        monkeypatch.setitem(settings_obj.entry_fields, settings.API_KEY_NAME, api_key)
        use_tmdb = MagicMock(name="use_tmdb_name", autospec=True)
        monkeypatch.setattr(settings.tk_facade, "Checkbutton", use_tmdb)
        monkeypatch.setitem(settings_obj.entry_fields, settings.USE_TMDB_NAME, use_tmdb)

        # Act
        settings_obj.save()

        # Assert
        with check:
            save_callback.assert_called_once_with(
                api_key.current_value,
                use_tmdb.current_value,
            )
        with check:
            destroy.assert_called_once_with()

    def test_destroy(self, settings_obj, monkeypatch):
        # Arrange
        toplevel = MagicMock(name="toplevel", autospec=True)
        monkeypatch.setattr(settings.tk, "Toplevel", toplevel)
        settings_obj.toplevel = toplevel()

        # Act
        settings_obj.destroy()

        # Assert
        # noinspection PyUnresolvedReferences
        settings_obj.toplevel.destroy.assert_called_once_with()

    @pytest.fixture(scope="function")
    def settings_obj(self, tk, ttk, monkeypatch):
        """Creates a Settings object without running its __post_init__ method."""
        monkeypatch.setattr(
            settings.Settings,
            "__post_init__",
            lambda *args, **kwargs: None,
        )
        # noinspection PyArgumentList
        return settings.Settings(
            settings.tk.Tk(),
            tmdb_api_key=self.tmdb_api_key,
            use_tmdb=self.use_tmdb,
            save_callback=self.save_callback,
        )
