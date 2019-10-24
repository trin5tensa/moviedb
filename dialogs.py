"""Manager of tkinter dialogs."""

#  Copyright© 2019. Stephen Rigden.
#  Last modified 10/24/19, 1:57 PM by stephen.
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
import tkinter as tk
import tkinter.ttk as ttk
# TODO Update module title and description
# TODO Remove layout reminder comments.
# TODO Remove the functions main() and suite beginning "if __name__ == '__main__'" if not needed.
# Python package imports
from dataclasses import dataclass
from typing import Callable, Dict, Optional, TypeVar


# Third party package imports


# Project Imports


# Constants
BODY_PADDING = '2m'

# Pure data Dataclasses & Named tuples
FocuseeWidget = TypeVar('FocuseeWidget', ttk.Entry, ttk.Button)


# API Classes


# API Functions


# Internal Module Classes
@dataclass
class Dialog:
    """This class provides the core functionality for a modal dialog.

    It offers two vertically arranged frames which are seen by the user. The lower is the
    buttonbox and this contains the buttons defined by the caller. The upper is
    the body frame which is undefined in this base class. Subclasses are required and should
    define the content of the body frame as a minimum.

    If called the class will return the button clicked by the user.

    Size
    ----
    The size of the dialog window is fixed and will be made large enough to display all of the
    widgets which it contains. A convenience method,
    'make_resizable', is available for subclasses. See its documentation for details.

    Placement
    ---------
    The dialog is centered on the parent window. If this causes the dialog to either be
    off screen at the top or off screen at the left it will be moved down or to the right
    respectively. Note thia assumes the dialog window will fit on the screen. If a subclass
    creates a window that is too large then that subclass is responsible for handling the
    excess,

    Internal Frames
    ---------------
    The method 'create_widgets' creates a body frame and a buttonbox frame placed vertically
    beneath it. Override create_widgets to create other configurations.

    Focus
    -----
    Set initial focus to a widget by returning an optional focus widget from the body method.
    If the  body method returns None then return an optional focus widget from the buttonbox
    method.
    If neither method returns a focus widget the dialog will take focus for itself. If both
    methods return widgets the body widget will get focus.

    Body
    ----
    Override the body method to create content for the body of the dialog. This can be as
    simple as a line of text for a simple alert dialog or a complex hierarchy of widgets.

    Buttonbox and Buttons
    ---------------------
    The caller can determine the number of buttons and their internal names. Each button
    must have labels which are the text seen by the user.

        Cancel Button and Other Cancel Actions
        --------------------------------------
        The rightmost button will close the dialog without taking any further action. The
        rightmost button will be returned to the user if the user cancels by either clicking
        the rightmost button, pressing the <Escape> key, or clicking the window's close button.
        The rightmost button will get focus unless an overriding subclass sets focus to a widget in
        the dialog body.

        Other buttons
        -------------
        All other buttons will call the substantive method. This calls the methods validate
        and keep_alive. Subclasses may override these methods if they wish to:
            Implement a validation method or
            Carry out button action processing including conditionally closing the window
            depending on which button is clicked.

        Button enabled/disabled status
        -------------------------------
        The caller does not have access to change the enabled state of buttons.

        If changes to the enabled state are desired before the dialog is closed and control is
        returned to the caller this class will need to be subclassed. The subclass will
        have to intercept events and switch the buttons' enabled status.


    The module is based on Fredrik Lundh's "An Introduction to Tkinter" November 2005.
    (http://effbot.org/tkinterbook/tkinter-dialog-windows.htm) For testability, however, the
    tk classes are not a superclass of Dialog but are implemented as attributes.
    """
    
    # Tkinter parent widget
    parent: ttk.Frame
    # Key: Internal button name used by program. e.g. ok, cancel
    # Value: Button label seen by user. e.g. OK, Cancel
    button_labels: Dict[str, str]
    window_title: Optional[str] = None
    
    def __post_init__(self):
        # Organize the buttons
        self.buttons = {name: Button(label) for name, label in self.button_labels.items()}
        # Set the rightmost button as the 'cancel dialog' button.
        self.cancel_button = list(self.buttons.keys())[-1]
        
        # Create window
        self.window = tk.Toplevel(self.parent)
        self.window.transient()
        self.window.resizable(width=False, height=False)
        self.window.bind('<Return>', self.do_button_action)
        self.window.bind('<Escape>', self.destroy)
        self.window.protocol('WM_DELETE_WINDOW',
                             lambda: self.destroy(button_name=self.cancel_button))
        self.set_geometry()
        
        # Create button frame and buttons.
        self.outer_button_frame = ttk.Frame(self.window)
        self.outer_button_frame.grid(row=1, sticky=tk.EW)
        buttonbox_frame = ttk.Frame(self.outer_button_frame, padding=BODY_PADDING)
        for name in self.buttons:
            if name == self.cancel_button:
                ttk_button = self.make_button(buttonbox_frame, name, self.destroy)
            else:
                ttk_button = self.make_button(buttonbox_frame, name, self.do_button_action)
            self.buttons[name].ttk_button = ttk_button
        
        # Create body frame and body.
        self.body_frame = ttk.Frame(self.window, padding=BODY_PADDING)
        self.body_frame.grid(row=0, sticky=tk.NSEW)
        body_focus = self.make_body(self.body_frame)
        
        # Set focus
        if body_focus:
            self.initial_focus: FocuseeWidget = body_focus
        else:
            self.initial_focus: FocuseeWidget = self.buttons[self.cancel_button].ttk_button
        
        # Make window modal
        self.window.wait_window()
    
    # TODO __call__(self) -> str:
    
    def set_geometry(self):
        # TODO Write tests
        pass
    
    def destroy(self, event: Optional[tk.Event] = None, button_name: str = None):
        # TODO Write tests
        pass
    
    def do_button_action(self, button_name: str = None):
        # TODO Write tests
        pass
    
    def make_button(self, buttonbox_frame: ttk.Frame, button_name: str, command: Callable
                    ) -> ttk.Button:
        # TODO Write tests
        pass
    
    def make_body(self, body_frame: ttk.Frame):
        """Overridable class for creating the widgets of the dialog body.

        Args:
            body_frame: Container for body widgets.

        Returns:
            Any widget that should get focus otherwise None.
        """
        # TODO Write tests
        raise NotImplementedError


@dataclass
class Button:
    """This is used for the values of a dictionary of buttons which are keyed on thw
    internal name of the button."""
    # Button text seen by user.
    label: str
    ttk_button: Optional[ttk.Button] = None


def main():
    pass


if __name__ == '__main__':
    sys.exit(main)
