"""Functions use in the `legends` package.

"""

from json import loads
from getpass import getuser
from plistlib import load
from legends.utils.functions import AESdecrypt
#pylint: disable-next=no-name-in-module
from legends.constants import (
    GSBaseStat, GSCharacter, GSGear, GSGearLevel, GSLevel, GSRank,
    GSSkillUpgrade
)
from legends.constants import Inventory, ITEMS, PART_STAT_VALUES, RARITIES

__all__ = [
    'charGearToMaxCost',
    'cleanTime',
    'decryptSaveFile',
    'gearToMaxCost',
    'gearUpgradeCost',
    'getCharStats',
    'getGearStats',
    'getPartStats',
    'levelFromXP',
    'saveFilePath',
    'skillToMaxCost',
    'skillUpgradeCost',
    'tokensNeeded',
    'xpFromLevel'
]

def charGearToMaxCost(rarity, role='Command'):
    """Computes and returns the cost of leveling all gear on a character
    of the given rarity and role from level 1 to the maximum possible
    level for that character.

    Args:
        rarity (str): The rarity of the character.
        role (str): The role of the character.

    Returns:
        legends.constants.Inventory: The items needed to upgrade are
            stored and returned in an `legends.constants.Inventory`
            instance.

    """
    maxGearLevel = 5 + 5 * RARITIES.index(rarity)
    cost = Inventory()
    for gearID, data in GSGear.items():
        if data['m_Role'] != role:
            continue
        cost += gearToMaxCost(gearID, 1, maxGearLevel)
    return cost

def cleanTime(delta):
    """Converts a `timedelta` object into a string description that
    shows the number of days (if positive), hours, and minutes.

    Args:
        delta (timedelta): The `timedelta` object to convert.

    Returns:
        str: The string description.

    """
    minutes = int(delta.total_seconds()/60)
    hours, minutes = minutes//60, minutes % 60
    days, hours = hours//24, hours % 24
    display = '{} days '.format(days) if days > 1 else ''
    display += '{} hrs {} min'.format(hours, minutes)
    return display

