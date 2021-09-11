"""This module contains the character class and related objects.

"""

from types import MethodType
from legends.utils.objrelations import Managed, OneToOne
#pylint: disable-next=no-name-in-module
from legends.constants import GSSkill, GSCharacter, GSLevel, GSGear, GSRank
from legends.constants import DESCRIPTIONS, RARITIES

__all__ = [
    'levelFromXP', 'tokensNeeded', 'Gear', 'Particle', 'GearSlot', 'PartSlot',
    'Character', 'Skill', 'Roster'
]

def levelFromXP(xp, rarity='Common'):
    """Calculates the level of the character from its XP.

    Args:
        xp (int): The XP of the character.
        rarity (str): The rarity of the character.

    Returns:
        int: The level of the character.

    """
    level = None
    for j in reversed(range(100)):
        xpNeeded = GSLevel[rarity + '_' + str(j)]['Experience']
        if xp >= xpNeeded:
            level = j
            break
    else:
        raise ValueError(repr(xp) + ' could not be converted from XP to level')
    return level

def tokensNeeded(rarity, rank):
    """Returns the number of tokens needed by a character of the given
    rarity and rank to move up to the next rank.
    """
    if rank == 9:
        return 0
    # pylint: disable-next=undefined-variable
    return GSRank['{}_{}'.format(rarity, rank)]['RequiredTokenCount']

class Gear(Managed):
    """A piece of gear in STL.

    Attributes:
        gearID (str): The in-code ID of the gear piece. Should be a key
            in `GSGear`.
        level (int): The level of the gear. Level is 1-based and
            includes rarity. For example, a Level 17 gear piece displays
            in game as "Epic, Level 2".

    """

    def __init__(self, gearID, level):
        self.gearID = gearID
        self.level = level

    @property
    def slot(self):
        """The slot index into which the gear must be placed."""
        return GSGear[self.gearID]['m_Slot']

    def __repr__(self):
        return '<' + repr(self.gearID) + ', level ' + repr(self.level) + '>'

class Particle(Managed):
    """A particle in STL.

    Attributes:
        typ (str): The type of the particle. This is what the data
            refers to as the particle's "display name".
        rarity (str): The particle's rarity.
        level (str): The particle's level.
        locked (bool): True if the particle is locked.
        statName (list of str): The names, as they appear in GSBaseStat,
            of the stats that are on the particle.

    """

    def __init__(self, name, rarity, level, locked=False):
        self.name = name
        self.rarity = rarity
        self.level = level
        self.locked = locked
        self.statNames = []

    def __repr__(self):
        return (
            '<' + repr(self.name) + ', ' + repr(self.rarity)
            + ', level ' + repr(self.level) + '>'
        )

class GearSlot(Managed): # pylint: disable=too-few-public-methods
    """A slot into which a piece of gear can be placed.

    Must be implemented as a class, rather than a tuple, so that it can
    be a Managed instance, eligible to be part of an object relation.

    Attributes:
        char (Character): The character that owns the slot.
        index (int): The 0-based index of the slot.

    """

    def __init__(self, char, index):
        self.char = char
        self.index = index

    def __repr__(self):
        return '<' + self.char.nameID + ', gear slot ' + str(self.index) + '>'

class PartSlot(Managed): # pylint: disable=too-few-public-methods
    """A slot into which a particle can be placed.

    Must be implemented as a class, rather than a tuple, so that it can
    be a Managed instance, eligible to be part of an object relation.

    Attributes:
        char (Character): The character that owns the slot.
        index (int): The 0-based index of the slot.

    """

    def __init__(self, char, index):
        self.char = char
        self.index = index

    def __repr__(self):
        return '<' + self.char.nameID + ', part slot ' + str(self.index) + '>'

