""" Test._guiwidgets_<..>.

This module contains new tests written after Brian Okken's course and book on pytest in Fall 2022 together with
mocks from Python's unittest.mok module.

Test strategies are noted for each class but, in general, they test the interface with other code and not the
internal implementation of widgets.
"""

#  Copyright (c) 2023-2023. Stephen Rigden.
#  Last modified 10/2/23, 8:21 AM by stephen.
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
from unittest.mock import MagicMock

import pytest
from pytest_check import check

import guiwidgets_2

TEST_TITLE = 'test moviedb'
TEST_VERSION = 'Test version'


# noinspection PyMissingOrEmptyDocstring
class TestMovieGUI:
    """
    Test Strategy:
    """
    # todo  Complete docstring

    def test_post_init(self, monkeypatch):
        monkeypatch.setattr('guiwidgets_2._create_entry_fields', mock_create_entry_fields := MagicMock())
        monkeypatch.setattr('guiwidgets_2.MovieGUI.original_values', mock_original_values := MagicMock())
        monkeypatch.setattr('guiwidgets_2.MovieGUI.framing', mock_framing := MagicMock())
        mock_framing.return_value = [MagicMock(), body_frame := MagicMock(), MagicMock(), MagicMock()]
        monkeypatch.setattr('guiwidgets_2._InputZone', mock_inputzone := MagicMock())

        with self.moviegui(monkeypatch) as cut:
            # Test initialize an internal dictionary to simplify field data management.
            with check:
                mock_create_entry_fields.assert_called_once_with(guiwidgets_2.MOVIE_FIELD_NAMES,
                                                                 guiwidgets_2.MOVIE_FIELD_TEXTS)
            check.equal(cut.title, guiwidgets_2.MOVIE_FIELD_NAMES[0])
            with check:
                mock_original_values.assert_called_once_with()

            # Test create frames to hold fields and buttons.
            with check:
                mock_framing.assert_called_once_with(cut.parent)
            with check:
                mock_inputzone.assert_called_once_with(body_frame)

            # Test create labels and entry widgets.
            print(f'\n{guiwidgets_2.MOVIE_FIELD_NAMES=}')
            print(f'{cut.entry_fields=}')
            # daybreak
            assert False

    @contextmanager
    def moviegui(self, monkeypatch):
        current_config = guiwidgets_2.config.CurrentConfig()
        current_config.tk_root = MagicMock()
        persistent_config = guiwidgets_2.config.PersistentConfig(TEST_TITLE, TEST_VERSION)

        monkeypatch.setattr('mainwindow.config', mock_config := MagicMock())
        mock_config.current = current_config
        mock_config.persistent = persistent_config

        # noinspection PyTypeChecker
        yield guiwidgets_2.MovieGUI(current_config.tk_root,
                                    tmdb_search_callback=MagicMock(),
                                    all_tags=['test tag 1', 'test tag 2', 'test tag 3', ])


class TestAddMovieGUI:
    """
    Test Strategy:
    """
    # todo


class TestEditMovieGUI:
    """
    Test Strategy:
    """
    # todo


class TestAddTagGUI:
    """
    Test Strategy:
    """
    # todo


class TestEditTagGUI:
    """
    Test Strategy:
    """
    # todo


class TestSearchTagGUI:
    """
    Test Strategy:
    """
    # todo


class TestSelectTagGUI:
    """
    Test Strategy:
    """
    # todo


class TestPreferencesGUI:
    """
    Test Strategy:
    """
    # todo


class TestCreateBodyAndButtonFrames:
    """
    Test Strategy:
    """
    # todo


@pytest.mark.skip('Rewrite')
class TestGUIAskYesNo:
    def test_askyesno_called(self, monkeypatch):
        # askyesno = MagicMock(name='mock_gui_askyesno')
        # monkeypatch.setattr(guiwidgets_2.messagebox, 'askyesno', askyesno)
        # parent = DummyTk()
        # message = 'dummy message'
        #
        # # noinspection PyTypeChecker
        # guiwidgets_2.gui_askyesno(parent, message)
        #
        # askyesno.assert_called_once_with(parent, message, detail='', icon='question')
        ...


class TestInputZone:
    """
    Test Strategy:
    """
    # todo
