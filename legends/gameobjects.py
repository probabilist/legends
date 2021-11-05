"""The `legends.gameobjects.Character` class and related objects.

"""

from re import findall
from legends.utils.objrelations import Managed
#pylint: disable-next=no-name-in-module
from legends.constants import GSAccessoryItems, GSCharacter, GSGear
from legends.constants import (
    DESCRIPTIONS, ENABLED, PART_STAT_UNLOCKED, RARITIES, UPCOMING
)
from legends.constants import Inventory
from legends.functions import (
    gearToMaxCost, getBasicGearID, getCharStats, getGearStats, getPartStats,
    levelFromXP, xpFromLevel
)
from legends.stats import PartEffects, Stats
from legends.skill import BridgeSkill, Skill

__all__ = [
    'allSkillEffectTags',
    'Character',
    'Gear',
    'GearSlot',
    'Particle',
    'PartSlot'
]

def allSkillEffectTags():
    """Returns the list of tags on all skill effects produced by all
    skills of all levels of all playable characters, including both
    current and upcoming.

    Returns:
        list of str: The list of tags.

    """
    effTags = []
    for nameID in ENABLED + UPCOMING:
        effTags.extend(Character(nameID).skillEffectTags(True))
    return sorted(list(set(effTags)))

class Character():
    """A character in STL.

    Attributes:
        skills (dict): {`str`:`legends.skill.Skill`} A dictionary
            mapping skill IDs (found in `GSSkill`) to Skill objects.
        bridgeSkill (legends.skill.Skill): The character's bridge skill.
        gearSlots (list of GearSlot): The list of the character's gear
            slots.
        partSlots (list of PartSlot): The list of the character's
            particle slots.

    """

    def __init__(self, nameID, rank=1, xp=0):
        """The constructor stores the passed arguments in a private
        dictionary, whose values are accessed and managed by class
        properties.

        Args:
            nameID (str): The name ID of the character to create.
            rank (int): The rank to assign on creation.
            xp (int): The xp to assign on creation.

        """
        self._data = {
            'nameID': nameID,
            'rank': rank,
            'xp': xp
        }
        self._stats = Stats(self)
        self.updateStats()
        self.skills = {}
        for skillID in GSCharacter[self.nameID]['SkillIDs']:
            skill = Skill(skillID)
            if skill.startWith:
                skill.unlocked = True
            self.skills[skillID] = skill
        try:
            self.bridgeSkill = BridgeSkill(
                GSCharacter[self.nameID]['BridgeSkill']
            )
        except KeyError:
            self.bridgeSkill = None
        self.gearSlots = []
        for slot in range(4):
            self.gearSlots.append(GearSlot(self, slot))
        self.partSlots = []
        for slot in range(2):
            self.partSlots.append(PartSlot(self, slot))

    @property
    def nameID(self):
        """`str`: The in-data name of the character. Should match a key in
        `GSCharacter`.
        """
        return self._data['nameID']

    @property
    def name(self):
        """`str`: The in-game display name of the character."""
        return DESCRIPTIONS[GSCharacter[self.nameID]['Name']]

    @property
    def shortName(self):
        """`str`: A shortened version of the character's display name.
        """
        if self.rarity == 'Common':
            L = findall('[A-Z][^A-Z]*', self.nameID)
            return L[1] + ' ' + L[2][:-2]
        betterNames = {
            'Nine': 'Seven',
            'Nerys': 'Kira',
            'Scott': 'Scotty',
            'Torchbearer': 'Torch',
            'BorgQueen': 'Borg Queen',
            'PicardDixon': 'Dixon',
            'JadziaDax': 'Jadzia Dax',
            'PicardOld': 'Old Picard',
            'JudgeQ': 'Q',
            'NumberOne': 'Number One'
        }
        return betterNames.get(self.nameID, self.nameID)

    @property
    def rank(self):
        """`int`: The rank of the character. Modifying this property
        also calls the `Character.updateStats` method.
        """
        return self._data['rank']

    @rank.setter
    def rank(self, value):
        self._data['rank'] = value
        self.updateStats()

    @property
    def xp(self):
        """`int`: The xp of the character. Modifying this property also
        calls the `Character.updateStats` method.
        """
        return self._data['xp']

    @xp.setter
    def xp(self, value):
        self._data['xp'] = value
        self.updateStats()

    @property
    def level(self):
        """`int`: The level of the character. Setting this to a value
        different from its current value will change the `xp` property
        to the minimum xp required to attain the new level.
        """
        return levelFromXP(self.xp)

    @level.setter
    def level(self, value):
        if self.level != value:
            self._data['xp'] = xpFromLevel(value, self.rarity)
            self.updateStats()

    @property
    def stats(self):
        """`legends.stats.Stats`: The Stats object that stores the
        character's naked stats (i.e. the stats they would have without
        any gear or particles).
        """
        return self._stats

    @property
    def rarity(self):
        """`str`: The rarity of the character."""
        return GSCharacter[self.nameID]['Rarity']

    @property
    def rarityIndex(self):
        """`int`: The index of the rarity in `RARITIES`."""
        return RARITIES.index(self.rarity)

    @property
    def role(self):
        """`str`: The role of the character."""
        return GSCharacter[self.nameID]['Role']

    @property
    def tags(self):
        """`list`: [`str`] A list of the character's in-game tags.
        """
        return GSCharacter[self.nameID]['Tags']

    @property
    def bridgeStations(self):
        """`list` of `str`: The list of bridge stations this character
        is eligible to occupy.
        """
        return [
            station for station in GSCharacter[self.nameID]['BridgeStations']
            if station != 'None'
        ]

    @property
    def missingSkillLevels(self):
        """`int`: The number of missing skill levels. Assumes the
        maximum level for every skill is 2.
        """
        missingLevels = 0
        for skill in self.skills.values():
            missingLevels += 2
            if skill.unlocked:
                missingLevels -= skill.level
        return missingLevels

    def updateStats(self):
        """Updates the `stats` attribute.

        """
        self.stats.update(getCharStats(self.nameID, self.rank, self.level))

    def totalStats(self, roster):
        """Constructs and returns a `legends.stats.Stats` object
        containing the total stats (including gear and particles) of the
        character.

        Args:
            roster (legends.roster.Roster): The roster to which the
                character belongs.

        Returns:
            legends.stats.Stats: The character's total stats.

        """
        gears = (
            roster.containsGear[gearSlot] for gearSlot in self.gearSlots
            if gearSlot in roster.containsGear
        )
        gearStats = sum(
            (gear.stats for gear in gears if gear is not None),
            Stats()
        )
        parts = (
            roster.containsPart[partSlot] for partSlot in self.partSlots
            if partSlot in roster.containsPart
        )
        partStats = sum(
            (part.stats for part in parts if part is not None),
            Stats()
        )
        return self.stats + gearStats + partStats

    def partEffects(self, roster):
        """Computes and return the total effects of all particles
        equipped on the character.

        Args:
            roster (legends.roster.Roster): The roster to which the
                character belongs.

        Returns:
            legends.stats.PartEffects: The total effects of the
                character's particles.

        """
        effects = PartEffects()
        for slot in self.partSlots:
            try:
                part = roster.containsPart[slot]
                effects += part.effects
            except KeyError:
                continue
        return effects

    def skillEffectTags(self, showLocked=False, timings=None):
        """Returns the list of tags on all skill effects produced by all
        skills of this character.

        Args:
            showLocked (bool): If `True`, includes all effect types of
                all skill levels; otherwise, shows only effects of
                currently unlocked skill levels.
            timings (list of str): A list of strings from among 'basic',
                'r1', 'r2', and 'r3'. Skills whose `timing` property is
                not on the list will be ignored. If this argument is
                `None`, all skills will be allowed.

        Returns:
            list of str: The list of tags.

        """
        effTags = []
        for skillID, skill in self.skills.items():
            if timings is not None and skill.timing not in timings:
                continue
            for level in (1,2):
                if showLocked or (skill.level == level and skill.unlocked):
                    effTags.extend(Skill(skillID, level).effectTags)
        return list(set(effTags))

    def aiSkillOrder(self):
        """Returns an infinite generator that yields the skills used by
        the AI, in order of use.

        The order returned will not exactly match that used in an actual
        battle. The simple algorithm used by this method is to simply
        use the rightmost skill available at any given time.

        Yields:
            Skill: The skill used by the AI.

        """
        skillIDs = sorted(self.skills.keys(), reverse=True)
        activeCooldowns = {
            skillID: self.skills[skillID].startingCooldown + 1
            for skillID in skillIDs
        }
        while True:
            for skillID in skillIDs:
                activeCooldowns[skillID] -= 1
            for skillID in skillIDs:
                if activeCooldowns[skillID] <= 0:
                    skill = self.skills[skillID]
                    yield skill
                    activeCooldowns[skillID] = skill.cooldown + 1
                    break

    def itemsToMaxGear(self, roster):
        """Computes and returns the items needed to level all gear on
        this character to its maximum level. The roster to which the
        character belongs must be passed as an argument.

        Args:
            roster (legends.roster.Roster): The roster to which the
                character belongs.

        Returns:
            legends.constants.Inventory: The list of items needed.

        """
        cost = Inventory()
        for slot in self.gearSlots:
            try:
                cost += roster.containsGear[slot].itemsToMax(roster)
            except KeyError:
                cost += gearToMaxCost(
                    getBasicGearID(self.role, slot.index),
                    1,
                    5 + 5 * self.rarityIndex
                )
        return cost

    def __repr__(self):
        return (
            '<' + repr(self.name) + ', rank ' + repr(self.rank)
            + ', level ' + repr(self.level) + '>'
        )