class Character():
    """A character in STL.

    Attributes:
        nameID (str): The in-data name of the character. Should match a
            key in `GSCharacter`.
        rank (int): The rank of the character.
        tokens (int): The number of tokens obtained toward ranking the
            character.
        xp (int): The xp the character has.
        skills (dict): A dictionary mapping skill IDs (found in
            `GSSkill`) to Skill objects.

    """
    def __init__(self, nameID, rank=1, xp=0):
        self.nameID = nameID
        self.rank = rank
        self.xp = xp
        self.skills = {
            skillID: Skill(skillID)
            for skillID in GSCharacter[self.nameID]['SkillIDs']
        }
        self.gearSlots = []
        for slot in range(4):
            self.gearSlots.append(GearSlot(self, slot))
        self.partSlots = []
        for slot in range(2):
            self.partSlots.append(PartSlot(self, slot))

    @property
    def name(self):
        """The in-game display name of the character."""
        return DESCRIPTIONS[GSCharacter[self.nameID]['Name']]

    @property
    def level(self):
        """int: The level of the character."""
        return levelFromXP(self.xp)

    @property
    def rarity(self):
        """str: The rarity of the character."""
        return GSCharacter[self.nameID]['Rarity']

    @property
    def rarityIndex(self):
        """int: The index of the rarity in RARITIES."""
        return RARITIES.index(self.rarity)

    @property
    def role(self):
        """str:The role of the character."""
        return GSCharacter[self.nameID]['Role']

    @property
    def tokensNeeded(self):
        """int: The total number of tokens needed for the character to
        reach the next rank.
        """
        return tokensNeeded(self.rarity, self.rank)

    def __repr__(self):
        return (
            '<' + repr(self.name) + ', rank ' + repr(self.rank)
            + ', level ' + repr(self.level) + '>'
        )

class Skill():
    """A skill in STL.

    Attributes:
        skillID (str): The skill's ID, as it appears in `GSSkill`.
        level (int): The level of the skill.
        unlocked (bool): True if the character has unlocked this skill.
        data (dict): The skill data from `GSSkill`.

    """
    def __init__(self, skillID, level=1, unlocked=False):
        self.skillID = skillID
        self.level = level
        self.unlocked = unlocked
        key = (
            'GSSkillKey(id = "' + self.skillID
            + '", level = "' + str(self.level) + '")'
        )
        self.data = GSSkill[key]

    @property
    def name(self):
        """The in-game display name of the skill."""
        return DESCRIPTIONS[self.data['name']]

    def __repr__(self):
        return (
            '<Skill: ' + self.name + ', Level ' + str(self.level) + ', '
            + ('unlocked' if self.unlocked else 'locked') + '>'
        )

class Roster():
    """A collection of related Characters, Gear, and Particles.

    Attributes:
        gear (dict of int:Gear): A dictionary mapping id numbers to Gear
            objects.
        parts (dict of int:Particle): A dictionary mapping id numbers to
            Particle objects.
        chars (dict of str:Character): A dictionary mapping nameIDs to
            Character objects.
        inGearSlot (OneToOne): A relation mapping Gear objects to
            GearSlot objects.
        inPartSlot (OneToOne): A relation mapping Particle objects to
            PartSlot objects.

    """
    def __init__(self):
        self.gear = {}
        self.parts = {}
        self.chars = {}
        self.inGearSlot = OneToOne()
        def validate(slf, gear, gearSlot): # pylint: disable=unused-argument
            char = gearSlot.char
            index = gearSlot.index
            maxGearLevel = 5 + 5 * char.rarityIndex
            if gear.level > maxGearLevel or gear.slot != index:
                raise ValueError((gear, gearSlot))
            return True
        self.inGearSlot.validate = MethodType(validate, self.inGearSlot)
        self.inPartSlot = OneToOne()

    @property
    def containsGear(self):
        """OneToOne: The inverse of `inGearSlot`."""
        return self.inGearSlot.inverse

    @property
    def containsPart(self):
        """OneToOne: The inverse of `inPartSlot`."""
        return self.inPartSlot.inverse
