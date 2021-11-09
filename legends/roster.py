"""The `legends.roster.Roster` class and related objects.

"""

from collections.abc import MutableMapping, MutableSequence
from warnings import warn
from legends.utils.eventhandler import Event, EventHandler
from legends.utils.objrelations import OneToOne
#pylint: disable-next=no-name-in-module
from legends.constants import GSAccessoryItems, GSCharacter
from legends.constants import DESCRIPTIONS, SUMMON_POOL
from legends.stats import checkForStats
from legends.gameobjects import Character, Gear, Particle

__all__ = [
    'readGear',
    'readParts',
    'OneToOneChangeEvent',
    'WatchedOneToOne',
    'InGearSlot',
    'WatchedCollection',
    'WatchedList',
    'WatchedDict',
    'Roster'
]

def readGear(save, slot):
    """The STL save file contains a list of gear, each one having a
    unique ID number. This method makes a `legends.gameobjects.Gear`
    object for each gear piece, and builds a dictionary mapping its ID
    number in the save file to the associated `legends.gameobjects.Gear`
    object.

    Args:
        save (dict): A decrypted dictionary representation of the
            player's save file, as returned by the
            `legends.functions.decryptSaveFile` function.
        slot (int): The 0-based index of the save slot from which to
            read the data.

    Returns:
        dict: {`int`:`legends.gameobjects.Gear`} The dictionary mapping
            IDs to gear.

    """
    slotData = save['{} data'.format(slot)]
    gear = {}
    for indexStr, data in slotData['gears'].items():
        index = int(indexStr)
        gear[index] = Gear(data['gearid'], data['level'])
    return gear

