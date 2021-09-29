"""A package for working with data from *Star Trek: Legends*.

All objects that reside in one of the direct submodules of the `legends`
package can be accessed from the `legends` namespace, with the exception
of the `ui` and `utils` submodules.

Example:
    >>> import legends
    >>> legends.Character is legends.gameobjects.Character
    True

"""

from legends import utils
from legends import ui
from legends.constants import *
from legends.functions import *
from legends.stats import *
from legends.gameobjects import *
from legends.roster import *
from legends.saveslot import *
