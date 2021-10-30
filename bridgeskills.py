"""Exports data about bridge skills to a spreadsheet.

"""

from csv import DictWriter
from legends.constants import BRIDGE_STATIONS, ENABLED, UPCOMING
from legends.gameobjects import Character

def bridgeSkillToDict(char):
    """Creates and returns a dictionary of data about the given
    character's bridge skill.

    Args:
        char (legends.gameobjects.Character): The dictionary is based on
            this character's bridge skill.

    Returns:
        dict: A dictionary of data about the given character's bridge
            skill.

    """
    D = {'name': char.shortName}
    tag = char.bridgeSkill.tagAffected
    tag = 'All' if tag is None else tag
    D['applies to'] = tag
    num = char.bridgeSkill.effect.statSourceFrac
    num = num if num < 1 else char.bridgeSkill.effect.chanceToResist
    D['num'] = num
    ability = char.bridgeSkill.effect.statAffected
    ability = (
        ability if ability is not None
        else f'Resistance vs {char.bridgeSkill.effect.resistanceType}'
    )
    D['ability'] = ability
    for station in BRIDGE_STATIONS:
        D[station] = station in char.bridgeStations
    return D

def bridgeSkillsToCSV():
    """Compiles data about the bridge skill of every enabled and
    upcoming character (except 'Q') that has a bridge skill, and exports
    it to a file named, 'bridgeskills.csv' in the current working
    directory.

    """
    nameIDs = ENABLED + UPCOMING
    nameIDs.remove('JudgeQ')    # his bridge skill has no effects
    nameIDs.remove('NumberOne') # her bridge skill has no effects
    chars = [Character(nameID) for nameID in nameIDs]
    chars = [char for char in chars if char.bridgeSkill is not None]
    skillDicts = [bridgeSkillToDict(char) for char in chars]
    fields = skillDicts[0].keys()
    with open('bridgeskills.csv', 'w', newline='', encoding='utf-8') as f:
        writer = DictWriter(f, fields)
        writer.writeheader()
        writer.writerows(skillDicts)

if __name__ == '__main__':
    bridgeSkillsToCSV()
