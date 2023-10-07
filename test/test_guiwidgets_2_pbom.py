""" Test._guiwidgets_<..>.

This module contains new tests written after Brian Okken's course and book on pytest in Fall 2022 together with
mocks from Python's unittest.mok module.

Test strategies are noted for each class but, in general, they test the interface with other code and not the
internal implementation of widgets.
"""

#  Copyright (c) 2023-2023. Stephen Rigden.
#  Last modified 10/7/23, 8:20 AM by stephen.
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

import pytest
from pytest_check import check

import guiwidgets_2

TEST_TITLE = 'test moviedb'
TEST_VERSION = 'Test version'


# noinspection PyMissingOrEmptyDocstring
class TestMovieGUI:
    """
    Test Strategy:
    __post_init__ Ensure initial values are set and calls to set up methods and functions are made with the correct
        arguments.
    """
    # todo  Complete docstring

    def test_post_init(self, monkeypatch):
        monkeypatch.setattr('guiwidgets_2._create_entry_fields', mock_create_entry_fields := MagicMock())
        monkeypatch.setattr('guiwidgets_2.MovieGUI.original_values', mock_original_values := MagicMock())
        monkeypatch.setattr('guiwidgets_2.MovieGUI.framing', mock_framing := MagicMock())
        mock_framing.return_value = [MagicMock(), body_frame := MagicMock(),
                                     mock_buttonbox := MagicMock(),
                                     mock_internet_frame := MagicMock()]
        monkeypatch.setattr('guiwidgets_2._InputZone', mock_inputzone := MagicMock())
        monkeypatch.setattr('guiwidgets_2._focus_set', mock_focus_set := MagicMock())
        monkeypatch.setattr('guiwidgets_2.MovieGUI.set_initial_tag_selection',
                            mock_set_initial_tag_selection := MagicMock())
        monkeypatch.setattr('guiwidgets_2.ttk.Treeview', mock_treeview := MagicMock())
        monkeypatch.setattr('guiwidgets_2.MovieGUI._create_buttons', mock_create_buttons := MagicMock())
        monkeypatch.setattr('guiwidgets_2.itertools.count', MagicMock())
        monkeypatch.setattr('guiwidgets_2._create_button', mock_create_button := MagicMock())
        monkeypatch.setattr('guiwidgets_2.MovieGUI.tmdb_consumer', mock_tmdb_consumer := MagicMock())

        with self.moviegui(monkeypatch) as cut:
            # Test initialize an internal dictionary.
            with check:
                mock_create_entry_fields.assert_called_once_with(guiwidgets_2.MOVIE_FIELD_NAMES,
                                                                 guiwidgets_2.MOVIE_FIELD_TEXTS)
            check.equal(cut.title, guiwidgets_2.MOVIE_FIELD_NAMES[0])
            with check:
                mock_original_values.assert_called_once_with()
            cut.entry_fields.fromkeys(guiwidgets_2.MOVIE_FIELD_NAMES)

            # Test create frames.
            with check:
                mock_framing.assert_called_once_with(cut.parent)
            with check:
                mock_inputzone.assert_called_once_with(body_frame)

            # Test create labels and entry widgets.
            check.equal(mock_inputzone().add_entry_row.call_count, 4)
            arg = cut.entry_fields['dummy']
            with check:
                mock_inputzone().add_entry_row.assert_has_calls([call(arg), call(arg), call(arg), call(arg)])
            with check:
                mock_focus_set.assert_called_once_with(cut.entry_fields[cut.title].widget)

            # Test create label and text widget.
            check.equal(mock_inputzone().add_text_row.call_count, 1)
            with check:
                mock_inputzone().add_text_row.assert_called_once_with(cut.entry_fields['dummy'])

            # Test create a label and treeview for movie tags.
            check.equal(mock_inputzone().add_treeview_row.call_count, 1)
            with check:
                mock_inputzone().add_treeview_row.assert_called_once_with(
                    'Tags', items=['test tag 1', 'test tag 2', 'test tag 3'],
                    callers_callback=cut.tags_treeview_callback)
            with check:
                mock_set_initial_tag_selection.assert_called_once_with()

            # Test create a treeview for movies retrieved from tmdb.
            with check:
                mock_treeview.assert_called_once_with(
                    mock_internet_frame, columns=('title', 'year', 'director'),
                    show=['headings'], height=20, selectmode='browse')
            check.equal(cut.tmdb_treeview.column.call_count, 3)
            with check:
                cut.tmdb_treeview.column.assert_has_calls([
                    call('title', width=300, stretch=True),
                    call('year', width=40, stretch=True),
                    call('director', width=200, stretch=True),
                    ])
            check.equal(cut.tmdb_treeview.heading.call_count, 3)
            with check:
                cut.tmdb_treeview.heading.assert_has_calls([
                    call('title', text='Title', anchor='w'),
                    call('year', text='Year', anchor='w'),
                    call('director', text='Director', anchor='w')
                    ])
            with check:
                cut.tmdb_treeview.grid.assert_called_once_with(column=0, row=0, sticky='nsew')
            with check:
                cut.tmdb_treeview.bind.assert_called_once_with('<<TreeviewSelect>>',
                                                               func=cut.tmdb_treeview_callback)

            # Test populate buttonbox with buttons.
            column_num = guiwidgets_2.itertools.count()
            with check:
                mock_create_buttons.assert_called_once_with(mock_buttonbox, column_num)
            with check:
                mock_create_button.assert_called_once_with(
                    mock_buttonbox, guiwidgets_2.CANCEL_TEXT, column=next(column_num),
                    command=cut.destroy, default='active')

            # Test start the tmdb_work_queue polling
            with check:
                mock_tmdb_consumer.assert_called_once_with()

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
