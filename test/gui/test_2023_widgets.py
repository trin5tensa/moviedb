""" Test module. """

#  Copyright© 2025. Stephen Rigden.
#  Last modified 2/18/25, 6:56 AM by stephen.
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

from contextlib import contextmanager
from unittest.mock import MagicMock, call

from pytest_check import check

import guiwidgets_2
from gui import common

TEST_TK_ROOT = "test tk_root"
TEST_TITLE = "test moviedb"
TEST_VERSION = "Test version"


# noinspection PyMissingOrEmptyDocstring
class TestCreateBodyAndButtonFrames:
    escape_key_callback = "test escape key callback"

    def test_framing(self, monkeypatch):
        monkeypatch.setattr("guiwidgets_2.ttk.Frame", mock_frame := MagicMock())
        mock_destroy = MagicMock(name="mock destroy")

        # noinspection PyArgumentList
        with self.create_frames(monkeypatch, mock_destroy) as fut:
            outer_frame, body_frame, buttonbox = fut
            check.equal(mock_frame.call_count, 3)
            check.equal(mock_frame().grid.call_count, 3)
            check.equal(mock_frame().columnconfigure.call_count, 1)
            with check:
                mock_frame.assert_has_calls(
                    [
                        call(
                            guiwidgets_2.config.current.tk_root,
                            name=self.escape_key_callback,
                        ),
                        call(outer_frame, padding=(10, 25, 10, 0)),
                        call(outer_frame, padding=(5, 5, 10, 10)),
                    ],
                    any_order=True,
                )
            check.equal(
                guiwidgets_2.config.current.escape_key_dict,
                {self.escape_key_callback: mock_destroy},
            )
            with check:
                outer_frame.assert_has_calls(
                    [
                        call.grid(column=0, row=0, sticky="nsew"),
                        call.columnconfigure(0, weight=1),
                    ]
                )
            with check:
                body_frame.grid.assert_has_calls([call(column=0, row=0, sticky="n")])
            with check:
                buttonbox.grid.assert_has_calls([call(column=0, row=1, sticky="e")])

    @contextmanager
    def create_frames(self, monkeypatch, mock_destroy):
        yield guiwidgets_2.create_body_and_button_frames(
            patch_config(monkeypatch).current.tk_root,
            self.escape_key_callback,
            mock_destroy,
        )


class TestGUIAskYesNo:
    def test_askyesno_called(self, monkeypatch):
        monkeypatch.setattr(
            guiwidgets_2.messagebox,
            "askyesno",
            mock_askyesno := MagicMock(name="mock_gui_askyesno"),
        )
        parent = MagicMock()
        message = "dummy message"

        guiwidgets_2.gui_askyesno(parent, message)
        mock_askyesno.assert_called_once_with(
            parent, message, detail="", icon="question", default="no"
        )


class TestEnableButton:
    def test_enable_button(self, monkeypatch):
        monkeypatch.setattr("guiwidgets_2.tk", MagicMock())
        monkeypatch.setattr("guiwidgets_2.ttk", mock_ttk := MagicMock())

        common.enable_button(mock_ttk.Button, state=True)
        common.enable_button(mock_ttk.Button, state=False)
        with check:
            mock_ttk.Button.assert_has_calls(
                [
                    call.state(["!disabled"]),
                    call.configure(default="active"),
                    call.state(["disabled"]),
                    call.configure(default="disabled"),
                ]
            )


# noinspection PyMissingOrEmptyDocstring
def patch_config(monkeypatch):
    dummy_current_config = guiwidgets_2.config.CurrentConfig()
    dummy_current_config.tk_root = MagicMock(name=TEST_TK_ROOT)
    dummy_current_config.escape_key_dict = guiwidgets_2.config.UserDict()
    dummy_persistent_config = guiwidgets_2.config.PersistentConfig(
        TEST_TITLE, TEST_VERSION
    )

    monkeypatch.setattr("guiwidgets_2.config", mock_config := MagicMock(name="config"))
    mock_config.current = dummy_current_config
    mock_config.persistent = dummy_persistent_config

    return mock_config
