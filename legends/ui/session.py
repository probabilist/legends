"""The `legends.ui.session.Session` class and related objects.

"""

import tkinter as tk
from tkinter import ttk
from getpass import getuser
from legends.utils.relations import bidict
from legends.utils.scrollframe import ScrollFrame
from legends.constants import ITEMS
from legends.functions import cleanTime, levelFromXP, xpFromLevel
from legends.saveslot import Inventory
from legends.ui.dialogs import ModalMessage
from legends.ui.rostertab import RosterTab, RosterFilter
from legends.ui.chartab import CharTab

__all__ = [
    'InventoryScreen',
    'MissingMissions',
    'Session',
    'SessionSettings',
    'SurvivalEffects'
]

class InventoryScreen(ModalMessage):
    """A message dialog showing the player's inventory.

    Attributes:
        levelMap (legends.utils.relations.bidict): {`int`:`int`} After
            fully leveling, from 1 to 99, as many characters as possible
            with the bio-gel items in the inventory, a certain amount of
            excess bio-gel will remain. A `key`, `value` pair in this
            dictionary means that this excess bio-gel can level a
            character of level `key` to level `value`.
        startLevel (tk.StringVar): The level displayed in the starting
            level combo-box.
        endLevel (tk.StringVar): The level displayed in the ending level
            combo-box.

    """
    def __init__(self, root, parent=None):
        self.root = root
        self.levelMap = bidict()
        extraXP = self.inventory.xp % xpFromLevel(99)
        for start in range(1,99):
            end = levelFromXP(xpFromLevel(start) + extraXP)
            if start > 1 and start == end:
                break
            try:
                self.levelMap[start] = end
            except ValueError:
                pass
        self.startLevel = tk.StringVar(None, '1')
        self.endLevel = tk.StringVar()
        self.setEndLevel()
        ModalMessage.__init__(self, root, parent, 'Inventory')

    @property
    def inventory(self):
        """`legends.constants.Inventory`: The inventory associated
        with the current session.
        """
        return self.root.session.saveslot.inventory

    @property
    def roster(self):
        """`legends.roster.Roster`: The roster associated with the
        current session.
        """
        return self.root.session.saveslot.roster

    def body(self, master):
        """Create the body of the dialog.

        """
        # grid the inventory quantities
        self.displayCat(master, 'Currency', (0, 0))
        self.displayCat(master, 'General Items', (0, 2))
        self.displayCat(master, 'Bio-Gel', (4, 0), True)
        self.displayCat(master, 'Protomatter', (10, 0), True)
        self.displayCat(master, 'Gear Leveling Materials', (16, 0), True)
        self.displayCat(master, 'Gear Ranking Materials', (16, 2), True)

        # show total XP
        tk.Label(
            master, text='TOTAL BIO-GEL XP:', font=(None, 13, 'italic')
        ).grid(row=5, column=2, sticky=tk.W, padx=(20,0))
        tk.Label(
            master, text='{:,}'.format(self.inventory.xp)
        ).grid(row=5, column=3, sticky=tk.E, padx=(0,20))

        # show number of characters can level
        chars = int(self.inventory.xp/xpFromLevel(99))
        tk.Label(
            master,
            text='Can fully level {} character{},'.format(
                chars,
                's' if chars > 1 else ''
            )
        ).grid(row=6, column=2, columnspan=2, padx=(20,20))

        # show additional character, partial level
        tk.Label(
            master, text='and one more from'
        ).grid(row=7, column=2, columnspan=2, padx=(20,20))

        # build combo-box level-checking tool
        bar = tk.Frame(master)

        # starting level combo-box
        tk.Label(bar, text='Level').pack(side=tk.LEFT)
        startLevelBox = ttk.Combobox(
            bar, textvariable=self.startLevel,
            values=[str(level) for level in self.levelMap],
            state='readonly', width=2
        )
        startLevelBox.pack(side=tk.LEFT)
        startLevelBox.bind(
            '<<ComboboxSelected>>', lambda event:self.setEndLevel()
        )

        # ending level combo-box
        tk.Label(
            bar, text='to'
        ).pack(side=tk.LEFT)
        endLevelBox = ttk.Combobox(
            bar, textvariable=self.endLevel,
            values=[str(level) for level in self.levelMap.values()],
            state='readonly', width=2
        )
        endLevelBox.pack(side=tk.LEFT)
        endLevelBox.bind(
            '<<ComboboxSelected>>', lambda event:self.setStartLevel()
        )

        # pack combo-box level-checking tool
        bar.grid(row=8, column=2, columnspan=2, padx=(20,20))

        # show protomatter needed to max roster
        tk.Label(
            master, text='Needed to Max Roster', font=(None, 13, 'italic')
        ).grid(row=10, column=2, columnspan=2, sticky=tk.W, pady=(20,0))
        for index, item in enumerate(self.inventory.keysByCat('Protomatter')):
            totalNeeded = Inventory()
            for char in self.roster.chars.values():
                if char.role == item.role:
                    totalNeeded = sum(
                        (skill.itemsToMax for skill in char.skills.values()),
                        totalNeeded
                    )
            tk.Label(
                master, text='{:,} + {:,} Latinum'.format(
                    totalNeeded[item],
                    totalNeeded[ITEMS['Latinum']]
                )
            ).grid(row=11 + index, column=2, sticky=tk.W)

    def setStartLevel(self):
        """Sets the `tkinter` variable in the `startLevel` attribute
        according to the value of `endLevel`.

        """
        self.startLevel.set(str(
            self.levelMap.inverse[int(self.endLevel.get())]
        ))

    def setEndLevel(self):
        """Sets the `tkinter` variable in the `endLevel` attribute
        according to the value of `startLevel`.

        """
        self.endLevel.set(str(
            self.levelMap[int(self.startLevel.get())]
        ))

    def displayCat(self, master, cat, coords, pad=False):
        """Grids the headings, labels, and item quantities for the given
        category onto the given master object.

        Args:
            master (obj): The `tkinter` object to assign as master.
            cat (str): The category of items to grid.
            coords (tuple): (`int`,`int`) The row and column of the top
                left corner of the display.
            pad (bool): `True` if the display should have vertical
                padding above it.

        """
        row, col = coords
        catLabel = tk.Label(master, text=cat, font=(None, 13, 'bold'))
        catLabel.grid(row=row, column=col, columnspan=2, sticky=tk.W)
        if pad:
            catLabel.grid_configure(pady=(20,0))
        row += 1
        for item, qty in self.inventory.itemsByCat(cat):
            tk.Label(master, text=item.name).grid(
                row=row, column=col, sticky=tk.W, padx=(20,0)
            )
            tk.Label(master, text='{:,}'.format(qty)).grid(
                row=row, column=col + 1, sticky=tk.E, padx=(0,20)
            )
            row += 1

