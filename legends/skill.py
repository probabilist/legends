"""The `legends.skill.Skill` class and related objects.

"""

from legends.utils.functions import collapse
#pylint: disable-next=no-name-in-module
from legends.constants import GSEffect, GSEffectType, GSSkill, GSSkillUpgrade
from legends.constants import DESCRIPTIONS
from legends.functions import skillToMaxCost

__all__ = ['EffectChain', 'Skill', 'SkillEffect']

class EffectChain(list):
    """A list of linked of `SkillEffect` objects.

    Each object in the list, except the last, triggers the effect that
    appears after it on the list. The last effect on the list does not
    trigger any other effect.

    """
    def __init__(self, *args, **kargs):
        list.__init__(self, *args, **kargs)

    @property
    def damageEffects(self):
        """`list`: The sublist of effects that deal damage."""
        return [effect for effect in self if effect.doesDamage]

    @property
    def numHits(self):
        """`int`: The number of effects in the chain that deal damage.
        """
        return len(self.damageEffects)

    @property
    def damageType(self):
        """`str`: Either a stat name, 'Mixed', or `None`. If no effect
        in the chain deals damage, damage type is `None`. Otherwise,
        damage type is the common stat source of all damage-dealing
        effects in the chain. If there are multiple stat sources, damage
        type is 'Mixed'.
        """
        return collapse(effect.statSource for effect in self.damageEffects)

    @property
    def damageFrac(self):
        """`str`: Either a number between 0 and 1, 'Mixed', or `None`.
        If no effect in the chain deals damage, damage frac is `None`.
        Otherwise, damage frac is the common stat source fraction of all
        damage-dealing effects in the chain. If there are multiple stat
        source fractions, damage frac is 'Mixed'.
        """
        return collapse(effect.statSourceFrac for effect in self.damageEffects)

    def __repr__(self):
        return 'EffectChain({})'.format(list.__repr__(self))

class Skill():
    """A skill in STL.

    Attributes:
        skillID (str): The skill's ID, as it appears in `GSSkill`.
        level (int): The level of the skill.
        unlocked (bool): True if the character has unlocked this skill.
            Cannot be set False for skills that come with a newly
            summoned character.
        effects (list of SkillEffect): The effects that are applied when
            this skill is used.

    """
    def __init__(self, skillID, level=1, unlocked=False):
        self.skillID = skillID
        self.level = level
        self.unlocked = unlocked
        self._key = 'GSSkillKey(id = "{}", level = "{}")'.format(
            self.skillID, self.level
        )
        if self._key not in GSSkillUpgrade:
            self.unlocked = True
        self.effects = [
            SkillEffect(effectDict['effect'], effectDict['fraction'])
            for effectDict in self.data['effects']
        ]

    @property
    def name(self):
        """The in-game display name of the skill."""
        return DESCRIPTIONS[self.data['name']]

    @property
    def data(self):
        """`dict`: The skill data from `GSSkill`."""
        return GSSkill[self._key]

    @property
    def cooldown(self):
        """`int`: The skill's cooldown. Specifically, the number of
        turns for which the skill will be unavailable before next use.
        For example, a skill with cooldown 1 can be used every other
        turn.
        """
        return self.data['cooldown']

    @property
    def startingCooldown(self):
        """`int`: The skill's starting cooldown. Specifically, the
        number of initial turns for which the skill will be unavailable.
        For example, a skill with starting cooldown 2 can be used for
        the first time on the third turn.
        """
        return self.data['startingCooldown']

    @property
    def itemsToMax(self):
        """`legends.constants.Inventory`: The items needed to upgrade
        the skill to Level 2.
        """
        level = self.level if self.unlocked else 0
        return skillToMaxCost(self.skillID, level)

    def __repr__(self):
        return (
            '<Skill: ' + self.name + ', Level ' + str(self.level) + ', '
            + ('unlocked' if self.unlocked else 'locked') + '>'
        )

class SkillEffect():
    """A skill effect in STL.

    A skill effect consists of a raw effect and a fraction. Data on the
    raw effects can be found in `GSEffect`. The fraction is used to
    modify the intensity of the raw effect.

    Attributes:
        effectID (str): The effect ID, as found in `GSEffect`.
        fraction (float): The fraction of the effect applied.
        triggersEffect (SkillEffect): The skill effect which is
            immediately triggered after this effect has been applied.
            Can be `None`.

    """

    def __init__(self, effectID, fraction):
        if effectID not in GSEffect:
            raise KeyError('{} not recognized'.format(effectID))
        self.effectID = effectID
        self.fraction = fraction
        try:
            newEffectID = self.data['sequenceID']
            self.triggersEffect = SkillEffect(newEffectID, self.fraction)
        except KeyError:
            self.triggersEffect = None

    @property
    def data(self):
        """`dict`: The effect data from `GSEffect`."""
        return GSEffect[self.effectID]

    @property
    def statSource(self):
        """`str`: The name of the statistic that serves as the source of
        the effect.
        """
        return self.data['statSource']

    @property
    def statSourceFrac(self):
        """`float`: The proportion of the source statistic that is used
        for the effect.
        """
        return self.data['statSourceFraction']

    @property
    def effectType(self):
        """`type`: The effect's type, as found in the 'type' field in
        `GSEffectType`.
        """
        return GSEffectType[self.data['typeID']]['type']

    @property
    def doesDamage(self):
        """`bool`: True if the effect type is one that deals damage."""
        return self.effectType[:6] == 'Damage'

    @property
    def chain(self):
        """`EffectChain`: The chain of effects triggered by this effect.
        Includes this effect.
        """
        effectChain = EffectChain([self])
        while True:
            nextEffect = effectChain[-1].triggersEffect
            if nextEffect is None:
                break
            effectChain.append(nextEffect)
        return effectChain

    def __repr__(self):
        return '<SkillEffect: {!r}>'.format(self.effectID)
