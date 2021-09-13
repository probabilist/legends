# Change log

## Version 0.3.0

* Added the constants `SUMMON_POOL` and `SUMMON_POOL_IDS`.
* Edited the README instructions for launching the app interactively. It now suggests to use `STLPlanner()` instead of `STLPlanner().mainloop()`. There is no need to call `mainloop()` interactively, and omitting it allows you to do interactive testing while the app is running.
* Corrected a typo in the change log for version 0.2.0. (It failed to mention that Resolve was added to character cards.)

## Version 0.2.0

* Changes made to the `rostertab` module:
    - Added the 11 basic stats (Health, Attack, Speed, Defense, Tech, Crit Chance, Crit Damage, Glancing Chance, Glancing Damage, Resolve, and Power) to the character cards.
    - Characters can now be sorted by stats.
    - Added total roster power to the info bar at the bottom.
    - Added a tip to the user about toggling favorites.
    - Reduced the number of columns to 5 to account for wider character cards.
    - Character cards now have fixed dimensions for more consistency when filtering.
    - Added a `roster` argument to the `RosterTab.makeStats` method to allow for the computing of total power; modified its use in the `RosterTab.fillCards` method.
* Added the constant, `PART_STAT_UNLOCKED`, that stores the number of unlocked stats on a particle by rarity and level.
* Added a `get` method to the `Stats` class to allow for stat retrieval by stat name.
* Changed the binding in the `ScrollFrame` class, so that the mouse wheel will only control one object at a time. (As it was, it was controlling both the roster tab and the sorting combobox simultaneously.)
* Added a `numStats` property to the `Particle` class that returns the number of unlocked stats on the particle.
* Modified the `Particle.updateStats` method to account of the `numStats` property.

## Version 0.1.0

* Added the constant, `PART_STAT_VALUES`, that stores the stat values of particles according to their rarity and level.
* Added the following functions to the `gameobjects` module: `xpFromLevel`, `getCharStats`, `getGearStats`, `getPartStats`.
* Made the following changes to the `Gear` class:
    - Added a `stats` attribute and an `updateStats` method.
    - Changed the `level` attribute to a property, and coded its setter to call the `updateStats` method.
* Made the following changes to the `Particle` class:
    - Added a `stats` attribute and an `updateStats` method.
    - Changed the `level` attribute to a property, and coded its setter to call the `updateStats` method.
    - Changed the `statNames` attribute to a read-only property, and added a `setStatName` method to modify it. The `setStatName` method also calls the `updateStats` method.
* Made the following changes to the `Character` class:
    - Added a `stats` attribute and an `updateStats` method. The stats attribute contains only the character's "naked" stats.
    - Consolidated the `nameID`, `rank`, and `xp` attributes into a private `_data` attribute; these attributes are now properties. The `rank` and `xp` setters call the `updateStats` method.
    - Added a setter to the `level` property. Changing the level changes the `xp` value to the minimum possible xp to achieve that level.
* Added a `charStats` method to the `Roster` class that computes characters' total stats (including gear and particles).
* Added a missing docstring to the `SaveSlot` class constructor.
* Modified the `SaveSlot.readParts` method to account for the new `Particle.setStatName` setter method.
* Modified the `StatObject.__repr__` method to remove ambiguity between a `StatObject` instance and a dictionary.
* Fixed a fatal error in the `Stats` class constructor.

## Version 0.0.3

* Added numbering to the README.

## Version 0.0.2

* Added a download link to the README.

## Version 0.0.1

* Initial build. A rudimentary incarnation of what will eventually become a full-featured app that can help manage and optimize all of your Star Trek: Legends data. See the README file for more details.