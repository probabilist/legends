"""The STL Planner main window and supporting objects.

"""

import tkinter as tk
from tkinter import GROOVE, LEFT, X, Y, YES, DISABLED, NORMAL
from legends.constants import ENABLED
from legends.functions import decryptSaveFile
from legends.saveslot import SaveSlot
from legends.ui.dialogs import showerror, askSlot
from legends.ui.rostertab import RosterTab

__all__ = ['cleanTime', 'STLPlanner', 'StartFrame']

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
        self.disableOnModal = []
        self.timePerDayLabel = tk.StringVar(self, '')
        self.timePerDayToggle = tk.BooleanVar(self, True)
        self.timePerDayToggle.trace('w', self.setTimePerDayLabel)
        self._menuEnabled = True

        # build menu bar
        menuBar = tk.Menu(self)
        fileMenu = tk.Menu(menuBar)
        newSession = tk.Menu(fileMenu)
        viewMenu = tk.Menu(menuBar)
        menuBar.add_cascade(label='File', menu=fileMenu)
        menuBar.add_cascade(label='View', menu=viewMenu)
        fileMenu.add_cascade(label='New session', menu=newSession)
        newSession.add_command(
            label='From save file...', command=self.newFromFile
        )
        newSession.add_command(
            label='Maxed characters', command=self.newMaxChars
        )
        viewMenu.add_checkbutton(
            label='Show play time per day', variable=self.timePerDayToggle
        )
        self.config(menu=menuBar)
        self.disableOnModal.append((newSession, 0))
        self.disableOnModal.append((newSession, 1))
        self.disableOnModal.append((viewMenu, 0))

        # show start screen
        self.mainFrame = tk.Frame(self)
        self.mainFrame.pack()
        # startFrame = StartFrame(self.mainFrame)
        # startFrame.pack()
        # self.wait_variable(startFrame.built)
        # self.saveslot = startFrame.saveslot
        # startFrame.destroy()

        # build info bar and roster tab
        # self.infoBar().pack()
        # RosterTab(self).pack(expand=YES, fill=Y)

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

    def newMaxChars(self):
        self.saveslot = SaveSlot()
        self.saveslot.roster.fillChars(ENABLED)
        self.clear()
        self.infoBar().pack()
        RosterTab(self).pack(expand=YES, fill=Y)

class StartFrame(tk.Frame):
    """The starting frame of the STL Planner app.

    Attributes:
        root (STLPlanner): The currently running STLPlanner instance.
        built (tk.BooleanVar): True if the `saveslot` property contains
            a SaveSlot object. Used by other UI objects to detect when
            the SaveSlot object has been built.

    """

    def __init__(self, root, parent=None, **options):
        tk.Frame.__init__(self, parent, **options)
        self.root = root
        self.built = tk.BooleanVar()
        self.saveslot = None
        panel = tk.Frame(self)
        tk.Button(
            panel, text='extract save data', command=self.extractFromHD
        ).pack(expand=YES, fill=X)
        tk.Button(
            panel, text='make max', command=self.makeMax
        ).pack(expand=YES, fill=X)
        panel.pack(padx=50, pady=50)

    @property
    def saveslot(self):
        """SaveSlot: The SaveSlot object that will be used by the app.
        When setting this property, the `built` attribute is also
        changed.
        """
        return self._saveslot

    @saveslot.setter
    def saveslot(self, value):
        self._saveslot = value
        self.built.set(isinstance(value, SaveSlot))

    def extractFromHD(self):
        """Prompts the user for a save slot, then builds and stores a
        SaveSlot object.

        """
        try:
            save = decryptSaveFile()
        except FileNotFoundError:
            showerror(self.root, 'File Not Found', 'Save file not found.')
            return
        saveslot = askSlot(self.root, save)
        if saveslot is not None:
            self.saveslot = saveslot

    def makeMax(self):
        saveslot = SaveSlot()
        saveslot.roster.fillChars(ENABLED)
        self.saveslot = saveslot
