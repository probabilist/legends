"""This module contains the Roster class and related objects.

"""

from types import MethodType
from warnings import warn
from legends.utils.objrelations import OneToOne
#pylint: disable-next=no-name-in-module
from legends.constants import GSAccessoryItems, GSCharacter
from legends.constants import DESCRIPTIONS, SUMMON_POOL
from legends.gameobjects import Gear, Particle, Character
from legends.stats import Stats

__all__ = ['readGear', 'readParts', 'Roster']

def readGear(save, slot):
    """The save slot contains a list of gear, each one having a unique
    ID number. This method makes a Gear object for each gear piece, and
    builds a dictionary mapping its ID number to the associated Gear
    object.

    Args:
        save (dict): A decrypted dictionary representation of the
            player's save file, as returned by the `decryptSaveFile`
            function.
        slot (int): The 0-based index of the save slot from which to
            read the data.

    Returns:
        dict of int:Gear: The dictionary mapping IDs to gear.

    """
    slotData = save['{} data'.format(slot)]
    gear = {}
    for indexStr, data in slotData['gears'].items():
        index = int(indexStr)
        gear[index] = Gear(data['gearid'], data['level'])
    return gear

def readParts(save, slot):
    """The save slot contains a list of particles, each one having a
    unique ID number. This method makes a Particle object for each
    particle, and builds a dictionary mapping its ID number to the
    associated Particle object.

    Args:
        save (dict): A decrypted dictionary representation of the
            player's save file, as returned by the `decryptSaveFile`
            function.
        slot (int): The 0-based index of the save slot from which to
            read the data.

    Returns:
        dict of int:Particle: The dictionary mapping IDs to
            particles.

    """
    parts = {}
    slotData = save['{} data'.format(slot)]
    for saveIndexStr, data in slotData['accessories'].items():
        saveIndex = int(saveIndexStr)
        name = DESCRIPTIONS[GSAccessoryItems[data['accessoryid']]['Name']]
        rarity = GSAccessoryItems[data['accessoryid']]['Rarity']
        part = Particle(name, rarity, data['level'], data['locked'])
        for statIndex, statName in enumerate(data['stats'].values()):
            part.setStatName(statIndex, statName)
        parts[saveIndex] = part
    return parts

