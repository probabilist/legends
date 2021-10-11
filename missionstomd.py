"""Creates a markdown file of all *Star Trek: Legends* mission.

"""

from legends import DIFFICULTIES, Mission

def getToText(nodes, edge):
    """Given a list of mission nodes and a node edge, find the edge's
    end node in the list and inserts its 1-based index in that last into
    the string ' (to {})', then returns the string.

    Args:
        nodes (list of MissionNode): The list of nodes.
        edge (NodeConnection): The edge whose end node to look for.

    Returns:
        str: The ' (to {})' formatted string.

    """
    return ' (to {})'.format(nodes.index(edge.endNode) + 1)

def missionToMarkdown(episode, orderIndex, difficulty):
    """Creates a markdown-formatted description and map of a mission.

    Args:
        episode (int): The 1-based index of the episode in which the
            mission resides.
        orderIndex (int): The 1-based index of where in the episode the
            mission occurs.
        difficulty (str): One of 'Normal', 'Advanced', or 'Expert'.

    Returns:
        str: The markdown-formatted data.

    """
    mission = Mission(episode, orderIndex, difficulty)
    mdown = '{}\n\n{}\n\nSuggest Power: {}\n\n'.format(
        mission.name, mission.description, mission.power
    )
    nodes = list(mission.nodes.values())
    for node in nodes:
        edges = [
            edge for edge in mission.nodeConnections if edge.startNode is node
        ]
        mdown += '{}. {}{}\n'.format(
            nodes.index(node) + 1,
            node.type,
            (
                '' if node.type == 'Explore' or len(edges) != 1
                else getToText(nodes, edges[0])
            )
        )
        if node.type == 'Combat':
            slots = (
                'None' if not node.coverSlots else
                ', '.join(str(slot + 1) for slot in node.coverSlots)
            )
            mdown += '    * Cover Slots: {}\n'.format(slots)
        if node.type == 'Resource':
            for item, qty in node.rewards.items():
                if qty > 0:
                    mdown += '    * {}: {}\n'.format(item.name, qty)
        if node.type == 'Explore':
            for edge in edges:
                role, power = edge.nodeOption.role, edge.nodeOption.power
                profText = (
                    '' if role is None else ' ({} {})'.format(power, role)
                )
                mdown += '    *{} {}{}\n'.format(
                    profText, edge.nodeOption.name, getToText(nodes, edge)
                )
    return mdown

def missionsToFile():
    """Creates a markdown file of all missions. Saves the file as
    'missions.md' in the current working directory.

    """
    text = ''
    for difficulty in DIFFICULTIES:
        for episode in range(1,8):
            for orderIndex in range(1,7):
                text += '# Episode {} Mission {} -- {}\n\n'.format(
                    episode, orderIndex, difficulty
                )
                text += missionToMarkdown(episode, orderIndex, difficulty)
                text += '\n'
    with open('missions.md', 'w', encoding='utf-8') as f:
        f.write(text)

if __name__ == '__main__':
    missionsToFile()
