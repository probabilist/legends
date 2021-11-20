"""Tools used to calculate effective stats for characters.

"""

import itertools
from legends.utils.functions import formatDict
from legends.gameobjects import Particle
from legends.roster import Roster
from legends.stats import EffStats, StatMods, ThreatStats

__all__ = [
    'pvpMeta',
    'EffStatCalc',
    'EffStatSettings',
    'EnemyChar',
    'EnemyCharSettings'
]

def pvpMeta():
    """Builds and returns a list of enemy characters representing the
    current pvp meta (as of Nov 19, 2021), which is T'Pol, Garak,
    Tomalak, and Scotty.

    The enemy characters are given no gear and set to maximum level and
    rank. To maximize their damage threat, they are given level 5
    legendary amplify force particles with attack, tech, crit chance,
    and crit damage.

    It is assumed the average battle against these enemy characters will
    last 3 rounds.

    Returns:
        list of EnemyChar: The list of enemy characters in the pvp meta
            team.

    """
    # build roster of maxed meta characters with no gear
    nameIDs = ['TPol', 'Garak', 'Tomalak', 'Scott']
    roster = Roster()
    roster.fillChars(nameIDs, False)

    # add particles
    statNames = ['Attack', 'Tech', 'CritChance', 'CritDamage']
    for nameID, slotIndex in itertools.product(nameIDs, (0, 1)):
        part = Particle('Amplify Force', 'Legendary', 5)
        for index, statName in enumerate(statNames):
            part.setStatName(index, statName)
        roster.parts.append(part)
        roster.inPartSlot[part] = roster.chars[nameID].partSlots[slotIndex]

    # build and return enemy list
    enemyList = []
    for nameID in nameIDs:
        enemyList.append(EnemyChar(roster.chars[nameID], roster))
    return enemyList

class EnemyCharSettings():
    """Settings for an `EnemyChar` instance.

    """

    def __init__(self, parent, char, roster=None, rounds=3):
        """The constructor sets the `parent`, `char`, `roster`, and
        `rounds` properties to the given values. If no roster is given,
        a new, empty roster is created and the given character is added
        to it.

        """
        if roster is None:
            roster = Roster()
            roster.chars[char.nameID] = char

        self._parent = parent
        self._char = char
        self._roster = roster

        self._rounds = rounds

        self._statMods = StatMods()

        self.roster.charChangeWatcher.subscribe(self.onCharChange)
        self.statMods.onChange.subscribe(lambda event:self.parent.update())

    @property
    def parent(self):
        """`EnemyChar`: The `EnemyChar` instance to which these settings
        belong.
        """
        return self._parent

    @property
    def char(self):
        """`legends.gameobjects.Character`: The character associated
        with the parent `EnemyChar` instance.
        """
        return self._char

    @property
    def roster(self):
        """`legends.roster.Roster`: The roster to which the enemy
        character belongs.
        """
        return self._roster

    @property
    def rounds(self):
        """`int`: The number of combat rounds used to calculate the
        threat assessment. Should be a positive integer. Setting this
        property forces the parent `EnemyChar` instance to update its
        threat statistics.
        """
        return self._rounds

    @rounds.setter
    def rounds(self, value):
        self._rounds = value
        self.parent.update()

    @property
    def statMods(self):
        """`legends.stats.StatMods`: Stat modifiers to be applied to the
        enemy character. Defaults to a newly created instance of
        `legends.stats.StatMods`. This property cannot be set, but its
        value can be changed in place. Doing so forces the parent
        `EnemyChar` instance to update its threat statistics.
        """
        return self._statMods

    def onCharChange(self, charChangeEvent):
        """Triggered when the associated roster sends a
        `legends.roster.CharChangeEvent`. If it is the enemy character
        that changed, the parent `EnemyChar` instance is forced to
        update its threat statistics. Otherwise, nothing happens.

        Args:
            charChangeEvent (legends.roster.CharChangeEvent): The event
                sent by the associated roster.

        """
        if charChangeEvent.char is self.char:
            self.parent.update()

