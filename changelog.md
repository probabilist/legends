# Change log

## Version 0.26.2

* Dax added to summon pool.
* `BRIDGE_STATIONS` sorted alphabetically.
* Added `EFF_STATS` constant.
* Corrected bug in `StatMods` constructor that instantiated multiplicative mods as 0's.
* Added `EffStats` class.
* Corrected bugs in `EnemyCharSettings` constructor.
* Added `EffStatCalc` class, which is the effective stat calculator.
* Added `EffStatSettings` class, which holds the settings for an effective stat calculator.
* Added `pvpMeta` function, which sets the settings to correspond to the current pvp meta.
* Changes to underlying game data:
    - Dax added to store.
    - Bashir added to character list, but with no stats or skills.

## Version 0.26.1

* Added a `THREAT_STATS` constant.
* Added `StatMods` and `ThreatStats` classes.
* Added a `statObj` attribute to the `StatChangeEvent` class.
* Added an `effstatcalc` module with two classes: `EnemyChar` and `EnemyCharSettings`.

## Version 0.26.0

* Added a `CharChangeEvent` class.
* Added a `CharChangeWatcher` class.
* Changed the `Roster` constructor so that it does not subscribe to any event handlers.
* Added a `Roster.charChangeWatcher` attribute.
* Deleted the unused `Roster.onCharChange` attribute.
* Deleted the `Roster.charChangeWatcher()` placeholder method.

## Version 0.25.0

* Replaced the `callback` attribute of `WatchedCollection` with a `_subscribers` attribute that contains a list of callbacks; eliminated the `callback` argument from the constructor; edited `WatchedCollection` methods to subscribe and unsubscribe from all callbacks in the `_subscribers` attribute; edited `WatchedList`, `WatchedDict`, and `Roster` to accommodate these changes.
* Added `values`, `subscribe`, and `unsubscribe` methods to `WatchedCollection`; edited `WatchedList`, `WatchedDict`, and `Roster` to accommodate these changes.
* Replaced `attrName`, `oldVal`, and `newVal` attributes in `StatChangeEvent` with a single `oldStats` attribute.
* Added `oldStats` and `asDict` properties to the `StatObject` class.
* Added a `StatObject.notify()` method and edited the `__setattr__` method accordingly.
* Edited the `StatObject.update()` method to send a single `StatChangeEvent` at the end of the update.

## Version 0.24.0

* Eliminated the `maxGearLevel` and `tokensNeeded` properties of the `Character` class. Made changes throughout the package to adjust for this. (The `Character` class had grown too large and needed to be simplified.)
* Edited the `WatchedOneToOne` class so that changes trigger the event handler of both itself and its inverse. Client classes now need only subscribe to one event handler.
* Fixed an error in `SaveSlot.sort()` that prevented sorting when the method tried to set the now read-only `Roster.chars` property.

## Version 0.23.0

* Edited `AskRosterFilter` to add spaces in character tags that are expressed in camel case.
* Added `objDict` function to `utils` module.
* Added the `eventhandler` module.
* Changed the `stats` attributes of `Character`, `Gear`, and `Particle` to read-only properties.
* Added a `StatChangeEvent` class.
* Changed the `StatObject.statAbbrs` from an attribute pointing to an iterable to a read-only property pointing to a dict.
* Changed the `StatObject` constructor signature.
* Added `silent`, `onChange`, and `parent` attributes to `StatObject`.
* Customized the `StatObject.__setattr__()` method to create a `StatChangeEvent` upon attribute assignment to any stat, and to notify the subscribers of its `onChange` attribute.
* Added a `checkForStats` function to the `stats` module.
* Added a `OneToOneChangeEvent` class to the `roster` module.
* Added `WatchedOneToOne`, `WatchedCollection`, `WatchedList`, and `WatchedDict` classes to the `roster` module.
* Changed the `InGearSlot` class to inherit from `WatchedOneToOne`.
* Changed the `gear`, `parts`, and `chars` attributes of `Roster` to read-only properties, and edited `Roster.fromSaveData` accordingly.
* Added a `Roster.charChangeWatcher()` placeholder method.
* Edited the `Roster` constructor to initialize `gear`, `parts`, `chars`, `inGearSlot`, and `inPartSlot` as instances of the watched version of their previous data type, with the `charChangeWatcher()` method sent as argument.

