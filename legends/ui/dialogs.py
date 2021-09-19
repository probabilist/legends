"""Dialog windows for use with the `legends` package.

"""

import tkinter as tk
from tkinter import (
    ttk, E, W, HORIZONTAL, LEFT, RIGHT, ACTIVE, YES, X, DISABLED
)
from tkinter.messagebox import showerror as _showerror
from tkinter.messagebox import showinfo as _showinfo
from tkinter.messagebox import askyesno as _askyesno
from tkinter.simpledialog import Dialog
from tkinter.scrolledtext import ScrolledText
# pylint: disable-next=no-name-in-module
from legends.constants import GSCharacter
from legends.constants import (
    RARITIES, ROLES, ENABLED, UPCOMING, SUMMON_POOL, HELP, STAT_INITIALS
)
from legends.saveslot import SaveSlot

__all__ = [
    'addroot', 'showerror', 'showinfo', 'askyesno', 'askSlot',
    'askRosterFilter', 'askMaxChars', 'ModalMessage', 'ModalDialog', 'AskSlot',
    'RosterFilter', 'AskRosterFilter', 'AskMaxChars', 'HelpScreen',
    'OptimalSummons'
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

def askyesno(root, *args, **kargs):
    """A wrapper around `tk.messagebox.askyesno` that disables the root
    menu while the dialog is open.

    Args:
        root (legends.ui.stlplanner.STLPlanner): The currently running
            `legends.ui.stlplanner.STLPlanner` instance.

    """
    return addroot(_askyesno)(root, *args, **kargs)

def askSlot(root, save):
    """Raises an `AskSlot` dialog window, prompting the user to select a
    save slot.

    Args:
        root (legends.ui.stlplanner.STLPlanner): The currently running
            `legends.ui.stlplanner.STLPlanner` instance.
        save (dict): A decrypted dictionary representation of the
            player's save file, as returned by the
            `legends.savefile.decryptSaveFile` function.

    Returns:
        legends.saveslot.SaveSlot or None: Returns a
            `legends.saveslot.SaveSlot` instance created from the chosen
            slot number. Returns `None` if no slot was selected.

    """
    dialog = AskSlot(root, save)
    return dialog.result

def askRosterFilter(root, filt):
    """Raises an `AskRosterFilter` dialog window, prompting the user to
    adjust the filters for the roster tab. The dialog window is
    initialized to display the filters passed by the `filt` argument.

    Args:
        root (legends.ui.stlplanner.STLPlanner): The currently running
            `legends.ui.stlplanner.STLPlanner` instance.
        filt (RosterFilter): The filter used to initialize the dialog
            window. This filter is not modified.

    Returns:
        RosterFilter or None: Returns a new `RosterFilter` object
            representing the user's choices. Returns `None` if no
            choices were confirmed.

    """
    dialog = AskRosterFilter(root, filt)
    return dialog.result

def askMaxChars(root):
    """Raises an `AskMaxChars` dialog window, prompting the user to
    select from an array of options for creating a roster of maxed
    characters.

    Args:
        root (legends.ui.stlplanner.STLPlanner): The currently running
            `legends.ui.stlplanner.STLPlanner` instance.

    Returns:
        tuple: ([`str`], `bool`) The first value in the tuple is the
            list of name IDs of characters the user wants to include in
            the roster. The second value is `True` if the user wants the
            maxed characters to also have maxed gear.

    """
    dialog = AskMaxChars(root)
    return dialog.result

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
        self.box = tk.Frame(self)

        tk.Button(
            self.box, text="OK", width=10, command=self.ok, default=ACTIVE
        ).pack(side=RIGHT, padx=5, pady=5)

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
        ).pack(side=RIGHT, padx=5, pady=5)

        self.bind("<Escape>", self.cancel)

