"""Menu handlers.

This module is the glue between the user's selection of a menu item and the gui."""

#  Copyright© 2019. Stephen Rigden.
#  Last modified 12/12/19, 12:34 PM by stephen.
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys
# TODO Move all tkinter calls to guiwidgets module
from tkinter import Button, Tk, filedialog, messagebox
from typing import Sequence

import config
import database
import guiwidgets
import impexp


def about_dialog():
    """Display the about dialog."""
    messagebox.showinfo(parent=config.app.tk_root, message=config.app.name,
                        detail=config.app.version)


def add_movie():
    # moviedb-#94 Test this function
    tags = database.all_tags()
    guiwidgets.MovieGUI(config.app.tk_root, tags, add_movie_callback)


def add_movie_callback(movie: config.MovieDict, tags: Sequence[str]):
    # moviedb-#94 Error handling:
    #   Here for SQL
    #       Non-unique title and year combination
    #       Invalid year (>1877 and <10000)
    #   Give warning to user if errors and pass boolean fail back to caller
    # moviedb-#94 Test this function
    
    database.add_movie(movie)
    
    # TODO Remove note when fixed
    #   Pycharm reported bug:  https://youtrack.jetbrains.com/issue/PY-39404
    movies = (config.MovieKeyDict(title=movie['title'], year=movie['year']),)
    for tag in tags:
        database.add_tag_and_links(tag, movies)


def import_movies():
    """Open a csv file and load the contents into the database."""
    csv_fn = filedialog.askopenfilename(parent=config.app.tk_root,
                                        filetypes=(('Movie import files', '*.csv'),))
    try:
        impexp.import_movies(csv_fn)
    except impexp.MoviedbInvalidImportData as exc:
        messagebox.showinfo(parent=config.app.tk_root,
                            message='Errors were found in the input file.',
                            detail=exc.args[0], icon='warning')


def test_about_dialog():
    """Integration tests."""
    # Set up test environment.
    root = Tk()
    print()
    print(f"{root=}")
    root.geometry('400x300+250+200')
    Button(root, text='Integration Test').pack()
    config.app = config.Config('Test program name', 'Test version 42.0.0.0')
    config.app.tk_root = root
    
    # About Dialog.
    about_dialog()
    print('About dialog called.')


if __name__ == '__main__':
    sys.exit(test_about_dialog())
