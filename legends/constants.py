"""The constants used in the `legends` package.

Each json file in `legends/data` is converted to a constant. The
variable name is the file name without extension, and the variable
points to a Python dictionary built from the file's contents.

NOTE: The constant `GSBaseStat` differs from the data file
`GSBaseStat.json`. In the constant, 'MaxHealth' is renamed to 'Health'.

Attributes:
    DESCRIPTIONS (dict): The key-value pairs in `lang_en_us['List']` put
        into a Python dictionary.
    ENABLED (list of str): A list of name IDs of characters that appear
        on the Crew screen.
    HELP (str): The contents of the file, `legends/help.txt`.
    POWER_GRADIENT (dict): {`str`:`float`} A dictionary mapping stat
        names to the amount that a character's power would increase if
        that stat were to increase by 1.
    POWER_AT_ORIGIN (float): The theoretical power of a character whose
        every stat is 0.
    RARITIES (list of str): A list of rarities in the game, from low to
        high.
    RARITY_COLORS (dict): {`str`:`str`} A dictionary mapping character
        rarities to color names in tkinter.
    ROLES (list of str): A list of roles in the game.
    STAT_ABBREVIATIONS (dict): A dictionary mapping stat names as they
        appear in `GSBaseStat` to abbreviations used throughout this
        package, typically for attribute names.
    SUMMON_POOL (dict): {`str`:`dict`} A dictionary mapping pool names
        ('Core' or one the roles in `ROLES`) to a dictionary with three
        keys: 'nameIDs', which maps to a dictionary connecting name IDs
        of the characters in that particular summon pool to their summon
        probabilities; 'rarityChances', which maps to the probabilities
        of summoning the available rarities; and 'cost', which maps to
        the number of orbs required to summon from that pool. See the
        examples below.
    SUMMON_POOL_IDS (legends.utils.relations.bidict): An invertible
        dictionary mapping pool names their summon IDs, which are used
        by the game data to identify particular summon pools.
    PART_STAT_UNLOCKED (dict): {`str`:[`int`]}: A dictionary
        mapping particle rarities to a list whose indices denote the
        0-based level of the particle and whose values denote the number
        of unlocked stats on a particle of that rarity and level. See
        the examples below.
    PART_STAT_VALUES (dict): {`str`:{`str`:[`float`]}}: A
        dictionary mapping stat names to a dictionary mapping rarity
        names to a list whose indices denote the 0-based level of the
        particle and whose values denote the value of the given stat on
        a particle of the given rarity and level. See the examples
        below.
    UPCOMING (list of str): A list of name IDs of characters believed to
        be in the queue for future release.

Examples:
    A Very Rare, Level 3 particle has 2 stats unlocked:
    >>> PART_STAT_UNLOCKED['VeryRare'][2]
    2

    If an Epic, Level 1 particle has Attack as one of its stats, the
    Attack value will be 32:
    >>> PART_STAT_VALUES['Attack']['Epic'][0]
    32.0

    The probability of summoning Kirk from the Command pool is 1%:
    >>> SUMMON_POOL['Command']['nameIDs']['Kirk']
    0.01

    The probability of summoning an Epic character from the 'Core' pool
    is 10%:
    >>> SUMMON_POOL['Core']['rarityChances']['Epic']
    0.1

    It costs 75 orbs to summon once from the Science pool:
    >>> SUMMON_POOL['Science']['cost']
    75

"""

from os import listdir
from os.path import abspath, dirname
from json import load
from legends.utils import bidict

__all__ = [
    'STAT_ABBREVIATIONS', 'STAT_INITIALS', 'POWER_GRADIENT', 'POWER_AT_ORIGIN',
    'DESCRIPTIONS', 'ROLES', 'RARITIES', 'RARITY_COLORS', 'PART_STAT_UNLOCKED',
    'PART_STAT_VALUES', 'ENABLED', 'UPCOMING', 'SUMMON_POOL',
    'SUMMON_POOL_IDS', 'HELP'
]

rootPath = abspath(dirname(__file__))

# convert all json files in `/data` to dictionaries and assign to a
# variable whose name is the file name without extension
for fileName in listdir(rootPath + '/data'):
    if fileName[0] == '.':
        continue
    varName = fileName.split('.')[0]
    with open(rootPath + '/data/' + fileName, encoding='utf-8') as f:
        globals()[varName] = load(f)
    __all__.append(varName)

# rename 'MaxHealth' in `GSBaseStat` to 'Health'
# pylint: disable-next=used-before-assignment
_ = {'Health': GSBaseStat['MaxHealth']}
_.update(GSBaseStat)
del _['MaxHealth']
GSBaseStat = _

STAT_ABBREVIATIONS = {
    'Health': 'hlth',
    'Attack': 'att',
    'Speed': 'spd',
    'Defense': 'dfn',
    'Tech': 'tech',
    'CritDamage': 'cd',
    'CritChance': 'cc',
    'GlancingDamage': 'gd',
    'GlancingChance': 'gc',
    'Resolve': 'res'
}
STAT_INITIALS = {
    'Health': 'H',
    'Attack': 'A',
    'Speed': 'S',
    'Defense': 'D',
    'Tech': 'T',
    'CritDamage': 'CD',
    'CritChance': 'CC',
    'GlancingDamage': 'GD',
    'GlancingChance': 'GC',
    'Resolve': 'R'
}