class Roster():
    """A collection of related Characters, Gear, and Particles.

    Attributes:
        gear (list of Gear): A list of Gear objects.
        parts (list of Particle): A list of Particle objects.
        chars (dict of str:Character): A dictionary mapping nameIDs to
            Character objects.
        inGearSlot (OneToOne): A relation mapping Gear objects to
            GearSlot objects.
        inPartSlot (OneToOne): A relation mapping Particle objects to
            PartSlot objects.

    """
    def __init__(self, save=None, slot=0):
        self.gear = []
        self.parts = []
        self.chars = {}
        self.inGearSlot = OneToOne()
        def validate(slf, gear, gearSlot): # pylint: disable=unused-argument
            char = gearSlot.char
            index = gearSlot.index
            if gear.level > char.maxGearLevel or gear.slot != index:
                raise ValueError((gear, gearSlot))
            return True
        self.inGearSlot.validate = MethodType(validate, self.inGearSlot)
        self.inPartSlot = OneToOne()
        if save is not None:
            self.fromSaveData(save, slot)

    @property
    def containsGear(self):
        """OneToOne: The inverse of `inGearSlot`."""
        return self.inGearSlot.inverse

    @property
    def containsPart(self):
        """OneToOne: The inverse of `inPartSlot`."""
        return self.inPartSlot.inverse

    def clear(self):
        """Completely clears all items in the roster.

        """
        self.gear.clear()
        self.parts.clear()
        self.chars.clear()
        self.inGearSlot.clear()
        self.inPartSlot.clear()

    def fromSaveData(self, save, slot):
        """Completely empties the roster, then re-populates it with data
        from the given save data and slot.

        Args:
            save (dict): A decrypted dictionary representation of the
                player's save file, as returned by the `decryptSaveFile`
                function.
            slot (int): The 0-based index of the save slot from which to
                read the data.

        """
        self.clear()

        # fill gear and particles
        gearDict = readGear(save, slot)
        self.gear = list(gearDict.values())
        partDict = readParts(save, slot)
        self.parts = list(partDict.values())

        # cycle through characters in save data
        slotData = save['{} data'.format(slot)]
        for nameID, data in slotData['units'].items():
            char = Character(nameID, data['rank'], data['xp'])

            # add skills to character
            for skillID, level in data['skills'].items():
                if level > 0:
                    try:
                        char.skills[skillID].unlocked = True
                        char.skills[skillID].level = level
                    except KeyError:
                        warn(
                            repr(skillID)
                            + ' found in save file but not in game data'
                        )

            # add gear to character
            for slotIndex, itemSaveIndex in enumerate(data['gears'].values()):
                if itemSaveIndex > 0:
                    item = gearDict[itemSaveIndex]
                    slot = char.gearSlots[slotIndex]
                    self.inGearSlot[item] = slot

            # add particles to character
            for slotIndex, itemSaveIndex in (
                enumerate(data['accessories'].values())
            ):
                if itemSaveIndex > 0:
                    item = partDict[itemSaveIndex]
                    slot = char.partSlots[slotIndex]
                    self.inPartSlot[item] = slot

            # add character to roster
            self.chars[nameID] = char

    def fillChars(self, nameIDs, maxGear=True):
        """For each name ID in the given list of name IDs, a character
        with that name ID is added to the roster, if it is not already
        present. The character is added at maximum rank and level.

        If the `maxGear` attribute is True, maxed gear pieces will be
        created, added to the roster, and equipped to the characters.

        Args:
            nameIDs (iterable of str): The name IDs of the characters to
                add.
            maxGear (bool): True if characters are to be equipped with
                maxed gear.

        """
        gearNames = [
            'Starfleet PADD 2256',
            'Type II Phaser 2256',
            'Communicator 2256',
            'Tricorder 2256'
        ]
        for nameID in nameIDs:
            if nameID in self.chars:
                continue
            char = Character(nameID, 9)
            char.level = 99
            self.chars[nameID] = char
            if not maxGear:
                continue
            for slot, gearName in enumerate(gearNames):
                gear = Gear(
                    '{} {}'.format(gearName, char.role), char.maxGearLevel
                )
                self.gear.append(gear)
                self.inGearSlot[gear] = char.gearSlots[slot]

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

    def missingGearLevels(self, nameID):
        """Computes and returns the number of missing gear levels for
        the character with the given name ID.

        Args:
            nameID (str): The name ID of the character.

        Returns:
            int: The number of missing gear levels.

        """
        char = self.chars[nameID]
        gearLevels = 0
        for slot in char.gearSlots:
            try:
                gearLevels += self.containsGear[slot].level
            except (KeyError, AttributeError):
                pass
        return 4 * char.maxGearLevel - gearLevels

    def missingGearRanks(self, nameID):
        """Computes and returns the number of missing gear ranks for the
        character with the given name ID.

        Args:
            nameID (str): The name ID of the character.

        Returns:
            int: The number of missing gear ranks.

        """
        char = self.chars[nameID]
        gearRanks = 0
        for slot in char.gearSlots:
            try:
                gearRanks += self.containsGear[slot].rarityIndex + 1
            except (KeyError, AttributeError):
                pass
        return 4 * (char.rarityIndex + 1) - gearRanks

    def tokensPerOrb(self, pool, excludeCommons=True):
        """Computes and returns the expected number of tokens per orb
        the player will receive from using the given summon pool.

        Args:
            pool (str): One of the keys of SUMMON_POOL.
            excludeCommons (bool): If True, ignores tokens for common
                characters.

        Returns:
            float: The expected number of tokens per orb.

        """
        tokens = 0
        for nameID, prob in SUMMON_POOL[pool]['nameIDs'].items():
            if excludeCommons and GSCharacter[nameID]['Rarity'] == 'Common':
                continue
            if nameID in self.chars and self.chars[nameID].rank == 9:
                continue
            tokens += 10 * prob
        return tokens/SUMMON_POOL[pool]['cost']
