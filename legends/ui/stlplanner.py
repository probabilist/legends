"""The `legends.ui.stlplanner.STLPlanner` class and related objects.

The *STL PLanner* app can be launched with `STLPlanner().mainloop()`.

"""

import tkinter as tk
from tkinter import GROOVE, LEFT, Y, YES, DISABLED, NORMAL, W, EW, TOP, BOTTOM
from legends.constants import ITEMS
from legends.savefile import decryptSaveFile
from legends.saveslot import SaveSlot
from legends.ui.dialogs import (
    showerror, askSlot, askMaxChars, askyesno, HelpScreen
)
from legends.ui.rostertab import RosterTab

__all__ = ['cleanTime', 'STLPlanner', 'Session']

def cleanTime(delta):
    """Converts a `timedelta` object into a string description that
    shows the number of days (if positive), hours, and minutes.

    Args:
        delta (timedelta): The `timedelta` object to convert.

    Returns:
        str: The string description.

    """
    minutes = int(delta.total_seconds()/60)
    hours, minutes = minutes//60, minutes % 60
    days, hours = hours//24, hours % 24
    display = '{} days '.format(days) if days > 1 else ''
    display += '{} hrs {} min'.format(hours, minutes)
    return display

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
        session (Session): The currently running user session. Defaults
            to a new `Session` instance with no save slot.

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
        self._menuEnabled = True
        self.buildMenu()
        self.session = Session(self)
        self.session.pack()

    @property
    def menuEnabled(self):
        """`bool`: `True` if the menu options in `disableOnModal` are
        enabled. Upon setting this property, those menu options' states
        are set accordingly.
        """
        return self._menuEnabled

    @menuEnabled.setter
    def menuEnabled(self, value):
        self._menuEnabled = value
        state = NORMAL if value else DISABLED
        for menu, index in self.disableOnModal:
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
            label='Maxed Characters', command=self.newMaxChars
        )
        self.disableOnModal.append((newSessionSubmenu, 1))

        # build and populate the Session menu
        sessionMenu = tk.Menu(menuBar)
        menuBar.add_cascade(label='Session', menu=sessionMenu)
        sessionMenu.add_checkbutton(
            label='Show Timestamps', variable=self.showTimestamps,
            command=self.setTimestamps
        )
        self.disableOnModal.append((sessionMenu, 0))
        sessionMenu.add_command(label='Inventory...', command=self.inventory)
        self.disableOnModal.append((sessionMenu, 1))

        # build and populate the Help menu
        helpMenu = tk.Menu(menuBar)
        menuBar.add_cascade(label='Help', menu=helpMenu)
        helpMenu.add_command(
            label='STL Planner Help', command=lambda: HelpScreen(self)
        )
        self.disableOnModal.append((helpMenu, 0))

    def newSession(self, saveslot):
        """Clears the current session and starts a new one with the
        given `legends.saveslot.SaveSlot` object.

        Args:
            saveslot (legends.saveslot.SaveSlot): The
                `legends.saveslot.SaveSlot` instance to associate with
                the new session.

        """
        self.session.destroy()
        self.session = Session(self, saveslot)
        self.session.pack()

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
            saveslot = askSlot(self, save)
            if saveslot is None:
                return
            self.newSession(saveslot)

    def newMaxChars(self):
        """Prompts the user to choose from an array of options, then
        starts a new session using a roster of maxed characters.

        """
        if self.askCloseSession():
            result = askMaxChars(self)
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

    def inventory(self):
        """Prints the inventory of the save slot associated with the
        current session to the console. Organizes the data by category.
        Ignores the categories 'Token', 'PlayerAvatar', and 'Emote'.
        Ignores a number of other items that are either not relevant to
        the current implementation of *Star Trek: Legends*, or are not
        relevant to the *STL Planner* app.
        """
        # TODO: Replace with a dialog window. <>
        ignoredCategories = ['Token', 'PlayerAvatar', 'Emote']
        ignoredItemIDs = [
            'Credits', 'Dilithium', 'Tritanium', 'Player XP', 'PvP Stamina',
            'Alliance Stamina', 'EventPoint', 'PvP Chest Points',
            'Shards Advanced', 'Shards Elite', 'Shards Credit',
            'Shards Biomimetic', 'Shards Protomatter', 'Shards_Worf',
            'Shards_McCoy'
        ]
        categories = []
        for item in ITEMS.values():
            cat = item.category
            if cat in ignoredCategories:
                continue
            if cat not in categories:
                categories.append(cat)
        for cat in categories:
            print('# {}'.format(cat))
            for itemID, qty in self.session.saveslot.inventory.items():
                if itemID in ignoredItemIDs:
                    continue
                item = ITEMS[itemID]
                if item.category == cat:
                    print('    * {}: {}'.format(item.name, qty))


