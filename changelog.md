# Change log

## Version 0.5.1

* Added a new base class, `ModalDialog`, which is a subclass of `tkinter.simpledialog.Dialog` that disables root menus while the dialog is open.
* Rewrote the `AskSlot` class as a subclass of `ModalDialog`, and rewrote the `askSlot` function to better mimic the analogous functions in the `tkinter.simpledialog` module.
* Added missing items to `__all__` list in the following modules: `constants`, `dialogs`, `rostertab`, `stlplanner`.
* Edited "legends/__init__.py" to reflect new `roster` module.

## Version 0.5.0

* Menu options were not being automatically disabled when modal dialog windows would appear. Made a number of changes to correct this.
    - Added `disableOnModal` attribute and `setMenuState` method to the `STLPlanner` class.
    - Restructured `StartFrame` and `RosterTab` constructor to receive the `STLPlanner` instance.
    - Edited all objects in `dialogs` module, and included custom versions of `showerror` and `showinfo`.
    - Edited references to dialogs to account for these changes.
* Removed all attributes of `SaveSlot` that reference the actual raw data from the save slot. This was necessary in order to allow for virtual save slots, such as one composed of maxed characters. The following changes relate to this:
    - Added an `STLTimeStamps` class to store and manage timestamp data. Consolidated timestamp-related properties in `SaveSlot` class into an instance of `STLTimeStamps`.
    - Restructured `SaveSlot` constructor to build an empty instance if no slot is passed.
    - Moved `Roster` class to its own module, `roster`.
    - The `SaveSlot` instance no longer populates the roster with gear, particles, and characters. This is now handled by the `Roster` instance.
    - Moved the `readGear` and `readParts` methods from the `SaveSlot` class to the `roster` module, and made them functions.
    - Moved the `readChars` method from the `SaveSlot` class to the the `Roster` class, making it part of the new `fromSaveData` method.
    - Deleted an error where the old `SaveSlot.readChars` method was adding a `tokens` attribute to character instances.
    - Converted `gear` and `parts` attributes of `Roster` class from dictionaries to lists, so that `Roster` class no longer stores the arbitrary gear and particle ID numbers from the save file.
    - Added a `clear` method to the `Roster` class.
    - Added a `fillChars` method to the `Roster` class that adds missing characters.
* Changed the stat initial of Resolve from 'RES' to 'R'.
* Edited the `CharCard` class for improved visual display.
* Added `makeMax` method to `StartFrame` class, and a corresponding button.
* Fixed an error that incorrectly calculated the number of tokens needed for a character to rank up.
* Added the ability to sort characters by name.

## Version 0.4.1

* Adjusted character cards in roster view for more consistent alignment of text.
* Added a character count to the info bar at the bottom of the roster view.
* Completely rewrote the README file for clarity, and added a screenshot.
* Added the constant, `ENABLED`, that lists all characters in the Crew screen.
* Added the constant `UPCOMING`, that lists all characters believed to be intended for future release.
* Manually edited `GSCharacter` to enable Garak and Shinzon. (Can remove this manual edit when and if current hotfix data becomes accessible again.)

## Version 0.4.0

* The character cards now show (and can be sorted by) the following stats: missing gear levels, missing gear ranks, missing skill levels.
* Added a 'Stat glossary' button that pops up an information dialog.
* Added `STAT_INITIALS` to the `constants` module.
* Added `rarity` and `rarityIndex` properties to the `Gear` class.
* Added `maxGearLevel` and `missingSkillLevels` properties to the `Character` class.
* Added `missingGearLevels` and `missingGearRanks` methods to the `Roster` class.

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