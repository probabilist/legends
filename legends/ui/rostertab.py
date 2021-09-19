"""The `legends.ui.rostertab.RosterTab` class and related objects.

"""

import tkinter as tk
from tkinter import ttk, X, BOTH, GROOVE, LEFT, RIGHT, NSEW, YES, W
from tkinter.filedialog import asksaveasfilename
from getpass import getuser
from csv import DictWriter
from legends.utils.scrollframe import ScrollFrame
# pylint: disable-next=no-name-in-module
from legends.constants import GSLevel
from legends.constants import (
    RARITY_COLORS, STAT_INITIALS, POWER_AT_ORIGIN, ENABLED, SUMMON_POOL
)
from legends.ui.dialogs import askRosterFilter, RosterFilter

__all__ = ['maxXP', 'RosterTab', 'CharCard', 'RosterInfoBar']

def maxXP(rarity):
    """Returns the maximum XP of a character of the given rarity.

    Args:
        rarity (str): The rarity of the character.

    """
    return GSLevel[rarity + '_99']['Experience']

class RosterTab(tk.Frame):
    """Displays the player's character collection.

    Attributes:
        filter (legends.ui.dialogs.RosterFilter): The
            `legends.ui.dialogs.RosterFilter` object storing the current
            filter settings.
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
            session (legends.ui.stlplanner.Session): The session to
                assign as the instance's parent.

        """
        # build frame and initialize variables
        tk.Frame.__init__(self, session, **options)
        self.filter = RosterFilter()

        # build widgets
        self.scrollArea = ScrollFrame(self)
        self.scrollArea.canvas.config(height=0.7 * self.winfo_screenheight())
        self.infoBar = RosterInfoBar(self)

        # pack frame content
        self.actionBar().pack(expand=YES, fill=X)
        self.scrollArea.pack(expand=YES, fill=BOTH)
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
        """`dict`: {`str`:`CharCard`} A dictionary mapping a character's
        name ID attribute to its character card.
        """
        return {
            card.char.nameID : card
            for card in self.scrollArea.content.winfo_children()
            if isinstance(card, CharCard)
        }

    def checkFilter(self, char):
        """Checks if the given character passes the current filter
        options.

        Args:
            char (legends.gameobjects.Character): The character to
                check.

        Returns:
            bool: `True` if the character passes.

        """
        filt = self.filter.dictify()
        return(
            filt['rarities'][char.rarity]
            and filt['roles'][char.role]
            and filt['ranks'][0] <= char.rank <= filt['ranks'][1]
            and filt['levels'][0] <= char.level <= filt['levels'][1]
        )

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
        chars = [
            char for char in self.roster.chars.values()
            if self.checkFilter(char)
        ]
        for char in chars:
            CharCard(char, self).grid(
                row=count // columns, column=count % columns, sticky=NSEW
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
                c.tokensNeeded - s.tokens[c.nameID]
            )
        }
        for statName in STAT_INITIALS:
            self.sortFuncs[statName] = lambda c,r=ros,n=statName: (
                r.charStats(c.nameID).get(n)
            )
        self.sortFuncs['Power'] = lambda c,r=ros: (
            POWER_AT_ORIGIN + r.charStats(c.nameID).power
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
        tk.Label(bar, text='sort by:').pack(side=LEFT)
        sortMenu.pack(side=LEFT)
        tk.Checkbutton(
            bar, text='descending', variable=self.descending, command=self.sort
        ).pack(side=LEFT)
        tk.Button(
            bar, text='filter', width=6, command=self.adjustFilter
        ).pack(side=LEFT)
        tk.Button(
            bar, text='export', width=6, command=self.export
        ).pack(side=LEFT)
        tk.Button(
            bar, text='summon pools', command=self.optimalSummons
        ).pack(side=RIGHT)
        return bar

    def optimalSummons(self):
        for pool in SUMMON_POOL:
            print(pool, 150 * self.roster.tokensPerOrb(pool))

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
        """Creates an `legends.ui.dialogs.AskRosterFilter` window,
        giving the user an opportunity to adjust the filter settings.
        Then refreshes the character cards and info bar.

        """
        filt = askRosterFilter(self.root, self.filter)
        if filt is not None:
            self.filter = filt
            self.refresh()

    def export(self):
        """Exports the data in the character cards to a csv file. Each
        row in the file corresponds to a card, and the data in that row
        is the data generated by the card's `CharCard.dictify` method.

        """
        filename = asksaveasfilename(
            defaultextension='csv',
            initialdir='/Users/' + getuser() + '/Documents/',
            initialfile='roster.csv',
            title='Export Roster',
            filetypes=[('Text CSV', '*.csv')]
        )
        if not filename:
            return
        cardDicts = [card.dictify() for card in self.cards.values()]
        fields = cardDicts[0].keys()
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = DictWriter(f, fields)
            writer.writeheader()
            writer.writerows(cardDicts)

class CharCard(tk.Frame):
    """A small tile containing basic information about a character.

    Attributes:
        char (legends.gameobjects.Character): The character from which
            the card is built.
        nameLabel (tk.Label): The label containing the character's name.
            Clicking it toggles the character's `favorite` property.

    """

    def __init__(self, char, rostertab, **options):
        """The constructor builds the card and associates it with the
        given `legends.ui.rostertab.RosterTab`.

        Args:
            char (legends.gameobjects.Character): The character from
                which to build the card.
            rostertab (legends.ui.rostertab.RosterTab): The
                `legends.ui.rostertab.RosterTab` object to which this
                card belongs.

        """
        # build card and initialize variables
        tk.Frame.__init__(self, rostertab.scrollArea.content, **options)
        self.char = char

        # build name and stat plates
        bgColor = RARITY_COLORS[char.rarity]
        namePlate = self.namePlate(bgColor)
        statPlate = self.statPlate(bgColor)

        # set card color configuration
        self.config(bg=bgColor, highlightthickness=2)
        self.colorByFav()

        # pack card contents
        namePlate.pack(side=LEFT)
        statPlate.pack(side=RIGHT)

    @property
    def favorite(self):
        """`bool`: True if the player has selected this character as a
        favorite.
        """
        return self.char in self.saveslot.favorites

    @property
    def saveslot(self):
        """`legends.saveslot.SaveSlot`: The save slot in which the
        character is located.
        """
        content = self.master
        canvas = content.master
        scrollArea = canvas.master
        rostertab = scrollArea.master
        session = rostertab.master
        return session.saveslot

    def namePlate(self, bgColor):
        """Builds and returns the character name plate with the given
        background color.

        Args:
            bgColor (str): The `tkinter` name of the given background
                color.

        Returns:
            tk.Frame: The constructed name plate.

        """
        plate = tk.Frame(self, bg=bgColor, height=118, width=105)
        plate.pack_propagate(0)
        data = self.dictify()

        # build name label
        self.nameLabel = tk.Label(
            plate, text=data['name'], bg=bgColor,
            font=(None, 16, 'bold')
        )
        self.nameLabel.bind('<Button-1>', self.toggleFav)

        # pack name plate contents and return the plate
        tk.Label(
            plate,
            text='{}\nRank {}\nTokens: {}/{}'.format(
                data['role'],
                data['rank'],
                data['tokens'],
                data['tokensNeeded']
            ),
            bg=bgColor,
            font=(None, 11, 'italic')
        ).pack()
        self.nameLabel.pack(expand=YES, fill=X)
        tk.Label(
            plate,
            text=('Level {}\nXP: {:,}\n({:.1%})'.format(
                data['level'],
                data['xp'],
                data['xp']/maxXP(data['rarity'])
            )),
            bg=bgColor,
            font=(None, 11, 'italic')
        ).pack()
        return plate

    def statPlate(self, bgColor):
        """Build and returns the character stat plate with the given
        background color.

        Args:
            bgColor (str): The `tkinter` name of the given background
                color.

        Returns:
            tk.Frame: The constructed stat plate.

        """
        plate = tk.Frame(self, bg=bgColor)
        data = self.dictify()
        # statObj = self.saveslot.roster.charStats(self.char.nameID)
        font = (None, 9)

        # cycle through the 10 basic stats
        for index, statName in enumerate(STAT_INITIALS):
            # format the stat value
            statVal = data[statName]
            if index == 2: # the speed stat
                statText = '{:.2f}'.format(statVal)
            elif index > 4: # the percentage stats
                statText = (
                    '{:.1f}'.format(100 * statVal).rstrip('0').rstrip('.')
                    + '%'
                )
            else:
                statText = '{:.0f}'.format(statVal)

            # grid the 10 basic stats
            row, col = index % 5, 2 * int(index/5)
            tk.Label(
                plate, text=STAT_INITIALS[statName] + ':',
                bg=bgColor, font=font
            ).grid(row=row, column=col, sticky=W)
            tk.Label(
                plate, text=statText, bg=bgColor, font=font,
                width=4 + col, anchor=W
            ).grid(row=row, column=col + 1, sticky=W)

        # grid the extra stats
        moreStats = {k + ':': data[k] for k in ['MGL', 'MGR', 'MSL']}
        for row, item in enumerate(moreStats.items()):
            text, statVal = item
            tk.Label(
                plate, text=text, bg=bgColor, font=font
            ).grid(row=row, column=5, sticky=W)
            tk.Label(
                plate, text=str(statVal), bg=bgColor, font=font,
                width=5, anchor=W
            ).grid(row=row, column=6, sticky=W)

        # grid the power stat and return the plate
        tk.Label(
            plate,
            text='POWER: {:.0f}'.format(data['power']),
            bg=bgColor, font=(None, 11) + ('bold',)
        ).grid(row=5, column=0, columnspan=4)
        return plate

    def toggleFav(self, event): # pylint: disable=unused-argument
        """Toggles the character's `favorite` property and recolors the
        card.
        """
        if self.char in self.saveslot.favorites:
            self.saveslot.favorites.remove(self.char)
        else:
            self.saveslot.favorites.append(self.char)
        self.colorByFav()

    def colorByFav(self):
        """Colors the border and name of the character red if marked as
        a favorite; black otherwise.

        """
        color = 'red2' if self.favorite else 'black'
        self.config(
            highlightbackground=color, highlightcolor=color
        )
        self.nameLabel.config(fg=color)

    def dictify(self):
        """Creates and returns a dictionary representation of the data
        depicted on this card.

        Returns:
            dict: The dictionary of data from the card.

        """
        D = {
            'name': self.char.shortName,
            'rarity': self.char.rarity,
            'role': self.char.role,
            'rank': self.char.rank,
            'tokens': self.saveslot.tokens[self.char.nameID],
            'tokensNeeded': self.char.tokensNeeded,
            'level': self.char.level,
            'xp': self.char.xp
        }
        statObj = self.saveslot.roster.charStats(self.char.nameID)
        for statName in STAT_INITIALS:
            D[statName] = statObj.get(statName)
        D['power'] = POWER_AT_ORIGIN + statObj.power
        D.update({
            'MGL': self.saveslot.roster.missingGearLevels(self.char.nameID),
            'MGR': self.saveslot.roster.missingGearRanks(self.char.nameID),
            'MSL': self.char.missingSkillLevels
        })
        return D

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
        self.totalXP = tk.Label(self, borderwidth=2, relief=GROOVE, padx=10)
        self.totalXP.pack(side=LEFT)
        self.totalPower = tk.Label(self, borderwidth=2, relief=GROOVE, padx=10)
        self.totalPower.pack(side=LEFT)
        self.charCount = tk.Label(self, borderwidth=2, relief=GROOVE, padx=10)
        self.charCount.pack(side=LEFT)

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
            POWER_AT_ORIGIN + roster.charStats(char.nameID).power
            for char in chars
        )))
        self.charCount.config(text='Characters: {}/{}'.format(
            len(list(chars)), len(ENABLED)
        ))