class Session(tk.Frame):
    """A user session in the *STL Planner* app.

    Attributes:
        saveslot (legends.saveslot.SaveSlot): The
            `legends.saveslot.SaveSlot` object associated with the
            session.
        timeBar (tk.Frame): The horizontal bar at the top of the session
            frame that displays time stamp info connected with the
            associated save slot.
        tab (tk.Frame): The visible tab in the session frame.

    """
    def __init__(self, stlplanner, saveslot=None, **options):
        """The constructor creates a new session associated with the
        given `legends.saveslot.SaveSlot` object. If none is provided,
        the session displays buttons that activate choices from the
        `File` menu.

        Args:
            stlplanner (STLPlanner): The `STLPlanner` instance to be
                assigned as the parent of this session.

        """
        tk.Frame.__init__(self, stlplanner, **options)
        self.saveslot = saveslot
        self.timeBar = None
        self.tab = tk.Frame(self)
        self.tab.pack()
        if saveslot is None:
            self.startFrame()
        else:
            self.makeTimeBar()
            self.rosterTab()

    def startFrame(self):
        """Build the starting frame, with choices from the `File` menu.

        """
        buttonbox = tk.Frame(self.tab)
        tk.Button(
            buttonbox, text='from HD', command=self.master.newFromFile
        ).grid(row=0, column=0, sticky=EW)
        tk.Button(
            buttonbox, text='MAX', command=self.master.newMaxChars
        ).grid(row=1, column=0, sticky=EW)
        tk.Label(
            buttonbox, text='Extract data from your local save file'
        ).grid(row=0, column=1, sticky=W)
        tk.Label(
            buttonbox, text='Create a roster of maxed characters'
        ).grid(row=1, column=1, sticky=W)
        buttonbox.pack(padx=50, pady=50)

    def makeTimeBar(self):
        """Builds a horizontal bar (a `tk.Frame` instance) containing
        timestamp information from the associated save slot, then
        assigns the bar to the `timeBar` attribute. If there is no save
        slot, or the time bar already exists, or the `STLPlanner` master
        prohibits it, the method does nothing.

        """
        if (
            self.saveslot is None
            or self.timeBar is not None
            or not self.master.showTimestamps.get()
        ):
            return

        # build bar and initialize variables
        self.timeBar = tk.Frame(self)
        timestamps = self.saveslot.timestamps
        start = (
            'start date: '
            + timestamps.startDate.strftime('%b %-d %Y %H:%M %Z')
        )
        last = (
            'last played: '
            + timestamps.timeLastPlayed.strftime('%b %-d %Y %H:%M %Z')
        )
        total = (
            'play duration: ' + cleanTime(timestamps.playDuration)
        )
        average = (
            'play time per day: ' + cleanTime(timestamps.playTimePerDay)
        )

        # build labels
        labels = [None] * 4
        for j in range(4):
            labels[j] = tk.Label(
                self.timeBar, borderwidth=2, relief=GROOVE, padx=10
            )
        for index, text in enumerate([start, last, total, average]):
            labels[index].config(text=text)

        # pack labels and bar
        for label in labels:
            label.pack(side=LEFT)
        self.timeBar.pack(side=TOP)

    def removeTimeBar(self):
        """If the time bar exists, it is destroyed and the `timeBar`
        attribute is set to `None`.

        """
        if self.timeBar is not None:
            self.timeBar.destroy()
            self.timeBar = None

    def rosterTab(self):
        """Loads a new `legends.ui.rostertab.RosterTab` instance into
        the `tab` attribute.

        """
        self.tab.destroy()
        self.tab = RosterTab(self)
        self.tab.pack(side=BOTTOM, expand=YES, fill=Y)
        self.master.title('STL Planner - Roster')
