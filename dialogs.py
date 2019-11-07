"""Manager of tkinter dialogs."""

#  Copyright© 2019. Stephen Rigden.
#  Last modified 11/7/19, 9:13 AM by stephen.
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
from dataclasses import dataclass
from typing import Callable, Dict, Optional, TypeVar


BODY_PADDING = '2m'
BUTTON_PADDING = '1m'
ROOTY_OFFSET = 11

FocuseeWidget = TypeVar('FocuseeWidget', ttk.Entry, ttk.Button)
DialogParent = TypeVar('DialogParent', tk.Tk, ttk.Frame)


@dataclass
class ModalDialogBase:
    """This class provides the core functionality for a modal dialog.

    It offers two vertically arranged frames which are seen by the user. The lower is the
    buttonbox and this contains the buttons defined by the caller. The upper is
    the body frame which is undefined in this base class. Subclasses are required and should
    define the content of the body frame as a minimum.

    If called the class will return the button clicked by the user.

    Size
    ----
    The size of the dialog window is fixed and will be made large enough to display all of the
    widgets which it contains.

    Placement
    ---------
    The dialog is centered on the parent window. If this causes the dialog to either be
    off screen at the top or off screen at the left it will be moved down or to the right
    respectively.
    NB: This assumes the dialog window will fit on the screen. If a subclass
    creates a window that is too large then that subclass is responsible for handling the
    excess.

    Internal Frames
    ---------------
    The method '__call__' creates a body frame and a buttonbox frame placed vertically
    beneath it. Override this method to create other configurations.

    Initial Focus
    -----
    The focus will default to the rightmost button.
    This default can be overridden for widgets in the body by returning the widget from the body
    method of subclasses.

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

        Other buttons
        -------------
        All other buttons will call the do_button_action method. The base class method simply sets the
        button_clicked attribute and calls the destroy method.

    The module is based on Fredrik Lundh's "An Introduction to Tkinter" November 2005.
    (http://effbot.org/tkinterbook/tkinter-dialog-windows.htm) the except the
    tk classes are not a superclass of Dialog but are implemented as attributes.
    """

    def __init__(self, parent: DialogParent, button_labels: Dict[str, str], title: str = ''):
        """Args:
            parent: Tkinter parent widget
            button_labels:
                Key: Internal button name used by program. e.g. ok, cancel
                Value: Button label seen by user. e.g. OK, Cancel
            title: Optional window title
        """
        self.parent = parent
        self.button_labels = button_labels
        self.title = title
        
        # Organize the buttons
        self.buttons = {name: Button(label) for name, label in self.button_labels.items()}
        # Set the rightmost button as the 'cancel dialog' button.
        self.destroy_button = list(self.buttons.keys())[-1]
        
        self.window: Optional[tk.Toplevel] = None
        self.button_clicked: Optional[str] = None
    
    def __call__(self) -> str:
        # Create the window
        self.window = tk.Toplevel(self.parent)
        self.window.withdraw()
        self.window.title(self.title)
        self.window.grab_set()
        self.window.transient()
        self.window.resizable(width=False, height=False)
        self.window.protocol('WM_DELETE_WINDOW',
                             lambda: self.destroy(button_name=self.destroy_button))

        # Create button frame and buttons.
        self.outer_button_frame = ttk.Frame(self.window)
        self.outer_button_frame.grid(row=1, sticky=tk.EW)
        buttonbox_frame = ttk.Frame(self.outer_button_frame, padding=BODY_PADDING)
        for name in self.buttons:
            if name == self.destroy_button:
                ttk_button = self.make_button(buttonbox_frame, name, self.destroy)
            else:
                ttk_button = self.make_button(buttonbox_frame, name, self.do_button_action)
            self.buttons[name].ttk_button = ttk_button
        if len(self.buttons) == 1:
            # Center a single button
            buttonbox_frame.pack()
        else:
            buttonbox_frame.pack(side='right')

        # Create body frame and body.
        self.body_frame = ttk.Frame(self.window, padding=BODY_PADDING)
        self.body_frame.grid(row=0, sticky=tk.NSEW)
        body_focus = self.make_body(self.body_frame)

        # Set focus
        if body_focus:
            body_focus.focus_set()
        else:
            self.buttons[self.destroy_button].ttk_button.focus_set()

        # Make window visible to user
        # The pattern withdraw/update_idletasks/deiconify/set_geometry causes the dialog to be drawn
        # without flickering or ghosting in front of the parent.
        self.parent.update_idletasks()
        self.window.deiconify()
        self.set_geometry()

        # Wait for user then give back control to Tk parent
        self.parent.update_idletasks()
        self.window.wait_window()
        self.parent.focus_set()
        return self.button_clicked

    def make_button(self, buttonbox_frame: ttk.Frame, button_name: str, command: Callable
                    ) -> ttk.Button:
        """Create a ttk button.

        Args:
            buttonbox_frame: Parent
            button_name: Internal button name
            command: Handler when button is clicked either do_button_action method or destroy method.

        Returns:
            The ttk button.
        """
        ttk_button = ttk.Button(buttonbox_frame, text=self.buttons[button_name].label,
                                name=button_name)
        ttk_button.configure(command=lambda b=button_name: command(button_name=b))
        ttk_button.pack(side='left', padx=BUTTON_PADDING, pady=BUTTON_PADDING)
        # If any button has focus and <Return> is pressed, treat it as a click on that button.
        ttk_button.bind('<Return>', lambda event, b=ttk_button: b.invoke())
        # If <Escape> is pressed treat it as a click on the destroy_button.
        if button_name == self.destroy_button:
            self.window.bind('<Escape>', lambda event, b=ttk_button: b.invoke())
        return ttk_button

    def set_geometry(self):
        """Center dialog on parent window."""
        self.parent.update_idletasks()
        parent_center_x = int(self.parent.winfo_width() / 2) + self.parent.winfo_rootx()
        parent_center_y = int(self.parent.winfo_height() / 2) + self.parent.winfo_rooty() - ROOTY_OFFSET
        dialog_x = parent_center_x - int(self.window.winfo_width() / 2)
        if dialog_x < 0:
            dialog_x = 0
        dialog_y = parent_center_y - int(self.window.winfo_height() / 2)
        if dialog_y < 0:
            dialog_y = 0
        self.window.geometry(f"+{dialog_x}+{dialog_y}")
    
    def make_body(self, body_frame: ttk.Frame) -> Optional[FocuseeWidget]:
        """Create the widgets of the dialog body.

        Args:
            body_frame: Container for body widgets.

        Returns:
            Any widget that should get focus otherwise None.
        """
        raise NotImplementedError

    def do_button_action(self, button_name: str):
        """Record which button was clicked and close the dialog.
        
        Args:
            button_name:
        """
        self.button_clicked = button_name
        self.destroy()

    def destroy(self, event: tk.Event = None, button_name: str = None):
        """Closes the dialog window.
        
        Args:
            event:
            button_name:
        """
        if button_name == self.destroy_button or event and event.keysym == 'Escape':
            self.button_clicked = self.destroy_button
        self.window.withdraw()
        self.window.update_idletasks()
        self.window.destroy()


