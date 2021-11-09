"""Tools for storing and manipulating STL object statistics.

"""

from legends.utils.functions import formatDict
from legends.utils.eventhandler import Event, EventHandler
from legends.constants import PART_EFFECTS, POWER_GRADIENT, STAT_ABBREVIATIONS

__all__ = [
    'checkForStats',
    'PartEffects',
    'StatChangeEvent',
    'StatObject',
    'Stats'
]

def checkForStats(obj):
    """Checks if the given objects has a 'stats' attribute that points
    to a `StatObject` instance.

    Args:
        obj (obj): The object to check.

    Raises:
        ValueError: If the object fails the check.

    """
    if not hasattr(obj, 'stats'):
        raise ValueError('{} has no `stats` attribute'.format(obj))
    if not isinstance(obj.stats, StatObject):
        raise ValueError(
            '{} is not an instance of `StatObject`'.format(obj.stats)
        )

class StatChangeEvent(Event): # pylint: disable=too-few-public-methods
    """Created when one of a `StatObject`'s attributes changes.

    Should only be created when the changing attribute is a statistic.

    Attributes:
        parent (obj): The object whose statistics have changed.
        oldStats (dict): {`str`:`int` or `float`} A dictionary mapping
            stat names (the keys of the `StatObject`'s `statAbbrs`
            property) to their previous values (at the time of the last
            issuance of a `StatChangeEvent`).

    """

    def __init__(self, parent, oldStats):
        self.parent = parent
        self.oldStats = oldStats

class StatObject():
    """An object that stores named statistics as attributes.

    The `StatObject` class is meant to be subclassed. Subclasses must
    set `statAbbrs` to an iterable that iterates over the names
    (typically abbreviations) of the statistics being stored in the
    subclass. The subclass constructor must be able to accept no
    arguments, and when it does, it should create an object, all of
    whose statistics are zero.

    Two `StatObject` instances can be added/multiplied. The result is a
    new `StatObject` instance whose statistics are the sum/product of
    the statistics of the given instances.

    Attributes:
        parent (obj): The object to which these stats belong.
        onChange (legends.utils.eventhandler.EventHandler): Sends a
            `StatChangeEvent` to subscribers when a statistic changes.
        silent (bool): Set to `True` to prevent the sending of a
            `StatChangeEvent` when a statistic changes. Defaults to
            `False`.

    """

    def __init__(self, statAbbrs, parent=None, initDict=None):
        """If a dictionary of stat values is provided, the constructor
        initializes the instance with these values.

        Args:
            statAbbrs (dict): {`str`:`str`} The dictionary to assign to
                the `statAbbrs` property.
            initDict (dict): {`str`:`int or float`} A dictionary mapping
                stat names to numerical values. The keys of `initDict`
                should match the keys of the `statAbbrs` property.

        """
        self._statAbbrs = statAbbrs
        self.parent = parent
        self.silent = False
        self.onChange = EventHandler()
        self._oldStats = {statName: 0 for statName in self.statAbbrs}
        if initDict is None:
            initDict = self._oldStats.copy()
        self.update(initDict)

    @property
    def statAbbrs(self):
        """`dict`: {`str`:`str`} A dictionary mapping the names of stats
        to be stored to the abbreviations that are to be used as
        attribute names.
        """
        return self._statAbbrs

    @property
    def oldStats(self):
        """`dict`: {`str`:`int or float`} A dictionary mapping stat
        names to the values they held the last time a `StatChangeEvent`
        was issued. If no `StatChangeEvent` has been issued, all values
        of this dictionary will be 0.
        """
        return self._oldStats

    @property
    def asDict(self):
        """`dict`: {`str`:`int or float`} A dictionary mapping stat
        names to their current values.
        """
        return {statName: self.get(statName) for statName in self.statAbbrs}

    def __setattr__(self, attrName, value):
        self.__dict__[attrName] = value
        if attrName in self.statAbbrs.values() and not self.silent:
            self.notify()

    def notify(self):
        """Sends a `StatChangeEvent` to the `onChange` subscribers, and
        updates the `oldStats` property.
        """
        self.onChange.notify(StatChangeEvent(self.parent, self.oldStats))
        self._oldStats = self.asDict

    def get(self, statName):
        """Looks up a stat value by its name, as it appears in the keys
        of the `statAbbrs` property.

        Args:
            statName (str): A stat name, as it appears in the keys of
                the `statAbbrs` property.

        Returns:
            int or float: The value of the given stat.

        """
        return getattr(self, self.statAbbrs[statName])

    def set(self, statName, value):
        """Sets a stat value by its name, as it appears in the keys of
        the `statAbbrs` property.

        Args:
            statName (str): A stat name, as it appears in the keys of
                the `statAbbrs` property.
            value (int or float): The value to assign.

        """
        setattr(self, self.statAbbrs[statName], value)

    def update(self, statDict):
        """Sets the stat attributes to those contained in the given stat
        dictionary. Suppresses all issuing of `StatChangeEvent`
        instances until the update is completed, then issues a single
        event to cover the entire update.

        Args:
            statDict (dict): {`str`:`int or float`} A dictionary mapping
                stat names to numerical values. The keys of `statDict`
                should match the keys of the `statAbbrs` attribute.

        """
        initSilent = self.silent
        self.silent = True
        for statName, statVal in statDict.items():
            setattr(self, self.statAbbrs[statName], statVal)
        self.silent = initSilent
        if not self.silent:
            self.notify()

    def __add__(self, other):
        result = self.__class__(self.statAbbrs)
        for statAbbr in self.statAbbrs.values():
            statSum = getattr(self, statAbbr) + getattr(other, statAbbr)
            setattr(result, statAbbr, statSum)
        return result

    def __mul__(self, other):
        result = self.__class__(self.statAbbrs)
        for statAbbr in self.statAbbrs.values():
            statProd = getattr(self, statAbbr) * getattr(other, statAbbr)
            setattr(result, statAbbr, statProd)
        return result

    def __repr__(self):
        return 'StatObject({})'.format(formatDict({
            statAbbr: getattr(self, statAbbr)
            for statAbbr in self.statAbbrs.values()
        }))

class Stats(StatObject):
    """Stores the basic stats in STL.

    A subclass of `StatObject` whose `statAbbrs` property is set to
    `STAT_ABBREVIATIONS`.

    """

    def __init__(self, parent=None, initDict=None):
        StatObject.__init__(self, STAT_ABBREVIATIONS.copy(), parent, initDict)

    @property
    def power(self):
        """The additional power that would be added to a character if
        its stats increased by the amounts given in the calling
        instance.
        """
        powerDelta = 0
        for statName in STAT_ABBREVIATIONS:
            statVal = self.get(statName)
            powerDelta += POWER_GRADIENT[statName] * statVal
        return powerDelta

class PartEffects(StatObject):
    """Stats describing effects of particles in STL.

    A subclass of `StatObject` whose `statAbbrs` property is set to
    `PART_EFFECTS`.

    """

    def __init__(self, parent=None, initDict=None):
        """If a dictionary of stat values is provided, the constructor
        initializes the instance with these values.

        Args:
            initDict (dict): {`str`:`int or float`} A dictionary mapping
                the stat names in the keys of `PART_EFFECTS` to
                numerical values.

        """
        StatObject.__init__(self, PART_EFFECTS, parent, initDict)