class Gear(Managed):
    """A piece of gear in STL.

    Attributes:
        gearID (str): The in-code ID of the gear piece. Should be a key
            in `GSGear`.

    """

    def __init__(self, gearID, level=1):
        """The constructor stores the given level in a private attribute
        that is managed by a class property. At instance creation, the
        level may be set to anything, without regard to the usual
        restrictions on gear leveling.

        Args:
            gearID (str): The gearID of the piece to create.
            level (int): The level of the piece to create.

        """
        self.gearID = gearID
        self._level = level
        self._stats = Stats(self)
        self.updateStats()

    @property
    def name(self):
        """`str`: The in-game name of the piece of gear."""
        return DESCRIPTIONS[GSGear[self.gearID]['m_NameLocKey']]

    @property
    def level(self):
        """`int`: The level of the gear. Level is 1-based and includes
        rarity. For example, a Level 17 gear piece displays in game as
        "Epic, Level 2". This property must be modified with the
        `Gear.setLevel` method.
        """
        return self._level

    @property
    def displayLevel(self):
        """`int`: The level of the gear piece, as it is displayed in
        game. The displayed level does not account for rarity, and is
        therefore an integer between 1 and 5, inclusive.
        """
        return self.level - 5 * self.rarityIndex

    @property
    def rarityIndex(self):
        """`int`: The index of the rarity in `RARITIES`."""
        return int((self.level - 1)/5)

    @property
    def rarity(self):
        """`str`: The rarity of the gear piece."""
        return RARITIES[self.rarityIndex]

    @property
    def role(self):
        """`str`: The role the gear piece is meant for. Is `None` if it
        is not restricted to a particular role.
        """
        gearRole = GSGear[self.gearID]['m_Role']
        return None if gearRole == 'None' else gearRole

    @property
    def stats(self):
        """`legends.stats.Stats`: The Stats object that stores the
        gear's total stats.
        """
        return self._stats

    @property
    def slot(self):
        """`int`: The 0-based index of the slot into which the gear must
        be placed. In game, slots are displayed clockwise, starting from
        the top left.
        """
        return GSGear[self.gearID]['m_Slot']

    def setLevel(self, roster, value):
        """Sets the `level` property to the given value, then calls the
        `Gear.updateStats` method. A gear piece may only be leveled up
        if it is equipped on a character, and in that case, the gear
        piece may not be leveled beyond the rarity of that character.
        This method must be passed a `legends.roster.Roster` object to
        which the calling instance belongs. The roster will enforce the
        leveling requirements.

        Args:
            roster (legends.roster.Roster): A roster to which the
                calling belongs.
            value (int): The value to assign to the `level` property.

        """
        maxLevel = roster.maxGearLevel(self)
        if value > maxLevel:
            raise ValueError(
                '{} cannot go past Level {}'.format(self, maxLevel)
            )
        self._level = value
        self.updateStats()

    def updateStats(self):
        """Updates the `stats` attribute.

        """
        self.stats.update(getGearStats(self.gearID, self.level))

    def itemsToMax(self, roster):
        """Computes and returns the items needed to level this gear to
        its maximum level. The gear must be equipped on a character, and
        the roster to which the gear and character belong must be passed
        as an argument.

        Args:
            roster (legends.roster.Roster): The roster to which the gear
                piece belongs.

        Returns:
            legends.constants.Inventory: The list of items needed.

        """
        maxLevel = roster.maxGearLevel(self)
        return gearToMaxCost(self.gearID, self.level, maxLevel)

    def __repr__(self):
        return '<' + repr(self.gearID) + ', level ' + repr(self.level) + '>'

