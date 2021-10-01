"""The `legends.saveslot.SaveSlot` class and related objects.

"""

from datetime import datetime, timedelta, timezone
from legends.utils.functions import ticksToDatetime, ticksToTimedelta
# pylint: disable-next=no-name-in-module
from legends.constants import (
    GSCharacter, GSMissionNodes, GSMissionRewards, GSMissions, GSNodeRewards
)
from legends.constants import DIFFICULTIES, Inventory, ITEMS
from legends.roster import Roster

__all__ = [
    'Mission',
    'MissionNode',
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
        nodes (list of MissionNode): The nodes in the mission.
        rewards (legends.constants.Inventory): The rewards earned from
            100% completion of the mission.
        complete (float): The proportion of the mission that has been
            completed.

    """
    def __init__(self, episode, orderIndex, difficulty):
        self.episode = episode
        self.orderIndex = orderIndex
        self.difficulty = difficulty
        self._key = 'episode {} mission {}-{}'.format(
            self.episode,
            self.orderIndex,
            DIFFICULTIES[self.difficulty]
        )
        self.nodes = []
        for nodeID in GSMissionNodes[
            'e{}_m{}'.format(self.episode, self.orderIndex)
        ]['Nodes']:
            self.nodes.append(MissionNode(nodeID, self.difficulty))
        try:
            initDict = GSMissionRewards['e{}_m{}_complete-{}'.format(
                self.episode, self.orderIndex, DIFFICULTIES[self.difficulty]
            )]['reward']['AllItems']
        except KeyError:
            initDict = {}
        self.rewards = Inventory(initDict)
        self.complete = 0

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
            (node.rewards for node in self.nodes if not node.complete),
            Inventory()
        )

    def __repr__(self):
        return 'Mission({!r})'.format(self._key)

class MissionNode(): # pylint: disable=too-few-public-methods
    """A mission node in STL.

    Attributes:
        nodeID (str): The node's ID as it appears in `GSMissionNodes`.
        difficulty (str): One of 'Normal', 'Advanced', or 'Expert'.
        rewards (legends.constants.Inventory): The rewards earned from
            completing this node.
        complete (bool): `True` if the node has been completed.

    """
    def __init__(self, nodeID, difficulty):
        self.nodeID = nodeID
        self.difficulty = difficulty
        try:
            initDict = GSNodeRewards['{}-{}'.format(
                self.nodeID, DIFFICULTIES[self.difficulty]
            )]['reward']['AllItems']
        except KeyError:
            initDict = {}
        self.rewards = Inventory(initDict)
        self.complete = False

    def __repr__(self):
        return 'MissionNode({!r})'.format(self.nodeID)

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
            for node in mission.nodes:
                try:
                    node.complete = data['nodes'][node.nodeID]['complete']
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
        self.timeLastPlayed = ticksToDatetime(
            int(save['{} timeLastPlayed'.format(slot)])
        )
        self.playDuration = ticksToTimedelta(
            int(save['{} playDuration'.format(slot)])
        )