## Version 0.22.1

* Data updated for hotfix 8172.
    - Important changes:
        + Old Picard replaced by Elnor in `GSBattleEnemy`.
        + Tuvok added to summon pool and store.
        + Guinan and Number One added to `GSCharacter`.
        + Set Dax event to start Nov 1, 8:00 AM UTC.
        + Added Gowron event to start Nov 15, 8:00 AM UTC.
    - Effects on `legends` constants:
        + 'ElAurian' added to `CHARACTER_TAGS`.
        + `DESCRIPTIONS` updated from hotfix 8172.
        + 'Gowron' and 'JadziaDax' added to `ENABLED`.
        + `SUMMON_POOL` updated to account for the addition of Tuvok.
* 'Guinan' and 'NumberOne' added to `UPCOMING`.
* The `Character.shortName` property modified to use the short name, 'Number One'.
* Additional changes:
    - Max character spreadsheet updated.
    - Web page of skill data updated.
    - Bridge buff worksheet updated.

## Version 0.22.0

* Added a `PART_EFFECTS` constant.
* Fixed a bug in the `decompressData` function that could prevent the app from importing player data.
* Replaced the `Roster.charStats()` method with `Character.totalStats()`; modified `CharCard` and `RosterTab` accordingly.
* Added a `Character.partEffects()` method.
* Changes to `Particle` class:
    - Converted `typ` and `rarity` attributes to read-only properties.
    - Added `passive` and `effects` attributes.
    - Added a `data` property.
* Subclasses of `StatObject` now support the multiplication operator.
* Added a `Stats.set()` method.
* Added a `PartEffects` subclass of `StatObject`.
* `CharTab.makeGearCardFrame()` now uses `winfo_reqheight()` and `winfo_reqwidth()` instead of `winfo_height()` and `winfo_width()`, so that the test card does not need to be packed.
* Fixed a bug in `stlplannerapp.spec` that was affecting Windows builds, and also reformatted the file for improved readability.
* Added `InGearSlot` class with an `enforceLevel` Boolean attribute.
* Modified `Roster.fromSaveData()` to allow gear whose level exceeds the character level. Now raises a warning instead of an exception.

## Version 0.21.0

* Added a `timing` property to the `Skill` class, indicating if the skill is 'basic', 'r1', 'r2', or 'r3'.
* Added a `timing` argument to `Character.skillEffectTags()` to allow for restricting the tags to skills whose cooldowns and starting cooldowns match certain criteria.
* Added a 'Cooldowns...' button to the `AskRosterFilter` dialog.
* Added `AskRosterFilter.setCooldowns()`.
* Added an `AskSkillTimings` class.
* Added a `skillTimings` attribute to the `RosterFilter` class; modified `RosterFilter.set()`, `RosterFilter.dictify()`, and `Session.checkFilter()` accordingly.

## Version 0.20.0

* Added a Windows version of the app icon.
* Edited 'stlplannerapp.spec' to check the operating system and choose the appropriate icon.
* Imported data changes from recent game updates.
* Modified `Session.makeTimeBar` to work as expected in both macOS, Windows, and Linux.
* Modified the `Roster.fillChars()` method to max all skills on added characters.
* Added the function, `getBasicGearID`.
* Added the `Gear.itemsToMax()` method.
* Added the `Character.itemsToMaxGear()` method.
* Added the `name`, `displayLevel`, and `role` properties to the `Gear` class.
* Moved the `checkFilter` method from `RosterTab` to `Session`.
* Added the `Session.charList` property and modified `RosterTab.fillCards()` to use it.
* Modified the `InventoryScreen` dialog to show materials needed to max all gear.
* Added `nextChar` and `prevChar` methods to the `Session` class.
* Added the `displaySkill` function to the `chartab` module.
* Added the `GearCard` class to the `chartab` module.
* Centered the action bar of the character tab and added 'next' and 'prev' buttons.
* Added character role to the character tab.
* Added gear information to the character tab.
* Added the `CharTab.roster` property.
* Added `makeGearCardFrame` and `makeGearUpgradeFrame` to the `CharTab` class.