class GearSlot(Managed): # pylint: disable=too-few-public-methods
    """A slot into which a piece of gear can be placed.

    Must be implemented as a class, rather than a tuple, so that it can
    be a `legends.utils.objrelations.Managed` instance, eligible to be
    part of an object-based relation.

    Attributes:
        char (Character): The character that owns the slot.
        index (int): The 0-based index of the slot.

    """

    def __init__(self, char, index):
        self.char = char
        self.index = index

    def __repr__(self):
        return '<' + self.char.nameID + ', gear slot ' + str(self.index) + '>'

class Particle(Managed):
    """A particle in STL.

    Attributes:
        locked (bool): True if the particle is locked.
        passive (legends.skill.Skill): The passive skill granted to the
            character by this particle.
        effects (legends.stats.PartEffects): The particle effect stats
            granted by this particle.

    """

    def __init__(self, typ, rarity, level, locked=False):
        """The constructor passes the given type, rarity, and level to a
        private dictionary that is managed by class properties.

        Args:
            typ (str): The type of particle to create.
            rarity (str): The rarity of the created particle.
            level (int): The level of the created particle.

        """
        self._data = {
            'typ': typ,
            'rarity': rarity,
            'level': level
        }
        self._key = ''.join(self.typ.split(' ')) + '_' + self.rarity
        self.passive = Skill(self.data['CombatEffectId'], unlocked=True)
        self.effects = PartEffects()
        frac = self.passive.effects[0].statSourceFrac
        if self.typ == 'Amplify Force':
            self.effects.attUp = frac
        elif self.typ == 'Nexus Field':
            self.effects.shield = frac
        elif self.typ == 'Undo Damage':
            self.effects.regen = frac
        self.locked = locked
        self._statNames = [None] * 4
        self._stats = Stats(self)

    @property
    def data(self):
        """`dict`: The particle data from `GSAccessoryItems`."""
        return GSAccessoryItems[self._key]

    @property
    def typ(self):
        """`str`: The type of the particle. This is what the data refers
        to as the particle's "display name". Should be one of
        'Accelerated Coagulation', 'Amplify Force', 'Nexus Field',
        'Temporal Flux', or 'Undo Damage'.
        """
        return self._data['typ']

    @property
    def rarity(self):
        """`str`: The particle's rarity."""
        return self._data['rarity']

    @property
    def level(self):
        """`str`: The particle's level. Modifying this property also
        calls the `Particle.updateStats` method.
        """
        return self._data['level']

    @level.setter
    def level(self, value):
        self._data['level'] = value
        self.updateStats()

    @property
    def stats(self):
        """`legends.stats.Stats`: The Stats object that stores the
        particle's total stats.
        """
        return self._stats

    @property
    def numStats(self):
        """`int`: The number of unlocked stats on the particle."""
        return PART_STAT_UNLOCKED[self.rarity][self.level - 1]

    @property
    def statNames(self):
        """`tuple of str`: The names, as they appear in `GSBaseStat`, of
        the stats that are on the particle. It is always a 4-tuple,
        though some values may be `None`.
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
            statName for statName in self.statNames[:self.numStats]
            if statName is not None
        ]
        self.stats.update(getPartStats(self.rarity, self.level, statList))

    def __repr__(self):
        return (
            '<' + repr(self.typ) + ', ' + repr(self.rarity)
            + ', level ' + repr(self.level) + '>'
        )

class PartSlot(Managed): # pylint: disable=too-few-public-methods
    """A slot into which a particle can be placed.

    Must be implemented as a class, rather than a tuple, so that it can
    be a `legends.utils.objrelations.Managed` instance, eligible to be
    part of an object-based relation.

    Attributes:
        char (Character): The character that owns the slot.
        index (int): The 0-based index of the slot.

    """

    def __init__(self, char, index):
        self.char = char
        self.index = index

    def __repr__(self):
        return '<' + self.char.nameID + ', part slot ' + str(self.index) + '>'
