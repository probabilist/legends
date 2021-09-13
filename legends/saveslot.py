"""The SaveSlot class and supporting objects.

"""

from base64 import decodebytes
from datetime import datetime, timedelta, timezone
from getpass import getuser
from json import loads
from plistlib import load
from warnings import warn
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
#pylint: disable-next=no-name-in-module
from legends.constants import GSAccessoryItems
from legends.constants import DESCRIPTIONS
from legends.gameobjects import Gear, Particle, Character, Roster

__all__ = [
    'saveFilePath', 'AESdecrypt', 'decryptSaveFile', 'ticksToTimedelta',
    'ticksToDatetime', 'SaveSlot'
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
        slot (int): The 0-based save slot in the player's save file that
            this SaveSlot object represents.
        save (dict): The dictionary representation of the player's
            entire (decrypted) save file.
        roster (Roster): A Roster object built from the save slot data.
        favorites (list of Character): A list of characters the player
            has marked as 'favorite'.

    """

    def __init__(self, slot=0):
        """Constructs a SaveSlot object by extracting data from the
        user's Star Trek: Legends save file, stored on the local HD.

        Args:
            slot (int): The 0-based index of the save slot from which to
                draw the data.

        Raises:
            ValueError: If no save data is found in the given slot.

        """
        self.save = decryptSaveFile()
        key = '{} data'.format(slot)
        if key not in self.save or not self.save[key]:
            raise ValueError(slot)
        self.slot = slot
        self.roster = Roster()
        self.roster.gear = self.readGear()
        self.roster.parts = self.readParts()
        self.roster.chars = self.readChars()
        self.favorites = []

    @property
    def slotData(self):
        """The portion of the save file contained in the save slot."""
        return self.save[str(self.slot) + ' data']

    @property
    def startDate(self):
        """datetime: The save slot's start date."""
        return datetime.fromtimestamp(
            self.slotData['createts'],
            tz=timezone.utc
        )

    @property
    def timeLastPlayed(self):
        """datetime: The last time this save slot was played."""
        return ticksToDatetime(
            int(self.save[str(self.slot) + ' timeLastPlayed'])
        )

    @property
    def playDuration(self):
        """timedelta: The amount of time spent on this save slot."""
        return ticksToTimedelta(
            int(self.save[str(self.slot) + ' playDuration'])
        )

    @property
    def playTimePerDay(self):
        """timedelta: The amount of time per day spent on this save
        slot.
        """
        return (
            self.playDuration/(self.timeLastPlayed - self.startDate).days
        )

    @property
    def tokens(self):
        """dict of str:int: A dictionary mapping a character nameID to
        the number of tokens for that character in the player's
        possession.
        """
        return {
            nameID: self.slotData['items'].get(nameID, 0)
            for nameID in self.roster.chars
        }

    def readGear(self):
        """The save slot contains a list of gear, each one having a
        unique ID number. This method makes a Gear object for each
        gear piece, and builds a dictionary mapping its ID number to the
        associated Gear object.

        Returns:
            dict of int:Gear: The dictionary mapping IDs to gear.

        """
        gear = {}
        for indexStr, data in self.slotData['gears'].items():
            index = int(indexStr)
            gear[index] = Gear(data['gearid'], data['level'])
        return gear

    def readParts(self):
        """The save slot contains a list of particles, each one having a
        unique ID number. This method makes a Particle object for each
        particle, and builds a dictionary mapping its ID number to the
        associated Particle object.

        Returns:
            dict of int:Particle: The dictionary mapping IDs to
                particles.

        """
        parts = {}
        for saveIndexStr, data in self.slotData['accessories'].items():
            saveIndex = int(saveIndexStr)
            name = DESCRIPTIONS[GSAccessoryItems[data['accessoryid']]['Name']]
            rarity = GSAccessoryItems[data['accessoryid']]['Rarity']
            part = Particle(name, rarity, data['level'], data['locked'])
            for statIndex, statName in enumerate(data['stats'].values()):
                part.setStatName(statIndex, statName)
            parts[saveIndex] = part
        return parts

    def readChars(self):
        """The save slot contains a list of characters, indexed by the
        in-data name of the character. (These names are the keys in
        `GSCharacter`.) This method makes a Character object for each
        character, and builds a dictionary mapping its in-data name to
        the associated Character object.

        It also associates each Character with the Gear and Particles
        that it has equipped. So this method should not be called until
        the calling instances `roster` attribute has been set and filled
        with gear and particles from the save file.

        Returns:
            dict of str:Character: The dictionary mapping in-data names
                to characters.

        """
        chars = {}
        for nameID, data in self.slotData['units'].items():
            char = Character(nameID, data['rank'], data['xp'])
            char.tokens = self.slotData['items'].get(char.nameID, 0)
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
            for slotIndex, gearSaveIndex in enumerate(data['gears'].values()):
                if gearSaveIndex > 0:
                    gear = self.roster.gear[gearSaveIndex]
                    slot = char.gearSlots[slotIndex]
                    self.roster.inGearSlot[gear] = slot
            for slotIndex, partSaveIndex in (
                enumerate(data['accessories'].values())
            ):
                if partSaveIndex > 0:
                    part = self.roster.parts[partSaveIndex]
                    slot = char.partSlots[slotIndex]
                    self.roster.inPartSlot[part] = slot
            chars[nameID] = char
        return chars
