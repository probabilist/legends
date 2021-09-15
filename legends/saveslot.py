"""The SaveSlot class and supporting objects.

"""

from base64 import decodebytes
from datetime import datetime, timedelta, timezone
from getpass import getuser
from json import loads
from plistlib import load
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
# pylint: disable-next=no-name-in-module
from legends.constants import GSCharacter
from legends.roster import Roster

__all__ = [
    'saveFilePath', 'AESdecrypt', 'decryptSaveFile', 'ticksToTimedelta',
    'ticksToDatetime', 'SaveSlot', 'STLTimeStamps'
]

def saveFilePath():
    """Creates and return the complete path of the save file.

    Returns:
        str: The complete path of the save file.

    """
    return (
        '/Users/' + getuser() + '/Library/Containers/'
        + 'com.tiltingpoint.startrek/Data/Library/Preferences/'
        + 'com.tiltingpoint.startrek.plist'
    )

def AESdecrypt(cipherText, key, iv):
    """Decrypts the given cipher text, using the provided key and iv.

    Args:
        cipherText (str): The message to be decrypted.
        key (str): The decryption key.
        iv (str): The iv.

    Returns:
        str: The decrypted message.

    """
    keyB = key.encode('ascii')
    ivB = decodebytes(iv.encode('ascii'))
    cipherTextB = decodebytes(cipherText.encode('ascii'))

    cipher = AES.new(keyB, AES.MODE_CBC, ivB)

    return unpad(cipher.decrypt(cipherTextB), AES.block_size).decode('UTF-8')

def decryptSaveFile():
    """Decrypts and parses the save file into a dictionary.

    Returns:
        dict: The decrypted save file as a dictionary.

    """
    with open(saveFilePath(), 'rb') as f:
        saveFile = load(f)
    saveFile.pop('CloudKitAccountInfoCache', None)
    for i in range(3):
        key = str(i) + ' data'
        if len(saveFile.get(key, '')) == 0:
            saveFile[key] = {}
            continue
        saveFile[key] = loads(AESdecrypt(
            saveFile[key],
            'K1FjcmVkc2Vhc29u',
            'LH75Qxpyf0prVvImu4gqxg=='
        ))
    return saveFile

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

    def __init__(self, slot=None):
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
        if slot is not None:
            self.fromFile(slot)

    def fromFile(self, slot):
        """Populates the calling instance's attribute with data from the
        locally stored save file.

        Args:
            slot (int): The 0-based index of the save slot from which to
                draw the data.

        """
        save = decryptSaveFile()
        key = '{} data'.format(slot)
        if key not in save or not save[key]:
            raise ValueError(slot)
        self.timestamps.fromSaveData(save, slot)
        self.roster.fromSaveData(save, slot)
        for nameID in self.tokens:
            self.tokens[nameID] = save[key]['items'].get(nameID, 0)

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
