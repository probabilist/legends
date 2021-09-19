"""UI objects used with the `legends` package.

All objects that reside in one of the direct submodules of `legends.ui`
can be accessed from the `legends.ui` namespace.

Example:
    >>> import legends
    >>> legends.ui.Session is legends.ui.stlplanner.Session
    True

"""

from legends.ui.dialogs import *
from legends.ui.rostertab import *
from legends.ui.stlplanner import *