## Version 0.19.4

* Edited character card sizing and packing to account for different operating systems.

## Version 0.19.3

* Added a `BRIDGE_STATIONS` constant.
* Added a `bridgeSkill` attribute to the `Character` class.
* Added a `bridgeStations` property to the `Character` class.
* Added a console warning when a skill is created without effects.
* Added an `effectTags` property to the `EffectChain` class.
* Modified the `triggersEffect` attribute in the `SkillEffect` class to look at the 'effectID' key in the game data if the 'sequenceID' key is not present.
* Added a `statAffected` property to the `SkillEffect` class.
* Modified the `statSource` property of `SkillEffect` to be `None` instead of 'None' when not present.
* Added `tagAffected`, `resistanceType`, and `chanceToResist` properties to `SkillEffect`.
* Modified the `effectTags` property of `SkillEffect` to the ignore the 'Placeholder' tag.
* Added a `BridgeSkill` class.

## Version 0.19.2

* Added `name` and `description` properties to the `Mission` class.

## Version 0.19.1

* Data updated for hotfix 8147.

## Version 0.19.0

* Bug fix: added `DIFFICULTIES` to the `__all__` attribute of the `constants` module.
* Added `MISSION_NODE_TYPES` to `constants`.
* Changes to `saveslot` module:
    - Added an `OptionError` class.
    - Added `NodeOption` and `NodeConnection` classes.
    - Changes to `Mission` class:
        + Changed `nodes` attribute from a list to a dict; edited `missingNodeRewards()` and `SaveSlot.fromFile()` accordingly.
        + Added `nodeConnections` attribute.
        + Changed `_key` from a private attribute to a private property.
    - Changes to `MissionNode` class:
        + Added `data`, `_key`, and `options` attribute.
        + Added `type` and `coverSlots` attributes.

## Version 0.18.3

* Changed the `survivalEffects` attribute of `SaveSlot` to have lists as values, to account for stacked survival effects. Edited the `SurvivalEffects` class in the `session` module accordingly.
* Edited the `effectType` property of the `SkillEffect` class to account for a misspelling in the game data.

## Version 0.18.2

* Added the constant, `CHARACTER_TAGS`.
* Added the `tags` property to the  `Character` class.
* Added the `survivalEffects` attribute to the `SaveSlot` class and modified `SaveSlot.fromFile()` accordingly.
* Added more information to the `CharTab` class.
* Added character tags and skill tags to the `RosterFilter` class; added options to adjust them in the `AskRosterFilter` class; and revised `RosterTab.checkFilter()` accordingly.
* Added the `SurvivalEffects` class.
* Added a 'Survival Effects' option to the menu.

## Version 0.18.1

* Added `description`, `isAOE`, `isMultiRandom`, and `numTargets` properties to the `Skill` class.
* Added a `description` property to the `SkillEffect` class.
* Edited the `effectTags` property of the `Skill` class to return the tags in alphabetical order.
* Expanded the `CharTab` class to display skill information.
* Added a `showwarning` function to the `dialogs` module.
* Modified `RosterTab.optimalSummons()` to pop up a warning about inaccuracies if normal missions are not completed (and therefore not all characters in the summon pool have been unlocked).
* Added an `HTMLTagStripper` class to the `utils` subpackage. It is used to parse skill descriptions.
* Added `ScrollFrame.onDestroy()` to unbind the mouse wheel when the scroll frame is destroyed.

## Version 0.18.0

