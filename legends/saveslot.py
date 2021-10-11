"""The `legends.saveslot.SaveSlot` class and related objects.

"""

from datetime import datetime, timedelta, timezone
from warnings import warn
from legends.utils.functions import ticksToDatetime, ticksToTimedelta
# pylint: disable-next=no-name-in-module
from legends.constants import (
    GSBattle, GSBattleModifier, GSCharacter, GSMissionEffects, GSMissionNodes,
    GSMissionRewards, GSMissions, GSNodeExploration, GSNodeRewards, GSTooltip
)
from legends.constants import (
    DESCRIPTIONS, DIFFICULTIES, Inventory, ITEMS, MISSION_NODE_TYPES
)
from legends.roster import Roster

__all__ = [
    'Mission',
    'MissionNode',
    'NodeConnection',
    'NodeOption',
    'OptionError',
    'SaveSlot',
    'STLTimeStamps'
]

class Mission():
    """A mission in STL.

    Attributes:
        episode (int): The 1-based index of the episode in which the
            mission resides.
        orderIndex (int): The 1-based index of where in the episode the
            mission occurs.
        difficulty (str): One of 'Normal', 'Advanced', or 'Expert'.
        nodes (dict): {`str`:`MissionNode`} A dictionary mapping the
            node IDs of the nodes in the mission to their corresponding
            `MissionNode` instances.
        nodeConnections (list of NodeConnection): A list of the node
            connections in this mission.
        rewards (legends.constants.Inventory): The rewards earned from
            100% completion of the mission.
        complete (float): The proportion of the mission that has been
            completed.

    """
    def __init__(self, episode, orderIndex, difficulty):
        self.episode = episode
        self.orderIndex = orderIndex
        self.difficulty = difficulty

        self.nodes = {}
        for nodeID in GSMissionNodes[
            'e{}_m{}'.format(self.episode, self.orderIndex)
        ]['Nodes']:
            self.nodes[nodeID] = MissionNode(nodeID, self.difficulty)

        self.nodeConnections = []
        for node in self.nodes.values():
            nextNodeIDs = node.data['NextNodeIds']
            if node.type != 'Explore' and len(nextNodeIDs) > 0:
                nextNodeID = nextNodeIDs[0]
                self.nodeConnections.append(
                    NodeConnection(node, self.nodes[nextNodeID])
                )
            elif node.type == 'Explore':
                for nodeOption in node.options[1:]:
                    self.nodeConnections.append(NodeConnection(
                        node,
                        self.nodes[nodeOption.nextNodeID],
                        nodeOption.optionNum
                    ))

        try:
            initDict = GSMissionRewards['e{}_m{}_complete-{}'.format(
                self.episode, self.orderIndex, DIFFICULTIES[self.difficulty]
            )]['reward']['AllItems']
        except KeyError:
            initDict = {}
        self.rewards = Inventory(initDict)

        self.complete = 0

    @property
    def _key(self):
        return 'episode {} mission {}-{}'.format(
            self.episode,
            self.orderIndex,
            DIFFICULTIES[self.difficulty]
        )

    @property
    def name(self):
        """`str`: The in-game name of the mission."""
        return DESCRIPTIONS[GSMissions[self._key]['Name']]

    @property
    def description(self):
        """`str`:The in-game description of the mission."""
        return DESCRIPTIONS[GSMissions[self._key]['Description']]

    @property
    def power(self):
        """`int`: The recommended team power for the mission."""
        return GSMissions[self._key]['SuggestedPower']

    @property
    def missingNodeRewards(self):
        """Computes and returns the missing node rewards from this
        mission.

        Returns:
            legends.constants.Inventory: The total of all uncollected
                rewards from nodes within the mission.

        """
        return sum(
            (
                node.rewards for node in self.nodes.values()
                if not node.complete
            ),
            Inventory()
        )

    def __repr__(self):
        return 'Mission({!r})'.format(self._key)

