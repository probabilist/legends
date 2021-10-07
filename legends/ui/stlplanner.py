"""The `legends.ui.stlplanner.STLPlanner` class and related objects.

The *STL PLanner* app can be launched with `STLPlanner().mainloop()`.

"""

import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from json import loads
# pylint: disable-next=no-name-in-module
from legends.constants import GSCharacter
from legends.constants import (
    ENABLED, HELP, SUMMON_POOL, STAT_INITIALS, UPCOMING
)
from legends.functions import decompressData, decryptSaveFile
from legends.saveslot import SaveSlot
from legends.ui.dialogs import (
    askyesno, ModalDialog, ModalMessage, showerror
)
from legends.ui.session import (
    InventoryScreen, MissingMissions, Session, SurvivalEffects
)

__all__ = [
    'AskClipboard',
    'AskMaxChars',
    'AskSlot',
    'HelpScreen',
    'STLPlanner'
]

class AskClipboard(ModalDialog):
    """A modal dialog for extracting save data from the clipboard.

    Provides instructions for copying the data and prompts the user to
    confirm after they have done so.

    Attributes:
        result (legends.saveslot.SaveSlot or None): Inherited from
            `legends.ui.dialogs.ModalDialog`, which inherited it from
            `tk.simpledialog.Dialog`. Defaults to `None`. Is set by the
            `AskClipboard.validate` method to a
            `legends.saveslot.SaveSlot` instance created from the
            clipboard contents.

    """
    def __init__(self, root, parent=None):
        ModalDialog.__init__(self, root, parent, 'Get Data From Clipboard')

    def body(self, master):
        """Create the body of the dialog.

        """
        msg = (
            'Open Star Trek: Legends on any device and load your save slot. '
            + 'From the main game screen, tap your profile name in the top '
            + 'left, then select the "Options" tab. Tap on the "Support" '
            + 'button. This will open an email. Change the "To:" field to an '
            + 'address you can access on this computer, and send it.\n\n'
            + 'Now, on this computer, open that email and copy everything '
            + 'below the word "data:" to the clipboard. When this is done, '
            + 'press "OK".'
        )
        tk.Label(master, wraplength=250, justify=tk.LEFT, text=msg).pack()

    def validate(self):
        """Try to create a `legends.saveslot.SaveSlot` instance from the
        clipboard contents. On success, set the `result` attribute and
        return `True`. On failure, raise an error message and return
        `False`.

        """
        try:
            text = self.clipboard_get()
            stringData = decompressData(text)
            if stringData[:6] == 'compr-':
                stringData = decompressData(stringData[6:])
            slotData = loads(stringData)
            save = {'0 data': slotData}
            self.result = SaveSlot()
            self.result.fromFile(save, 0)
            return True
        except Exception: # pylint: disable=broad-except
            showerror(
                self.root,
                'Clipboard Error',
                'Cannot get save data from clipboard.'
            )
            return False

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
        ).pack(anchor=tk.W, padx=5)
        tk.Checkbutton(
            master, text='include upcoming characters',
            variable=self.upcoming
        ).pack(anchor=tk.W, padx=5)
        tk.Checkbutton(
            master, text='exclude non-summonable characters',
            variable=self.summonableOnly
        ).pack(anchor=tk.W, padx=5, pady=(15,0))
        tk.Checkbutton(
            master, text='exclude characters not in daily store',
            variable=self.storeOnly
        ).pack(anchor=tk.W, padx=5)
        tk.Checkbutton(
            master, text='equip max gear on characters',
            variable=self.maxGear
        ).pack(anchor=tk.W, padx=5, pady=(15,0))

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