class MissingMissions(ModalMessage):
    """A message showing the player's incomplete missions.

    Also shows the total uncollected gear ranking materials.

    """

    def __init__(self, root, parent=None):
        ModalMessage.__init__(self, root, parent, 'Incomplete Missions')

    def body(self, master):
        """Create the body of the dialog.

        """
        scrollFrame = ScrollFrame(master)
        display = tk.Frame(scrollFrame.content)
        scrollFrame.canvas.config(height=0.5 * self.winfo_screenheight())
        incompleteMissions = [
            mission for mission in self.root.session.saveslot.missions
            if mission.complete < 1
        ]
        missingRewards = Inventory()
        for mission in incompleteMissions:
            missingRewards = missingRewards + mission.missingNodeRewards
            missingRewards = missingRewards + mission.rewards
        tk.Label(
            display,
            text='Uncollected Gear Ranking Materials',
            font=(None, 13, 'bold')
        ).grid(row=0, column=0, columnspan=3, sticky=tk.W)
        row = 1
        for item, qty in missingRewards.itemsByCat('Gear Ranking Materials'):
            tk.Label(
                display, text=item.name
            ).grid(row=row, column=0, columnspan=2, sticky=tk.W)
            tk.Label(
                display, text='{:,}'.format(qty)
            ).grid(row=row, column=2, sticky=tk.E)
            row += 1
        tk.Label(
            display, text='Incomplete Missions', font=(None, 13, 'bold')
        ).grid(row=row, column=0, columnspan=3, sticky=tk.W, pady=(20,0))
        row += 1
        for mission in incompleteMissions:
            tk.Label(
                display, text=mission.difficulty
            ).grid(row=row, column=0, sticky=tk.W)
            tk.Label(
                display,
                text='Episode {} Mission {}'.format(
                    mission.episode,
                    mission.orderIndex
                )
            ).grid(row=row, column=1, sticky=tk.W)
            tk.Label(
                display, text='{:.0%}'.format(mission.complete)
            ).grid(row=row, column=2, sticky=tk.E)
            row += 1
        display.pack(padx=20)
        scrollFrame.pack(expand=tk.YES, fill=tk.BOTH)