class MissionNode():
    """A mission node in STL.

    Attributes:
        nodeID (str): The node's ID as it appears in `GSMissionNodes`.
        data (dict): The node's data as found in `GSMissionNodes`.
        difficulty (str): One of 'Normal', 'Advanced', or 'Expert' (the
            keys of `DIFFICULTIES`).
        rewards (legends.constants.Inventory): The rewards earned from
            completing this node.
        options (list of NodeOption): The first item in this list is
            always `None`. If the node is 'Explore' type, there will be
            additional items representing the options available to the
            player from this node.
        complete (bool): `True` if the node has been completed.

    """
    def __init__(self, nodeID, difficulty):
        self.nodeID = nodeID

        nodeAssetsIDs = []
        for nodeAssetID, data in GSMissionNodes.items():
            if self.nodeID in data['Nodes']:
                nodeAssetsIDs.append(nodeAssetID)
        if len(nodeAssetsIDs) > 1:
            warn('Node ID found in multiple node assets.')
        self.data = GSMissionNodes[nodeAssetsIDs[0]]['Nodes'][self.nodeID]

        self.difficulty = difficulty

        self._key = '{}-{}'.format(self.nodeID, DIFFICULTIES[self.difficulty])
        try:
            initDict = GSNodeRewards[self._key]['reward']['AllItems']
        except KeyError:
            initDict = {}
        self.rewards = Inventory(initDict)

        self.options = [None]
        if self.type == 'Explore':
            optionNum = 1
            while True:
                try:
                    self.options.append(NodeOption(self, optionNum))
                except OptionError:
                    break
                optionNum += 1

        self.complete = False

    @property
    def type(self):
        """`str`: The type of node it is, as displayed in the game. Will
        match one of the four values in `MISSION_NODE_TYPES`.
        """
        return MISSION_NODE_TYPES[self.data['Type']]

    @property
    def coverSlots(self):
        """`list` of `int`: The list of 0-based indices of the cover
        slots in this node, if the node type is 'Combat'; otherwise,
        `None`.
        """
        if self.type != 'Combat':
            return None
        return GSBattle[self._key]['CoverSlotIndices']

    def __repr__(self):
        return 'MissionNode({!r})'.format(self.nodeID)

class NodeConnection(): # pylint: disable=too-few-public-methods
    """A connection from one node in a mission to another.

    Attributes:
        startNode (MissionNode): The starting node of the connection.
        endNode (MissionNode): The ending node of the connection.
        nodeOption (NodeOption): The node option from the start node's
            `options` attribute that corresponds to this connection.

    """

    def __init__(self, startNode, endNode, optionNum=0):
        """The constructor builds a `NodeConnection` instance from the
        given start node, end node, and option number.

        Args:
            optionNum (int): The index of the option in the start node's
                `options` attribute.

        Raises:
            ValueError: If (1) start node does not lead to end node,
                (2) start node is 'Explore' type and option number is 0,
                (3) start node has no option with the given option
                number, or (4) the given option does not lead to end
                node.

        """
        if endNode.nodeID not in startNode.data['NextNodeIds']:
            raise ValueError(
                '{} does not lead to {}.'.format(startNode, endNode)
            )
        if startNode.type == 'Explore':
            if optionNum == 0:
                raise ValueError(
                    'Must specify an option value for {}'.format(startNode)
                )
            try:
                nextNodeID = startNode.options[optionNum].nextNodeID
                if nextNodeID != endNode.nodeID:
                    raise ValueError(
                        'option {} of {} does not lead to {}'.format(
                            optionNum, startNode, endNode
                        )
                    )
            except IndexError as ex:
                raise ValueError('{} has no option number {}'.format(
                    startNode, optionNum
                )) from ex

        self.startNode = startNode
        self.endNode = endNode
        self.nodeOption = startNode.options[optionNum]

    def __repr__(self):
        return 'NodeConnection({}-{}, option {})'.format(
            self.startNode, self.endNode, self.nodeOption.optionNum
        )

class NodeOption(): # pylint: disable=too-few-public-methods
    """An option in an exploration node.

    Attributes:
        node (MissionNode): The node in which the option is given.
        optionNum (int): The 1-based index of the option.
        name (str): The text that appears in the game for the
            corresponding option.
        role (str): The proficiency role needed for this option. Can be
            `None`.
        power (int): The proficiency power required for this option. Can
            be `None`.
        nextNodeID (str): The node ID of the node to which this option
            leads.

    """

    def __init__(self, node, optionNum):
        """The constructor builds a `NodeOption` instance from the given
        node and option number.

        Raises:
            OptionError: If the given node does not have an option
                corresponding to the given option number.

        """
        self.node = node
        self.optionNum = optionNum
        key = '{}_option{:02d}-{}'.format(
                self.node.nodeID,
                self.optionNum,
                DIFFICULTIES[self.node.difficulty]
            )
        try:
            data = GSNodeExploration[key]
        except KeyError as ex:
            raise OptionError('Option {} not found for {}'.format(
                self.optionNum, self.node
            )) from ex
        self.name = DESCRIPTIONS[data['HeaderLoc']]
        self.role = data['RequiredProficiency']
        if self.role == 'None':
            self.role = None
        self.power = data['RequiredProficiencyValue']
        self.nextNodeID = data['BranchingNodeId']

    def __repr__(self):
        return '{!r}, option {!r}, {!r}'.format(
            self.node, self.optionNum, self.name
        )

class OptionError(Exception):
    """Raised when a given option cannot be found in a mission node.

    """

    pass # pylint: disable=unnecessary-pass

