"""Tools for storing and manipulating STL object statistics.

"""

from legends.constants import STAT_ABBREVIATIONS, POWER_GRADIENT

__all__ = ['formatDict', 'StatObject', 'Stats']

def formatDict(D):
    """Formats the given dictionary for display, putting each key-value
    pair on its own line.

    Args:
        D (dict): The dictionary to format.

    Returns:
        str: The formatted string.

    """
    lines = [repr(k) + ': ' + repr(v) for k, v in D.items()]
    display = '{' + lines[0] + ',\n'
    for line in lines[1:-1]:
        display += ' ' + line + ',\n'
    display += ' ' + lines[-1] + '}'
    return display

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
        for statName in self.statAbbrs:
            statSum = getattr(self, statName) + getattr(other, statName)
            setattr(result, statName, statSum)
        return result

    def __repr__(self):
        return 'StatObject({})'.format(formatDict({
            statName: getattr(self, statName) for statName in self.statAbbrs
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
