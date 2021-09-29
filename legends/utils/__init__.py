"""Generic coding structures needed in the `legends` package.

All objects that reside in one of the direct submodules of
`legends.utils` can be accessed from the `legends.utils` namespace.

Example:
    >>> import legends
    >>> legends.utils.bidict is legends.utils.relations.bidict
    True

"""

from legends.utils.functions import *
from legends.utils.customabcs import *
from legends.utils.relations import *
from legends.utils.objrelations import *
from legends.utils.scrollframe import *
