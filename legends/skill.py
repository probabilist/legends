"""The `legends.skill.Skill` class and related objects.

"""

from warnings import warn
from legends.utils.functions import camelToSpace, collapse
from legends.utils.htmltagstripper import HTMLTagStripper
#pylint: disable-next=no-name-in-module
from legends.constants import GSEffect, GSEffectType, GSSkill, GSSkillUpgrade
from legends.constants import DESCRIPTIONS
from legends.functions import skillToMaxCost

__all__ = ['BridgeSkill', 'EffectChain', 'Skill', 'SkillEffect']

class EffectChain(list):
    """A list of linked `SkillEffect` objects.

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

    @property
    def effectTags(self):
        """`list` of `str`: A list of all tags on skill effects in this
        chain.
        """
        tags = []
        for effect in self:
            tags.extend(effect.effectTags)
        return tags

    def __repr__(self):
        return 'EffectChain({})'.format(list.__repr__(self))

class Skill():
    """A skill in STL.

    Attributes:
        skillID (str): The skill's ID, as it appears in `GSSkill`.
        level (int): The level of the skill.
        unlocked (bool): True if the character has unlocked this skill.
        casterEffect (SkillEffect): The caster effect that is applied
            when this skill is used.
        effects (list of SkillEffect): The effects that are applied when
            this skill is used. Does not include the caster effect.

    """

    def __init__(self, skillID, level=1, unlocked=False):
        self.skillID = skillID
        self.level = level
        self.unlocked = unlocked
        self._key = 'GSSkillKey(id = "{}", level = "{}")'.format(
            self.skillID, self.level
        )
        self.effects = [
            SkillEffect(effectDict['effect'], effectDict['fraction'])
            for effectDict in self.data['effects']
        ]
        self.casterEffect = None
        casterEffect = self.data['casterEffect']
        if 'effect' in casterEffect:
            self.casterEffect = SkillEffect(
                casterEffect['effect'], casterEffect['fraction']
            )
        if len(self.effects) == 0 and self.casterEffect is None:
            warn('Skill ID {} has no effects'.format(self.skillID))

    @property
    def name(self):
        """The in-game display name of the skill."""
        return DESCRIPTIONS[self.data['name']]

    @property
    def data(self):
        """`dict`: The skill data from `GSSkill`."""
        return GSSkill[self._key]

    @property
    def startWith(self):
        """`bool`: `True` if the character starts with this skill."""
        return self._key not in GSSkillUpgrade

    @property
    def description(self):
        """The in-game description of the skill."""
        return HTMLTagStripper(DESCRIPTIONS[self.data['description']]).text

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
    def timing(self):
        """`str`: One of 'basic', 'r1', 'r2', or 'r3', describing,
        respectively, whether the skill is a basic attack (cooldown 0),
        a Round 1 skill (positive cooldown, starting cooldown 0), a
        Round 2 skill (positive cooldown, starting cooldown 1), or a
        skill available in Round 3 or later (positive cooldown, starting
        cooldown at least 2).
        """
        if self.cooldown == 0:
            return 'basic'
        if self.startingCooldown == 0:
            return 'r1'
        if self.startingCooldown == 1:
            return 'r2'
        return 'r3'

    @property
    def isAOE(self):
        """`bool`: `True` if the skill is AOE."""
        return self.data['isAOE']

    @property
    def isMultiRandom(self):
        """`bool`: `True` if the skill has multiple random targets."""
        return self.data['isMultiRandom']

    @property
    def numTargets(self):
        """`int`: The number of targets for this skill."""
        return self.data['numTargets']

    @property
    def effectTags(self):
        """`list` of `str`: A list of all tags on skill effects produced
        by this skill, including the caster effect.
        """
        effTags = []
        for effect in self.effects:
            effTags.extend(effect.chain.effectTags)
        if self.casterEffect is not None:
            effTags.extend(self.casterEffect.chain.effectTags)
        return sorted(list(set(effTags)))

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
            try:
                newEffectID = self.data['effectID']
                self.triggersEffect = SkillEffect(newEffectID, self.fraction)
            except KeyError:
                self.triggersEffect = None

    @property
    def data(self):
        """`dict`: The effect data from `GSEffect`."""
        return GSEffect[self.effectID]

    @property
    def description(self):
        """`str`: A plain text description of the effect."""
        return '{} ({:g}x)'.format(self.effectID, self.fraction)

    @property
    def statAffected(self):
        """`str`: The name of the statistic that is affected by this
        effect.
        """
        stat = self.data['statAffected']
        return None if stat == 'None' else stat

    @property
    def statSource(self):
        """`str`: The name of the statistic that serves as the source of
        the effect.
        """
        stat = self.data['statSource']
        return None if stat == 'None' else stat

    @property
    def statSourceFrac(self):
        """`float`: The proportion of the source statistic that is used
        for the effect.
        """
        return self.data['statSourceFraction']

    @property
    def tagAffected(self):
        """`str`: The character tag affected by this skill, if the skill
        is restricted to a particular character tag. Otherwise, `None`.
        """
        tag = self.data['property']
        return None if tag == '' else tag

    @property
    def resistanceType(self):
        """`str`: If the skill offers a chance to resist a detrimental
        effect, this is the effect. Otherwise, `None`.
        """
        typ = self.data['resistanceType']
        return None if typ == 'None' else typ

    @property
    def chanceToResist(self):
        """`str`: If the skill offers a chance to resist a detrimental
        effect, this is the probability. Otherwise, 0.
        """
        return self.data['chanceToResist']

    @property
    def effectType(self):
        """`str`: The effect's type, as found in the 'type' field in
        `GSEffectType`, with one exception. The value,
        'DamegeCoverBreakBonusEffect', which is found in `GSEffectType`,
        is changed to 'DamageCoverBreakBonusEffect'.
        """
        effectType =  GSEffectType[self.data['typeID']]['type']
        if effectType == 'DamegeCoverBreakBonusEffect':
            effectType = 'DamageCoverBreakBonusEffect'
        return effectType

    @property
    def effectTags(self):
        """`list` of `str`: The effect type is modified from camel case
        to have spaces inserted, then added as a tag. If the skill does
        damage, it also gets the 'Damage' tag, if it doesn't already
        have it, as well as either a 'Damage (Attack)' or 'Damage
        (Tech)' tag. If the effect type is 'Placeholder', it is ignored
        and not added as a tag.
        """
        tags = (
            [camelToSpace(self.effectType)]
            if self.effectType != 'Placeholder' else []
        )
        if self.doesDamage:
            tags.append('Damage ({})'.format(self.statSource))
            if 'Damage' not in tags:
                tags.append('Damage')
        return tags

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

class BridgeSkill(Skill):
    """A bridge skill in STL.

    Bridge skills are passive skills that offer increased stats,
    sometimes only to particular factions, or increased chance to resist
    detrimental effects.

    """

    def __init__(self, skillID):
        """Bridge skills are created unlocked.

        """
        Skill.__init__(self, skillID, unlocked=True)

    @property
    def tagAffected(self):
        """`str`: If the skill only applies to a certain character tag,
        this is that tag, otherwise `None`.
        """
        return self.effects[0].tagAffected

    @property
    def effect(self):
        """`SkillEffect`: The primary effect of the skill. (In the game
        assets, the primary effect is not always the first effect in the
        effect's chain. For a bridge skill that applies only to a
        certain faction, the first effect is to check the faction. The
        second effect is the primary effect.)
        """
        return (
            self.effects[0] if self.tagAffected is None
            else self.effects[0].chain[1]
        )