class EnemyChar():
    """Used to calculate the threat posed by an enemy character.

    Attributes:
        pauseUpdate (bool): Defaults to `False`. Set to `True` to
            prevent the `update` method from running.

    """

    def __init__(self, char, roster=None, rounds=3):
        """The constructor passes the given arguments to the
        `EnemyCharSettings` constructor and assigns the resulting
        `EnemyCharSettings` instance to the `settings` property.

        The `threatStats` property is assigned a new instance of
        `legends.stats.ThreatStats` and the `update` method is called.

        """
        self.pauseUpdate = False
        self._settings = EnemyCharSettings(self, char, roster, rounds)
        self._threatStats = ThreatStats()
        self.update()

    @property
    def settings(self):
        """`EnemyCharSettings`: The settings for this `EnemyChar`
        instance.
        """
        return self._settings

    @property
    def threatStats(self):
        """`legends.stats.ThreatStats`: The threat statistics for this
        `EnemyChar` instance. There are four threat statistics: 'Attack
        Hits Per Round', 'Tech Hits Per Round', 'Attack Damage Per
        Round', and 'Tech Damage Per Round'. Given a particular allied
        character, the value of 'Attack Hits Per Round' is the average
        number of times per round that the enemy character will do
        attack damage to the given allied character. The other threat
        statistics should be interpreted similarly.
        """
        return self._threatStats

    def getStat(self, statName, firstRound=False):
        """Fetches the value of the given statistic for the enemy
        character, modifies it according to the stat modifiers in the
        `settings` attribute, then modifies it, as needed, for any
        Amplify Force particles that may be equipped.

        Args:
            statName (str): One of the stat names in
                `STAT_ABBREVIATIONS`.
            firstRound (bool): If `True` and `statName` is 'Attack', the
                stat is modified by any Amplify Force particles that the
                enemy character may have equipped.

        Return:
            `int` or `float`: The modified value of the statistic.

        """
        char = self.settings.char
        roster = self.settings.roster
        stats = char.totalStats(roster)
        stat = self.settings.statMods.apply(stats).get(statName)
        if firstRound and statName == 'Attack':
            stat *= char.partEffects(roster).get('Attack Up')
        return stat

    def update(self):
        """Uses the current value of the `settings` property to update
        the `threatStats` property. Does nothing if `pauseUpdate` is
        set to `True`.

        """
        # pylint: disable=invalid-name
        if self.pauseUpdate:
            return
        cc = self.getStat('CritChance')
        cd = self.getStat('CritDamage')
        numHits = {'Attack': 0, 'Tech': 0}
        dmg = {'Attack': 0, 'Tech': 0}
        skillSequence = self.settings.char.aiSkillOrder()
        rounds = self.settings.rounds
        firstRound = True
        while rounds > 0:
            skill = next(skillSequence)
            if 'Damage' not in skill.effectTags:
                continue
            numTargets = 4 if skill.isAOE else skill.numTargets
            effects = sum((effect.chain for effect in skill.effects), [])
            effects = [effect for effect in effects if effect.doesDamage]
            for effect in effects:
                numHits[effect.statSource] += 1
                dmg[effect.statSource] += (
                    (numTargets/4)          # chance to be targeted
                    * self.getStat(         # raw stat value
                        effect.statSource,
                        firstRound
                    )
                    * effect.fraction       # fractions determined
                    * effect.statSourceFrac #   by skill effect
                    * (1 + cc * (cd - 1))   # effect of potential crits
                )
            firstRound = False
            rounds -= 1
        self.threatStats.update({
            'Attack Hits Per Round': numHits['Attack'] / self.settings.rounds,
            'Tech Hits Per Round': numHits['Tech'] / self.settings.rounds,
            'Attack Damage Per Round': dmg['Attack'] / self.settings.rounds,
            'Tech Damage Per Round': dmg['Tech'] / self.settings.rounds
        })

