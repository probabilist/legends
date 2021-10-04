"""Dialog windows for use with the `legends` package.

"""

import tkinter as tk
from tkinter.messagebox import askyesno as _askyesno
from tkinter.messagebox import showerror as _showerror
from tkinter.messagebox import showinfo as _showinfo
from tkinter.filedialog import asksaveasfilename as _asksaveasfilename
from tkinter.simpledialog import Dialog

__all__ = [
    'addroot',
    'asksaveasfilename',
    'askyesno',
    'ModalMessage',
    'ModalDialog',
    'showerror',
    'showinfo'
]

def addroot(func):
    """Creates and returns a new function from the given function by
    adding a `root` positional argument at the front, which should be
    the currently running `legends.ui.stlplanner.STLPlanner` instance.
    The new function will ensure that the menus of `root` are disabled
    before calling the given function, and will return the menus to
    their original state after calling the given function.

    """
    def newFunc(root, *args, **kargs):
        state = root.menuEnabled
        if state:
            root.menuEnabled = False
        result = func(*args, **kargs)
        if state:
            root.menuEnabled = True
        return result
    return newFunc

def asksaveasfilename(root, *args, **kargs):
    """A wrapper around `tk.filedialog.asksaveasfilename` that disables
    the root menu while the dialog is open.

    Args:
        root (legends.ui.stlplanner.STLPlanner): The currently running
            `legends.ui.stlplanner.STLPlanner` instance.

    """
    return addroot(_asksaveasfilename)(root, *args, **kargs)

def askyesno(root, *args, **kargs):
    """A wrapper around `tk.messagebox.askyesno` that disables the root
    menu while the dialog is open.

    Args:
        root (legends.ui.stlplanner.STLPlanner): The currently running
            `legends.ui.stlplanner.STLPlanner` instance.

    """
    return addroot(_askyesno)(root, *args, **kargs)

def showerror(root, *args, **kargs):
    """A wrapper around `tk.messagebox.showerror` that disables the root
    menu while the dialog is open.

    Args:
        root (legends.ui.stlplanner.STLPlanner): The currently running
            `legends.ui.stlplanner.STLPlanner` instance.

    """
    return addroot(_showerror)(root, *args, **kargs)

def showinfo(root, *args, **kargs):
    """A wrapper around `tk.messagebox.showinfo` that disables the root
    menu while the dialog is open.

    Args:
        root (legends.ui.stlplanner.STLPlanner): The currently running
            `legends.ui.stlplanner.STLPlanner` instance.

    """
    return addroot(_showinfo)(root, *args, **kargs)

class ModalMessage(Dialog):
    """A subclass of `tk.simpledialog.Dialog` that disables menus. Has
    an 'OK' button, but no 'Cancel' button.

    Attributes:
        root (legends.ui.stlplanner.STLPlanner): The currently running
            `legends.ui.stlplanner.STLPlanner` instance.
        initialMenuState (bool): `True` if the root menu is enabled at
            the moment the dialog opens.
        box (tk.Frame): The frame that holds the buttons.

    """
    def __init__(self, root, parent=None, title=None):
        """The constructor disables the root menu before calling the
        `tk.simpledialog.Dialog` constructor.

        """
        self.root = root
        self.initialMenuState = self.root.menuEnabled
        if self.initialMenuState:
            self.root.menuEnabled = False
        if parent is None:
            parent = tk._default_root
        Dialog.__init__(self, parent, title)

    def buttonbox(self):
        """Builds the standard 'OK' button of the
        `tk.simpledialog.Dialog` class.

        """
        body = self.winfo_children()[0]
        body.pack_forget()
        body.pack(padx=5, pady=5, expand=tk.YES, fill=tk.Y)
        self.box = tk.Frame(self)

        tk.Button(
            self.box, text="OK", width=10, command=self.ok, default=tk.ACTIVE
        ).pack(side=tk.RIGHT, padx=5, pady=5)

        self.bind("<Return>", self.ok)

        self.box.pack()

    def destroy(self):
        """Restores root menu options to their original state, then
        destroys the window.

        """
        self.initial_focus = None
        if self.initialMenuState:
            self.root.menuEnabled = True
        tk.Toplevel.destroy(self)

class ModalDialog(ModalMessage):
    """A subclass of `ModalMessage` that has a 'Cancel' button.

    Attributes:
        root (legends.ui.stlplanner.STLPlanner): The currently running
            `legends.ui.stlplanner.STLPlanner` instance.
        initialMenuState (bool): `True` if the root menu is enabled at
            the moment the dialog opens.
        box (tk.Frame): The frame that holds the 'OK' and 'Cancel'
            buttons.

    """
    def __init__(self, root, parent=None, title=None):
        ModalMessage.__init__(self, root, parent, title)

    def buttonbox(self):
        """Adds the standard 'Cancel' button of the
        `tk.simpledialog.Dialog` class.

        """
        ModalMessage.buttonbox(self)

        tk.Button(
            self.box, text="Cancel", width=10, command=self.cancel
        ).pack(side=tk.RIGHT, padx=5, pady=5)

        self.bind("<Escape>", self.cancel)