def decryptSaveFile():
    """Finds the STL save file on the local hard drive, then decrypts
    and parses it into a dictionary.

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

def gearToMaxCost(gearID, currLvl, finalLvl):
    """Computes and returns the cost of leveling the given gear from the
    given current level to the given final level.

    Args:
        gearID (str): The gear ID, as it appears in `GSGear`, of the
            given skill.
        currLevel (int): The current level of the gear.
        finalLevel (int): The final level of the gear.

    Returns:
        legends.constants.Inventory: The items needed to upgrade are
            stored and returned in an `legends.constants.Inventory`
            instance.

    """
    cost = Inventory()
    while currLvl < finalLvl:
        currLvl += 1
        cost += gearUpgradeCost(gearID, currLvl)
    return cost

def gearUpgradeCost(gearID, level):
    """Computes and returns the cost of leveling the given gear to the
    given level, from the previous level.

    Args:
        gearID (str): The gear ID, as it appears in `GSGear`, of the
            given skill.
        level (int): The level to which the gear is being upgraded.

    Returns:
        legends.constants.Inventory: The items needed to upgrade are
            stored and returned in an `legends.constants.Inventory`
            instance.

    """
    key = '[{}, {}]'.format(gearID, level)
    cost = Inventory()
    for itemID, qty in GSGearLevel[key]['m_UpgradePrice']['AllItems'].items():
        cost[ITEMS[itemID]] += qty
    return cost

def getCharStats(nameID, rank, level):
    """Calculates a character's naked stats from its nameID, rank, and
    level.

    Args:
        nameID (str): The name ID of the character, as it appears in
            `GSCharacter`.
        rank (int): The rank of the character.
        level (int): The level of the character.

    Returns:
        dict: A dictionary mapping stat names, as they appear in
            `GSBaseStat`, to stat values.

    """
    rarity = GSCharacter[nameID]['Rarity']
    stats = {}
    for statName, data in GSBaseStat.items():
        m = data['MinValue'] #pylint: disable=invalid-name
        M = data['MaxValue'] #pylint: disable=invalid-name
        t = GSCharacter[nameID][statName] #pylint: disable=invalid-name
        baseStat = m + t * (M - m)
        try:
            levelMod = GSLevel[rarity + '_' + str(level)][
                    statName + 'Modifier'
                ]
            rankMod = GSRank[rarity + '_' + str(rank)][
                    statName + 'Modifier'
                ]
        except KeyError:
            levelMod = 1
            rankMod = 1
        statVal = baseStat * levelMod * rankMod
        stats[statName] = statVal
    return stats

def getGearStats(gearID, level):
    """Calculates a gear's stats from its gear ID and level.

    Args:
        gearID (str): The gear ID as it appears in `GSGear`.
        level (int): The level of the gear. (See `Gear.level`.)

    Returns:
        dict: A dictionary mapping stat names, as they appear in
            `GSBaseStat`, to stat values.

    """
    stats = {statName: 0 for statName in GSBaseStat}
    gearLevelID = '[{}, {}]'.format(gearID, level)
    numStats = GSGearLevel[gearLevelID]['m_StatBrancheCount']
    for i in range(numStats):
        data = GSGear[gearID]['m_Stats'][i]
        statName = data['m_Type']
        statBase = data['m_BaseValue']
        statIncr = data['m_IncreaseValue']
        statVal = statBase + (level - 10 * i) * statIncr
        stats[statName] += statVal
    return stats

def getPartStats(rarity, level, statList):
    """Calculates a particle's stats from its rarity, level, and list of
    stat names.

    Args:
        rarity (str): The particle's rarity.
        level (int): The particle's level.
        statList (list of str): The stat names on the particle.

    Returns:
        dict: A dictionary mapping stat names, as they appear in
            `GSBaseStat`, to stat values.

    """
    stats = {statName: 0 for statName in GSBaseStat}
    for statName in statList:
        stats[statName] = (
            PART_STAT_VALUES[statName][rarity][level - 1]
        )
    return stats

def levelFromXP(xp, rarity='Common'):
    """Calculates the level of a character from its XP.

    Args:
        xp (int): The XP of the character.
        rarity (str): The rarity of the character.

    Returns:
        int: The level of the character.

    Raises:
        ValueError: If the level cannot be determined from the given xp
            value and the data in `GSLevel`.

    """
    level = None
    for j in reversed(range(100)):
        xpNeeded = GSLevel[rarity + '_' + str(j)]['Experience']
        if xp >= xpNeeded:
            level = j
            break
    else:
        raise ValueError(repr(xp) + ' could not be converted from XP to level')
    return level

def saveFilePath():
    """Creates and return the complete path of the STL save file.

    Returns:
        str: The complete path of the save file.

    """
    return (
        '/Users/' + getuser() + '/Library/Containers/'
        + 'com.tiltingpoint.startrek/Data/Library/Preferences/'
        + 'com.tiltingpoint.startrek.plist'
    )

def skillToMaxCost(skillID, currLvl):
    """Computes and returns the cost of leveling the given skill to
    Level 2, from the given current level.

    Args:
        skillID (str): The skill ID, as it appears in `GSSkill`, of the
            given skill.
        currLevel (int): The current level of the skill. If set to 0,
            the skill is currently locked.

    Returns:
        legends.constants.Inventory: The items needed to upgrade are
            stored and returned in an `legends.constants.Inventory`
            instance.

    """
    cost = Inventory()
    while currLvl < 2:
        currLvl += 1
        cost += skillUpgradeCost(skillID, currLvl)
    return cost

def skillUpgradeCost(skillID, level):
    """Computes and returns the cost of leveling the given skill to the
    given level, from the previous level.

    Args:
        skillID (str): The skill ID, as it appears in `GSSkill`, of the
            given skill.
        level (int): The level to which the skill is being upgraded. If
            set to 1, returns the cost of unlocking the skill.

    Returns:
        legends.constants.Inventory: The items needed to upgrade are
            stored and returned in an `legends.constants.Inventory`
            instance.

    """
    key = 'GSSkillKey(id = "{}", level = "{}")'.format(skillID, level)
    cost = Inventory()
    for itemID, qty in GSSkillUpgrade[key]['price']['AllItems'].items():
        cost[ITEMS[itemID]] += qty
    return cost

def tokensNeeded(rarity, rank):
    """Returns the number of tokens needed by a character of the given
    rarity and rank to move up to the next rank.

    Args:
        rarity (str): The rarity of the character.
        rank (int): The current rank of the character.

    Returns:
        int: The total number of tokens need for the character to
            advance to the next rank.

    """
    if rank == 9:
        return 0
    # pylint: disable-next=undefined-variable
    return GSRank['{}_{}'.format(rarity, rank + 1)]['RequiredTokenCount']

def xpFromLevel(level, rarity='Common'):
    """Calculates the minimum XP of a character from its level.

    Args:
        level (int): The level of the character.
        rarity (str): The rarity of the character.

    Returns:
        int: The minimum possible XP the character could have.

    """
    return GSLevel[rarity + '_' + str(level)]['Experience']
