""" Test module. """

#  Copyright© 2025. Stephen Rigden.
#  Last modified 2/21/25, 6:49 AM by stephen.
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


import guiwidgets_2


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
