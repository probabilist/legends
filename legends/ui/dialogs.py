"""Dialog frames and windows for use with the `legends` package.

"""

import tkinter as tk
from tkinter import ttk, E, W, HORIZONTAL, LEFT, RIGHT, YES, X
from legends.constants import RARITIES, ROLES

__all__ = ['askSlot', 'askRosterFilter', 'RosterFilter']

def askSlot():
    """Raised a dialog window, prompting the user to select a save slot.

    Returns:
        int or None: Returns the 0-based index of the user's selected
            slot. Returns `None` if no slot was selected.

    """
    intVar = tk.IntVar()
    AskSlot(intVar)
    slot = intVar.get()
    return None if slot == -1 else slot

def askRosterFilter(filt):
    """Raises a dialog window, prompting the user to adjust the filters
    for the RosterTab. The dialog window is initialized to display the
    filters passed by the `filt` argument.

    Args:
        filt (RosterFilter): The filter used to initialize the dialog
            window. This filter is not modified.

    Returns:
        RosterFilter: Returns a new RosterFilter object representing the
            user's choices.

    """
    filtCopy = RosterFilter(filt)
    AskRosterFilter(filtCopy)
    return filtCopy

class AskSlot(tk.Toplevel):
    """A modal dialog that prompts the user to select a save slot.

    Save slots are denoted in the game data as 0, 1, or 2. In the
    AskSlot window, they are shown to the user as '1', '2', or '3'.

    The constructor must be given a tkinter integer variable. The
    AskSlot instance will store the 0-based index of the user's chosen
    slot in this variable. It will store -1 if the user closes the
    window without making a choice.

    Attributes:
        intVar (tk.IntVar): The tkinter variable passed to the instance
            by the constructor. Used to relay the user's choice.
        displaySlot (tk.StringVar): The currently selected slot, as it
            is displayed in the window.

    """
    def __init__(self, intVar, *args, **kargs):
        # create the window and keep it in front of others
        tk.Toplevel.__init__(self, *args, **kargs)
        self.attributes('-topmost', True)
        self.title('Choose a save slot')

        # define and initialize variables
        self.intVar = intVar
        self.intVar.set(-1)
        self.displaySlot = tk.StringVar(self, '1')

        # create the main content frame
        mainFrame = tk.Frame(self)

        # create the subframe used for selecting the slot
        slotBar = tk.Frame(mainFrame)
        tk.Label(slotBar, text='Extract from save slot:').pack(side=LEFT)
        ttk.Combobox(
            slotBar,
            textvariable=self.displaySlot,
            values=['1', '2', '3'],
            state='readonly',
            width=1
        ).pack()

        # create the subframe with OK and Cancel buttons
        buttonBar = tk.Frame(mainFrame)
        tk.Button(buttonBar, text='OK', command=self.choose).pack(side=RIGHT)
        tk.Button(
            buttonBar, text='Cancel', command=self.destroy
        ).pack(side=RIGHT)
        self.bind_all('<Return>', lambda event:self.choose())

        # pack everything, including an information message
        msg = (
            "Open Star Trek: Legends on this Mac and let it load to the "
            + "splash screen. This will allow your cloud save to sync to "
            + "the local hard drive. Then choose the save slot data you would "
            + "like to use."
        )
        tk.Label(mainFrame, wraplength=250, justify=LEFT, text=msg).pack()
        slotBar.pack(pady=10)
        buttonBar.pack(expand=YES, fill=X)
        mainFrame.pack(padx=10, pady=10)

        # force user to respond to window before continuing
        self.focus_set()
        self.grab_set()
        self.wait_window()

    def choose(self):
        """Sets the linked tkinter variable to the 0-based index
        associated with the current value displayed in the window. Then
        destroys the window.

        """
        self.intVar.set(int(self.displaySlot.get()) - 1)
        self.destroy()

class RosterFilter():
    """Stores information about filtering a RosterTab.

    Attributes:
        rarities (dict of str:tk.BooleanVar): A dictionary mapping
            rarities to tkinter boolean variables indicating whether the
            rarity is to be included in the RosterTab.
        roles (dict of str:tk.BooleanVar): A dictionary mapping roles to
            tkinter boolean variables indicating whether the role is to
            be included in the RosterTab.
        ranks (2-tuple of tk.IntVar): The first value is the minimum
            rank to include in the RosterTab. The second is the maximum.
        levels (2-tuple of tk.IntVar): The first value is the minimum
            level to include in the RosterTab. The second is the maximum.

    """

    def __init__(self, filt=None):
        """Creates a new RosterFilter object with the same values as the
        given RosterFilter object. If none is provided, the new filter
        will not omit anything.

        Args:
            filt (RosterFilter): The filter used to initialize the new
                filter.

        """
        self.rarities = {
            rarity: tk.BooleanVar(None, True) for rarity in RARITIES
        }
        self.roles = {
            role: tk.BooleanVar(None, True) for role in ROLES
        }
        self.ranks = (tk.IntVar(None, 1), tk.IntVar(None, 9))
        self.levels = (tk.IntVar(None, 1), tk.IntVar(None, 99))
        if filt is not None:
            self.set(filt)

    def set(self, filt):
        """Sets the values of the calling RosterFilter to match those of
        the given filter.

        Args:
            filt (RosterFilter): The filter from which to copy values.

        """
        for rarity, var in self.rarities.items():
            var.set(filt.rarities[rarity].get())
        for role, var in self.roles.items():
            var.set(filt.roles[role].get())
        for j in (0, 1):
            self.ranks[j].set(filt.ranks[j].get())
        for j in (0, 1):
            self.levels[j].set(filt.levels[j].get())

    def dictify(self):
        """Creates and returns a dictionary mapping the calling
        instance's attribute names to its values, with each tkinter
        variable replaced by its value.

        Returns:
            dict: The constructed dictionary.

        """
        D = {}
        D['rarities'] = {
            rarity: var.get() for rarity, var in self.rarities.items()
        }
        D['roles'] = {
            role: var.get() for role, var in self.roles.items()
        }
        D['ranks'] = (self.ranks[0].get(), self.ranks[1].get())
        D['levels'] = (self.levels[0].get(), self.levels[1].get())
        return D

    def __eq__(self, other):
        return self.dictify() == other.dictify()

    def __repr__(self):
        return 'RosterFilter({})'.format(self.dictify())