* Added an `effectTags` property to the `SkillEffect` class.
* Added a `casterEffect` attribute to `Skill`.
* In `Skill`, changes the `effectTypes` property to `effectTags`; added the `casterEffect` chain to this property.
* Changed `Character.skillEffectTypes()` to `Character.skillEffectTags()`.
* Changes `allSkillEffectTypes` function to `allSkillEffectTags`.
* Modified `Skill` constructor to allow for starting skills to be locked upon creation; added a `startWith` property, and modified the `Character` constructor accordingly.
* Added a `chartab` module and edited to `ui.__init__` to import from it.
* Added a `session` property to `CharCard`.
* Added a clickable 'OPEN' label to `CharCard`.
* Added `Session.charTab()`.
* Added `camelToSpace` function.
* Fixed typo in column numbering in `CharCard`'s stat plate.

## Version 0.17.1

* Added an `effectTypes` property to the `Skill` class.
* Added a `skillEffectTypes` method to the `Character` class.
* Added an `allSkillEffectTypes` function to the `gameobjects` module.
* Fixed packing issues so that the scrolling areas of character cards and missing missions would expand properly under window resizing.

## Version 0.17.0

* Moved the `Skill`, `SkillEffect`, and `EffectChain` classes to their own module.

## Version 0.16.1

* Added `collapse` function to `utils`.
* Added `SkillEffect` and `EffectChain` classes.
* To `Skill` class, added `effects` attribute and `cooldown` and `startingCooldown` properties.
* Added `aiSkillOrder` method to `Character` class.

## Version 0.16.0

* `decompressSave` function renamed to `decompressedData`. Functionality altered to return only decompressed string. `decryptSaveFile` function revised accordingly.
* `STLTimeStamps.fromSaveData()` revised to allow for the possibility of missing time stamps.
* 'from Clipboard' button added to start screen.
* Added `AskClipboard` modal dialog class.
* Added 'From Clipboard...' menu options.
* Added `STLPlanner.newFromClipboard()`.

## Version 0.15.2

* Added a `decompressSave` function.
* Edited the `decryptSaveFile` function to decompress data when needed.
* Updated game data.

## Version 0.15.1

* Added the following functions: `gearUpgradeCost`, `gearToMaxCost`, and `charGearToMaxCost`.

## Version 0.15.0

* Added a `DIFFICULTIES` constant.
* Corrected `ui.__init__` to import from the `charcard` and `session` modules.
* Deleted the `inventory` method from the `STLPlanner` class and edited the 'Inventory...' menu item accordingly.
* Added `Mission` and `MissionNode` classes.
* Added a `missions` attribute to the `SaveSlot` class and edited the `fromFile` method accordingly.
* Added a `MissingMissions` class.
* Added a 'Missions...' menu item.

## Version 0.14.0

* Added a `SessionSettings` class to store session settings that should be remembered.
* Added a `settings` attribute to the `Session` class.
* Edited the `OptimalSummons` class to remember the user's choice about excluding commons.
* The `filter` attribute of the `RosterTab` class is now the `rosterFilter` attribute of the `SessionSettings` class.
* Edited the `export` method of the `RosterTab` class to remember the user's choice of directory and file name.

## Version 0.13.0

* Added a `maxGearLevel` attribute to the `Roster` class.
* Removed the setter for the `level` property of the `Gear` class and added a `setLevel` method that enforces gear leveling restrictions.
* Added a `_key` attribute to the `Skill` class and revised its constructor so that skills that come with a newly summoned character are unlocked upon instance creation.
* Added a custom `asksaveasfilename` function to the `dialogs` module and edited the `RosterTab.export` method to use it.
* Edited the `InventoryScreen` class to trim the combo-boxes when the player is unable to level a character to 99.
* Changes to the `STLPlanner` class:
    - Added a `sessionOnly` attribute for menu items that should only be enabled when there is an active session.
    - Changed the `session` attribute to a read-only property.
    - Changed the `menuEnabled` setter to account for the `sessionOnly` menu items.
    - Added the 'Inventory...' menu item to `sessionOnly` and set it to be initially disabled.
    - Edited the `newSession` method to enable `sessionOnly` menu items on session creation.

## Version 0.12.0

