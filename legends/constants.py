"""This module contains the constants used in the `legends` package.
Most data is read from the json files in the 'data' folder, which were
parsed from the Unity game assets. They need to be updated each time an
update to the game is released.

Instructions for updating game assets: Open Star Trek: Legends and let
it play for a while to be sure all assets download. Run
`legends.build.getAssets`. In Visual Studio, create an empty C# project,
add reference to 'Assembly-CSharp.dll', then add the code in 'temp.cs'
somewhere in the project. Use `legends.build.exportData` to export the
current data to the current working directory. Compare the new data and
the current data to be sure everything looks okay. Once satisfied, use
`legends.build.updateData` to replace the data inside the `legends`
package with the contents of the `data-new` folder.

Attributes:
    CHARACTER (dict): A direct parsing of `data/GSCharacter.json`
    SUMMONABLE (dict): A subdictionary of CHARACTER that includes only
        those that have been enabled for player use.
    SUMMON_POOL (dict of str:(dict of str:float)): A dictionary mapping
        pool names (either 'Crew' or a role) to a dictionary mapping
        character names in that summon pool to the probability of
        receiving them on a single summon.
    LEVEL (dict): A direct parsing of `data/GSLevel.json`
    RANK (dict): A direct parsing of `data/GSRank.json`
    GEAR (dict): A direct parsing of `data/GSGear.json`
    GEAR_LEVEL (dict): A direct parsing of `data/GSGearLevel.json`
    SKILL (dict): A direct parsing of `data/GSSkill.json`
    SKILL_IDS (list of str): A list of skill IDs for all characters that
        are enabled for player use.
    BASE_STAT (dict): A direct parsing of `data/GSBaseStat.json`, but
        with the key, 'MaxHealth', replaced by 'Health' for consistency
        with other constants.
    ITEMS (dict of str:(dict of str:dict)): A dictionary storing data
        about items that can be held in the player's inventory. An item
        has a name, a category, and a collection of data about it. The
        `ITEMS` dictionary is structures as `ITEMS[category][name] =
        data`. This dictionary is build from data in `data/GSItem.json`.
        It contains latinum, power cells, alliance currency, bio-gel,
        protomatter, pvp medals, orbs, gear leveling mats, and gear
        ranking mats.

        Example: `ITEMS['GearRankingMat']['Antineutron']` is a
        dictionary of data related to antineutrons.

    RARITIES (list of str): A list of rarities in the game, from low to
        high. The index of a rarity in this list is referred to as a
        'tier' in this package.
    GEAR_NAMES (list of str): A list of basic gear names.
    PART_STAT_UNLOCKED (dict of str:(list of int)): A dictionary mapping
        particle rarities to a list whose indices denote the 0-based
        level of the particle and whose values denote the number of
        unlocked stats on a particle of that rarity and level.
        
        Example: `PART_STAT_UNLOCKED['VeryRare'][2]` is the number of
        unlocked stats on a Level 3, Very Rare particle.
    PART_STAT_VALUES (dict of str:(dict of str:(list of float))): A
        dictionary mapping stat names to a dictionary mapping rarity
        names to a list whose indices denote the 0-based level of the
        particle and whose values denote the value of the given stat on
        a particle of the given rarity and level.

        Example: `PART_STAT_VALUES['Attack']['Epic'][0]` is the value of
        the attack stat on a Level 1, Epic particle.
    PART_EFFECTS (dict of str:(dict of str:obj)) A dictionary mapping
        particle types to their effects. The keys are the particle
        types. Each value is a dictionary with three keys, 'effect',
        'baseVal', and 'incrPerTier'.

        The value of 'effect' is either `None` (for particle types not
        implemented in this package) or a string representation of the
        effect. Each effect is connected to a particular stat. For
        example, the 'shield' effect of the 'Nexus Field' type particle
        is connected to the tech stat. The values of 'baseVal' and
        'incrPerTier' refer to the proportion of the related stat that
        contributes to the effect. The value of 'baseVal' is for a Tier
        0 (Common) particle. The value of 'incrPerTier' is how much this
        proportion increases with each increase in the tier of the
        particle.
    POWER_GRADIENT (dict of str:float) A dictionary mapping stat
        names to the amount that a character's power would increase if
        that stat were to increase by 1.
    POWER_AT_ORIGIN (float): The theoretical power of a character whose
        every stat is 0.

"""

from legends.utils.functions import readData
from legends.build import (
    ROOT, getItems, getSummonPool, getPartStats, getPowerFunc, getSkillIDs
)

CHARACTER = readData('GSCharacter', ROOT)
SUMMONABLE = {k:v for k,v in CHARACTER.items() if v['Type'] == 'Normal'}
SUMMON_POOL = getSummonPool(SUMMONABLE)
LEVEL = readData('GSLevel', ROOT)
RANK = readData('GSRank', ROOT)
GEAR = readData('GSGear', ROOT)
GEAR_LEVEL = readData('GSGearLevel', ROOT)
SKILL = readData('GSSkill', ROOT)
SKILL_IDS = getSkillIDs(CHARACTER)
BASE_STAT = {'Health': None}
BASE_STAT.update(readData('GSBaseStat', ROOT))
BASE_STAT['Health'] = BASE_STAT['MaxHealth']
del BASE_STAT['MaxHealth']
ITEMS = getItems()

RARITIES = ['Common', 'Rare', 'VeryRare', 'Epic', 'Legendary']

GEAR_NAMES = [
    'Starfleet PADD', 'Type II Phaser', 'Communicator', 'Tricorder'
]

PART_STAT_UNLOCKED = {
    'Common': [1, 2, 2, 2, 2],
    'Rare': [1, 2, 2, 2, 2],
    'VeryRare': [1, 2, 2, 3, 3],
    'Epic': [2, 3, 3, 4, 4],
    'Legendary': [2, 3, 3, 4, 4]
}

PART_STAT_VALUES = getPartStats(RARITIES)

PART_EFFECTS = {
    'Accelerated Coagulation': {
        'effect': None,
        'baseVal': 0,
        'incrPerTier': 0
    },
    'Amplify Force': {
        'effect': 'attBonus',
        'baseVal': 0.05,
        'incrPerTier': 0.05
    },
    'Nexus Field': {
        'effect': 'shield',
        'baseVal': 0.05,
        'incrPerTier': 0.05
    },
    'Temporal Flux': {
        'effect': None,
        'baseVal': 0,
        'incrPerTier': 0
    },
    'Undo Damage': {
        'effect': 'regen',
        'baseVal': 0.06,
        'incrPerTier': 0.01
    }
}

POWER_GRADIENT, POWER_AT_ORIGIN = getPowerFunc(BASE_STAT)