class EffStatSettings():
    """Setting for an `EffStatCalc` instance.

    There are no default settings. Users must instantiate each setting.

    """

    def __init__(self, parent):
        self._parent = parent
        self._settings = {
            'attDmg': None,
            'techDmg': None,
            'techChance': None,
            'cloak': None,
            'undoDmgRounds': None,
            'ampForceRounds': None
        }
        self._statMods = StatMods()
        self._statMods.onChange.subscribe(self.updateParent)

    @property
    def parent(self):
        """`EffStatCalc`: The `EffStatCalc` instance to which these
        settings belong.
        """
        return self._parent

    @property
    def ready(self):
        """`bool`: True if all settings (attack damage, tech damage,
        cloak, undo damage rounds, and amp force rounds) have been set.
        """
        return not any(
            getattr(self, attrName) is None
            for attrName in [
                'attDmg', 'techDmg', 'techChance',
                'cloak', 'undoDmgRounds', 'ampForceRounds'
            ]
        )

    @property
    def attDmg(self):
        """`float`: The average incoming attack damage delivered by
        enemy attack hits that do not glance. Setting this property
        triggers the `EffStatSettings.updateParent` method.
        """
        return self._settings['attDmg']

    @attDmg.setter
    def attDmg(self, value):
        self._settings['attDmg'] = value
        self.updateParent()

    @property
    def techDmg(self):
        """`float`: The average incoming tech damage delivered by enemy
        tech hits that do not glance. Setting this property triggers the
        `EffStatSettings.updateParent` method.
        """
        return self._settings['techDmg']

    @techDmg.setter
    def techDmg(self, value):
        self._settings['techDmg'] = value
        self.updateParent()

    @property
    def techChance(self):
        """`float`: The proportion of all incoming enemy hits that
        deliver tech damage. Setting this property triggers the
        `EffStatSettings.updateParent` method.
        """
        return self._settings['techChance']

    @techChance.setter
    def techChance(self, value):
        self._settings['techChance'] = value
        self.updateParent()

    @property
    def cloak(self):
        """`float`: The proportion of turns during which the character
        is cloaked. Setting this property triggers the
        `EffStatSettings.updateParent` method.
        """
        return self._settings['cloak']

    @cloak.setter
    def cloak(self, value):
        self._settings['cloak'] = value
        self.updateParent()

    @property
    def undoDmgRounds(self):
        """`float`: The expected number of regenerations triggered by
        any Undo Damage particles that might be equipped. Should be a
        number between 0 and 2. Setting this property triggers the
        `EffStatSettings.updateParent` method.
        """
        return self._settings['undoDmgRounds']

    @undoDmgRounds.setter
    def undoDmgRounds(self, value):
        self._settings['undoDmgRounds'] = value
        self.updateParent()

    @property
    def ampForceRounds(self):
        """`float`: The proportion of rounds during which the character
        will receive the benefit of any Amplify Force particles that may
        be equipped. Should be a number between 0 and 1. Setting this
        property triggers the `EffStatSettings.updateParent` method.
        """
        return self._settings['ampForceRounds']

    @ampForceRounds.setter
    def ampForceRounds(self, value):
        self._settings['ampForceRounds'] = value
        self.updateParent()

    @property
    def statMods(self):
        """`legends.stats.StatMods`: Stat modifiers to be applied to the
        allied character. Modifying any of the stat modifiers triggers
        the `EffStatSettings.updateParent` method.
        """
        return self._statMods

    def updateParent(self):
        """If the `ready` property is `True`, causes the parent
        `EffStatCalc` instance to recalculate all effective stats in its
        underlying data dictionary. Otherwise, does nothing.
        """
        if self.ready:
            self.parent.updateAll()

    def fromEnemies(self, *enemyChars):
        """Sets the `attDmg`, `techDmg`, and `techChance` properties
        using the given enemy characters.

        Args:
            enemyChars (list of EnemyChar): The enemy characters from
                which to derive the property values.

        """
        threatStats = sum(
            (enemyChar.threatStats for enemyChar in enemyChars), ThreatStats()
        )
        self.attDmg = (
            0 if threatStats.attHits == 0 else
            threatStats.attDmg / threatStats.attHits
        )
        self.techDmg = (
            0 if threatStats.techHits == 0 else
            threatStats.techDmg / threatStats.techHits
        )
        totalHits = threatStats.attHits + threatStats.techHits
        self.techChance = (
            0.5 if totalHits == 0 else
            threatStats.techHits / totalHits
        )

    def __repr__(self):
        return 'EffStatSettings({})'.format(formatDict(self._settings))