class AskSlot(ModalDialog):
    """A modal dialog that prompts the user to select a save slot.

    Save slots are denoted in the game data as 0, 1, or 2. In the
    `AskSlot` window, they are shown to the user as '1', '2', or '3'.

    Attributes:
        save (dict): A decrypted dictionary representation of the
            player's save file, as returned by the
            `legends.savefile.decryptSaveFile` function.
        displaySlot (tk.StringVar): The currently selected slot, as it
            is displayed in the window.
        result (SaveSlot or None): Inherited from `ModalDialog`, which
            inherited it from `tk.simpledialog.Dialog`. Defaults to
            `None`. Is set by the `AskSlot.validate` method to a
            `SaveSlot` instance created from the chosen slot number.

    """
    def __init__(self, root, save, parent=None):
        self.save = save
        self.displaySlot = tk.StringVar(None, '1')
        ModalDialog.__init__(self, root, parent, 'Choose a save slot')

    def body(self, master):
        """Create the body of the dialog.

        """
        # create an informational label
        msg = (
            "Open Star Trek: Legends on this Mac and let it load to the "
            + "splash screen. This will allow your cloud save to sync to "
            + "the local hard drive. Then choose the save slot data you would "
            + "like to use."
        )
        tk.Label(master, wraplength=250, justify=LEFT, text=msg).pack()

        # create the subframe used for selecting the slot
        slotBar = tk.Frame(master)
        tk.Label(slotBar, text='Extract from save slot:').pack(side=LEFT)
        cbox = ttk.Combobox(
            slotBar,
            textvariable=self.displaySlot,
            values=['1', '2', '3'],
            state='readonly',
            width=1
        )
        cbox.pack()

        # pack the subframe and return the combobox for focus
        slotBar.pack(pady=10)
        return cbox

    def validate(self):
        """Set the `result` attribute and return `True`.

        """
        slot = int(self.displaySlot.get()) - 1
        key = '{} data'.format(slot)
        if key not in self.save or not self.save[key]:
            showerror(
                self.root,
                'Slot Error',
                'No save data found in slot {}.'.format(slot + 1)
            )
            return False
        self.result = SaveSlot()
        self.result.fromFile(self.save, slot)
        return True

class RosterFilter():
    """Stores information about filtering a
    `legends.ui.rostertab.RosterTab`.

    Attributes:
        rarities (dict): {`str`:`tk.BooleanVar`} A dictionary mapping
            rarities to `tkinter` boolean variables indicating whether
            the rarity is to be included in the
            `legends.ui.rostertab.RosterTab`.
        roles (dict): {`str`:`tk.BooleanVar`} A dictionary mapping roles
            to `tkinter` boolean variables indicating whether the role
            is to be included in the `legends.ui.rostertab.RosterTab`.
        ranks (tuple): (`tk.IntVar`, `tk.IntVar`) The first value is the
            minimum rank to include in the
            `legends.ui.rostertab.RosterTab`. The second is the maximum.
        levels (tuple): (`tk.IntVar`, `tk.IntVar`) The first value is
            the minimum level to include in the
            `legends.ui.rostertab.RosterTab`. The second is the maximum.

    """

    def __init__(self, filt=None):
        """The constructor creates a new `RosterFilter` object with the
        same values as the given `RosterFilter` object. If `None` is
        provided, the new filter will not omit anything.

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
        """Sets the values of the calling instance to match those of the
        given filter.

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
        instance's attribute names to its values, with each `tkinter`
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

