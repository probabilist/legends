"""The `legends.ui.chartab.CharTab` class and related objects.

"""

import tkinter as tk
from tkinter import ttk
from legends.utils.functions import camelToSpace
from legends.utils.scrollframe import ScrollFrame
from legends.constants import ITEMS, RARITY_COLORS
from legends.functions import tokensNeeded, xpFromLevel
from legends.gameobjects import Gear
from legends.skill import Skill

__all__ = ['displaySkill', 'CharTab', 'GearCard']

def displaySkill(master, skill, row, column):
    """Constructs information about the given skill and grids it onto
    the given frame. The information is gridded as a block with its top
    right corner placed at the given row and column.

    Args:
        master (tk.Frame): The frame onto which to grid the skill
            information.
        skill (legends.skill.Skill): The skill from which to draw
            information.
        row (int): The row of the top-left corner of the block of
            information.
        column (int): The column of the top-left corner of the block of
            information.

    """
    bgColor = 'cyan' if skill.unlocked else 'cornsilk2'
    fgColor = None if skill.unlocked else 'gray'

    # add skill name and level
    frame = tk.Frame(master, bg=bgColor)
    frame.grid(row=row, column=column, columnspan=2, sticky=tk.NSEW)
    tk.Label(
        frame,
        text='{} - Level {}'.format(skill.name, skill.level),
        bg=bgColor,
        fg=fgColor,
        font=(None, 16, 'bold')
    ).pack(pady=(5,10))

    # place headers
    headers = [
        'Description', 'Effects', 'Caster Effect', 'Target', 'Cooldown',
        'Effect Tags'
    ]
    for offset, header in enumerate(headers):
        frame = tk.Frame(master, bg=bgColor)
        frame.grid(row=row + 1 + offset, column=column, sticky=tk.NSEW)
        label = tk.Label(
            frame,
            text=header + ':',
            bg=bgColor,
            fg=fgColor,
            font=(None, 13, 'bold')
        )
        label.pack(anchor=tk.NE, padx=(5,0))
    label.pack_configure(pady=(0,5))

    # set up content variables
    cEff = skill.casterEffect
    target = '{} {} {} ({})'.format(
        'All' if skill.isAOE else skill.numTargets,
        skill.data['targetState'],
        skill.data['targetType'],
        'multiple' if skill.isAOE else (
            'multiple random' if skill.isMultiRandom else 'single'
        )
    )
    info = [
        skill.description,
        ', '.join([effect.description for effect in skill.effects]),
        'None' if cEff is None else cEff.description,
        target,
        '{} ({} start)'.format(skill.cooldown, skill.startingCooldown),
        ', '.join(skill.effectTags)
    ]

    # place content
    for offset, text in enumerate(info):
        frame = tk.Frame(master, bg=bgColor)
        frame.grid(row=row + 1 + offset, column=column + 1, sticky=tk.NSEW)
        label = tk.Label(
            frame,
            text=text,
            bg=bgColor,
            fg=fgColor,
            wraplength=400,
            justify=tk.LEFT
        )
        label.pack(anchor=tk.NW, padx=(0,5))
    label.pack_configure(pady=(0,10))

