"""Menu handlers.

This module is the glue between the user's selection of a menu item and the gui."""

#  Copyright© 2019. Stephen Rigden.
#  Last modified 11/9/19, 8:14 AM by stephen.
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

import config
import dialogs


def about_dialog():
    """Display the about dialog."""
    dialogs.ModalDialog(f'{config.app.name}', config.app.root_window, dict(ok='OK'),
                        f'{config.app.version}')()


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