class AskRosterFilter(ModalDialog):
    """A modal dialog used for adjusting `RosterFilter` objects.

    The constructor must be given a `RosterFilter` object. That object
    will be used to initialize the window, but will not be modified.

    Attributes:
        filt (RosterFilter): The `RosterFilter` object controlled and
            modified by the dialog window.
        result (RosterFilter or None): Inherited from `ModalDialog`,
            which inherited it from `tk.simpledialog.Dialog`. Defaults
            to `None`. Is set by the `AskRosterFilter.apply` method to
            the value of the `filt` attribute.

    """
    def __init__(self, root, rosterFilter, parent=None):
        """The constructor sets the `filt` attribute, then calls the
        `ModalDialog` constructor.

        Args:
            root (legends.ui.stlplanner.STLPlanner): The currently
                running `legends.ui.stlplanner.STLPlanner` instance.
                Passed to the `ModalDialog` constructor.
            rosterFilter (RosterFilter): The instance's `filt` attribute
                is assigned a copy of this argument.

        """
        self.filt = RosterFilter(rosterFilter)
        ModalDialog.__init__(self, root, parent, 'Filter characters')

    def body(self, master):
        """Create the body of the dialog.

        """
        widgets = {}

        # create the rarity and role checkboxes
        widgets['rarityCheckboxes'] = tk.Frame(master)
        for rarity in RARITIES:
            tk.Checkbutton(
                widgets['rarityCheckboxes'], text=rarity,
                variable=self.filt.rarities[rarity]
            ).pack(side=LEFT)
        widgets['roleCheckboxes'] = tk.Frame(master)
        for role in ROLES:
            tk.Checkbutton(
                widgets['roleCheckboxes'], text=role,
                variable=self.filt.roles[role]
            ).pack(side=LEFT)

        # create the rank and level linked scales
        widgets['rankMinScale'], widgets['rankMaxScale'] = (
            self.makeLinkedScales(master, 'ranks', 9)
        )
        widgets['levelMinScale'], widgets['levelMaxScale'] = (
            self.makeLinkedScales(master, 'levels', 99)
        )

        # grid the body content
        labels = [
            'Rarity:', 'Role:',
            'Min rank:', 'Max rank:', 'Min level:', 'Max level:'
        ]
        for row, label, widget in zip(range(6), labels, widgets.values()):
            tk.Label(master, text=label, font=(None, 13, 'bold')).grid(
                row=row, column=0, sticky=E
            )
            widget.grid(row=row, column=1, sticky=W)

    def makeLinkedScales(self, master, attrName, maxVal):
        """Creates and returns a pair of linked Scale widgets. Each
        scale has values from 1 to `maxVal`. If `attrName` is 'ranks',
        the scales are associated with the `tkinter` variables stored in
        the `ranks` attribute of the calling instance's `filt`
        attribute. Similarly if `attrName` is 'levels'.

        The first scale controls the minimum value; the second controls
        the maximum. The scales are configured so that the minimum value
        cannot exceed the maximum.

        The given `master` argument is assigned as the parent of both
        scales.

        Args:
            master (obj): The tkinter object to assign as parent.
            attrName (str): One of 'ranks' or 'levels'
            maxVal (int): The maximum value of the linked scales.

        Returns:
            list of tk.Scale: The two linked scales.

        """
        varTuple = getattr(self.filt, attrName)
        funcs = [min, max]
        scales = [None, None]
        for j in (0, 1):
            k = 1 - j
            scales[j] = tk.Scale(
                master, variable=varTuple[j], from_=1, to=maxVal,
                length=400, orient=HORIZONTAL
            )
            scales[j].config(command=lambda val, k=k: varTuple[k].set(
                funcs[k](int(val), varTuple[k].get()))
            )
        return scales

    def buttonbox(self):
        """Add a 'Clear All' button to the button box.

        """
        ModalDialog.buttonbox(self)
        self.box.pack_forget()
        tk.Button(
            self.box, text="Clear All", width=10, command=self.clear
        ).pack(side=LEFT, padx=5, pady=5)
        self.box.pack(expand=YES, fill=X)

    def clear(self):
        """Reset the `filt` attribute to default values.

        """
        self.filt.set(RosterFilter())

    def apply(self):
        """Set the `result` attribute.

        """
        self.result = self.filt

class AskMaxChars(ModalDialog):
    """A modal dialog used for creating a maxed roster.

    Attributes:
        crew (tk.BooleanVar): True if the user wants to use the
            characters in the Crew screen (i.e. those that are not
            disabled).
        upcoming (tk.BooleanVar): True if the user wants to use upcoming
            characters.
        summonableOnly (tk.BooleanVar): True if the user wants to
            exclude characters that are not summonable.
        storeOnly (tk.BooleanVar): True if the user wants to exclude
            characters whose tokens are not in the daily store.
        maxGear (tk.BooleanVar): True if the user wants the maxed
            characters to also have maxed gear.
        result (tuple): ([`str`], `bool`) The first value in the tuple is
            the list of name IDs of characters the user wants to include
            in the roster. The second value is `True` if the user wants
            the maxed characters to also have maxed gear.

    """
    def __init__(self, root, parent=None):
        self.crew = tk.BooleanVar(None, True)
        self.upcoming = tk.BooleanVar(None, False)
        self.summonableOnly = tk.BooleanVar(None, False)
        self.storeOnly = tk.BooleanVar(None, False)
        self.maxGear = tk.BooleanVar(None, True)
        ModalDialog.__init__(self, root, parent, 'Choose character options')

    def body(self, master):
        """Create the body of the dialog.

        """
        tk.Checkbutton(
            master, text='include characters in Crew screen',
            variable=self.crew
        ).pack(anchor=W, padx=5)
        tk.Checkbutton(
            master, text='include upcoming characters',
            variable=self.upcoming
        ).pack(anchor=W, padx=5)
        tk.Checkbutton(
            master, text='exclude non-summonable characters',
            variable=self.summonableOnly
        ).pack(anchor=W, padx=5, pady=(15,0))
        tk.Checkbutton(
            master, text='exclude characters not in daily store',
            variable=self.storeOnly
        ).pack(anchor=W, padx=5)
        tk.Checkbutton(
            master, text='equip max gear on characters',
            variable=self.maxGear
        ).pack(anchor=W, padx=5, pady=(15,0))

    def validate(self):
        """Ensure that the user has selected at least one character,
        then set the result.

        """
        include = ENABLED if self.crew.get() else []
        include.extend(UPCOMING if self.upcoming.get() else [])
        nameIDs = []
        for nameID in include:
            if (
                self.summonableOnly.get()
                and nameID not in SUMMON_POOL['Core']['nameIDs']
            ):
                continue
            if (
                self.storeOnly.get()
                and not GSCharacter[nameID]['DailyTokenVisible']
            ):
                continue
            nameIDs.append(nameID)
        if len(nameIDs) == 0:
            showerror(
                self.root, 'Empty Selection',
                'These choices produce no characters.'
            )
            return False
        self.result = nameIDs, self.maxGear.get()
        return True