class CharTab(tk.Frame):
    """Displays details about a character.

    Attributes:
        char (legends.gameobjects.Character): The character associated
            with the character tab.
        scrollArea (legends.utils.scrollframe.ScrollFrame): The
            `legends.utils.scrollframe.ScrollFrame` used to hold the
            character information.
        skillFrame (tk.Frame): The frame that holds information about
            the character's skills.

    """
    def __init__(self, char, session, **options):
        """The constructor creates an instance as a child of the given
        session.

        Args:
            session (legends.ui.session.Session): The session to assign
                as the instance's parent.

        """
        tk.Frame.__init__(self, session, **options)
        self.char = char
        self.bgColor = None
        self.scrollArea = ScrollFrame(self)
        self.scrollArea.canvas.config(height=0.7 * self.winfo_screenheight())
        self.scrollArea.content.config(bg=self.bgColor)
        self.actionBar().pack()
        self.scrollArea.pack(expand=tk.YES, fill=tk.BOTH)

        # add character information
        tk.Label(
            self.scrollArea.content,
            text=self.char.name,
            bg=self.bgColor,
            font=(None, 36, 'bold italic')
        ).pack()
        tk.Label(
            self.scrollArea.content,
            text='({})'.format(', '.join(self.char.tags)),
            bg=self.bgColor,
            font=(None, 16, 'bold')
        ).pack()
        tk.Label(
            self.scrollArea.content,
            text='{}, Rank {}, Level {}, {}'.format(
                camelToSpace(self.char.rarity),
                self.char.rank,
                self.char.level,
                self.char.role
            ),
            bg=self.bgColor,
            font=(None, 20, 'bold italic')
        ).pack()
        tk.Label(
            self.scrollArea.content,
            text=(
                'Tokens: {} ({} needed for next rank), '
                + 'XP: {:,} ({:.1%} toward maximum level)'
            ).format(
                self.master.saveslot.tokens[self.char.nameID],
                tokensNeeded(self.char.rarity, self.char.rank),
                self.char.xp,
                self.char.xp/xpFromLevel(99)
            ),
            bg=self.bgColor,
            font=(None, 13, 'bold')
        ).pack()

        # add gear
        tk.Label(
            self.scrollArea.content,
            text='GEAR:',
            bg=self.bgColor,
            font=(None, 21, 'bold italic')
        ).pack(anchor=tk.W)
        gearFrame = tk.Frame(
            self.scrollArea.content, bg='ivory', highlightthickness=1,
            highlightbackground='black', highlightcolor='black'
        )
        gearFrame.pack(anchor=tk.W)
        self.makeGearCardFrame(gearFrame).pack()
        self.makeGearUpgradeFrame(gearFrame, 'ivory').pack()

        # add skills
        tk.Label(
            self.scrollArea.content,
            text='SKILLS:',
            bg=self.bgColor,
            font=(None, 21, 'bold italic')
        ).pack(anchor=tk.W)
        self.skillFrame().pack()

    @property
    def roster(self):
        """`legends.roster.Roster`: The roster associated with the
        active session.
        """
        return self.master.saveslot.roster

    def actionBar(self):
        """Builds and returns an action bar that allows the user to
        interact with the `CharTab`.

        """
        bar = tk.Frame(self)
        tk.Button(
            bar,
            text='back to roster',
            command=self.master.rosterTab
        ).pack(side=tk.LEFT)
        nextChar = self.master.nextChar(self.char)
        prevChar = self.master.prevChar(self.char)
        tk.Button(
            bar,
            text='prev',
            command=lambda: self.master.charTab(prevChar),
            state=tk.DISABLED if prevChar is None else tk.NORMAL
        ).pack(side=tk.LEFT)
        tk.Button(
            bar,
            text='next',
            command=lambda: self.master.charTab(nextChar),
            state=tk.DISABLED if nextChar is None else tk.NORMAL
        ).pack(side=tk.LEFT)
        return bar

    def skillFrame(self):
        """Builds and packs the frame that will hold the skill
        information, and stores it in the `skillFrame` attribute.
        Horizontal and vertical separators are placed, leaving room for
        a 7 x 2 grid for each skill-level combination. Then the skill
        descriptions are individually placed in each open grid area.

        """
        skillFrame = tk.Frame(self.scrollArea.content)
        skillGrid = tk.Frame(skillFrame)
        skillGrid.pack()
        skillGrid.columnconfigure(1, weight=1, uniform='headers')
        skillGrid.columnconfigure(4, weight=1, uniform='headers')
        skillGrid.columnconfigure(2, weight=1, uniform='descriptions')
        skillGrid.columnconfigure(5, weight=1, uniform='descriptions')
        numSkills = len(self.char.skills)
        for index in range(numSkills + 1):
            ttk.Separator(skillGrid, orient='horizontal').grid(
                row=8 * index, column=0,
                columnspan=7, sticky=tk.EW
            )
        for index in range(3):
            ttk.Separator(skillGrid, orient='vertical').grid(
                row=0, column=3 * index,
                rowspan=8 * numSkills + 1, sticky=tk.NS
            )
        for index, item in enumerate(self.char.skills.items()):
            skillID, skill = item
            for level in (1,2):
                tempSkill = Skill(
                    skillID,
                    level,
                    skill.level == level and skill.unlocked
                )
                displaySkill(
                    skillGrid,
                    tempSkill,
                    8 * index + 1,
                    3 * (level - 1) + 1
                )
        return skillFrame

    def makeGearCardFrame(self, master):
        """Builds and returns a frame that displays a gear card for each
        of the character's gear pieces.

        Args:
            master (tk.Frame): The frame that holds all gear-related
                information.

        Returns:
            tk.Frame: The constructed gear-card frame, a child of the
                given master frame.

        """
        # get test card dimensions
        testCard = GearCard('test', master)
        testCard.update_idletasks()
        height = testCard.winfo_reqheight()
        width = testCard.winfo_reqwidth()
        testCard.destroy()

        # setup card frame
        cardFrame = tk.Frame(master)
        cardFrame.grid_rowconfigure(0, minsize=height)
        cardFrame.grid_rowconfigure(1, minsize=height)
        cardFrame.grid_columnconfigure(0, minsize=width)
        cardFrame.grid_columnconfigure(1, minsize=width)

        # add gear cards
        for index in range(4):
            try:
                gear = self.roster.containsGear[self.char.gearSlots[index]]
            except KeyError:
                gear = None
            card = GearCard(gear, cardFrame)
            card.grid(
                row=int(index/2),
                column=index if index < 2 else 3 - index,
                sticky=tk.NSEW
            )
        return cardFrame

    def makeGearUpgradeFrame(self, master, bgColor):
        """Builds and returns a frame with information about items
        needed to upgrade the character's gear.

        Args:
            master (tk.Frame): The frame that holds all gear-related
                information.
            bgColor (str): The background color of the master frame.

        Returns:
            tk.Frame: The constructed gear-upgrade frame, a child of the
                given master frame.

        """
        upgradeFrame = tk.Frame(master, bg=bgColor)
        upgradeFrame.grid_columnconfigure(2, minsize=20)
        items = self.char.itemsToMaxGear(self.roster)
        tk.Label(
            upgradeFrame,
            text='Items Needed to Max All Gear',
            bg=bgColor,
            font=(None, 13, 'bold italic')
        ).grid(row=0, column=0, columnspan=5)
        headers = {
            'Gear Leveling Materials': 'Leveling Mats',
            'Gear Ranking Materials': 'Ranking Mats'
        }
        col = 0
        for cat, header in headers.items():
            tk.Label(
                upgradeFrame, text=header, bg=bgColor, font=(None, 13, 'bold')
            ).grid(row=1, column=col, columnspan=2, sticky=tk.W)
            row = 2
            for item, qty in items.itemsByCat(cat):
                tk.Label(
                    upgradeFrame, text=item.name + ':', bg=bgColor
                ).grid(row=row, column=col, sticky=tk.W)
                tk.Label(
                    upgradeFrame, text='{:,}'.format(qty), bg=bgColor
                ).grid(row=row, column=col + 1, sticky=tk.E)
                row += 1
            col += 3
        tk.Label(
            upgradeFrame,
            text='Latinum: {:,}'.format(items[ITEMS['Latinum']]),
            bg=bgColor
        ).grid(row=5, column=0, columnspan=4)
        return upgradeFrame

