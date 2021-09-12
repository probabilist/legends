# Change log

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