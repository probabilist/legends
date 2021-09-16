"""The SaveSlot class and supporting objects.

"""

from datetime import datetime, timedelta, timezone
# pylint: disable-next=no-name-in-module
from legends.constants import GSCharacter
from legends.roster import Roster

__all__ = [
    'ticksToTimedelta', 'ticksToDatetime', 'SaveSlot', 'STLTimeStamps'
]

def ticksToTimedelta(ticks):
    """Converts a duration measured in "ticks" to a Python `timedelta`
    object. There are 10 "ticks" in a microsecond. The .NET framework
    uses ticks to mark time.

    Args:
        ticks (int): The number of tenths of a microsecond.

    Returns:
        timedelta: The converted duration.

    """
    return timedelta(microseconds=ticks//10)

def ticksToDatetime(ticks):
    """Converts a .NET timestamp to a Python `datetime` object. .NET
    timestamps return the number of "ticks" since 1/1/0001. There are 10
    "ticks" in a microsecond. (For comparison, a POSIX timestamp returns
    the number of seconds since 1/1/1970.)

    Args:
        ticks (int): A timestamp in the .NET format.

    Returns:
        datetime: The converted timestamp.

    """
    return (
        datetime(1, 1, 1, tzinfo=timezone.utc)
        + timedelta(microseconds=ticks//10)
    )

class SaveSlot():
    """One of three player save slots.

    Attributes:
        timestamps (STLTimeStamps): Stores the timestamp data for the
            save slot.
        roster (Roster): A Roster object built from the save slot data.
        tokens (dict of str:int0: A dictionary mapping a character
            nameID to the number of tokens for that character in the
            player's possession.
        favorites (list of Character): A list of characters the player
            has marked as 'favorite'.

    """

    def __init__(self):
        """Constructs a SaveSlot object by extracting data from the
        user's Star Trek: Legends save file, stored on the local HD.

        Args:
            slot (int): The 0-based index of the save slot from which to
                draw the data.

        Raises:
            ValueError: If no save data is found in the given slot.

        """
        self.timestamps = STLTimeStamps()
        self.roster = Roster()
        self.tokens = {nameID: 0 for nameID in GSCharacter}
        self.favorites = []

    def fromFile(self, save, slot):
        """Populates the calling instance's attribute with data from the
        locally stored save file.

        Args:
            save (dict): A decrypted dictionary representation of the
                player's save file, as returned by the `decryptSaveFile`
                function.
            slot (int): The 0-based index of the save slot from which to
                draw the data.

        """
        key = '{} data'.format(slot)
        if key not in save or not save[key]:
            raise ValueError(slot)
        self.timestamps.fromSaveData(save, slot)
        self.roster.fromSaveData(save, slot)
        for nameID in self.tokens:
            self.tokens[nameID] = save[key]['items'].get(nameID, 0)

    def sort(self, func, descending=True):
        """Sorts the dictionary of characters stored in the associated
        Roster object according the currently selected sorting field.

        Args:
            func (function): Should be a function mapping a Character
                object and a SaveSlot object to a sortable value.

        """
        self.roster.chars = dict(sorted(
            self.roster.chars.items(),
            key=lambda item:func(item[1], self),
            reverse=descending
        ))
        # rewrite sort method in rostertab


class STLTimeStamps():
    """An object for storing and managing Star Trek: Legends timestamps.

    An STLTimeStamps object is associated to a specific save slot in a
    particular user's save file.

    Attributes:
        startDate (datetime): The time the user first played the
            associated save slot. Defaults to launch of Star Trek:
            Legends.
        timeLastPlayed (datetime): The time the user last played the
            associated save slot. Defaults to the time the STLTimeStamps
            instance is created.
        playDuration (timedelta): The amount of time the user has spent
            playing the associated save slot. Defaults to 0.

    """

    def __init__(self):
        self.startDate = datetime(2021, 4, 2, 12, tzinfo=timezone.utc)
        self.timeLastPlayed = datetime.now(tz=timezone.utc)
        self.playDuration = timedelta()

    @property
    def playTimePerDay(self):
        """timedelta: The amount of time per day spent on the associated
        save slot.
        """
        return (
            self.playDuration/(self.timeLastPlayed - self.startDate).days
        )

    def fromSaveData(self, save, slot):
        """Sets the attributes of the calling instance to match the data
        contained in the given save slot of the give save file data.

        Args:
            save (dict): A decrypted dictionary representation of the
                player's save file, as returned by the `decryptSaveFile`
                function.
            slot (int): The 0-based index of the save slot from which to
                read the time stamps.

        """
        self.startDate = datetime.fromtimestamp(
            save['{} data'.format(slot)]['createts'], tz=timezone.utc
        )
        self.timeLastPlayed = ticksToDatetime(
            int(save['{} timeLastPlayed'.format(slot)])
        )
        self.playDuration = ticksToTimedelta(
            int(save['{} playDuration'.format(slot)])
        )