class GearCard(tk.Frame):
    """A small tile containing basic information about a gear piece.

    """

    def __init__(self, gear, *args, **kargs):
        """The constructor builds the card from the given gear piece and
        passes its remaining arguments to the `tk.Frame` constructor.

        Args:
            gear (legends.gameobjects.Gear): The gear piece from which
                to build the card. If `None`, a tile displaying "None"
                is created. Can also be "test", in which case a card is
                created, all of whose display texts are as large as
                possible. The test card can be used to test sizes when
                displaying cards.

        """
        # set up gear and card configuration
        tk.Frame.__init__(self, *args, **kargs)
        bgColor = (
            RARITY_COLORS[gear.rarity] if isinstance(gear, Gear)
            else 'cornsilk2'
        )
        if gear == 'test':
            gear = Gear('Starfleet PADD 2256 Engineering', 25)
            gear.stats.hlth = 999.99
            gear.stats.att = 999.99
            gear.stats.tech = 999.99
            gear.stats.dfn = 99.99
        self.config(
            bg=bgColor, highlightthickness=2, highlightbackground='black',
            highlightcolor='black'
        )

        # make 'NONE' card
        if gear is None:
            tk.Label(
                self, text='NONE', bg=bgColor, font=(None, 16, 'bold italic'),
                state=tk.DISABLED
            ).pack(expand=tk.YES)
            return

        # make and pack name and info
        tk.Label(
            self,
            text=f'{gear.name}',
            bg=bgColor,
            font=(None, 16, 'bold italic')
        ).pack()
        tk.Label(
            self,
            text='{}, Level {}, {}'.format(
                camelToSpace(gear.rarity), gear.displayLevel, gear.role
            ),
            bg=bgColor,
            font=(None, 12, 'italic')
        ).pack()

        # build stat frame
        statFrame = tk.Frame(self, bg=bgColor)
        for column in range(4):
            statFrame.columnconfigure(
                column, weight=1, uniform=(
                    'names' if column % 2 == 0 else 'values'
                )
            )
        stats = ['Health', 'Attack', 'Defense', 'Tech']
        for index in range(4):
            tk.Label(
                statFrame,
                text=f'{stats[index]}:',
                bg=bgColor
            ).grid(row=int(index/2), column=2 * (index % 2), sticky=tk.W)
            tk.Label(
                statFrame,
                text=f'{gear.stats.get(stats[index]):.2f}',
                bg=bgColor
            ).grid(row=int(index/2), column=2 * (index % 2) + 1, sticky=tk.E)
        statFrame.pack(expand=tk.YES, fill=tk.X)
