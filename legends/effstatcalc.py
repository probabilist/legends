# TODO: Make this auto-update on stat changes
# from legends.constants import STAT_ABBREVIATIONS

# class ThreatCalc():
#     """Used to calculate the threat posed by an enemy character.

#     Attributes:
#         char (legends.gameobjects.Character): The character being
#             considered.
#         roster (legends.roster.Roster): The roster to which the
#             character belongs.
#         rounds (int): The number of combat rounds used to calculate the
#             threat assessment.
#         multMods (legends.stats.Stats): A `legends.stats.Stats` object
#             that stores the multiplicative stat modifiers to be applied
#             to the character.
#         preAddMods (legends.stats.Stats): A `legends.stats.Stats` object
#             that stores additive stat modifiers to be applied to the
#             character. These modifiers are applied before the
#             multiplicative modifiers.
#         postAddMods (legends.stats.Stats): A `legends.stats.Stats`
#             object that stores additive stat modifiers to be applied to
#             the character. These modifiers are applied after the
#             multiplicative modifiers. Note: The attack up modifier from
#             an Amplify Force particle is applied after the `postAddMods`
#             modifiers.

#     """

#     def __init__(self, char, roster=None, rounds=3):
#         """The constructor sets the `char`, `roster`, and `rounds`
#         attributes using the given arguments. If no roster is given, a
#         new, empty roster is created and the given character is added to
#         it.

#         New `legends.stats.Stats` objects are created for the
#         multiplicative and additive modifiers. All multiplicative
#         modifiers default to 1; all additive modifiers default to 0.

#         """
#         self.char = char
#         self.roster = roster
#         if self.roster is None:
#             self.roster = Roster()
#             self.roster.chars[self.char.nameID] = self.char
#         self.rounds = rounds
#         self.multMods = Stats({statName: 1 for statName in STAT_ABBREVIATIONS})
#         self.preAddMods = Stats()
#         self.postAddMods = Stats()
#         self._data = {
#             'techChance': None,
#             'attDmg': None,
#             'techDmg': None
#         }

#     @property
#     def techChance(self):
#         return self._data['techChance']

#     @property
#     def attDmg(self):
#         return self._data['attDmg']

#     @property
#     def techDmg(self):
#         return self._data['techDmg']

#     def getStat(self, statName, firstRound=False):
#         stat = self.char.totalStats(self.roster).get(statName)
#         stat = (
#             (stat + self.preAddMods.get(statName))
#             * self.multMods.get(statName) + self.postAddMods.get(statName)
#         )
#         if firstRound and statName == 'Attack':
#             stat *= self.char.partEffects(self.roster).get('Attack Up')
#         return stat

#     def calculate(self):
#         cc = self.getStat('CritChance')
#         cd = self.getStat('CritDamage')
#         numHits = {'Attack': 0, 'Tech': 0}
#         dmg = {'Attack': 0, 'Tech': 0}
#         skillSequence = char.aiSkillOrder()
#         rounds = self.rounds
#         firstRound = True
#         while rounds > 0:
#             skill = next(skillSequence)
#             if 'Damage' not in skill.effectTags:
#                 continue
#             numTargets = 4 if skill.isAOE else skill.numTargets
#             effects = sum((effect.chain for effect in skill.effects), [])
#             effects = [effect for effect in effects if effect.doesDamage]
#             for effect in effects:
#                 numHits[effect.statSource] += 1
#                 dmg[effect.statSource] += (
#                     (numTargets/4)          # chance to be targeted
#                     * self.getStat(         # raw stat value
#                         effect.statSource,
#                         firstRound
#                     )
#                     * effect.fraction       # fractions determined
#                     * effect.statSourceFrac #   by skill effect
#                     * (1 + cc * (cd - 1)))  # effect of potential crits
#             firstRound = False
#             rounds -= 1
#         self._data['techChance'] = (
#             numHits['Tech'] / max( 1, sum(numHits.values()) )
#         )
#         self._data['attDmg'] = dmg['Attack']/max(1, numHits['Attack'])
#         self._data['techDmg'] = dmg['Tech']/max(1, numHits['Tech'])
