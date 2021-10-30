"""Constants and custom data structures used in the `legends` package.

Each json file in `legends/data` is converted to a constant. The
variable name is the file name without extension, and the variable
points to a Python dictionary built from the file's contents.

NOTE: (1) The constant `GSBaseStat` differs from the data file
'GSBaseStat.json'. In the constant, 'MaxHealth' is renamed to 'Health'.
(2) The file 'Item.json' is converted to the constant `Item_asset` to
prevent conflict with the `Item` class.

Attributes:
    BRIDGE_STATIONS (list of str): A list of all possible bridge
        stations that characters can occupy.
    CHARACTER_TAGS (list): [`str`] A list of all in-game characters tags
        for all playable characters, both enabled and upcoming.
    DESCRIPTIONS (dict): The key-value pairs in `lang_en_us['List']` put
        into a Python dictionary.
    DIFFICULTIES (dict): {`str`:`str`} A dictionary mapping the in-game
        name of the PVE difficulties to the names used in the game data.
    ENABLED (list of str): A list of name IDs of characters that appear
        on the Crew screen.
    HELP (str): The contents of the file, `legends/help.txt`.
    ITEMS (dict): {`str`:`Item`} A dictionary mapping each item ID in
        `GSItem` to an `Item` instance built from that item ID.
    MISSION_NODE_TYPES (dict): {`str`:`str`} A dictionary mapping the
        names of mission node types as they appear in `GSMissionNodes`
        to the names as they appear in the game.
    POWER_GRADIENT (dict): {`str`:`float`} A dictionary mapping stat
        names to the amount that a character's power would increase if
        that stat were to increase by 1.
    POWER_AT_ORIGIN (float): The theoretical power of a character whose
        every stat is 0.
    RARITIES (list of str): A list of rarities in the game, from low to
        high.
    RARITY_COLORS (dict): {`str`:`str`} A dictionary mapping character
        rarities to color names in `tkinter`.
    ROLES (list of str): A list of roles in the game.
    PART_EFFECTS (dict): {`str`:`str`} The `legends` package only tracks
        the primary effects of three particle types: Amplified Force,
        Nexus Field, and Undo Damage. This dictionary maps the names of
        these effects ('Attack Up', 'Shield', and 'Regenerate') to
        abbreviations used throughout the `legends` package, typically
        for object attribute names.
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
    STAT_ABBREVIATIONS (dict): {`str`:`str`} A dictionary mapping stat
        names as they appear in `GSBaseStat` to abbreviations used
        throughout this package, typically for attribute names.
    STAT_INITIALS (dict): {`str`:`str`} A dictionary mapping stat names
        as they appear in `GSBaseStat` to one or two letter short forms,
        typically used in GUI elements where brevity is essential.
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

from collections.abc import MutableMapping
from json import load
from os import listdir
from os.path import abspath, dirname
from legends.utils.relations import bidict

__all__ = [
    'BRIDGE_STATIONS',
    'CHARACTER_TAGS',
    'DESCRIPTIONS',
    'DIFFICULTIES',
    'ENABLED',
    'HELP',
    'Item',
    'ITEMS',
    'MISSION_NODE_TYPES',
    'POWER_GRADIENT',
    'POWER_AT_ORIGIN',
    'PART_STAT_UNLOCKED',
    'RARITIES',
    'PART_EFFECTS',
    'PART_STAT_VALUES',
    'RARITY_COLORS',
    'ROLES',
    'STAT_ABBREVIATIONS',
    'STAT_INITIALS',
    'SUMMON_POOL',
    'SUMMON_POOL_IDS',
    'UPCOMING',
    'Inventory'
]

rootPath = abspath(dirname(__file__))

# convert all json files in `/data` to dictionaries and assign to a
# variable whose name is the file name without extension
for fileName in listdir(rootPath + '/data'):
    if fileName[0] == '.':
        continue
    varName = fileName.split('.')[0]
    if varName == 'Item':
        varName = 'Item_asset' # pylint: disable=invalid-name
    with open(rootPath + '/data/' + fileName, encoding='utf-8') as f:
        globals()[varName] = load(f)
    __all__.append(varName)

# rename 'MaxHealth' in `GSBaseStat` to 'Health'
# pylint: disable-next=used-before-assignment
_ = {'Health': GSBaseStat['MaxHealth']}
_.update(GSBaseStat)
del _['MaxHealth']
GSBaseStat = _

BRIDGE_STATIONS = []
for data in GSCharacter.values(): # pylint: disable=undefined-variable
    if data['BridgeStations'] != ['None']:
        BRIDGE_STATIONS.extend(data['BridgeStations'])
BRIDGE_STATIONS = list(set(BRIDGE_STATIONS))

DESCRIPTIONS = {}
for D in lang_en_us['List']: # pylint: disable=undefined-variable
    key = D['key']
    value = D['value']
    if key:
        DESCRIPTIONS[key] = value

DIFFICULTIES = {
    'Normal': 'Easy',
    'Advanced': 'Hard',
    'Expert': 'Doom'
}

ENABLED = [
    # pylint: disable-next=undefined-variable
    nameID for nameID, data in GSCharacter.items() if data['Type'] == 'Normal'
]

# read and store the help file
with open(rootPath + '/help.txt', encoding='utf-8') as f:
    HELP = f.read()

class Item():
    """An item in STL.

    An `Item` instance has no public attributes. All its data should be
    accessed through its read-only properties. It is meant to be used
    like an immutable data type.

    """

    _betterCategoryNames = {
        'BiomimeticGel': 'Bio-Gel',
        'Item': 'General Items',
        'ProtoMatter': 'Protomatter',
    }

    def __init__(self, itemID):
        """The constructor builds the item from the given item ID,
        which should match a key in `GSItem`.

        """
        self._itemID = itemID
        itemData = GSItem[itemID] # pylint: disable=undefined-variable
        dataCat = itemData['category']
        self._category = self._betterCategoryNames.get(dataCat, dataCat)
        if itemData['icon'][:4] == 'Gear':
            if itemData['rarity'] == 'Common':
                self._category = 'Gear Leveling Materials'
            else:
                self._category = 'Gear Ranking Materials'

    @property
    def itemID(self):
        """`str`: The in-data item ID of the item. Should match a key in
        `GSItem`.
        """
        return self._itemID

    @property
    def name(self):
        """`str`: The in-game name of the item."""
        # pylint: disable-next=undefined-variable
        itemData = GSItem[self.itemID]
        return (
            DESCRIPTIONS[itemData['name']] if 'name' in itemData
            else self.itemID
        )

    @property
    def category(self):
        """`str`: The category of the item. Categories appear in
        `GSItem`. The `Item` class replaces the category found there in
        the following cases. It replaces 'BiomimeticGel' with 'Bio-Gel',
        'Item' with 'General Items', and 'ProtoMatter' with
        'Protomatter'. Also, if the item is a gear-leveling or gear
        ranking material, the category is replaced by 'Gear Leveling
        Materials' or 'Gear Ranking Materials', respectively.
        """
        return self._category

    @property
    def xp(self):
        """`int`: If the item is a bio-gel, this is the amount of xp it
        awards; otherwise it is 0.
        """
        try:
            # pylint: disable-next=undefined-variable
            return GSItem[self.itemID]['DataBiomimeticGel']['Xp']
        except KeyError:
            return 0

    @property
    def role(self):
        """`str`: If the item is protomatter, this is the role that the
        protomatter is meant for; otherwise it is `None`.
        """
        if self.category != 'Protomatter':
            return None
        roleName = self.itemID[6:-3]
        roleName = 'Engineering' if roleName == 'Engineer' else roleName
        return roleName

    def __repr__(self):
        return '<Item: {!r}>'.format(self.name)

# pylint: disable-next=undefined-variable
ITEMS = {itemID: Item(itemID) for itemID in GSItem}

MISSION_NODE_TYPES = {
    'Encounter': 'Combat',
    'Opportunity': 'Explore',
    'Story': 'Intel',
    'Resource': 'Resource'
}

POWER_GRADIENT = {}
POWER_AT_ORIGIN = 0
for statName, statData in GSBaseStat.items():
    m = statData['MinValue']
    M = statData['MaxValue']
    POWER_GRADIENT[statName] = 10 / (M - m)
    POWER_AT_ORIGIN += (-m) * 10 / (M - m)

PART_EFFECTS = {
    'Attack Up': 'attUp',
    'Shield': 'shield',
    'Regenerate': 'regen'
}

PART_STAT_UNLOCKED = {
    'Common': [1, 2, 2, 2, 2],
    'Rare': [1, 2, 2, 2, 2],
    'VeryRare': [1, 2, 2, 3, 3],
    'Epic': [2, 3, 3, 4, 4],
    'Legendary': [2, 3, 3, 4, 4]
}

RARITIES = ['Common', 'Rare', 'VeryRare', 'Epic', 'Legendary']

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

RARITY_COLORS = {
    'Common': 'cyan',
    'Rare': 'lawn green',
    'VeryRare': 'orange',
    'Epic': 'MediumPurple1',
    'Legendary': 'yellow'
}

ROLES = ['Command', 'Engineering', 'Medical', 'Science', 'Security']

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

UPCOMING = ['PicardOld', 'JudgeQ', 'Guinan', 'NumberOne']
UPCOMING = [nameID for nameID in UPCOMING if nameID not in ENABLED]

CHARACTER_TAGS = []
for nameID in UPCOMING + ENABLED:
    # pylint: disable-next=undefined-variable
    CHARACTER_TAGS.extend(GSCharacter[nameID]['Tags'])
CHARACTER_TAGS = sorted(list(set(CHARACTER_TAGS)))


class Inventory(MutableMapping):
    """A collection of items in STL.

    The `Inventory` class is a dictionary-like data structure, mapping
    each item in `ITEMS` to the quantity of that item that exists in the
    player's inventory. Keys cannot be deleted. Instead, deleting a key
    simply changes its value to 0. Iterating over an `Inventory` object
    will skip over items that are either irrelevant to the `legends`
    package, or are implemented elsewhere. The skipped items are
    determined by the `hiddenItemIDs` and `hiddenCategories` attributes.
    To iterate over all keys, simply iterate over `ITEMS.values()`.
    The `__len__()` method also does not consider these skipped items.

    """

    hiddenCategories = ['Token', 'PlayerAvatar', 'Emote']
    """`list of str`: A list of category names, as they appear in the
    `category` attribute of an `legends.constants.Item` instance, that
    are of limited use or implemented elsewhere in the `legends`
    package.
    """

    hiddenItemIDs = [
        'Credits', 'Dilithium', 'Tritanium', 'Player XP', 'PvP Stamina',
        'Alliance Stamina', 'EventPoint', 'PvP Chest Points',
        'Shards Advanced', 'Shards Elite', 'Shards Credit',
        'Shards Biomimetic', 'Shards Protomatter', 'Shards_Worf',
        'Shards_McCoy', 'Dungeon Currency', 'Dungeon Stamina'
    ]
    """`list of str`: A list of item IDs, as they appear in `GSItem`,
    that are of limited use or implemented elsewhere in the `legends`
    package.
    """

    def __init__(self, initDict=None):
        """The constructor initializes the `Inventory` instance with one
        key for each item in `ITEMS`, and all values 0. If the
        `initData` argument is given, it is used to initialize the
        values.

        Args:
            initData (dict): {`str`:`int`} A dictionary mapping item
                IDs, as they appear in `GSItem`, to nonnegative
                integers. Used to initialize the quantities in the
                `Inventory` instance.

        """
        self._data = {}
        for itemID in GSItem: # pylint: disable=undefined-variable
            self._data[itemID] = 0
        initDict = {} if initDict is None else initDict
        for itemID, qty in initDict.items():
            self._data[itemID] = qty

    @property
    def xp(self):
        """`int`: The total xp of all Bio-Gel items in the inventory."""
        return sum(qty * item.xp for item, qty in self.itemsByCat('Bio-Gel'))

    def __getitem__(self, item):
        return self._data[item.itemID]

    def __setitem__(self, item, qty):
        self._data[item.itemID] = qty

    def __delitem__(self, item):
        self._data[item.itemID] = 0

    def __iter__(self):
        for itemID in self._data:
            if not self._hidden(itemID):
                yield ITEMS[itemID]

    def __len__(self):
        count = 0
        for itemID in self._data:
            if not self._hidden(itemID):
                count += 1
        return count

    def __add__(self, other):
        result = Inventory()
        for item in self:
            result[item] = self[item] + other[item]
        return result

    def _hidden(self, itemID):
        if itemID in self.hiddenItemIDs:
            return True
        if ITEMS[itemID].category in self.hiddenCategories:
            return True
        return False

    def keysByCat(self, category):
        """Returns an iterator over all keys that match the given
        category, skipping any keys that are skipped during normal
        iteration.

        Args:
            category (str): The category to iterate over.

        """
        return (item for item in self if item.category == category)

    def itemsByCat(self, category):
        """Returns an iterator over all (key, value) tuples that match
        the given category, skipping any keys that are skipped during
        normal iteration.

        Args:
            category (str): The category to iterate over.

        """
        return (
            (item, qty) for item, qty in self.items()
            if item.category == category
        )

    def __repr__(self):
        return 'Inventory({!r})'.format({
            itemID: qty for itemID, qty in self._data.items()
            if qty > 0
        })
