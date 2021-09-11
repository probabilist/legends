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

    The StatObject class is meant to be subclassed. Subclasses must
    set `statNames` to an iterable that iterates over the names of the
    statistics being stored in the subclass. The subclass constructor
    must be able to accept no arguments, and when it does, should create
    an object, all of whose statistics are zero.

    Two StatObjects can be added. The result is a new StatObject whose
    statistics are the sum of the statistics of the given StatObjects.

    Attributes:
        statAbbrs (iter of str): Strings that represent the stored
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
        return formatDict({
            statName: getattr(self, statName) for statName in self.statAbbrs
        })

class Stats(StatObject):
    """Stores the basic stats in STL.

    Attributes:
        statAbbrs (iter of str): The values of STAT_ABBREVIATIONS, which
            are abbreviation for the keys of `GSBaseStat`.

    """

    def __init__(self, initDict=None):
        """Builds a Stats object from the given dictionary. If None is
        given, builds a Stats object with all zeros.

        Args:
            initDict (dict of str:(int or float)): A dictionary mapping
                the stat names in the keys of STAT_ABBREVIATIONS to
                numerical values.

        """
        StatObject.__init__(self)
        self.statAbbrs = STAT_ABBREVIATIONS.values()
        if initDict is None:
            initDict = {statName: 0 for statName in self.statAbbrs}
        self.update(initDict)

    @property
    def power(self):
        """The additional power that would be added to a character if
        its stats increased by the amounts given in the this Stats
        object.
        """
        powerDelta = 0
        for statName, statAbbr in STAT_ABBREVIATIONS.items():
            statVal = getattr(self, statAbbr)
            powerDelta += POWER_GRADIENT[statName] * statVal
        return powerDelta

    def update(self, statDict):
        """Sets the stat attributes to those contained in the given stat
        dictionary.

        Args:
            statDict (dict of str:(int or float)): A dictionary mapping
                the stat names in the keys of STAT_ABBREVIATIONS to
                numerical values.

        """
        for statName, statVal in statDict.items():
            setattr(self, STAT_ABBREVIATIONS[statName], statVal)