POWER_GRADIENT = {}
POWER_AT_ORIGIN = 0
for statName, statData in GSBaseStat.items():
    m = statData['MinValue']
    M = statData['MaxValue']
    POWER_GRADIENT[statName] = 10 / (M - m)
    POWER_AT_ORIGIN += (-m) * 10 / (M - m)

DESCRIPTIONS = {}
for D in lang_en_us['List']: # pylint: disable=undefined-variable
    key = D['key']
    value = D['value']
    if key:
        DESCRIPTIONS[key] = value

ROLES = ['Command', 'Engineering', 'Medical', 'Science', 'Security']
RARITIES = ['Common', 'Rare', 'VeryRare', 'Epic', 'Legendary']
RARITY_COLORS = {
    'Common': 'cyan',
    'Rare': 'lawn green',
    'VeryRare': 'orange',
    'Epic': 'MediumPurple1',
    'Legendary': 'yellow'
}

PART_STAT_UNLOCKED = {
    'Common': [1, 2, 2, 2, 2],
    'Rare': [1, 2, 2, 2, 2],
    'VeryRare': [1, 2, 2, 3, 3],
    'Epic': [2, 3, 3, 4, 4],
    'Legendary': [2, 3, 3, 4, 4]
}

# initialize PART_STAT_VALUES
PART_STAT_VALUES = {
    statName: {rarity: [0] * 5 for rarity in RARITIES}
    for statName in
    GSAccessoryStatGeneration # pylint: disable=undefined-variable
}
# fill PART_STAT_VALUES
# pylint: disable-next=undefined-variable
for data in GSAccessoryStatGrowth.values():
    statName = data['Stat']
    level = data['Level']
    rarity = data['Rarity']
    statVal = data['StatIncrease']
    PART_STAT_VALUES[statName][rarity][level - 1] = statVal

ENABLED = [
    # pylint: disable-next=undefined-variable
    nameID for nameID, data in GSCharacter.items() if data['Type'] == 'Normal'
]
UPCOMING = ['Tuvok', 'Gowron', 'JadziaDax', 'PicardOld']

# initialize SUMMON_POOL and SUMMON_POOL_IDS
SUMMON_POOL = {'Core': {'nameIDs': {}}}
SUMMON_POOL.update({role: {'nameIDs': {}} for role in ROLES})
SUMMON_POOL_IDS = bidict()
# build SUMMON_POOL_IDS; keep only highest unlocked summon pools
for pool in SUMMON_POOL:
    summonID = max(
        (
            # pylint: disable-next=undefined-variable
            data['summonId'] for key, data in GSSummonSetup.items()
            if key[7:10] == pool[:3]
        ),
        key=lambda summonID:int(summonID[-2:])
    )
    SUMMON_POOL_IDS[pool] = summonID
# retrieve rarity chances
for data in GSSummonPools.values(): # pylint: disable=undefined-variable
    summonID = data['summonID']
    if summonID in SUMMON_POOL_IDS.values():
        pool = SUMMON_POOL_IDS.inverse[summonID]
        SUMMON_POOL[pool]['rarityChances'] = data['rarityChances']
# retrieve costs
for data in GSSummonSetup.values(): # pylint: disable=undefined-variable
    summonID = data['summonId']
    if summonID in SUMMON_POOL_IDS.values():
        pool = SUMMON_POOL_IDS.inverse[summonID]
        SUMMON_POOL[pool]['cost'] = data['costQuantity']
# retrieve characters in each summon pool
for data in GSSummonItems.values(): # pylint: disable=undefined-variable
    for summonID in data['filterGroups']:
        if summonID in SUMMON_POOL_IDS.values():
            pool = SUMMON_POOL_IDS.inverse[summonID]
            SUMMON_POOL[pool]['nameIDs'][data['itemID']] = None
# raise an error if Core does not contain everyone in other pools
for pool, data in SUMMON_POOL.items():
    if pool == 'Core':
        continue
    for nameID in data['nameIDs']:
        if nameID not in SUMMON_POOL['Core']['nameIDs']:
            raise ValueError(
                '{} in {} summon pool but not in Core'.format(nameID, pool)
            )
# add summoning probabilities
for pool, data in SUMMON_POOL.items():
    for rarity in RARITIES:
        nameIDs = [
            nameID for nameID in data['nameIDs']
            # pylint: disable-next=undefined-variable
            if GSCharacter[nameID]['Rarity'] == rarity
        ]
        if nameIDs:
            prob = data['rarityChances'][rarity] / len(nameIDs)
            for nameID in nameIDs:
                data['nameIDs'][nameID] = prob

# read and store the help file
with open(rootPath + '/help.txt', encoding='utf-8') as f:
    HELP = f.read()
