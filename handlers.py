"""Menu handlers.

This module is the glue between the user's selection of a menu item and the gui."""

#  Copyright© 2019. Stephen Rigden.
#  Last modified 11/18/19, 7:56 AM by stephen.
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
from tkinter import filedialog, messagebox

import config
import dialogs
import impexp


def about_dialog():
    """Display the about dialog."""
    dialogs.ModalDialog(config.app.name, config.app.tk_root, dict(ok='OK'),
                        config.app.version)()
    # moviedb-#98
    #   tkinter.messagebox
    #   messagebox.showinfo(parent=config.app.tk_root, message=config.app.name,
    #                       detail=config.app.version)


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


def main():
    """Integration tests."""
    # Set up test environment.
    root = dialogs.tk.Tk()
    root.geometry('400x300+250+200')
    dialogs.tk.Label(root, text='Integration Test').pack()
    config.app = config.Config('Test program name', 'Test version 42.0.0.0')
    config.app.root_window = root
    
    # About Dialog.
    about_dialog()
    print('About dialog called.')


if __name__ == '__main__':
    sys.exit(main())