class AskSlot(ModalDialog):
    """A modal dialog that prompts the user to select a save slot.

    Save slots are denoted in the game data as 0, 1, or 2. In the
    `AskSlot` window, they are shown to the user as '1', '2', or '3'.

    Attributes:
        save (dict): A decrypted dictionary representation of the
            player's save file, as returned by the
            `legends.functions.decryptSaveFile` function.
        displaySlot (tk.StringVar): The currently selected slot, as it
            is displayed in the window.
        result (legends.saveslot.SaveSlot or None): Inherited from
            `legends.ui.dialogs.ModalDialog`, which inherited it from
            `tk.simpledialog.Dialog`. Defaults to `None`. Is set by the
            `AskSlot.validate` method to a `legends.saveslot.SaveSlot`
            instance created from the chosen slot number.

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
        tk.Label(master, wraplength=250, justify=tk.LEFT, text=msg).pack()

        # create the subframe used for selecting the slot
        slotBar = tk.Frame(master)
        tk.Label(slotBar, text='Extract from save slot:').pack(side=tk.LEFT)
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
        text.config(state=tk.DISABLED)
        text.focus()
        text.pack()

class STLPlanner(tk.Tk):
    """The *STL Planner* main window.

    Args:
        showTimestamps (tk.BooleanVar): `True` if the info bar with
            timestamp data should be shown. Defaults to `True`.
        disableOnModal (list): [(`tk.Menu`, `int`)]: Each item in this
            list is a 2-tuple that represents a menu option which should
            be disabled when a modal dialog is open. The first value is
            the menu in which the option exists. The second value is the
            0-based index of the option within that menu. Defaults to an
            empty list.
        sessionOnly (list): [(`tk.Menu`, `int`)]: Each item in this list
            is a 2-tuple that represents a menu option which should be
            disabled whenever there is no active session. The first
            value is the menu in which the option exists. The second
            value is the 0-based index of the option within that menu.
            Defaults to an empty list.

    """

    def __init__(self, *args, **kargs):
        """The constructor passes its arguments to the `tk.Tk`
        constructor.

        """
        # build window and initialize variables
        tk.Tk.__init__(self, *args, **kargs)
        self.title('STL Planner')
        self.showTimestamps = tk.BooleanVar(self, True)
        self.disableOnModal = []
        self.sessionOnly = []
        self._menuEnabled = True
        self.buildMenu()
        self._session = Session(self)
        self.session.pack()

    @property
    def session(self):
        """`legends.ui.session.Session`: The currently running user
        session. Defaults to a new `legends.ui.session.Session` instance
        with no save slot.
        """
        return self._session

    @property
    def menuEnabled(self):
        """`bool`: `True` if the menu options in `disableOnModal` are
        enabled. Upon setting this property, those menu options' states
        are set accordingly. Menu options in `sessionOnly` are
        unaffected by changes to this property when there is no active
        session.
        """
        return self._menuEnabled

    @menuEnabled.setter
    def menuEnabled(self, value):
        self._menuEnabled = value
        state = tk.NORMAL if value else tk.DISABLED
        for menu, index in self.disableOnModal:
            if ((menu, index) in self.sessionOnly
                and state == tk.NORMAL
                and self.session.saveslot is None
            ):
                continue
            menu.entryconfig(index, state=state)

    def buildMenu(self):
        """Builds the menu bar.

        """
        menuBar = tk.Menu(self)
        self.config(menu=menuBar)

        # build the File menu
        fileMenu = tk.Menu(menuBar)
        menuBar.add_cascade(label='File', menu=fileMenu)

        # build the File > New Session submenu
        newSessionSubmenu = tk.Menu(fileMenu)
        fileMenu.add_cascade(label='New Session', menu=newSessionSubmenu)

        # populate the File > New Session submenu
        newSessionSubmenu.add_command(
            label='From Save File...', command=self.newFromFile
        )
        self.disableOnModal.append((newSessionSubmenu, 0))
        newSessionSubmenu.add_command(
            label='From Clipboard', command=self.newFromClipboard
        )
        self.disableOnModal.append((newSessionSubmenu, 1))
        newSessionSubmenu.add_command(
            label='Maxed Characters...', command=self.newMaxChars
        )
        self.disableOnModal.append((newSessionSubmenu, 2))

        # build and populate the Session menu
        sessionMenu = tk.Menu(menuBar)
        menuBar.add_cascade(label='Session', menu=sessionMenu)
        sessionMenu.add_checkbutton(
            label='Show Timestamps', variable=self.showTimestamps,
            command=self.setTimestamps
        )
        self.disableOnModal.append((sessionMenu, 0))
        sessionMenu.add_command(
            label='Inventory',
            command=lambda: InventoryScreen(self),
            state=tk.DISABLED
        )
        self.disableOnModal.append((sessionMenu, 1))
        self.sessionOnly.append((sessionMenu, 1))
        sessionMenu.add_command(
            label='Missions',
            command=lambda: MissingMissions(self),
            state=tk.DISABLED
        )
        self.disableOnModal.append((sessionMenu, 2))
        self.sessionOnly.append((sessionMenu, 2))
        sessionMenu.add_command(
            label='Survival Effects',
            command=lambda: SurvivalEffects(self),
            state=tk.DISABLED
        )
        self.disableOnModal.append((sessionMenu, 3))
        self.sessionOnly.append((sessionMenu, 3))

        # build and populate the Help menu
        helpMenu = tk.Menu(menuBar)
        menuBar.add_cascade(label='Help', menu=helpMenu)
        helpMenu.add_command(
            label='STL Planner Help', command=lambda: HelpScreen(self)
        )
        self.disableOnModal.append((helpMenu, 0))

    def newSession(self, saveslot):
        """Clears the current session and starts a new one with the
        given `legends.saveslot.SaveSlot` object. Sets the `menuEnabled`
        property to `True`.

        Args:
            saveslot (legends.saveslot.SaveSlot): The
                `legends.saveslot.SaveSlot` instance to associate with
                the new session.

        """
        self.session.destroy()
        self._session = Session(self, saveslot)
        self.menuEnabled = True
        self.session.pack(expand=tk.YES, fill=tk.Y)

    def askCloseSession(self):
        """Returns `True` if there is no active session. (An active
        session is one whose `saveslot` attribute is not `None`.) If
        there is an active session, asks the user if it is okay to close
        it.

        Returns:
            bool: `True` if it is okay to close the current session.

        """
        if self.session.saveslot is None:
            return True
        return askyesno(self, 'Close Session', 'Close current session?')

    def newFromFile(self):
        """Prompts the user for a save slot, then builds a
        `legends.saveslot.SaveSlot` object and starts a new session.

        """
        if self.askCloseSession():
            try:
                save = decryptSaveFile()
            except FileNotFoundError:
                showerror(self, 'File Not Found', 'Save file not found.')
                return
            saveslot = AskSlot(self, save).result
            if saveslot is None:
                return
            self.newSession(saveslot)

    def newFromClipboard(self):
        """Provides instructions on copying save data to the clipboard,
        then builds a `legends.saveslot.SaveSlot` object and starts a
        new session.

        """
        if self.askCloseSession():
            saveslot = AskClipboard(self).result
            if saveslot is None:
                return
            self.newSession(saveslot)

    def newMaxChars(self):
        """Prompts the user to choose from an array of options, then
        starts a new session using a roster of maxed characters.

        """
        if self.askCloseSession():
            result = AskMaxChars(self).result
            if result is None:
                return
            chars, maxGear = result
            saveslot = SaveSlot()
            saveslot.roster.fillChars(chars, maxGear)
            self.newSession(saveslot)

    def setTimestamps(self, *args): # pylint: disable=unused-argument
        """Sets the visibility of the timestamps in the active session
        according to the value of the `showTimestamps` attribute.

        """
        if self.showTimestamps.get():
            self.session.makeTimeBar()
        else:
            self.session.removeTimeBar()
