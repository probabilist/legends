"""The module contains the `CharCard` class.

"""

import tkinter as tk
from legends.constants import POWER_AT_ORIGIN, RARITY_COLORS, STAT_INITIALS
from legends.functions import xpFromLevel

__all__ = ['CharCard']

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
        statPlate.pack(side=tk.RIGHT)
        namePlate.pack(side=tk.LEFT, expand=tk.YES, fill=tk.BOTH)

    @property
    def favorite(self):
        """`bool`: True if the player has selected this character as a
        favorite.
        """
        return self.char in self.saveslot.favorites

    @property
    def session(self):
        """`legends.ui.session.Session`: The currently running session.
        """
        content = self.master
        canvas = content.master
        scrollArea = canvas.master
        rostertab = scrollArea.master
        return rostertab.master

    @property
    def saveslot(self):
        """`legends.saveslot.SaveSlot`: The save slot in which the
        character is located.
        """
        return self.session.saveslot

    def namePlate(self, bgColor):
        """Builds and returns the character name plate with the given
        background color.

        Args:
            bgColor (str): The `tkinter` name of the given background
                color.

        Returns:
            tk.Frame: The constructed name plate.

        """
        plate = tk.Frame(self, bg=bgColor)
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
        self.nameLabel.pack(expand=tk.YES, fill=tk.X)
        tk.Label(
            plate,
            text=('Level {}\nXP: {:,}\n({:.1%})'.format(
                data['level'],
                data['xp'],
                data['xp']/xpFromLevel(99)
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
            ).grid(row=row, column=col, sticky=tk.W)
            tk.Label(
                plate, text=statText, bg=bgColor, font=font,
                width=4 + col, anchor=tk.W
            ).grid(row=row, column=col + 1, sticky=tk.W)

        # grid the extra stats
        moreStats = {k + ':': data[k] for k in ['MGL', 'MGR', 'MSL']}
        for row, item in enumerate(moreStats.items()):
            text, statVal = item
            tk.Label(
                plate, text=text, bg=bgColor, font=font
            ).grid(row=row, column=4, sticky=tk.W)
            tk.Label(
                plate, text=str(statVal), bg=bgColor, font=font,
                width=5, anchor=tk.W
            ).grid(row=row, column=5, sticky=tk.W)

        # grid the power stat and return the plate
        tk.Label(
            plate,
            text='POWER: {:.0f}'.format(data['power']),
            bg=bgColor, font=(None, 11, 'bold')
        ).grid(row=5, column=0, columnspan=4)

        openLabel = tk.Label(
            plate,
            text='OPEN',
            font=font + ('italic',),
            relief=tk.GROOVE
        )
        openLabel.grid(row=6, column=0, columnspan=6, sticky=tk.NSEW)
        openLabel.bind(
            '<Button-1>',
            lambda event: self.session.charTab(self.char)
        )

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
