"""Creates a markdown file of all *Star Trek: Legends* skills.

Includes skills for all playable characters, both current and upcoming.

"""

from html.parser import HTMLParser
from legends import GSSkill, GSCharacter, DESCRIPTIONS, ENABLED, UPCOMING

def skillToMarkdown(skillID, level):
    """Creates and returns a markdown string describing the given skill.
    Includes the name, description, effects, caster effect (if any),
    targets, and cooldowns.

    Args:
        skillID (str): The skill ID, as it appears in `legends.GSSkill`.
        level (int): The level of the skill.

    Returns:
        str: A markdown-formatted description of the skill.

    """
    key = 'GSSkillKey(id = "{}", level = "{}")'.format(skillID, level)
    data = GSSkill[key]

    mdown = '## {} - Level {}\n\n'.format(DESCRIPTIONS[data['name']], level)

    desc = DESCRIPTIONS[data['description']]
    desc = SkillHTMLParser(desc).text
    mdown += '**Description:** {}\n\n**Effects:** '.format(desc)

    effDescList = []
    for effect in data['effects']:
        effDescList.append(
            '{} ({:g}x)'.format(effect['effect'], effect['fraction'])
        )
    mdown += ', '.join(effDescList) + '\n\n'

    casEff = data['casterEffect']
    if 'effect' in casEff:
        mdown += '**Caster effect:** {} ({:g}x)\n\n'.format(
            casEff['effect'], casEff['fraction']
        )

    targetSelectionMethod = 'single'
    if data['isAOE']:
        targetSelectionMethod = 'multiple'
    elif data['isMultiRandom']:
        targetSelectionMethod = 'multiple random'
    mdown += '**Target:** {} {} {} ({})\n\n'.format(
        'All' if data['isAOE'] else data['numTargets'],
        data['targetState'],
        data['targetType'],
        targetSelectionMethod
    )

    mdown += '**Cooldown:** {} ({} start)\n\n'.format(
        data['cooldown'], data['startingCooldown']
    )

    return mdown

def skillsToFile():
    """Creates a markdown file of all skills for all playable
    characters, both current and upcoming. Saves the file as 'skills.md'
    in the current working directory.

    """
    text = ''
    for nameID in ENABLED + UPCOMING:
        name = DESCRIPTIONS[GSCharacter[nameID]['Name']]
        text += '# {}\n\n'.format(name)
        for skillID in sorted(GSCharacter[nameID]['SkillIDs']):
            text += skillToMarkdown(skillID, 1)
            text += skillToMarkdown(skillID, 2)
    with open('skills.md', 'w', encoding='utf-8') as f:
        f.write(text)

class SkillHTMLParser(HTMLParser): # pylint: disable=abstract-method
    """An HTML parser for the `skillToMarkdown` function.

    Attributes:
        text (str): The parsed HTML.

    """
    def __init__(self, data=None):
        """The constructor creates a new parser and parses the given
        data.

        Args:
            data (str): The HTML to parse.

        """
        HTMLParser.__init__(self)
        self.text = ''
        if data is not None:
            self.feed(data)

    def handle_starttag(self, tag, attrs):
        """Replace the color tags in the STL data with span tags and a
        darker shade of blue.

        """
        self.text += '<span style=color:blue>'

    def handle_data(self, data):
        """Copy data verbatim.

        """
        self.text += data

    def handle_endtag(self, tag):
        """Replace color end tags with span end tags.

        """
        self.text += '</span>'

if __name__ == '__main__':
    skillsToFile()
