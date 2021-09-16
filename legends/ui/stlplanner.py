"""The STL Planner main window and supporting objects.

"""

import tkinter as tk
from tkinter import GROOVE, LEFT, Y, YES, DISABLED, NORMAL, W, EW
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
        timePerDayLabel (tk.StringVar): The text that appears in the
            label on the info bar which displays the average amount of
            time per day the user has spent in the game.
        timePerDayToggle (tk.BooleanVar): If False, the time-per-day
            label will show 0; otherwise it shows the correct value.

    """

    def __init__(self, *args, **kargs):
        # build window and initialize variables
        tk.Tk.__init__(self, *args, **kargs)
        self.title('STL Planner')
        self.saveslot = None
        self.activeSession = False
        self.disableOnModal = []
        self.timePerDayLabel = tk.StringVar(self, '')
        self.timePerDayToggle = tk.BooleanVar(self, True)
        self.timePerDayToggle.trace('w', self.setTimePerDayLabel)
        self._menuEnabled = True
        self.mainFrame = tk.Frame(self)
        self.mainFrame.pack()

        # build menu bar
        menuBar = tk.Menu(self)
        fileMenu = tk.Menu(menuBar)
        newSession = tk.Menu(fileMenu)
        prefMenu = tk.Menu(menuBar)
        menuBar.add_cascade(label='File', menu=fileMenu)
        menuBar.add_cascade(label='Preferences', menu=prefMenu)
        fileMenu.add_cascade(label='New session', menu=newSession)
        newSession.add_command(
            label='From save file...', command=self.newFromFile
        )
        newSession.add_command(
            label='Maxed characters', command=self.newMaxChars
        )
        prefMenu.add_checkbutton(
            label='Show play time per day', variable=self.timePerDayToggle
        )
        self.config(menu=menuBar)
        self.disableOnModal.append((newSession, 0))
        self.disableOnModal.append((newSession, 1))
        self.disableOnModal.append((prefMenu, 0))

        # show start screen
        buttonbox = tk.Frame(self.mainFrame)
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

    # pylint: disable-next=unused-argument
    def setTimePerDayLabel(self, *args):
        """Updates the text of the time-per-day label, according to
        whether the user has selected the option to show time per day.

        """
        if self.timePerDayToggle.get() and self.saveslot is not None:
            self.timePerDayLabel.set(
                'play time per day: '
                + cleanTime(self.saveslot.timestamps.playTimePerDay)
            )
        else:
            self.timePerDayLabel.set('play time per day: 0 hrs 0 min')

    def clear(self):
        """Destroys, rebuild, and packs the `mainFrame` frame.

        """
        self.mainFrame.destroy()
        self.mainFrame = tk.Frame(self)
        self.mainFrame.pack()

    def infoBar(self):
        """Builds and returns an info bar frame containing basic
        timestamp information about the embedded save slot.

        Returns:
            Frame: The info bar. A child of the calling instance.

        """
        # build bar and initialize variables
        bar = tk.Frame(self.mainFrame)
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
        self.setTimePerDayLabel()

        # build labels
        labels = [None] * 4
        for j in range(4):
            labels[j] = tk.Label(bar, borderwidth=2, relief=GROOVE,padx=10)
        for index, text in enumerate([start, last, total]):
            labels[index].config(text=text)
        labels[3].config(textvariable=self.timePerDayLabel)

        # pack labels and return bar
        for label in labels:
            label.pack(side=LEFT)
        return bar

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
        self.clear()
        self.infoBar().pack()
        RosterTab(self).pack(expand=YES, fill=Y)
        self.activeSession = True

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
        self.clear()
        self.infoBar().pack()
        RosterTab(self).pack(expand=YES, fill=Y)
        self.activeSession = True