class EffStatCalc():
    """Calculates effective stats for an allied character.

    There are three effective stats used in this package.

    'Effective Attack Damage' is the average amount of attack damage
    done by the allied character. Crit chance and crit damage are
    accounted for, as well as any particles and modifiers included in
    the `settings` property.

    'Effective Tech Damage' is similar, but for tech damage.

    'Effective Health' is a measure of the character's survivability
    that takes into account nexus shields, defense, tech defense,
    glancing chance, and glancing damage. Effective health is
    characterized as follows. A character whose health equals the
    effective health and who has no nexus shields, 0 defense, 0 tech
    defense, and 0% glancing chance would survive, on average, the same
    number of hits as the given character.

    An effective stat calculator must be assigned to a roster and can
    only be used on characters in that roster.

    The `settings` property is used to access the `EffStatSettings`
    instance associated with the calculator. Since the attributes of
    `EffStatSettings` instances have no default values, client objects
    must set these attributes before using the calculator. Failing to do
    so will raise an error.

    """

    def __init__(self, roster):
        """The constructor assigns the constructed instance to the given
        roster, subscribes to the roster's `charChangeWatcher` event
        handler with the `EffStatCalc.onCharChange` method, and sets the
        `roster` property accordingly.

        """
        self._settings = EffStatSettings(self)
        self._roster = roster
        self._roster.charChangeWatcher.subscribe(self.onCharChange)
        self._data = {}

    @property
    def settings(self):
        """`EffStatSettings`: The settings for this `EffStatCalc`
        instance.
        """
        return self._settings

    @property
    def roster(self):
        """`legends.roster.Roster`: The roster to which this effective
        stat calculator belongs.
        """
        return self._roster

    @property
    def data(self):
        """`dict`: {`str`:`legends.stats.EffStats`} A dictionary
        mapping name IDs of characters in the roster to their
        effective stats. To avoid unnecessarily repeating calculations,
        calculation results are stored in a private dictionary for
        retrieval. This is a copy of that dictionary. The underlying
        data dictionary should not be changed directly. Event handlers
        are used to modify the underlying data when needed.
        """
        return self._data.copy()

    def get(self, char):
        """Returns the effective stats for the given character. Looks
        them up in the underlying database, if they exist. Otherwise,
        computes them.

        Args:
            char (legends.gameobjects.Character): The character whose
                effective stats to calculate. Should belong to the
                instance's associated roster.

        Returns:
            legends.stats.EffStats: The character's effective stats.

        """
        if char.nameID not in self._data:
            self._data[char.nameID] = EffStats()
            self._data[char.nameID].update(self.calculate(char))
        return self._data[char.nameID]

    def update(self, char):
        """Recalculates the effective stats for the given character and
        updates their data in the underlying dictionary.

        Args:
            char (legends.gameobjects.Character): The character whose
                effective stats to calculate. Should belong to the
                instance's associated roster.

        """
        self._data[char.nameID].update(self.calculate(char))

    def updateAll(self):
        """Recalculates the effective stats for all characters in the
        underlying data dictionary.

        """
        for nameID in self._data:
            self.update(self.roster.chars[nameID])

    def calculate(self, char):
        """Calculates the effective stats for the given character and
        returns them as a stat dictionary.

        Args:
            char (legends.gameobjects.Character): The character whose
                effective stats to calculate. Should belong to the
                instance's associated roster.

        Returns:
            dict: {`str`:`float`} A dictionary mapping effective stat
                names, as they appear in `EFF_STATS` to their values.

        Raises:
            ValueError: If any settings attributes have not yet been
                instantiated. (See `EffStatSettings.ready`.)

        """
        if not self.settings.ready:
            raise ValueError(
                'Effective stat calculator settings not fully instantiated.'
            )
        statDict = {}

        # get stats and particle effects
        stats = char.totalStats(self.roster)
        stats = self.settings.statMods.apply(stats)
        partEffects = char.partEffects(self.roster)

        # compute effective attack and tech damage
        stats.att *= 1 + partEffects.attUp * self.settings.ampForceRounds
        critFactor = stats.cc * stats.cd + (1 - stats.cc)
        statDict['Effective Attack Damage'] = stats.att * critFactor
        statDict['Effective Tech Damage'] = stats.tech * critFactor

        # adjust health and gc for nexus shields, undo damage, and cloak
        stats.hlth = (
            stats.hlth
            + partEffects.shield * stats.tech
            + partEffects.regen * stats.hlth * self.settings.undoDmgRounds
        )
        stats.gc = self.settings.cloak + (1 - self.settings.cloak) * stats.gc

        # compute average incoming damage per hit
        dmg = (
            self.settings.techChance * self.settings.techDmg
            + (1 - self.settings.techChance) * self.settings.attDmg
        )

        # compute reduced incoming attack damage per hit
        reducedAttDmg = (
            (1 - stats.gc) * max(
                self.settings.attDmg - stats.dfn, 1
            )
            + stats.gc * max(
                (1 - stats.gd) * self.settings.attDmg - stats.dfn, 1
            )
        )

        # compute reduced incoming tech damage per hit
        reducedTechDmg = (
            (1 - stats.gc) * max(
                self.settings.techDmg - 0.38 * stats.tech, 1
            )
            + stats.gc * max(
                (1 - stats.gd) * self.settings.techDmg - 0.38 * stats.dfn, 1
            )
        )

        # compute average reduced incoming damage per hit
        reducedDmg = (
            self.settings.techChance * reducedTechDmg
            + (1 - self.settings.techChance) * reducedAttDmg
        )

        # compute effective health and return stat dict
        numHits = stats.hlth / reducedDmg   # number of hits until death
        statDict['Effective Health'] = numHits * dmg  # effective health
        return statDict

    def onCharChange(self, charChangeEvent):
        """Recalculates effective stats when a character is modified.

        Args:
            charChangeEvent (legends.roster.CharChangeEvent): The event
                sent by the assigned roster's `charChangeWatcher` event
                handler.

        """
        if charChangeEvent.char.nameID in self._data:
            self.update(charChangeEvent.char)
