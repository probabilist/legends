"""The constants used in the `legends` package.

Each json file in `legends/data` is converted to a constant. The
variable name is the file name without extension, and the variable
points to a Python dictionary built from the file's contents.

Attributes:
    ROOT (str): The full, absolute path of the legends package.
    STAT_ABBREVIATIONS (dict): A dictionary mapping stat names as they
        appear in GSBaseStat to abbreviations used throughout this
        package, typically for attribute names.
    POWER_GRADIENT (dict of str:float) A dictionary mapping stat
        names to the amount that a character's power would increase if
        that stat were to increase by 1.
    POWER_AT_ORIGIN (float): The theoretical power of a character whose
        every stat is 0.
    DESCRIPTIONS (dict): The key-value pairs in `lang_en_us['List']` put
        into a Python dictionary.
    RARITIES (list of str): A list of rarities in the game, from low to
        high.
    ROLES (list of str): A list of roles in the game.
    RARITY_COLORS (dict of str:str): A dictionary mapping character
        rarities to color names in tkinter.

"""

from os import listdir
from os.path import abspath, dirname
from json import load

__all__ = [
    'ROOT', 'STAT_ABBREVIATIONS', 'POWER_GRADIENT', 'POWER_AT_ORIGIN',
    'DESCRIPTIONS', 'ROLES', 'RARITIES', 'RARITY_COLORS'
]

ROOT = abspath(dirname(__file__))

# convert all json files in `/data` to dictionaries and assign to a
# variable whose name is the file name without extension
for fileName in listdir(ROOT + '/data'):
    varName = fileName.split('.')[0]
    with open(ROOT + '/data/' + fileName, encoding='utf-8') as f:
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
