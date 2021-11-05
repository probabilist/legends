"""The `legends.ui.rostertab.RosterTab` class and related objects.

"""

import tkinter as tk
from tkinter import ttk
from csv import DictWriter
import os
from legends.utils.functions import camelToSpace
from legends.utils.scrollframe import ScrollFrame
# pylint: disable-next=no-name-in-module
from legends.constants import (
    CHARACTER_TAGS, ENABLED, POWER_AT_ORIGIN, RARITIES, ROLES, STAT_INITIALS,
    SUMMON_POOL
)
from legends.functions import tokensNeeded
from legends.gameobjects import allSkillEffectTags
from legends.ui.charcard import CharCard
from legends.ui.dialogs import (
    asksaveasfilename, ModalDialog, ModalMessage, showwarning
)

__all__ = [
    'AskRosterFilter',
    'AskSkillTimings',
    'OptimalSummons',
    'RosterFilter',
    'RosterInfoBar',
    'RosterTab'
]

class AskRosterFilter(ModalDialog):
    """A modal dialog used for adjusting `RosterFilter` objects.

    The constructor must be given a `RosterFilter` object. That object
    will be used to initialize the window, but will not be modified.

    Attributes:
        filt (RosterFilter): The `RosterFilter` object controlled and
            modified by the dialog window.
        result (RosterFilter or None): Inherited from
            `legends.ui.dialogs.ModalDialog`, which inherited it from
            `tk.simpledialog.Dialog`. Defaults to `None`. Is set by the
            `AskRosterFilter.apply` method to the value of the `filt`
            attribute.

    """
    def __init__(self, root, rosterFilter, parent=None):
        """The constructor sets the `filt` attribute, then calls the
        `legends.ui.dialogs.ModalDialog` constructor.

        Args:
            root (legends.ui.stlplanner.STLPlanner): The currently
                running `legends.ui.stlplanner.STLPlanner` instance.
                Passed to the `legends.ui.dialogs.ModalDialog`
                constructor.
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
            ).pack(side=tk.LEFT)
        widgets['roleCheckboxes'] = tk.Frame(master)
        for role in ROLES:
            tk.Checkbutton(
                widgets['roleCheckboxes'], text=role,
                variable=self.filt.roles[role]
            ).pack(side=tk.LEFT)

        # create the rank and level linked scales
        widgets['rankMinScale'], widgets['rankMaxScale'] = (
            self.makeLinkedScales(master, 'ranks', 9)
        )
        widgets['levelMinScale'], widgets['levelMaxScale'] = (
            self.makeLinkedScales(master, 'levels', 99)
        )

        # create the character tag checkboxes
        widgets['charTagCheckboxes'] = tk.Frame(
            master,
            highlightthickness=1,
            highlightbackground='black',
            highlightcolor='black'
        )
        rows = 4
        count = 0
        for charTag in CHARACTER_TAGS:
            tk.Checkbutton(
                widgets['charTagCheckboxes'], text=camelToSpace(charTag),
                variable=self.filt.charTags[charTag]
            ).grid(row=count % rows, column=int(count/rows), sticky=tk.W)
            count += 1
        count += 1
        tk.Button(
            widgets['charTagCheckboxes'],
            text='All',
            command = lambda: self.filt.setCharTags(True)
        ).grid(row=count % rows, column=int(count/rows), sticky=tk.EW)
        count += 1
        tk.Button(
            widgets['charTagCheckboxes'],
            text='None',
            command = lambda: self.filt.setCharTags(False)
        ).grid(row=count % rows, column=int(count/rows), sticky=tk.EW)

        # create the skill effect checkboxes
        widgets['effectTagCheckboxes'] = tk.Frame(
            master,
            highlightthickness=1,
            highlightbackground='black',
            highlightcolor='black'
        )
        rows = 13
        count = 0
        for effectTag in allSkillEffectTags():
            tk.Checkbutton(
                widgets['effectTagCheckboxes'], text=effectTag,
                variable=self.filt.effectTags[effectTag]
            ).grid(row=count % rows, column=int(count/rows), sticky=tk.W)
            count += 1
        tk.Button(
            widgets['effectTagCheckboxes'],
            text='All',
            command=lambda: self.filt.setEffectTags(True)
        ).grid(row=count % rows, column=int(count/rows), sticky=tk.EW)
        count += 1
        tk.Button(
            widgets['effectTagCheckboxes'],
            text='None',
            command=lambda: self.filt.setEffectTags(False)
        ).grid(row=count % rows, column=int(count/rows), sticky=tk.EW)
        count += 1
        tk.Button(
            widgets['effectTagCheckboxes'],
            text='Cooldowns...',
            command=self.setCooldowns
        ).grid(row=count % rows, column=int(count/rows), sticky=tk.EW)

        # grid the body content
        labels = [
            'Rarity:', 'Role:',
            'Min Rank:', 'Max Rank:', 'Min Level:', 'Max Level:',
            'Character Tags:', 'Skill Effects:'
        ]
        for row, label, widget in zip(range(8), labels, widgets.values()):
            tk.Label(master, text=label, font=(None, 13, 'bold')).grid(
                row=row, column=0, sticky=tk.NE
            )
            widget.grid(row=row, column=1)
            if row < 6:
                widget.grid_configure(sticky=tk.NW)
            else:
                widget.grid_configure(sticky=tk.NSEW)

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
                length=650, orient=tk.HORIZONTAL
            )
            scales[j].config(command=lambda val, k=k: varTuple[k].set(
                funcs[k](int(val), varTuple[k].get()))
            )
        return scales

    def setCooldowns(self):
        """Raises an `AskSkillTimings` dialog, then adjusts the `filt`
        attribute accordingly.

        """
        result = AskSkillTimings(self.root, self.filt).result
        if result is not None:
            self.filt.set(result)

    def buttonbox(self):
        """Add a 'Clear All' button to the button box.

        """
        ModalDialog.buttonbox(self)
        self.box.pack_forget()
        tk.Button(
            self.box, text="Clear All", width=10, command=self.clear
        ).pack(side=tk.LEFT, padx=5, pady=5)
        self.box.pack(expand=tk.YES, fill=tk.X)

    def clear(self):
        """Reset the `filt` attribute to default values.

        """
        self.filt.set(RosterFilter())

    def apply(self):
        """Set the `result` attribute.

        """
        self.result = self.filt

class AskSkillTimings(ModalDialog):
    """A modal dialog for selecting skill timings.

    The constructor must be given a `RosterFilter` object. That object's
    `skillTimings` attribute will be used to initialize the window, but
    will not be modified.

    Attributes:
        filt (RosterFilter): The `RosterFilter` object whose
            `skillTimings` attribute is  controlled and modified by the
            dialog window.
        result (RosterFilter or None): Inherited from
            `legends.ui.dialogs.ModalDialog`, which inherited it from
            `tk.simpledialog.Dialog`. Defaults to `None`. Is set by the
            `AskSkillTimings.apply` method to the value of the `filt`
            attribute.

    """

    def __init__(self, root, rosterFilter, parent=None):
        """The constructor sets the `filt` attribute, then calls the
        `legends.ui.dialogs.ModalDialog` constructor.

        Args:
            root (legends.ui.stlplanner.STLPlanner): The currently
                running `legends.ui.stlplanner.STLPlanner` instance.
                Passed to the `legends.ui.dialogs.ModalDialog`
                constructor.
            rosterFilter (RosterFilter): The instance's `filt` attribute
                is assigned a copy of this argument.

        """
        self.filt = RosterFilter(rosterFilter)
        ModalDialog.__init__(self, root, parent, 'Cooldowns')

    def body(self, master):
        """Create the body of the dialog.

        """
        tk.Label(
            master,
            text='Selected skill effects should match at least one of...',
            font=(None, 13, 'bold')
        ).pack()
        buttonLabels = {
            'basic': 'Basic attacks',
            'r1': 'Non-basic skills available in Round 1',
            'r2': 'Skills first available in Round 2',
            'r3': 'Skills first available in Round 3 or later',
        }
        for timing, description in buttonLabels.items():
            tk.Checkbutton(
                master,
                text=description,
                variable=self.filt.skillTimings[timing]
            ).pack(anchor=tk.W)

    def apply(self):
        """Set the `result` attribute.

        """
        self.result = self.filt

class OptimalSummons(ModalMessage):
    """A message dialog showing the summon pool rates.

    Attributes:
        values (dict): {`str`:`tk.StringVar`} A dictionary mapping pool
            names to a formatted string representation of the average
            number of tokens per 150 orbs received from the pool.
        labels (dict): {`str`:(`tk.Label`,`tk.Label`)} A dictionary
            mapping pool names to the pair of labels associated with
            that pool in the body of the message dialog.

    """
    def __init__(self, root, parent=None):
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
            self.labels[pool][0].grid(row=row, column=0, sticky=tk.W)
            self.labels[pool][1].grid(row=row, column=1, sticky=tk.E)
        tk.Checkbutton(
            master,
            text='exclude Common characters',
            variable=self.root.session.settings.excludeCommons,
            command=self.refresh
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
                pool, self.root.session.settings.excludeCommons.get()
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
        charTags (dict): {`str`:`tk.BooleanVar`} A dictionary mapping
            character tags to `tkinter` boolean variables indicating
            whether characters that match the tag should be included in
            the `legends.ui.rostertab.RosterTab`.
        effectTags (dict): {`str`:`tk.BooleanVar`} A dictionary mapping
            skill effect tags to `tkinter` boolean variables indicating
            whether characters with skills matching the tag should be
            included in the `legends.ui.rostertab.RosterTab`.
        skillTimings (dict): {`str`:`tk.BooleanVar`} A dictionary
            mapping timings to `tkinter` boolean variables indicating
            whether characters with skills matching the timing should be
            included in the `legends.ui.rostertab.RosterTab`. The timing
            strings are the possible values of the
            `legends.skill.Skill.timing` property.

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
        self.charTags = {
            charTag: tk.BooleanVar(None, True)
            for charTag in CHARACTER_TAGS
        }
        self.effectTags = {
            effectTag: tk.BooleanVar(None, True)
            for effectTag in allSkillEffectTags()
        }
        self.skillTimings = {
            'basic': tk.BooleanVar(None, True),
            'r1': tk.BooleanVar(None, True),
            'r2': tk.BooleanVar(None, True),
            'r3': tk.BooleanVar(None, True)
        }
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
        for charTag, var in self.charTags.items():
            var.set(filt.charTags[charTag].get())
        for effectTag, var in self.effectTags.items():
            var.set(filt.effectTags[effectTag].get())
        for timing, var in self.skillTimings.items():
            var.set(filt.skillTimings[timing].get())

    def setCharTags(self, val):
        """Sets all character tag variables to the given value.

        Args:
            val (bool): The value to assign to the tag variables.

        """
        for var in self.charTags.values():
            var.set(val)

    def setEffectTags(self, val):
        """Sets all skill effect variables to the given value.

        Args:
            val (bool): The value to assign to the tag variables.

        """
        for var in self.effectTags.values():
            var.set(val)

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
        D['charTags'] = {
            charTag: var.get() for charTag, var in self.charTags.items()
        }
        D['effectTags'] = {
            effectTag: var.get() for effectTag, var in self.effectTags.items()
        }
        D['skillTimings'] = {
            timing: var.get() for timing, var in self.skillTimings.items()
        }
        return D

    def __eq__(self, other):
        return self.dictify() == other.dictify()

    def __repr__(self):
        return 'RosterFilter({})'.format(self.dictify())

class RosterInfoBar(tk.Frame):
    """A frame for displaying aggregate data about the user's roster.

    Attributes:
        totalXP (tk.Label): A label displaying the total XP.
        totalPower (tk.Label): A label displaying the total power.
        charCount (tk.Label): A label displaying the number of
            characters in the roster.

    """
    def __init__(self, parent=None, **options):
        """The constructor passes its arguments to the `tk.Frame`
        constructor, then builds and packs the attribute labels.

        """
        tk.Frame.__init__(self, parent, **options)
        self.totalXP = tk.Label(
            self, borderwidth=2, relief=tk.GROOVE, padx=10
        )
        self.totalXP.pack(side=tk.LEFT)
        self.totalPower = tk.Label(
            self, borderwidth=2, relief=tk.GROOVE, padx=10
        )
        self.totalPower.pack(side=tk.LEFT)
        self.charCount = tk.Label(
            self, borderwidth=2, relief=tk.GROOVE, padx=10
        )
        self.charCount.pack(side=tk.LEFT)

    def makeStats(self, chars, roster):
        """Computes and redisplays roster statistics using the given
        collection of characters.

        Args:
            chars (iterable of legends.gameobjects.Character): The
                characters to use when computing statistics.
            roster (legends.roster.Roster): The roster to which the
                characters belong.

        """
        self.totalXP.config(text='Total XP: {:,}'.format(sum(
            char.xp for char in chars
        )))
        self.totalPower.config(text='Total power: {:,.0f}'.format(sum(
            POWER_AT_ORIGIN + char.totalStats(roster).power
            for char in chars
        )))
        self.charCount.config(text='Characters: {}/{}'.format(
            len(list(chars)), len(ENABLED)
        ))

class RosterTab(tk.Frame):
    """Displays the player's character collection.

    Attributes:
        scrollArea (legends.utils.scrollframe.ScrollFrame): The
            `legends.utils.scrollframe.ScrollFrame` used to hold the
            character cards.
        infoBar (RosterInfoBar): The info bar containing aggregate info
            about the currently displayed characters.
        sortFuncs (dict): {`str`:`func`} A dictionary mapping field
            names to functions that map `legends.gameobjects.Character`
            objects to a sortable value.
        sortField (tk.StringVar): The currently selected field name by
            which the characters are sorted.
        descending (tk.BooleanVar): `True` if characters should be
            sorted in descending order.

    """

    def __init__(self, session, **options):
        """The constructor creates an instance as a child of the given
        session.

        Args:
            session (legends.ui.session.Session): The session to assign
                as the instance's parent.

        """
        # build frame and initialize variables
        tk.Frame.__init__(self, session, **options)

        # build widgets
        self.scrollArea = ScrollFrame(self)
        self.scrollArea.canvas.config(height=0.7 * self.winfo_screenheight())
        self.infoBar = RosterInfoBar(self)

        # pack frame content
        self.actionBar().pack(fill=tk.X)
        self.scrollArea.pack(expand=tk.YES, fill=tk.BOTH)
        self.infoBar.pack()

        # fill scroll area with character cards
        self.fillCards()

    @property
    def root(self):
        """`legends.ui.stlplanner.STLPlanner`: The currently running
        `legends.ui.stlplanner.STLPlanner` instance.
        """
        return self.master.master

    @property
    def roster(self):
        """`legends.roster.Roster`: The roster associated with this
        roster tab.
        """
        return self.master.saveslot.roster

    @property
    def cards(self):
        """`dict`: {`str`:`legends.ui.charcard.CharCard`} A dictionary
        mapping a character's name ID attribute to its character card.
        """
        return {
            card.char.nameID : card
            for card in self.scrollArea.content.winfo_children()
            if isinstance(card, CharCard)
        }

    def fillCards(self):
        """Builds a card for each character in the player's collection
        and places it in the scroll area's content frame.

        """
        columns = 4
        for j in range(columns):
            self.scrollArea.content.columnconfigure(
                j, weight=1, uniform='roster'
            )
        count = 0
        chars = self.master.charList
        for char in chars:
            CharCard(char, self).grid(
                row=count // columns, column=count % columns, sticky=tk.NSEW
            )
            count += 1
        self.infoBar.makeStats(chars, self.roster)

    def actionBar(self):
        """Builds and returns an action bar that allows the user to
        interact with the `RosterTab`.

        """
        # define and initialize variables
        sslot = self.master.saveslot
        ros = self.roster
        self.sortFuncs = {
            'Name': lambda c: c.shortName,
            'Favorite': lambda c,s=sslot: c in s.favorites,
            'Level': lambda c: c.xp,
            'Rank': lambda c: c.rank,
            'Rarity': lambda c: c.rarityIndex,
            'Role': lambda c: c.role,
            'Tokens': lambda c,s=sslot: s.tokens[c.nameID],
            'Tokens needed': lambda c,s=sslot: (
                tokensNeeded(c.rarity, c.rank) - s.tokens[c.nameID]
            )
        }
        for statName in STAT_INITIALS:
            self.sortFuncs[statName] = lambda c,r=ros,n=statName: (
                c.totalStats(r).get(n)
            )
        self.sortFuncs['Power'] = lambda c,r=ros: (
            POWER_AT_ORIGIN + c.totalStats(r).power
        )
        self.sortFuncs.update({
            'Missing gear levels': lambda c,r=ros: (
                r.missingGearLevels(c.nameID)
            ),
            'Missing gear ranks': lambda c,r=ros: (
                r.missingGearRanks(c.nameID)
            ),
            'Missing skill levels': lambda c: c.missingSkillLevels
        })
        fields = list(self.sortFuncs.keys())
        self.sortField = tk.StringVar()
        self.descending = tk.BooleanVar()
        self.descending.set(True)

        # build bar and sorting Combobox
        bar = tk.Frame(self)
        sortMenu = ttk.Combobox(
            bar,
            textvariable=self.sortField,
            values=fields,
            state='readonly',
            width=max(len(field) for field in fields)
        )
        sortMenu.bind('<<ComboboxSelected>>', lambda event:self.sort())

        # pack and return bar
        tk.Label(bar, text='sort by:').pack(side=tk.LEFT)
        sortMenu.pack(side=tk.LEFT)
        tk.Checkbutton(
            bar, text='descending', variable=self.descending, command=self.sort
        ).pack(side=tk.LEFT)
        tk.Button(
            bar, text='filter', width=6, command=self.adjustFilter
        ).pack(side=tk.LEFT)
        tk.Button(
            bar, text='export', width=6, command=self.export
        ).pack(side=tk.LEFT)
        tk.Button(
            bar, text='summon pools', command=self.optimalSummons
        ).pack(side=tk.RIGHT)
        return bar

    def optimalSummons(self):
        """Raises an `OptimalSummons` message window showing the summon
        rates for the various summon pools. Warns the user if not all
        summonable characters have been unlocked.

        """
        e7m6 = [mission for mission in self.master.saveslot.missions if (
            mission.episode == 7
            and mission.orderIndex == 6
            and mission.difficulty == 'Normal'
        )]
        if e7m6[0].complete < 1:
            showwarning(
                self.root,
                'Missing Characters',
                'You have not yet completed Episode 7 Mission 6 on Normal '
                + 'Difficulty. Complete this mission to unlock all summonable '
                + 'characters. Until then, this tool may be inaccurate.'
            )
        OptimalSummons(self.root)

    def sort(self):
        """Sorts the dictionary of characters stored in the associated
        `legends.saveslot.SaveSlot` object according the currently
        selected sorting field. Then refreshes the character cards.

        """
        field = self.sortField.get()
        if field == '':
            return
        self.master.saveslot.sort(
            self.sortFuncs[field], self.descending.get()
        )
        self.refresh()

    def refresh(self):
        """Destroys and rebuilds all character cards.

        """
        for card in self.cards.values():
            card.destroy()
        self.fillCards()

    def adjustFilter(self):
        """Creates an `AskRosterFilter` window, giving the user an
        opportunity to adjust the filter settings. Then refreshes the
        character cards and info bar.

        """
        filt = AskRosterFilter(
            self.root, self.master.settings.rosterFilter
        ).result
        if filt is not None:
            self.master.settings.rosterFilter = filt
            self.refresh()

    def export(self):
        """Exports the data in the character cards to a csv file. Each
        row in the file corresponds to a card, and the data in that row
        is the data generated by the card's
        `legends.ui.charcard.CharCard.dictify` method.

        """
        initDir, initFile = os.path.split(
            self.master.settings.rosterExportFile
        )
        filename = asksaveasfilename(
            self.root,
            defaultextension='csv',
            initialdir=initDir,
            initialfile=initFile,
            title='Export Roster',
            filetypes=[('Text CSV', '*.csv')]
        )
        if not filename:
            return
        self.master.settings.rosterExportFile = filename
        cardDicts = [card.dictify() for card in self.cards.values()]
        fields = cardDicts[0].keys()
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = DictWriter(f, fields)
            writer.writeheader()
            writer.writerows(cardDicts)