* Restructured module for greater compartmentalization and natural groupings.

## Version 0.11.0

* Added a `role` property to the `Item` class.
* Added `skillUpgradeCost` and `skillToMaxCost` functions.
* Added an `itemsToMax` property to `Skill` class.
* Renamed `keysByCategory` method in `Inventory` to `keysByCat`.
* Added `itemsByCat` method to `Inventory`.
* Moved `Inventory` class to `gameobjects.py`.
* Added `levelMap`, `startLevel`, and `endLevel` attributes to `InventoryScreen` class.
* Added `inventory` and `roster` properties to `InventoryScreen` class.
* Rewrote `body` method in `InventoryScreen` class.
* Added `setStartLevel`, `setEndLevel`, and `displayCat` methods to `InventoryScreen`

## Version 0.10.4

* Rewrote the `Item` class to be immutable.
* Added an `Inventory` class to `saveslot.py`.
* In the `SaveSlot` class, changed the `inventory` attribute and the `fromFile` method to work with the new `Inventory` class.
* Changed the `InventoryScreen` class to be compatible with the changes to the `SaveSlot` class.

## Version 0.10.3

* The in-game name of the character with name ID, 'JudgeQ', is simply 'Q'. Because of this, changed the short name on the character card from 'Judge Q' to 'Q'.

## Version 0.10.2

* Added 'Judge Q' to the list of upcoming characters.
* Added an `InventoryScreen` modal message class.
* Edited `STLPlanner.inventory()` method to raise an `InventoryScreen` dialog.
* Data file 'Item.json' now imports as the variable, `Item_asset`, so as not to conflict with the `Item` class.
* Updated game data.

## Version 0.10.1

* Added an `Item` class and an `ITEMS` constant.
* Added a `SaveSlot.inventory` attribute.
* Edited `SaveSlot.fromFile()` to read and populate the `inventory` attribute.
* Added a 'Session > Inventory...' menu options.
* Added an `STLPlanner.inventory()` method to write the inventory to the console.
* Updated documentation.
* Updated README.
    - Changed link to app download because of Google Drive reorganization.
    - Added link to developer version of app.

## Version 0.10.0

* Added a `ModalMessage` class, which is the same as `ModalDialog` but has no 'Cancel' button.
* Changed `ModalDialog` to inherit from `ModalMessage`.
* Changed `HelpScreen` to inherit from `ModalMessage`.
* Created an `OptimalSummons` subclass of `ModalMessage` for displaying summon rates. Edited the `RosterTab.optimalSummons` method accordingly.
* Added help menu option to `disableOnModal` list.

## Version 0.9.3

* Alphabetized constants in docstring.
* Renamed `functions` module to `savefile` and revised docstrings accordingly.
* Improved documentation for the `Roster.inGearSlot` attribute.
* For compatibility with `pdcoc` formatting, edited docstrings in the following modules:
    - `objrelations`
    - `relations`
    - `scrollframe`
* Uploaded documentation produced by `pdoc`

## Version 0.9.2

* Removed the unnecessary `event` argument from `RosterTab.sort()` and revised `RosterTab.actionBar()` accordingly.
* In preparation for publishing detailed package documentation with `pdcoc`, edited docstrings in the following modules:
    - `dialogs`
    - `rostertab`
    - `stlplanner`
    - `customabcs`
    - `objrelations`
    - `relations`
    - `scrollframe`


## Version 0.9.1

* In preparation for publishing detailed package documentation with `pdcoc`, edited docstrings in the following modules:
    - `constants`
    - `gameobjects`
    - `saveslot`
    - `stats`
    - `dialogs`
    - `rostertab`
    - `stlplanner`

## Version 0.9.0

* Converted the `data` attribute in the `Skill` class to a property.
* Deleted the now unnecessary manual changes to `GSCharacter` that were designed to enable Garak and Shinzon before hotfix data was available.
* Edited the `SaveSlot.sort()` method to remove redundant self-reference in one of the arguments. Edited the `RosterTab` class to account for this.
* In preparation for publishing detailed package documentation with `pdcoc`, edited docstrings in the following modules:
    - `constants`
    - `functions`
    - `gameobjects`
    - `roster`
    - `saveslot`