class AskRosterFilter(tk.Toplevel):
    """A modal dialog used for adjusting RosterFilter objects.

    The constructor must be given a RosterFilter object. That object
    will be used to initialize the window. And when the window is
    destroyed, that object will have been modified by the user's actions
    during the window's lifetime.

    Attributes:
        filt (RosterFilter): The RosterFilter object passed to the
            constructor; it is the object that will be modified with
            each action taken in this dialog window.
        originalFilt (RosterFilter): A copy of the RosterFilter object
            passed to the constructor. Used for reverting changes.
        mainFrame (tk.Frame): The frame that contains the main controls
            for adjusting the filter.

    """
    def __init__(self, rosterFilter, *args, **kargs):
        # create the window and keep it in front of others
        tk.Toplevel.__init__(self, *args, **kargs)
        self.attributes('-topmost', True)
        self.title('Filter characters')

        # define and initialize variables
        self.filt = rosterFilter
        self.originalFilt = RosterFilter(rosterFilter)
        widgets = {}

        # create the main content frame
        self.mainFrame = tk.Frame(self)

        # create the rarity and role checkboxes
        widgets['rarityCheckboxes'] = tk.Frame(self.mainFrame)
        for rarity in RARITIES:
            tk.Checkbutton(
                widgets['rarityCheckboxes'], text=rarity,
                variable=self.filt.rarities[rarity]
            ).pack(side=LEFT)
        widgets['roleCheckboxes'] = tk.Frame(self.mainFrame)
        for role in ROLES:
            tk.Checkbutton(
                widgets['roleCheckboxes'], text=role,
                variable=self.filt.roles[role]
            ).pack(side=LEFT)

        # create the rank and level linked scales
        widgets['rankMinScale'], widgets['rankMaxScale'] = (
            self.makeLinkedScales('ranks', 9)
        )
        widgets['levelMinScale'], widgets['levelMaxScale'] = (
            self.makeLinkedScales('levels', 99)
        )

        # grid the main content
        labels = [
            'Rarity:', 'Role:',
            'Min rank:', 'Max rank:', 'Min level:', 'Max level:'
        ]
        for row, label, widget in zip(range(6), labels, widgets.values()):
            tk.Label(self.mainFrame, text=label, font=(None, 13, 'bold')).grid(
                row=row, column=0, sticky=E
            )
            widget.grid(row=row, column=1, sticky=W)

        # pack the window, with buttons
        self.mainFrame.pack()
        tk.Button(self, text='OK', command=self.destroy).pack(side=RIGHT)
        tk.Button(self, text='Cancel', command=self.cancel).pack(side=RIGHT)
        tk.Button(
            self, text='Clear All',
            command=lambda: self.filt.set(RosterFilter())
        ).pack(side=LEFT)

        # force user to respond to window before continuing
        self.focus_set()
        self.grab_set()
        self.wait_window()

    def makeLinkedScales(self, attrName, maxVal):
        """Creates and returns a pair of linked Scale widgets. Each
        scale has values from 1 to `maxVal`. If `attrName` is 'ranks',
        the scales are associated with the tkinter variables stored in
        the `ranks` attribute of the calling instance's `returnFilt`
        attribute. Similarly if `attrName` is 'levels'.

        The first scale controls the minimum value; the second controls
        the maximum. The scales are configured so that the minimum value
        cannot exceed the maximum.

        The calling instance's `mainFrame` attribute is assigned as the
        parent of both scales.

        Args:
            attrName (str): One of 'ranks' or 'levels'

        Returns:
            list of tk.Scale: The two linked scales.

        """
        varTuple = getattr(self.filt, attrName)
        funcs = [min, max]
        scales = [None, None]
        for j in (0, 1):
            k = 1 - j
            scales[j] = tk.Scale(
                self.mainFrame, variable=varTuple[j], from_=1, to=maxVal,
                length=400, orient=HORIZONTAL
            )
            scales[j].config(command=lambda val, k=k: varTuple[k].set(
                funcs[k](int(val), varTuple[k].get()))
            )
        return scales

    def cancel(self):
        """Reverts the filter to its original state and destroys the
        window.

        """
        self.filt.set(self.originalFilt)
        self.destroy()
