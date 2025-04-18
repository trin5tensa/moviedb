"""test_handlers_pbo

This module contains new tests written after Brian Okken's course and book on
pytest in Fall 2022.
"""

#  Copyright© 2025. Stephen Rigden.
#  Last modified 4/18/25, 8:13 AM by stephen.
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

from gui import common


# noinspection PyMissingOrEmptyDocstring
class TestEscapeKeyDict:
    def test_dict_setitem_(self, check):
        test_func = MagicMock()
        ecd = common.EscapeKeyDict()
        ecd["one"] = test_func
        check.equal(ecd, {"one": test_func})
        ecd["two"] = test_func
        check.equal(ecd, {"one": test_func, "two": test_func})
        ecd["one"] = test_func
        check.equal(ecd, {"one": test_func, "two": test_func})

    # noinspection DuplicatedCode
    # @pytest.mark.skip
    def test_escape(self, mock_config_current, monkeypatch, check):
        # Create an EscapeKeyDict object and get a window closure.
        ecd = common.EscapeKeyDict()
        parent = mock_config_current.tk_root
        accelerator = "<Escape>"
        # noinspection PyTypeChecker
        closure = ecd.escape(accelerator)

        # Create a mock keypress event, logging and gui_messagebox.
        keypress_event = MagicMock()
        mock_logging = MagicMock()
        monkeypatch.setattr(common, "logging", mock_logging)
        showinfo = MagicMock(name="showinfo", autospec=True)
        monkeypatch.setattr(common, "showinfo", showinfo)

        # Test 'no valid name' error handling
        keypress_event.widget = ".!frame.!frame.!button"
        message = f"{ecd.accelerator_txt} {accelerator} {ecd.no_valid_name_txt}"
        closure(keypress_event)
        logging_msg = f"{message} {keypress_event.widget=}"
        with check:
            mock_logging.warning.assert_called_with(logging_msg)
        with check:
            showinfo.assert_called_with(
                ecd.internal_error_txt, detail=message, icon="warning"
            )

        # Test 'more than one valid name' error handling
        keypress_event.widget = ".!frame.valid name.valid name"
        message = f"{ecd.accelerator_txt} {accelerator} {ecd.gt1_valid_name_txt}"
        closure(keypress_event)
        logging_msg = f"{message} {keypress_event.widget=}"
        with check:
            mock_logging.warning.assert_called_with(logging_msg)
        with check:
            showinfo.assert_called_with(
                ecd.internal_error_txt, detail=message, icon="warning"
            )

        # Set up for call to method 'destroy'
        keypress_event.widget = ".!frame.valid name.!entry"
        mock_func = MagicMock()

        # Test destroy method called
        ecd.data = {"valid name": mock_func}
        closure(keypress_event)
        with check:
            mock_func.assert_called_once_with()

        # Test key error handling
        ecd.data = {"a different valid name": mock_func}
        closure(keypress_event)
        message = f"{ecd.accelerator_txt}  {accelerator} {ecd.key_error_text}"
        with check:
            mock_logging.warning.assert_called_with(f"{message} {ecd.data.keys()}")
        with check:
            showinfo.assert_called_with(
                ecd.internal_error_txt, detail=message, icon="warning"
            )

        # Test type error handling
        bad_callback = None
        ecd.data = {"valid name": bad_callback}
        closure(keypress_event)
        message = f"{ecd.type_error_text} {ecd.accelerator_txt.lower()}  {accelerator}."
        with check:
            mock_logging.warning.assert_called_with(
                f"{message} {ecd.data['valid name']}"
            )
        with check:
            showinfo.assert_called_with(
                ecd.internal_error_txt, detail=message, icon="warning"
            )
