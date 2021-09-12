"""The RosterTab class and related objects.

"""

from re import findall
import tkinter as tk
from tkinter import ttk, X, BOTH, GROOVE, LEFT, NSEW, YES, W
from legends.utils.scrollframe import ScrollFrame
# pylint: disable-next=no-name-in-module
from legends.constants import GSLevel, GSBaseStat
from legends.constants import (
    RARITY_COLORS, STAT_ABBREVIATIONS, POWER_AT_ORIGIN
)
from legends.ui.dialogs import askRosterFilter, RosterFilter

__all__ = ['CharCard', 'RosterTab', 'RosterFilter', 'RosterTab']

def maxXP(rarity):
    """Returns the maximum XP of a character of the given rarity."""
    return GSLevel[rarity + '_99']['Experience']

def makeShortName(char):
    """Returns a short nickname for the given character.

    Args:
        char (Character): A Character object.

    Returns:
        str: The nickname for the character.

    """
    name = char.nameID
    if char.rarity == 'Common':
        L = findall('[A-Z][^A-Z]*', name)
        return L[1] + ' ' + L[2][:-2]
    betterNames = {
        'Nine': 'Seven',
        'Nerys': 'Kira',
        'Scott': 'Scotty',
        'Torchbearer': 'Torch',
        'BorgQueen': 'Borg Queen',
        'PicardDixon': 'Dixon'
    }
    return betterNames.get(name, name)

