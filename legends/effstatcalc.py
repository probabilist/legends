"""Tools used to calculate effective stats for characters.

"""

from legends.roster import Roster
from legends.stats import StatMods, ThreatStats

__all__ = ['EnemyChar', 'EnemyCharSettings']

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

        self.rounds = rounds

        self._statMods = StatMods()

        self.roster.onCharChange.subscribe(self.onCharChange)
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
        threat assessment. Must be a positive integer. Setting this
        property forces the parent `EnemyChar` instance to update its
        threat statistics.
        """
        return self._rounds

    @rounds.setter
    def rounds(self, value):
        if not isinstance(value, int) or value <= 0:
            raise ValueError('{!r} not a positive integer'.format(value))
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
            int or float: The modified value of the statistic.

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