class HelpScreen(ModalMessage):
    """A message dialog giving help on the *STL Planner* app.

    """
    def __init__(self, root, parent=None):
        ModalMessage.__init__(self, root, parent, 'Roster Help')

    def body(self, master):
        """Create the body of the dialog.

        """
        text = ScrolledText(master)
        glossary = '\n'.join(
            '    {} = {}'.format(v.rjust(3), k)
            for k,v in STAT_INITIALS.items()
        )
        glossary += (
            '\n    MGL = Missing gear levels'
            + '\n    MGR = Missing gear ranks'
            + '\n    MSL = Missing skill levels'
        )
        text.insert('1.0', HELP.format(glossary))
        text.config(state=DISABLED)
        text.focus()
        text.pack()

class OptimalSummons(ModalMessage):
    """A message dialog showing the summon pool rates.

    Attributes:
        excludeCommons (tk.BooleanVar): `True` is the summon rate
            calculations should exclude Common characters.
        values (dict): {`str`:`tk.StringVar`} A dictionary mapping pool
            names to a formatted string representation of the average
            number of tokens per 150 orbs received from the pool.
        labels (dict): {`str`:(`tk.Label`,`tk.Label`)} A dictionary
            mapping pool names to the pair of labels associated with
            that pool in the body of the message dialog.

    """
    def __init__(self, root, parent=None):
        self.excludeCommons = tk.BooleanVar(None, True)
        self.values = {}
        self.labels = {}
        for pool in SUMMON_POOL:
            self.values[pool] = tk.StringVar()
        ModalMessage.__init__(self, root, parent, 'Summon Rates')

    def body(self, master):
        """Create the body of the dialog.

        """
        tk.Label(
            master,
            text='Average Tokens per 150 Orbs',
            font=(None, 13, 'bold')
        ).pack(pady=(0,10))
        results = tk.Frame(master)
        results.pack()
        for row, pool in enumerate(SUMMON_POOL):
            self.labels[pool] = (
                tk.Label(
                    results, text='{} Pool:'.format(pool)
                ),
                tk.Label(
                    results, textvariable=self.values[pool], width=5
                )
            )
            self.labels[pool][0].grid(row=row, column=0, sticky=W)
            self.labels[pool][1].grid(row=row, column=1, sticky=E)
        tk.Checkbutton(
            master,
            text='exclude Common characters',
            variable=self.excludeCommons, command=self.refresh
        ).pack(pady=(10,0))
        self.refresh()

    def refresh(self):
        """Updates the values in the `values` attribute and sets the
        font emphasis of the labels so that the highest summon rate is
        bold and the others are normal.

        """
        bestPool = ''
        bestPoolTokens = -1
        tokens = {}
        for pool in SUMMON_POOL:
            roster = self.root.session.saveslot.roster
            tokens[pool] = 150 * roster.tokensPerOrb(
                pool, self.excludeCommons.get()
            )
            self.values[pool].set('{:.2f}'.format(tokens[pool]))
            self.setPoolEmphasis(pool, 'normal')
            if tokens[pool] > bestPoolTokens:
                bestPool, bestPoolTokens = pool, tokens[pool]
        self.setPoolEmphasis(bestPool, 'bold')

    def setPoolEmphasis(self, pool, emphasis):
        """Finds the labels associated with the given pool and sets
        their font to have the given emphasis.

        Args:
            pool (str): The name of a summon pool.
            emphasis (str): One of 'normal' or 'bold'.

        """
        self.labels[pool][0].config(font=(None, 11, emphasis))
        self.labels[pool][1].config(font=(None, 11, emphasis))