class Session(tk.Frame):
    """A user session in the *STL Planner* app.

    Attributes:
        saveslot (legends.saveslot.SaveSlot): The
            `legends.saveslot.SaveSlot` object associated with the
            session.
        settings (SessionSettings): The `SessionSettings` instance that
            stores the settings for the current session.
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
        self.settings = SessionSettings()
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
        ).grid(row=0, column=0, sticky=tk.EW)
        tk.Button(
            buttonbox,
            text='from Clipboard', command=self.master.newFromClipboard
        ).grid(row=1, column=0, sticky=tk.EW)
        tk.Button(
            buttonbox, text='MAX', command=self.master.newMaxChars
        ).grid(row=2, column=0, sticky=tk.EW)
        tk.Label(
            buttonbox, text='Extract data from your local save file'
        ).grid(row=0, column=1, sticky=tk.W)
        tk.Label(
            buttonbox, text='Use a support email to extract your data'
        ).grid(row=1, column=1, sticky=tk.W)
        tk.Label(
            buttonbox, text='Create a roster of maxed characters'
        ).grid(row=2, column=1, sticky=tk.W)
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
                self.timeBar, borderwidth=2, relief=tk.GROOVE, padx=10
            )
        for index, text in enumerate([start, last, total, average]):
            labels[index].config(text=text)

        # pack labels and bar
        for label in labels:
            label.pack(side=tk.LEFT)
        self.timeBar.pack(side=tk.TOP)

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
        self.tab.pack(side=tk.BOTTOM, expand=tk.YES, fill=tk.Y)
        self.master.title('STL Planner - Roster')

    def charTab(self, char):
        """Loads a new `legends.ui.chartab.CharTab` instance into the
        `tab` attribute.

        """
        self.tab.destroy()
        self.tab = CharTab(char, self)
        self.tab.pack(side=tk.BOTTOM, expand=tk.YES, fill=tk.Y)
        self.master.title('STL Planner - {}'.format(char.shortName))

class SessionSettings(): # pylint: disable=too-few-public-methods
    """Stores the settings for a `Session`.

    Attributes:
        rosterFilter (legends.ui.rostertab.RosterFilter): The
            `legends.ui.rostertab.RosterFilter` object storing the
            current filter settings for the roster tab.
        rosterExportFile (str): The path to use when prompting the user
            to export their roster to a spreadsheet.
        excludeCommons (tk.BooleanVar): `True` is the summon rate
            calculations made by the roster tab should exclude Common
            characters.

    """

    def __init__(self):
        self.rosterFilter = RosterFilter()
        self.rosterExportFile = '/Users/' + getuser() + '/Documents/roster.csv'
        self.excludeCommons = tk.BooleanVar(None, True)

class SurvivalEffects(ModalMessage):
    """A message showing the active battle modifiers in survival mode.

    """

    def __init__(self, root, parent=None):
        ModalMessage.__init__(self, root, parent, 'Active Survival Effects')

    def body(self, master):
        """Create the body of the dialog.

        """
        saveslot = self.root.session.saveslot
        count = 0
        for effect, durations in saveslot.survivalEffects.items():
            for duration in durations:
                tk.Label(
                    master, text=effect
                ).grid(row=count, column=0, sticky=tk.W, padx=(20,0))
                tk.Label(
                    master, text='({} battles remaining)'.format(duration)
                ).grid(row=count, column=1, sticky=tk.E, padx=(0,20))
                count += 1
