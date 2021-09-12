"""This module contains the character class and related objects.

"""

from types import MethodType
from legends.utils.objrelations import Managed, OneToOne
#pylint: disable-next=no-name-in-module
from legends.constants import (
    GSSkill, GSCharacter, GSLevel, GSGear, GSRank, GSBaseStat, GSGearLevel
)
from legends.constants import DESCRIPTIONS, RARITIES, PART_STAT_VALUES
from legends.stats import Stats

__all__ = [
    'levelFromXP', 'xpFromLevel', 'tokensNeeded', 'getCharStats',
    'getGearStats', 'getPartStats', 'Gear', 'Particle', 'GearSlot', 'PartSlot',
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

def xpFromLevel(level, rarity='Common'):
    """Calculates the minimum XP of the character from its level.

    Args:
        level (int): The level of the character.
        rarity (str): The rarity of the character.

    Returns:
        int: The minimum possible XP the character could have.

    """
    return GSLevel[rarity + '_' + str(level)]['Experience']

def tokensNeeded(rarity, rank):
    """Returns the number of tokens needed by a character of the given
    rarity and rank to move up to the next rank.
    """
    if rank == 9:
        return 0
    # pylint: disable-next=undefined-variable
    return GSRank['{}_{}'.format(rarity, rank)]['RequiredTokenCount']

def getCharStats(nameID, rank, level):
    """Calculates a character's naked stats from its nameID, rank, and
    level.

    Args:
        nameID (str): The name ID of the character, as it appears in
            `GSCharacter`.
        rank (int): The rank of the character.
        level (int): The level of the character.

    Returns:
        dict: A dictionary mapping stat names, as they appear in
            `GSBaseStat`, to stat values.

    """
    rarity = GSCharacter[nameID]['Rarity']
    stats = {}
    for statName, data in GSBaseStat.items():
        m = data['MinValue'] #pylint: disable=invalid-name
        M = data['MaxValue'] #pylint: disable=invalid-name
        t = GSCharacter[nameID][statName] #pylint: disable=invalid-name
        baseStat = m + t * (M - m)
        try:
            levelMod = GSLevel[rarity + '_' + str(level)][
                    statName + 'Modifier'
                ]
            rankMod = GSRank[rarity + '_' + str(rank)][
                    statName + 'Modifier'
                ]
        except KeyError:
            levelMod = 1
            rankMod = 1
        statVal = baseStat * levelMod * rankMod
        stats[statName] = statVal
    return stats

def getGearStats(gearID, level):
    """Calculates a gear's stats from its gear ID and level.

    Args:
        gearID (str): The gear ID as it appears in `GSGear`.
        level (int): The level of the gear. Level is 1-based and
            includes rarity. For example, a Level 17 gear piece displays
            in game as "Epic, Level 2".

    Returns:
        dict: A dictionary mapping stat names, as they appear in
            `GSBaseStat`, to stat values.

    """
    stats = {statName: 0 for statName in GSBaseStat}
    gearLevelID = '[{}, {}]'.format(gearID, level)
    numStats = GSGearLevel[gearLevelID]['m_StatBrancheCount']
    for i in range(numStats):
        data = GSGear[gearID]['m_Stats'][i]
        statName = data['m_Type']
        statBase = data['m_BaseValue']
        statIncr = data['m_IncreaseValue']
        statVal = statBase + (level - 10 * i) * statIncr
        stats[statName] += statVal
    return stats

def getPartStats(rarity, level, statList):
    """Calculates a particle's stats from its rarity, level, and list of
    stat names.

    Args:
        rarity (str): The particle's rarity.
        level (int): The particle's level.
        statList (list of str): The stat names on the particle.

    Returns:
        dict: A dictionary mapping stat names, as they appear in
            `GSBaseStat`, to stat values.

    """
    stats = {statName: 0 for statName in GSBaseStat}
    for statName in statList:
        stats[statName] = (
            PART_STAT_VALUES[statName][rarity][level - 1]
        )
    return stats

class Gear(Managed):
    """A piece of gear in STL.

    Attributes:
        gearID (str): The in-code ID of the gear piece. Should be a key
            in `GSGear`.
        level (int): The level of the gear. Level is 1-based and
            includes rarity. For example, a Level 17 gear piece displays
            in game as "Epic, Level 2".
        stats (Stats): The Stats object that stores the gear's total
            stats.

    """

    def __init__(self, gearID, level):
        self.gearID = gearID
        self._level = level
        self.stats = Stats()
        self.updateStats()

    @property
    def level(self):
        """int: The level of the gear. Level is 1-based and includes
        rarity. For example, a Level 17 gear piece displays in game as
        "Epic, Level 2". Modifying this property also calls the
        `updateStats` method.
        """
        return self._level

    @level.setter
    def level(self, value):
        self._level = value
        self.updateStats()

    @property
    def slot(self):
        """The slot index into which the gear must be placed."""
        return GSGear[self.gearID]['m_Slot']

    def updateStats(self):
        """Updates the `stats` attribute.

        """
        self.stats.update(getGearStats(self.gearID, self.level))

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

    """

    def __init__(self, name, rarity, level, locked=False):
        self.name = name
        self.rarity = rarity
        self._level = level
        self.locked = locked
        self._statNames = [None] * 4
        self.stats = Stats()

    @property
    def level(self):
        """str: The particle's level. Modifying this property also calls
        the `updateStats` method.
        """
        return self._level

    @level.setter
    def level(self, value):
        self._level = value
        self.updateStats()

    @property
    def statNames(self):
        """tuple of str: The names, as they appear in GSBaseStat, of the
        stats that are on the particle.
        """
        return tuple(self._statNames)

    def setStatName(self, index, statName):
        """Changes the `statNames` property by setting the value at the
        given index to the given stat name.

        Args:
            index (int): The 0-based index of the value in the
                `statNames` property to change.
            statName (str): The stat name to assign to the given index.

        """
        self._statNames[index] = statName
        self.updateStats()

    def updateStats(self):
        """Updates the `stats` attribute.

        """
        statList = [
            statName for statName in self.statNames if statName is not None
        ]
        self.stats.update(getPartStats(self.rarity, self.level, statList))

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
        stats (Stats): The Stats object that stores the character's
            naked stats (i.e. the stats they would have without any gear
            or particles).
        skills (dict): A dictionary mapping skill IDs (found in
            `GSSkill`) to Skill objects.

    """
    def __init__(self, nameID, rank=1, xp=0):
        self._data = {
            'nameID': nameID,
            'rank': rank,
            'xp': xp
        }
        self.stats = Stats()
        self.updateStats()
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
    def nameID(self):
        """str: The in-data name of the character. Should match a key in
        `GSCharacter`.
        """
        return self._data['nameID']

    @property
    def name(self):
        """The in-game display name of the character."""
        return DESCRIPTIONS[GSCharacter[self.nameID]['Name']]

    @property
    def rank(self):
        """int: The rank of the character. Modifying this property also
        calls the `updateStats` method.
        """
        return self._data['rank']

    @rank.setter
    def rank(self, value):
        self._data['rank'] = value
        self.updateStats()

    @property
    def xp(self):
        """int: The xp of the character. Modifying this property also
        calls the `updateStats` method.
        """
        return self._data['xp']

    @xp.setter
    def xp(self, value):
        self._data['xp'] = value
        self.updateStats()

    @property
    def level(self):
        """int: The level of the character. Setting this to a value
        different from its current value will change the `xp` property
        to minimum xp required to attain the new level.
        """
        return levelFromXP(self.xp)

    @level.setter
    def level(self, value):
        if self.level != value:
            self.xp = xpFromLevel(value, self.rarity)

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

    def updateStats(self):
        """Updates the `stats` attribute.

        """
        self.stats.update(getCharStats(self.nameID, self.rank, self.level))

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

    def charStats(self, nameID):
        """Constructs and returns a Stats object containing the total
        stats (including gear and particles) of the character with the
        given name ID.

        Args:
            nameID (str): The name ID of the character whose stats to
                build.

        Returns:
            Stats: The constructed Stats object.

        """
        char = self.chars[nameID]
        nakedStats = char.stats
        gears = (
            self.containsGear[gearSlot] for gearSlot in char.gearSlots
            if gearSlot in self.containsGear
        )
        gearStats = sum(
            (gear.stats for gear in gears if gear is not None),
            Stats()
        )
        parts = (
            self.containsPart[partSlot] for partSlot in char.partSlots
            if partSlot in self.containsPart
        )
        partStats = sum(
            (part.stats for part in parts if part is not None),
            Stats()
        )
        return nakedStats + gearStats + partStats