## Version 0.8.0

* Changed the structure of the `SUMMON_POOL` constant so that it contains summon probabilities for individual characters, as well as the orb-cost of each summon pool.
* Added the `Roster.tokensPerOrb` method.
* Changes to the `ui.RosterTab` class:
    - Added a `roster` property for convenience.
    - Added a 'summon pools' button to the action bar that is linked to a new method, `optimalSummons`.
    - Created temporary functionality in the `optimalSummons` method to print results to the console.
    - Added file types and a title to the export dialog.

## Version 0.7.4

* Added the ability to export a roster to a spreadsheet.

## Version 0.7.3

* Moved the help bar in the roster screen to a help dialog accessible from the menu bar.

## Version 0.7.2

* Created a new `Session` class and restructured the `STLPlanner` class to work with it. Small modifications were also made to the `RosterTab` class as a result. The idea is a re-envisioning of the structure of the app. The app loads a "session", which is associated with a save slot--either taken from an actual save file or created virtually. The session can load tabs. Currently, there is only a "roster" tab. But in the future, there will be "particle" and "character" tabs.

## Version 0.7.1

* Changed "Preferences > Show time per day" menu option to "Session > Show Timestamps".

## Version 0.7.0

* Added short names for Dax and Old Picard.
* Added a custom `askyesno` function that disables menu options.
* Added an `AskMaxChars` class and `askMaxChars` function to create a dialog offering options when creating a roster of maxed characters.
* Added a warning when starting a new session.
* Deleted the `StartFrame` class and added its logic to the `STLPlanner` constructor.
* Changed `View` menu name to `Preferences`.
* Updated README file with new screenshot and new version number.

## Version 0.6.0

* Temporarily disabled the use of the `StartFrame` class.
* Added menu items to `STLPlanner` to correspond to the buttons in `StartFrame`.
* Fixed an error where Modal dialogs would re-enable the main app menu options too soon. This happened because Modal dialogs would re-enable them when they closed. But if one Modal dialog called another, the second one would re-enable the menus while the first was still open. Now, Modal dialogs simply restore the state of the app menu options that existed when the dialog was open.
    - Added a `menuEnabled` property to the `STLPlanner` class, whose setter toggles the state of the menu options in the `disableOnModal` attribute.
    - Created a function decorator, `addroot`, to encode the menu toggling logic, and used it to redefine the custom versions of `showerror` and `showinfo`.
    - Adjusted the logic of the `ModalDialog` base class.
* Added an overriding `buttonbox` method to the `ModalDialog` base class that puts the 'ok' button on the right and assigns the button box to an attribute so that subclasses can more easily modify it.
* Rewrote the `AskRosterFilter` class to use the `ModalDialog` base class, and revised the `askRosterFilter` function accordingly.
* Removed the `slot` argument from the `SaveSlot` constructor.
* Moved the `saveFilePath`, `AESdecrypt`, and `decryptSaveFile` functions from the `saveslot` module to their own module, `functions`.
    - Added a `save` argument to the `SaveSlot.fromFile` method that represents the output of the `decryptSaveFile` function.
    - Added a similar `save` argument to the `AskSlot` constructor and `askSlot` function.
    - Edited the `AskSlot.validate` method to store the result as a `SaveSlot` object rather than the slot number as a 0-based integer.
* Added an `STLPlanner.mainFrame` attribute to hold the contents of the app window.
* Added an `STLPlanner.clear` method to clear the `mainFrame`.
* Added a `root` property to the `RosterTab` class.
* Removed the `makeShortName` function from the `rostertab` module, and converted it to a property of the `Character` class.
* Added a `SaveSlot.sort` method. The `RosterTab.sort` method no longer directly sorts the characters in the save slot, but instead calls the new method.
* Removed the `ROOT` constant, which was not used outside the `constants` module.

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