@dataclass
class ModalDialog(ModalDialogBase):
    """his creates a simple dialog with two lines of text.

    It offers the framework for any alert or simple dialog. Callers are responsible for
    providing the text seen by the user.

    If called, the class will return the button clicked by the user.
    """
    
    def __init__(self, text: str, parent: DialogParent, button_labels: Dict[str, str],
                 sub_text: str = '', title: str = ''):
        """Args:
            text: Text of dialog body.
            sub_text: Sub text of dialog body.
            See superclass docs for its arguments.
        """
        super().__init__(parent, button_labels, title)
        self.text = text
        self.sub_text = sub_text
    
    def make_body(self, body_frame: ttk.Frame):
        """Create the body widgets.

        Args:
            body_frame: The parent widget for the body widgets.

        Returns:
            Nothing since there are no widgets that should get focus.
        """
        text = ttk.Label(body_frame, text=self.text)
        text.pack(anchor='nw', fill='both', expand=True)
        if self.sub_text:
            explanation = ttk.Label(body_frame, text=self.sub_text)
            explanation.pack(anchor='nw', fill='both', expand=True)


@dataclass
class Button:
    """Data for managing a ttk button."""
    # Internal button name.
    label: str
    # Button text seen by user.
    ttk_button: Optional[ttk.Button] = None


def main():
    """Integration tests."""
    root = tk.Tk()
    root.geometry('400x100+250+200')
    
    tk.Button(root, text='Hello').pack()
    
    button = ModalDialog('One Button', root, dict(ok='OK'), 'This is a one button dialog',
                         'Modal Dialog')()
    print(f'One button dialog: {button=}')
    
    button = ModalDialog('Two Button', root, dict(ok='OK', cancel='Cancel'),
                         'This is a two button dialog', 'Modal Dialog')()
    print(f'Two button dialog: {button=}')
    
    root.mainloop()


if __name__ == '__main__':
    sys.exit(main())
