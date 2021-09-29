"""Tools for storing and manipulating STL object statistics.

"""

from legends.utils.functions import formatDict
from legends.constants import POWER_GRADIENT, STAT_ABBREVIATIONS

__all__ = ['StatObject', 'Stats']

class StatObject():
    """An object that stores named statistics as attributes.

    The `StatObject` class is meant to be subclassed. Subclasses must
    set `statAbbrs` to an iterable that iterates over the names
    (typically abbreviations) of the statistics being stored in the
    subclass. The subclass constructor must be able to accept no
    arguments, and when it does, it should create an object, all of
    whose statistics are zero.

    Two `StatObject` instances can be added. The result is a new
    `StatObject` instance whose statistics are the sum of the statistics
    of the given instances.

    Attributes:
        statAbbrs (iterable of str): Strings that represent the stored
            statistics. Typically abbreviations. Used to construct
            object attributes.

    """

    def __init__(self):
        self.statAbbrs = []

    def __add__(self, other):
        result = self.__class__()
        for statAbbr in self.statAbbrs:
            statSum = getattr(self, statAbbr) + getattr(other, statAbbr)
            setattr(result, statAbbr, statSum)
        return result

    def __repr__(self):
        return 'StatObject({})'.format(formatDict({
            statAbbr: getattr(self, statAbbr) for statAbbr in self.statAbbrs
        }))

class Stats(StatObject):
    """Stores the basic stats in STL.

    Attributes:
        statAbbrs (iterable of str): The values of `STAT_ABBREVIATIONS`,
            which are abbreviations for the keys of `GSBaseStat`.

    """

    def __init__(self, initDict=None):
        """If a dictionary of stat values is provided, the constructor
        initializes the instance with these values.

        Args:
            initDict (dict): {`str`:`int or float`} A dictionary mapping
                the stat names in the keys of `STAT_ABBREVIATIONS` to
                numerical values.

        """
        StatObject.__init__(self)
        self.statAbbrs = STAT_ABBREVIATIONS.values()
        if initDict is None:
            initDict = {statName: 0 for statName in STAT_ABBREVIATIONS}
        self.update(initDict)

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

    def get(self, statName):
        """Looks up a stat value by its full name, as it appears in
        `GSBaseStat`.

        Args:
            statName (str): A stat name, as it appears in `GSBaseStat`.

        Returns:
            int or float: The value of the given stat.

        """
        return getattr(self, STAT_ABBREVIATIONS[statName])

    def update(self, statDict):
        """Sets the stat attributes to those contained in the given stat
        dictionary.

        Args:
            statDict (dict): {`str`:`int or float`} A dictionary mapping
                the stat names in the keys of `STAT_ABBREVIATIONS` to
                numerical values.

        """
        for statName, statVal in statDict.items():
            setattr(self, STAT_ABBREVIATIONS[statName], statVal)
