"""Creates a markdown file of all *Star Trek: Legends* mission.

"""

import os
from graphviz import Digraph
from pdf2image import convert_from_path
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

def missionToMarkdown(episode, orderIndex, difficulty, mapLink=False):
    """Creates a markdown-formatted description and map of a mission.

    Args:
        episode (int): The 1-based index of the episode in which the
            mission resides.
        orderIndex (int): The 1-based index of where in the episode the
            mission occurs.
        difficulty (str): One of 'Normal', 'Advanced', or 'Expert'.
        mapLink (bool): True is a link to the mission map should be
            included.

    Returns:
        str: The markdown-formatted data.

    """
    mission = Mission(episode, orderIndex, difficulty)
    mdown = '{}\n\n{}\n\nSuggested Power: {}\n\n'.format(
        mission.name, mission.description, mission.power
    )
    if mapLink:
        mdown += ('[Mission Map]({}{}-{}-{}.jpg)\n\n'.format(
            'https://probabilist.github.io/legends/maps/mission',
            episode, orderIndex, difficulty
        ))
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

def missionToGraph(episode, orderIndex, difficulty):
    """Creates a graph of a mission and exports it to the current
    directory in jpg format.

    Args:
        episode (int): The 1-based index of the episode in which the
            mission resides.
        orderIndex (int): The 1-based index of where in the episode the
            mission occurs.
        difficulty (str): One of 'Normal', 'Advanced', or 'Expert'.

    """
    mission = Mission(episode, orderIndex, difficulty)
    name = 'mission{}-{}-{}'.format(
        episode, orderIndex, difficulty
    )
    graph = Digraph(filename=name)
    nodes = list(mission.nodes.values())
    nodeLabels = []
    for index, node in enumerate(nodes):
        nodeLabel = '{}. {}'.format(index + 1, node.type.upper())
        if node.type == 'Combat':
            slots = (
                'None' if not node.coverSlots else
                ','.join(str(slot + 1) for slot in node.coverSlots)
            )
            nodeLabel += '\n Cover Slots-{}'.format(slots)
        if node.type == 'Resource':
            for item, qty in node.rewards.items():
                if qty > 0:
                    nodeLabel += '\n{}-{}'.format(item.name, qty)
        nodeLabels.append(nodeLabel)
        graph.node(nodeLabel)
    for edge in mission.nodeConnections:
        startLabel = nodeLabels[nodes.index(edge.startNode)]
        endLabel = nodeLabels[nodes.index(edge.endNode)]
        edgeLabel = ''
        if edge.nodeOption is not None:
            profLabel = (
                '' if edge.nodeOption.role is None
                else '\n({} {})'.format(
                    edge.nodeOption.power, edge.nodeOption.role[:3]
                )
            )
            edgeLabel = edge.nodeOption.name + profLabel
        graph.edge(startLabel, endLabel, edgeLabel)
    graph.render(cleanup=True)
    convert_from_path(
        name + '.pdf', 300, os.getcwd(),
        fmt='jpg',
        output_file=name
    )
    os.remove(name + '.pdf')
    os.rename(name + '0001-1.jpg', name + '.jpg')

def missionsToFile(mapLink=False):
    """Creates a markdown file of all missions. Saves the file as
    'missions.md' in the current working directory.

    Args:
        mapLink (bool): True if links to maps should be included.

    """
    text = ''
    for difficulty in DIFFICULTIES:
        for episode in range(1,8):
            for orderIndex in range(1,7):
                text += '# Episode {} Mission {} -- {}\n\n'.format(
                    episode, orderIndex, difficulty
                )
                text += missionToMarkdown(
                    episode, orderIndex, difficulty, mapLink
                )
                text += '\n'
    with open('missions.md', 'w', encoding='utf-8') as f:
        f.write(text)

if __name__ == '__main__':
    missionsToFile(True)
    # for difficulty in DIFFICULTIES:
    #     for episode in range(1,8):
    #         for orderIndex in range(1,7):
    #             missionToGraph(episode, orderIndex, difficulty)
