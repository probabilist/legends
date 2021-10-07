"""The `legends.ui.chartab.CharTab` class and related objects.

"""

import tkinter as tk
from tkinter import ttk
from legends.utils.functions import camelToSpace
from legends.utils.scrollframe import ScrollFrame
from legends.functions import xpFromLevel
from legends.skill import Skill

__all__ = ['CharTab']

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
        bgColor = None
        self.scrollArea = ScrollFrame(self)
        self.scrollArea.canvas.config(height=0.7 * self.winfo_screenheight())
        self.scrollArea.content.config(bg=bgColor)
        self.actionBar().pack(fill=tk.X)
        self.scrollArea.pack(expand=tk.YES, fill=tk.BOTH)
        tk.Label(
            self.scrollArea.content,
            text=self.char.name,
            bg=bgColor,
            font=(None, 36, 'bold italic')
        ).pack()
        tk.Label(
            self.scrollArea.content,
            text='({})'.format(', '.join(self.char.tags)),
            bg=bgColor,
            font=(None, 16, 'bold')
        ).pack()
        tk.Label(
            self.scrollArea.content,
            text='{}, Rank {}, Level {}'.format(
                camelToSpace(self.char.rarity),
                self.char.rank,
                self.char.level
            ),
            bg=bgColor,
            font=(None, 20, 'bold italic')
        ).pack()
        tk.Label(
            self.scrollArea.content,
            text=(
                'Tokens: {} ({} needed for next rank), '
                + 'XP: {:,} ({:.1%} toward maximum level)'
            ).format(
                self.master.saveslot.tokens[self.char.nameID],
                self.char.tokensNeeded,
                self.char.xp,
                self.char.xp/xpFromLevel(99)
            ),
            bg=bgColor,
            font=(None, 13, 'bold')
        ).pack()
        tk.Label(
            self.scrollArea.content,
            text='SKILLS:',
            bg=bgColor,
            font=(None, 21, 'bold italic')
        ).pack(anchor=tk.W)
        self.buildSkillFrame()

    def buildSkillFrame(self):
        """Builds and packs the frame that will hold the skill
        information, and stores it in the `skillFrame` attribute.
        Horizontal and vertical separators are placed, leaving room for
        a 7 x 2 grid for each skill-level combination. Then the skill
        descriptions are individually placed in each open grid area.

        """
        self.skillFrame = tk.Frame(self.scrollArea.content)
        numSkills = len(self.char.skills)
        for index in range(numSkills + 1):
            ttk.Separator(self.skillFrame, orient='horizontal').grid(
                row=8 * index, column=0,
                columnspan=7, sticky=tk.EW
            )
        for index in range(3):
            ttk.Separator(self.skillFrame, orient='vertical').grid(
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
                self.displaySkill(
                    tempSkill,
                    8 * index + 1,
                    3 * (level - 1) + 1
                )
        self.skillFrame.pack()

    def displaySkill(self, skill, row, column):
        """Constructs information about the given skill and grids it
        onto the skill frame. The information is gridded as a block with
        its top right corner placed at the given row and column.

        Args:
            skill (legends.skill.Skill): The skill from which to draw
                information.
            row (int): The row of the top-left corner of the block of
                information.
            column (int): The column of the top-left corner of the block
                of information.

        """
        bgColor = 'cyan' if skill.unlocked else 'cornsilk2'
        fgColor = None if skill.unlocked else 'gray'
        frame = tk.Frame(self.skillFrame, bg=bgColor)
        frame.grid(row=row, column=column, columnspan=2, sticky=tk.NSEW)
        tk.Label(
            frame,
            text='{} - Level {}'.format(skill.name, skill.level),
            bg=bgColor,
            fg=fgColor,
            font=(None, 16, 'bold')
        ).pack(pady=(5,10))
        headers = [
            'Description', 'Effects', 'Caster Effect', 'Target', 'Cooldown',
            'Effect Tags'
        ]
        for offset, header in enumerate(headers):
            frame = tk.Frame(self.skillFrame, bg=bgColor)
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
        for offset, text in enumerate(info):
            frame = tk.Frame(self.skillFrame, bg=bgColor)
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
        return bar