class RosterTab(tk.Frame):
    """Displays the player's character collection.

    Attributes:
        saveslot (SaveSlot): The SaveSlot object from which this roster
            is drawn.
        filter (RosterFilter): The RosterFilter object storing the
            current filter settings.
        scrollArea (ScrollFrame): The ScrollFrame used to hold the
            character cards.
        infoBar (RosterInfoBar): The info bar containing aggregate info
            about the currently displayed characters.
        sortFuncs (dict of str:func): A dictionary mapping field names
            to functions that map a CharCard object and a SaveSlot
            object to a sortable value.
        sortField (StringVar): The currently selected field name by
            which the characters are sorted.
        descending (BooleanVar): True if characters should be sorted in
            descending order.

    """

    def __init__(self, saveslot, parent=None, **options):
        # build frame and initialize variables
        tk.Frame.__init__(self, parent, **options)
        self.saveslot = saveslot
        self.filter = RosterFilter()

        # build widgets
        self.scrollArea = ScrollFrame(self)
        self.scrollArea.canvas.config(height=0.7 * self.winfo_screenheight())
        self.infoBar = RosterInfoBar(self)

        # pack frame content
        tk.Label(
            self,
            text='TIP: Click a character name to mark it as a favorite.',
            anchor=W
        ).pack(expand=YES, fill=X)
        self.actionBar().pack(fill=X)
        self.scrollArea.pack(expand=YES, fill=BOTH)
        self.infoBar.pack()

        # fill scroll area with character cards
        self.fillCards()

    @property
    def cards(self):
        """dict of str:CharCard: A dictionary mapping a character's
        `nameID` attribute to its character card.
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
            char (Character): The character to check.

        Returns:
            bool: True if the character passes.

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
        columns = 5
        for j in range(columns):
            self.scrollArea.content.columnconfigure(
                j, weight=1, uniform='roster'
            )
        count = 0
        chars = [
            char for char in self.saveslot.roster.chars.values()
            if self.checkFilter(char)
        ]
        for char in chars:
            CharCard(char, self.saveslot, self.scrollArea.content).grid(
                row=count // columns, column=count % columns, sticky=NSEW
            )
            count += 1
        self.infoBar.makeStats(chars, self.saveslot.roster)

    def actionBar(self):
        """Builds and returns an action bar that allows the user to
        interact with the RosterTab.

        """
        # define and initialize variables
        self.sortFuncs = {
            'Favorite': lambda c,s: c in s.favorites,
            'Level': lambda c,s: c.xp,
            'Rank': lambda c,s: c.rank,
            'Rarity': lambda c,s: c.rarityIndex,
            'Role': lambda c,s: c.role,
            'Tokens': lambda c,s: s.tokens[c.nameID],
            'Tokens needed': lambda c,s: c.tokensNeeded - s.tokens[c.nameID]
        }
        for statName in GSBaseStat:
            self.sortFuncs[statName] = lambda c,s,n=statName: (
                s.roster.charStats(c.nameID).get(n)
            )
        self.sortFuncs['Power'] = lambda c,s: (
            POWER_AT_ORIGIN + s.roster.charStats(c.nameID).power
        )
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
        sortMenu.bind('<<ComboboxSelected>>', self.sort)

        # pack and return bar
        tk.Label(bar, text='sort by:').pack(side=LEFT)
        sortMenu.pack(side=LEFT)
        tk.Checkbutton(
            bar, text='descending', variable=self.descending, command=self.sort
        ).pack(side=LEFT)
        tk.Button(
            bar, text='filter', command=self.adjustFilter
        ).pack(side=LEFT)
        return bar

    def sort(self, event=None): # pylint: disable=unused-argument
        """Sorts the dictionary of characters stored in the associated
        SaveSlot object according the currently selected sorting field.
        Then destroys and rebuilds all character cards.

        """
        field = self.sortField.get()
        if field == '':
            return
        func = self.sortFuncs[field]
        sortedChars = dict(sorted(
            self.saveslot.roster.chars.items(),
            key=lambda item:func(item[1], self.saveslot),
            reverse=self.descending.get()
        ))
        self.saveslot.roster.chars = sortedChars
        self.refresh()

    def refresh(self):
        """Destroys and rebuilds all character cards.

        """
        for card in self.cards.values():
            card.destroy()
        self.fillCards()

    def adjustFilter(self):
        """Creates a FilterDialog window, giving the user an opportunity
        to adjust the filter settings. Then refreshes the character
        cards and info bar.

        """
        filt = askRosterFilter(self.filter)
        if filt != self.filter:
            self.filter = filt
            self.refresh()

class CharCard(tk.Frame):
    """A small tile containing basic information about a character.

    Attributes:
        char (Character): The character from which the card is built.
        saveslot (SaveSlot): The save slot in which the character is
            located.
        nameLabel (Label): The label containing the character's name.
            Clicking it toggles the character's `favorite` attribute.

    """

    def __init__(self, char, saveslot, parent=None, **options):
        """Builds a character card for the given Character object.

        Args:
            char (Character): The character from which to build the
                card.
            saveslot (SaveSlot): The SaveSlot object containing the
                character.
            nameLabel (tk.Label): The label containing the character's
                name.

        """
        # build card and initialize variables
        tk.Frame.__init__(self, parent, **options)
        self.config(width=230, height=120)
        self.pack_propagate(0)
        self.char = char
        self.saveslot = saveslot

        # build name and stat plates
        bgColor = RARITY_COLORS[char.rarity]
        namePlate = self.namePlate(bgColor)
        statPlate = self.statPlate(bgColor)

        # set card color configuration
        self.config(bg=bgColor, highlightthickness=2)
        self.colorByFav()

        # pack card contents
        namePlate.pack(side=LEFT)
        statPlate.pack()

    @property
    def favorite(self):
        """bool:True if the player has selected this character as a
        favorite.
        """
        return self.char in self.saveslot.favorites

    def namePlate(self, bgColor):
        """Build and returns the character name plate with the given
        background color.

        Args:
            bgColor (str): The tkinter name of the given background
                color.

        Returns:
            tk.Frame: The constructed name plate.

        """
        plate = tk.Frame(self, bg=bgColor)

        # build name label
        self.nameLabel = tk.Label(
            plate, text=makeShortName(self.char), bg=bgColor,
            font=(None, 16, 'bold')
        )
        self.nameLabel.bind('<Button-1>', self.toggleFav)

        # pack name plate contents and return the plate
        tk.Label(
            plate,
            text='{}\nRank {}\nTokens: {}/{}'.format(
                self.char.role,
                self.char.rank,
                self.saveslot.tokens[self.char.nameID],
                self.char.tokensNeeded
            ),
            bg=bgColor,
            font=(None, 11, 'italic')
        ).pack()
        self.nameLabel.pack(expand=YES, fill=X)
        tk.Label(
            plate,
            text=('Level {}\nXP: {:,}\n({:.1%})'.format(
                self.char.level,
                self.char.xp,
                self.char.xp/maxXP(self.char.rarity)
            )),
            bg=bgColor,
            font=(None, 11, 'italic')
        ).pack()
        return plate

    def statPlate(self, bgColor):
        """Build and returns the character stat plate with the given
        background color.

        Args:
            bgColor (str): The tkinter name of the given background
                color.

        Returns:
            tk.Frame: The constructed stat plate.

        """
        plate = tk.Frame(self, bg=bgColor)
        statObj = self.saveslot.roster.charStats(self.char.nameID)

        # cycle through the 10 basic stats
        for index, statAbbr in enumerate(STAT_ABBREVIATIONS.values()):
            # build the stat label
            initial = statAbbr if len(statAbbr) == 2 else statAbbr[0]
            initial = initial.upper()

            # format the stat value
            statVal = getattr(statObj, statAbbr)
            if index == 2: # the speed stat
                statText = '{:.2f}'.format(statVal)
            elif index > 4: # the percentage stats
                statText = (
                    '{:.2f}'.format(100 * statVal).rstrip('0').rstrip('.')
                    + '%'
                )
            else:
                statText = '{:.0f}'.format(statVal)

            # grid the 10 basic stats
            row, col = index % 5, 2 * int(index/5)
            tk.Label(
                plate, text=initial + ':', bg=bgColor, font=(None, 11)
            ).grid(row=row, column=col, sticky=W)
            tk.Label(
                plate, text=statText, bg=bgColor, font=(None, 11)
            ).grid(row=row, column=col + 1, sticky=W)

        # grid the power stat and return the plate
        tk.Label(
            plate,
            text='POWER: {:.0f}'.format(POWER_AT_ORIGIN + statObj.power),
            bg=bgColor, font=(None, 11)
        ).grid(row=5, column=0, columnspan=4)
        return plate

    def toggleFav(self, event): # pylint: disable=unused-argument
        """Toggles the character's `favorite` attribute and recolors the
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

class RosterInfoBar(tk.Frame):
    """A frame for displaying aggregate data about the user's roster.

    Attributes:
        totalXP (tk.Label): A label displaying the total XP.

    """
    def __init__(self, parent=None, **options):
        tk.Frame.__init__(self, parent, **options)
        self.totalXP = tk.Label(self, borderwidth=2, relief=GROOVE, padx=10)
        self.totalXP.pack(side=LEFT)
        self.totalPower = tk.Label(self, borderwidth=2, relief=GROOVE, padx=10)
        self.totalPower.pack(side=LEFT)

    def makeStats(self, chars, roster):
        """Computes and redisplays roster statistics using the given
        collection of characters.

        Args:
            chars (iterable of Character): The characters to use when
                computing statistics.
            roster (Roster): The roster to which the characters belong.

        """
        self.totalXP.config(text='Total XP: {:,}'.format(sum(
            char.xp for char in chars
        )))
        self.totalPower.config(text='Total power: {:,.0f}'.format(sum(
            POWER_AT_ORIGIN + roster.charStats(char.nameID).power
            for char in chars
        )))