class SaveSlot():
    """Data from one of three save slots in an STL save file.

    Attributes:
        timestamps (STLTimeStamps): Stores the timestamp data for the
            save slot.
        roster (legends.roster.Roster): A Roster object built from the
            save slot data.
        tokens (dict): {`str`:`int`} A dictionary mapping a character's
            name ID to the number of tokens for that character in the
            player's inventory.
        favorites (list of legends.gameobjects.Character): A list of
            characters the player has marked as 'favorite'.
        inventory (legends.constants.Inventory): The inventory
            associated with the save slot.
        missions (list of Mission): The list of missions associated with
            the save slot.
        survivalEffects (dict): {`str`:[`int`]} A dictionary mapping
            names of active battle modifiers in survival mode to a list.
            Each item in the list represent one instance of the
            modifier. (Since modifiers can stack, multiple instances can
            be active at a time.) For a given instance, the value in the
            list is the number of battles remaining for that effect.

    """

    def __init__(self):
        self.timestamps = STLTimeStamps()
        self.roster = Roster()
        self.tokens = {nameID: 0 for nameID in GSCharacter}
        self.favorites = []
        self.inventory = Inventory()
        self.missions = []
        for difficulty in ['Normal', 'Advanced', 'Expert']:
            for episode in range(1,8):
                for orderIndex in range(1,7):
                    self.missions.append(
                        Mission(episode, orderIndex, difficulty)
                    )
        self.survivalEffects = {}

    def fromFile(self, save, slot):
        """Uses the given save data to populate the calling instance's
        attributes.

        Args:
            save (dict): A decrypted dictionary representation of the
                player's save file, as returned by the
                `legends.functions.decryptSaveFile` function.
            slot (int): The 0-based index of the save slot from which to
                draw the data.

        Raises:
            ValueError: If the given slot is not in the given save data,
                or if the given save slot data is empty.

        """
        key = '{} data'.format(slot)
        if key not in save or not save[key]:
            raise ValueError(slot)
        self.timestamps.fromSaveData(save, slot)
        self.roster.fromSaveData(save, slot)
        for nameID in self.tokens:
            self.tokens[nameID] = save[key]['items'].get(nameID, 0)
        for itemID, qty in save[key]['items'].items():
            self.inventory[ITEMS[itemID]] = qty
        for mission in self.missions:
            missionKey = 'episode {} mission {}'.format(
                mission.episode, mission.orderIndex
            )
            try:
                data = save[key]['missions'][missionKey][
                    DIFFICULTIES[mission.difficulty]
                ]
            except KeyError:
                continue
            mission.complete = data['complete_pct']/100
            for node in mission.nodes.values():
                try:
                    node.complete = data['nodes'][node.nodeID]['complete']
                except KeyError:
                    pass
        try:
            for effectID, durations in (
                save[key]['dungeon']['mission_effects'].items()
            ):
                modID = GSMissionEffects[effectID]['battleModifierID']
                nameKey = (
                    GSTooltip[GSBattleModifier[modID]['TooltipID']]['headerText']
                )
                self.survivalEffects[DESCRIPTIONS[nameKey].title()] = durations
        except KeyError:
            pass

    def sort(self, func, descending=True):
        """Sorts the dictionary of characters stored in the `roster`
        attribute according the given function.

        Args:
            func (function): Should be a function that maps a
                `legends.gameobjects.Character` to a sortable value.
            descending (bool): True if the characters are to be sorted
                in descending order.

        """
        self.roster.chars = dict(sorted(
            self.roster.chars.items(),
            key=lambda item:func(item[1]),
            reverse=descending
        ))

class STLTimeStamps():
    """Stores and manages *Star Trek: Legends* timestamps.

    Each instance is associated to a specific save slot in a particular
    user's save file.

    Attributes:
        startDate (datetime): The time the user first played the
            associated save slot. Defaults to launch of Star Trek:
            Legends.
        timeLastPlayed (datetime): The time the user last played the
            associated save slot. Defaults to the time the instance is
            created.
        playDuration (timedelta): The amount of time the user has spent
            playing the associated save slot. Defaults to 0.

    """

    def __init__(self):
        self.startDate = datetime(2021, 4, 2, 12, tzinfo=timezone.utc)
        self.timeLastPlayed = datetime.now(tz=timezone.utc)
        self.playDuration = timedelta()

    @property
    def playTimePerDay(self):
        """`timedelta`: The amount of time per day spent on the
        associated save slot.
        """
        return (
            self.playDuration/(self.timeLastPlayed - self.startDate).days
        )

    def fromSaveData(self, save, slot):
        """Sets the attributes of the calling instance to match the data
        contained in the given save data.

        Args:
            save (dict): A decrypted dictionary representation of the
                player's save file, as returned by the
                `legends.functions.decryptSaveFile` function.
            slot (int): The 0-based index of the save slot from which to
                read the time stamps.

        """
        self.startDate = datetime.fromtimestamp(
            save['{} data'.format(slot)]['createts'], tz=timezone.utc
        )
        try:
            self.timeLastPlayed = ticksToDatetime(
                int(save['{} timeLastPlayed'.format(slot)])
            )
            self.playDuration = ticksToTimedelta(
                int(save['{} playDuration'.format(slot)])
            )
        except KeyError:
            return
