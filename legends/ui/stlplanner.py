"""The STL Planner main window and supporting objects.

"""

import tkinter as tk
from tkinter import GROOVE, LEFT, Y, YES, DISABLED, NORMAL, W, EW, TOP, BOTTOM
from legends.functions import decryptSaveFile
from legends.saveslot import SaveSlot
from legends.ui.dialogs import showerror, askSlot, askMaxChars, askyesno
from legends.ui.rostertab import RosterTab

__all__ = ['cleanTime', 'STLPlanner']

def cleanTime(delta):
    """Converts a timedelta object into a string description that shows
    the number of days (if positive), hours, and minutes.

    Args:
        delta (timedelta): The timedelta object to convert.

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
    """STL Planner main window.

    Run the STL Planner app with `STLPlanner().mainloop()`.

    Args:
        saveslot (SaveSlot): The user's save data.
        activeSession (bool): True if the app has an active session
            open.
        disableOnModal (list of (tk.Menu, int)): Each item in this list
            is a 2-tuple that represents a menu option which should be
            disabled when a modal dialog is open. The first value is the
            menu in which the option exists. The second value is the
            0-based index of the option within that menu.
        showTimestamps (tk.BooleanVar): True if the info bar with
            timestamp data should be shown.
        sessionFrame (tk.Frame): The frame that holds the contents of
            current session.
        infoBar (tk.Frame): A bar of timestamp information from the
            session save file.

    """

    def __init__(self, *args, **kargs):
        # build window and initialize variables
        tk.Tk.__init__(self, *args, **kargs)
        self.title('STL Planner')
        self.saveslot = None
        self.activeSession = False
        self.disableOnModal = []
        self.showTimestamps = tk.BooleanVar(self, True)
        self.showTimestamps.trace('w', self.setTimestamps)
        self._menuEnabled = True
        self.sessionFrame = tk.Frame(self)
        self.sessionFrame.pack()
        self.infoBar = None

        # build menu bar
        menuBar = tk.Menu(self)
        fileMenu = tk.Menu(menuBar)
        newSessionSubmenu = tk.Menu(fileMenu)
        sessionMenu = tk.Menu(menuBar)
        menuBar.add_cascade(label='File', menu=fileMenu)
        menuBar.add_cascade(label='Session', menu=sessionMenu)
        fileMenu.add_cascade(label='New Session', menu=newSessionSubmenu)
        newSessionSubmenu.add_command(
            label='From Save File...', command=self.newFromFile
        )
        newSessionSubmenu.add_command(
            label='Maxed Characters', command=self.newMaxChars
        )
        sessionMenu.add_checkbutton(
            label='Show Timestamps', variable=self.showTimestamps
        )
        self.config(menu=menuBar)
        self.disableOnModal.append((newSessionSubmenu, 0))
        self.disableOnModal.append((newSessionSubmenu, 1))
        self.disableOnModal.append((sessionMenu, 0))

        # show start screen
        buttonbox = tk.Frame(self.sessionFrame)
        tk.Button(
            buttonbox, text='from HD', command=self.newFromFile
        ).grid(row=0, column=0, sticky=EW)
        tk.Button(
            buttonbox, text='MAX', command=self.newMaxChars
        ).grid(row=1, column=0, sticky=EW)
        tk.Label(
            buttonbox, text='Extract data from your local save file'
        ).grid(row=0, column=1, sticky=W)
        tk.Label(
            buttonbox, text='Create a roster of maxed characters'
        ).grid(row=1, column=1, sticky=W)
        buttonbox.pack(padx=50, pady=50)

    @property
    def menuEnabled(self):
        """bool: True if the menu options in `disableOnModal` are
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

    def clear(self):
        """Destroys, rebuild, and packs the `sessionFrame` frame.

        """
        self.sessionFrame.destroy()
        self.infoBar = None
        self.sessionFrame = tk.Frame(self)
        self.sessionFrame.pack()

    def makeInfoBar(self):
        """Builds and returns an info bar frame containing basic
        timestamp information about the embedded save slot.

        Returns:
            Frame: The info bar. A child of the calling instance.

        """
        # build bar and initialize variables
        bar = tk.Frame(self.sessionFrame)
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
            labels[j] = tk.Label(bar, borderwidth=2, relief=GROOVE,padx=10)
        for index, text in enumerate([start, last, total, average]):
            labels[index].config(text=text)

        # pack labels and return bar
        for label in labels:
            label.pack(side=LEFT)
        return bar

    def setTimestamps(self, *args): # pylint: disable=unused-argument
        """Toggles the visibility of the info bar.

        """
        if not self.activeSession:
            return
        if self.showTimestamps.get():
            if self.infoBar is None:
                self.infoBar = self.makeInfoBar()
                self.infoBar.pack(side=TOP)
        else:
            if self.infoBar is not None:
                self.infoBar.destroy()
                self.infoBar = None

    def newFromFile(self):
        """Prompts the user for a save slot, then builds and stores a
        SaveSlot object.

        """
        if (self.activeSession and not askyesno(
            self, 'Close Session', 'Close current session?'
        )):
            return
        try:
            save = decryptSaveFile()
        except FileNotFoundError:
            showerror(self, 'File Not Found', 'Save file not found.')
            return
        saveslot = askSlot(self, save)
        if saveslot is None:
            return
        self.saveslot = saveslot
        self.newSession()

    def newSession(self):
        """Clears the current session, loads the info bar if needed,
        loads a new roster tab, and sets the `activeSession` attribute
        to True.

        """
        self.clear()
        self.activeSession = True
        self.setTimestamps()
        RosterTab(self).pack(side=BOTTOM, expand=YES, fill=Y)

    def newMaxChars(self):
        """Prompts the user to choose from an array of options, then
        starts a new session using a roster of maxed characters.

        """
        if (self.activeSession and not askyesno(
            self, 'Close Session', 'Close current session?'
        )):
            return
        self.activeSession = True
        result = askMaxChars(self)
        if result is None:
            return
        chars, maxGear = result
        self.saveslot = SaveSlot()
        self.saveslot.roster.fillChars(chars, maxGear)
        self.newSession()
