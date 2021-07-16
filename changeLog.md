# Change log

## Version 1.0.3

* Added `GSItem.json` to data.
* Added a `getItems` function to `setup.py`.
* Added an `ITEMS` constant to `constants.py`.
* Added `inventory` and `fullInventory` properties to the `SaveSlot` class.
* Updated `README` to illustrate viewing the inventory.

## Version 1.0.2

* Fixed typos in comments that offer mathematical explanations for the workings of the Sela stat calculator.
* Added a function, `roundSigFig`, to `utils.functions` that rounds numbers according to significant figures.
* Added a boolean `probability` attribute to the `Stat` class in the `particleguru` module, to indicate if the stat is meant to represent a probability.
* Changes to `guruipt` module:
    - Added a constant, `PROBABILITIES`, that lists all stat names which represent probabilities.
    - Added a boolean `location` argument to `partDisplay` function, giving the option to include the particle's location in the returned display string.
    - Modified `roundStat` function to use significant figures for stat values less than 10.
    - Changes to `GuruIPT` class:
        + Modified constructor to set the `probability` attribute of the `Stat` objects in the embedded stat menu.
        + Added `changeStat` and `removeStat` methods.
        + Added a boolean `logodds` argument to the `suggest` method, giving the option to display probabilities as log-odds.
        + For greater compartmentalization, separated off part of the `seePart` method to a new method, `seePartDisplay`. Modified these methods to utilize the new `location` argument in the `partDisplay` function, and to allow a list of particle IDs as arguments.
        + Added a boolean `force` argument to the `move` method, giving the option to unlock, move, and relock particles with a single method call.
        + Fixed the `changesDisplay` method to display stats as they appear on the particle in-game, rather than in alphabetical order.
        + Fixed the docstring for the `changes` method.

## Version 1.0.1

* Enabled Tilly.
* Made `EffStatCalc` and `GuruIPT` printable.
* Added a `copyStats` method to `GuruIPT`.
* Fixed `equip` and `show` methods in `GuruIPT` to work as intended when a single integer argument is passed.
* Added a `seePart` method to `GuruIPT`.
* For greater compartmentalization, separated off part of the `changes` method in `GuruIPT` to a new method, `changesDisplay`.
* Fixed the docstring for `GuruIPT.stats`.