def readParts(save, slot):
    """The STL save file contains a list of particles, each one having a
    unique ID number. This method makes a `legends.gameobjects.Particle`
    object for each particle, and builds a dictionary mapping its ID
    number in the save file to the associated
    `legends.gameobjects.Particle` object.

    Args:
        save (dict): A decrypted dictionary representation of the
            player's save file, as returned by the
            `legends.functions.decryptSaveFile` function.
        slot (int): The 0-based index of the save slot from which to
            read the data.

    Returns:
        dict: {`int`:`legends.gameobjects.Particle`} The dictionary
            mapping IDs to particles.

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

class OneToOneChangeEvent(Event): # pylint: disable=too-few-public-methods
    """A change in a `legends.utils.objrelations.OneToOne` relation.

    Attributes:
        rel (legends.utils.objrelations.OneToOne): The relation that has
            changed.
        key (obj): The key involved in the change.
        value (obj): The value involved in the change.
        changeType (str): Either 'added' or 'removed', indicating
            whether the key-value pair was added or removed. When a key
            that already has a value is assigned a new value, two events
            should be created, one to remove the old key-value pair, and
            another to add the new key-value pair.

    """

    def __init__(self, rel, key, value, changeType):
        self.rel = rel
        self.key = key
        self.value = value
        self.changeType = changeType

    def __repr__(self):
        return (
            '<OneToOneChangeEvent>: key-value pair ({!r}, {!r}) {!r}'
        ).format(self.key, self.value, self.changeType)

class WatchedOneToOne(OneToOne):
    """A one-to-one relation with an event handler.

    Changes made to the relation trigger the event handler of both the
    relation and its inverse.

    Attributes:

        onChange (legends.utils.eventhandler.EventHandler): When a
            key-value pair is added or removed, this event handler
            creates a `OneToOneChangeEvent` and sends it to all
            subscribers.

    """

    def __init__(self):
        OneToOne.__init__(self)
        self.onChange = EventHandler()

    def __delitem__(self, key):
        oldVal = self[key]
        OneToOne.__delitem__(self, key)
        self.onChange.notify(
            OneToOneChangeEvent(self, key, oldVal, 'removed')
        )
        self.inverse.onChange.notify(
            OneToOneChangeEvent(self, oldVal, key, 'removed')
        )

    def __setfreeval__(self, key, val):
        oldVal = self.get(key)
        OneToOne.__setfreeval__(self, key, val)
        newVal = self.get(key)
        if oldVal is newVal:
            return
        if oldVal is not None:
            self.onChange.notify(
                OneToOneChangeEvent(self, key, oldVal, 'removed')
            )
            self.inverse.onChange.notify(
                OneToOneChangeEvent(self, oldVal, key, 'removed')
            )
        if newVal is not None:
            self.onChange.notify(
                OneToOneChangeEvent(self, key, newVal, 'added')
            )
            self.inverse.onChange.notify(
                OneToOneChangeEvent(self, newVal, key, 'added')
            )

# pylint: disable-next=too-few-public-methods
class InGearSlot(WatchedOneToOne):
    """Models the relationship between gear and gear slots.

    The `InGearSlot` class is a one-to-one mapping from
    `legends.gameobjects.Gear` instances and
    `legends.gameobjects.GearSlot` instances.

    Attributes:
        enforceLevel (bool): If `True`, gear cannot be mapped to a gear
            slot if the level of the gear exceeds the level the
            character to which the slot belongs. Defaults to `True`.

    """

    def __init__(self):
        WatchedOneToOne.__init__(self)
        self.enforceLevel = True

    # pylint: disable-next=arguments-renamed
    def validate(self, gear, gearSlot):
        """Raises a value error if the `enforceLevel` attribute is
        `True` and the rarity of the given gear exceeds the rarity of
        the character to which the given gear slot belongs. Otherwise,
        returns `True`.

        """
        char = gearSlot.char
        index = gearSlot.index
        if gear.slot != index or (
            gear.level > 5 + 5 * char.rarityIndex and self.enforceLevel
        ):
            raise ValueError((gear, gearSlot))
        return True

class WatchedCollection():
    """A mix-in class for constructing watched collection data types.

    Objects added to a watched collection should have a `stats`
    attribute that points to a `legends.stats.StatObject` instance. A
    `ValueError` is raises when trying to add an object that does not
    satisfy this.

    A watched collection maintains a list of subscribers in a private
    attribute. Whenever a value is added to the collection, the
    `onChange` event handler of that value's `stats` attribute is
    subscribed to by every callable in the list of subscribers.
    Callbacks are automatically unsubscribed when values are removed
    from the collection.

    This mix-in class provides the following methods: `__getitem__`,
    `__setitem__`, `__delitem__`, and `__len__`. The `__setitem__`
    method does not unsubscribe callbacks from the old value's event
    handler in the case where there was an old value. Such behavior must
    be implemented by subclasses.

    Subclasses must override the `values()` method with a method that
    returns an iterator over the values contained in the collection.

    """
    def __init__(self, collectionType):
        """The constructor stores the collection data in a private
        attribute, to be managed by subclasses.

        Args:
            collectionType (class): The type of collection (`list`,
                `dict`, etc.)

        """
        self._data = collectionType()
        self._subscribers = []

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        checkForStats(value)
        self._data[key] = value
        for callback in self._subscribers:
            value.stats.onChange.subscribe(callback)

    def __delitem__(self, key):
        for callback in self._subscribers:
            self._data[key].stats.onChange.unsubscribe(callback)
        del self._data[key]

    def __len__(self):
        return len(self._data)

    def values(self):
        """Raises a `NotImplementedError`. Must be overridden by
        subclasses.

        """
        raise NotImplementedError

    def subscribe(self, callback):
        """Adds the given callback to the list of subscribers, then
        subscribes to the `onChange` event handler of the `stats`
        attribute of every value currently in the collection.

        Args:
            callback (callable): The callable object to send to the
                `onChange` event handlers.

        """
        self._subscribers.append(callback)
        for value in self.values():
            value.stats.onChange.subscribe(callback)

    def unsubscribe(self, callback):
        """Removes the given callback from the list of subscribers, then
        unsubscribes from the `onChange` event handler of the `stats`
        attribute of every value currently in the collection.

        Args:
            callback (callable): The callable object to unsubscribe from
                the `onChange` event handlers.

        """
        self._subscribers.remove(callback)
        for value in self.values():
            value.stats.onChange.unsubscribe(callback)

    def __repr__(self):
        return '{}({!r})'.format(self.__class__.__name__, self._data)

class WatchedList(WatchedCollection, MutableSequence):
    """A list of objects with a `stats` attribute.

    The `stats` attribute should point to a `legends.stats.StatObject`
    instance. Whenever an object is added to the list, the `onChange`
    event handler of that object's `stats` attribute is subscribed to by
    all callbacks in the `WatchedList` instance's list of subscribers
    (inherited from `WatchedCollection`).

    `WatchedList` does not implement slice assignment. Setting a value
    by index will unsubscribe from the old value's event handler.

    """

    def __init__(self, *args, **kargs):
        WatchedCollection.__init__(self, list)
        for value in list(*args, **kargs):
            self.append(value)

    def __setitem__(self, key, value):
        if isinstance(key, slice):
            raise NotImplementedError('Slice assignment not implemented')
        for callback in self._subscribers:
            self._data[key].stats.onChange.unsubscribe(callback)
        WatchedCollection.__setitem__(self, key, value)

    def insert(self, index, value):
        """Same as `list.insert()`, but subscribes to the value's event
        handler.

        """
        checkForStats(value)
        self._data.insert(index, value)
        for callback in self._subscribers:
            value.stats.onChange.subscribe(callback)

    def values(self):
        """An alias for `__iter__()`.

        """
        return self.__iter__()

class WatchedDict(WatchedCollection, MutableMapping):
    """A dictionary whose values have a `stats` attribute.

    The `stats` attribute should point to a `legends.stats.StatObject`
    instance. Whenever a value is added to the dictionary, the
    `onChange` event handler of that value's `stat` attribute is
    subscribed to by all callbacks in the `WatchedDict` instance's list
    of subscribers (inherited from `WatchedCollection`).

    Setting the value of a key that is already in the dictionary will
    unsubscribe from the old value's event handler.

    """

    def __init__(self, *args, **kargs):
        WatchedCollection.__init__(self, dict)
        for key, value in dict(*args, **kargs):
            self[key] = value

    def __setitem__(self, key, value):
        if key in self._data:
            for callback in self._subscribers:
                self._data[key].stats.onChange.unsubscribe(callback)
        WatchedCollection.__setitem__(self, key, value)

    def __iter__(self):
        return self._data.__iter__()

    def values(self):
        """Returns an iterator over the values of the watched
        dictionary.

        """
        return MutableMapping.values(self)

class Roster():
    """A collection of related characters, gear, and particles.

    Attributes:
        inGearSlot (InGearSlot): A relation mapping
            `legends.gameobjects.Gear` objects to
            `legends.gameobjects.GearSlot` objects.
        inPartSlot (WatchedOneToOne): A relation mapping
            `legends.gameobjects.Particle` objects to
            `legends.gameobjects.PartSlot` objects.

    """
    def __init__(self, save=None, slot=0):
        """If save data is provided, the constructor will populate the
        roster with objects built from the save data. Otherwise, an
        empty roster is created.

        Args:
            save (dict): A decrypted dictionary representation of the
                player's save file, as returned by the
                `legends.functions.decryptSaveFile` function.
            slot (int): The 0-based index of the save slot from which to
                read the data.

        """
        self._gear = WatchedList()
        self._gear.subscribe(self.charChangeWatcher)
        self._parts = WatchedList()
        self._parts.subscribe(self.charChangeWatcher)
        self._chars = WatchedDict()
        self._chars.subscribe(self.charChangeWatcher)
        self.inGearSlot = InGearSlot()
        self.inGearSlot.onChange.subscribe(self.charChangeWatcher)
        self.inPartSlot = WatchedOneToOne()
        self.inPartSlot.onChange.subscribe(self.charChangeWatcher)
        if save is not None:
            self.fromSaveData(save, slot)
        self.onCharChange = EventHandler()

    @property
    def gear(self):
        """`WatchedList of legends.gameobjects.Gear`: A list of the gear
        in the roster.
        """
        return self._gear

    @property
    def parts(self):
        """`WatchedList of legends.gameobjects.Particle`: A list of the
        particles in the roster.
        """
        return self._parts

    @property
    def chars(self):
        """`WatchedDict`: {`str`:`legends.gameobjects.Character`} A
        dictionary mapping name IDs to characters.
        """
        return self._chars

    @property
    def containsGear(self):
        """`legends.utils.objrelations.OneToOne`: The inverse of
        `inGearSlot`.
        """
        return self.inGearSlot.inverse

    @property
    def containsPart(self):
        """`legends.utils.objrelations.OneToOne`: The inverse of
        `inPartSlot`.
        """
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
                player's save file, as returned by the
                `legends.functions.decryptSaveFile` function.
            slot (int): The 0-based index of the save slot from which to
                read the data.

        """
        self.clear()

        # fill gear and particles
        gearDict = readGear(save, slot)
        self.gear.extend(gearDict.values())
        partDict = readParts(save, slot)
        self.parts.extend(partDict.values())

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
                    try:
                        self.inGearSlot[item] = slot
                    except ValueError:
                        warn('Rarity of {} exceeds rarity of {}'.format(
                            item, char
                        ))
                        self.inGearSlot.enforceLevel = False
                        self.inGearSlot[item] = slot
                        self.inGearSlot.enforceLevel = True

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
        present. The character is added at maximum rank and level, and
        with all skills maxed.

        If the `maxGear` attribute is True, maxed gear pieces will be
        created, added to the roster, and equipped to the newly added
        characters.

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
            for skill in char.skills.values():
                skill.unlocked = True
                skill.level = 2
            self.chars[nameID] = char
            if not maxGear:
                continue
            for slot, gearName in enumerate(gearNames):
                gear = Gear(
                    '{} {}'.format(gearName, char.role),
                    5 + 5 * char.rarityIndex
                )
                self.gear.append(gear)
                self.inGearSlot[gear] = char.gearSlots[slot]

    def charChangeWatcher(self, event):
        # TODO: Fill in this method.
        """This method is subscribed to the `gear`, `parts`, and `chars`
        watched collections, as well as to the `onChange` event handlers
        of the `inGearSlot` and `inPartSlot` relations. As such, this
        method is called when anything (gear, particle, character, or
        their relations) changes. For now, this method is just a
        placeholder to be updated later.

        """
        pass # pylint: disable=unnecessary-pass

    def maxGearLevel(self, gear):
        """Returns the maximum possible gear level of the given gear
        piece, which is determined by the rarity of the character on
        which it is equipped, and is 1 if it is not equipped.

        Args:
            gear (legends.gameobjects.Gear): A gear piece.

        Returns:
            int: The maximum possible level of the given gear piece.

        """
        if gear not in self.inGearSlot:
            return 1
        return 5 + 5 * self.inGearSlot[gear].char.rarityIndex

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
        maxGearLevel = 5 + 5 * char.rarityIndex
        return 4 * maxGearLevel - gearLevels

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
            pool (str): One of the keys of `SUMMON_POOL`.
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
