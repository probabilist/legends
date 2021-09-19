"""Custom dictionary-like data types.

Includes `bidict` (a one-to-one dictionary), `dictplus` (a dictionary
with a set-like `discard` method), `dictofsets` (a rudimentary
multi-valued dictionary), `multidict` (a robust multi-valued
dictionary), `inversedict` (a `multidict` whose keys cannot share
values), and `invertibledict` (a dictionary that can be inverted to an
`inversedict`).

"""

from collections import defaultdict
from legends.utils.customabcs import ordPair, BiMapping, MultiMapping

__all__ = [
    'bidict', 'dictplus', 'dictofsets', 'multidict', 'inversedict',
    'invertibledict'
]

class bidict(BiMapping): # pylint: disable=invalid-name
    """An invertible, one-to-one dictionary.

    The `bidict` object is implemented by linking a forward dictionary
    and a backward dictionary. Because of this, all keys and values must
    be immutable.

    """

    def __init__(self):
        """The constructor takes no arguments and creates an empty
        `bidict` object.

        """
        self._forward = {}
        self._backward = {}

    def __getitem__(self, key):
        return self._forward[key]

    def __delitem__(self, key):
        val = self._forward[key]
        del self._forward[key]
        del self._backward[val]

    def __iter__(self):
        return self._forward.__iter__()

    def __len__(self):
        return len(self._forward)

    def __setfreeval__(self, key, val):
        self._forward[key] = val
        self._backward[val] = key

    def __inverse__(self):
        # pylint: disable=protected-access
        inverse = bidict()
        inverse._forward = self._backward
        inverse._backward = self._forward
        return inverse

    def __repr__(self):
        return 'bidict(' + repr(self._forward) + ')'

class dictplus(dict): # pylint: disable=invalid-name
    """A dictionary with a `discard` method.

    """

    def discard(self, elem):
        """Removes the given key-value pair, if present. Does nothing if
        `elem` is not a 2-tuple.

        Args:
            elem (tuple): (`key`, `value`) The key-value pair to remove.

        """
        if ordPair(elem):
            key, val = elem
            if key in self and self[key] == val:
                del self[key]

    def __repr__(self):
        return 'dictplus(' + dict.__repr__(self) + ')'

class dictofsets(MultiMapping): # pylint: disable=invalid-name
    """A rudimentary multi-valued dictionary.

    A `dictofsets` object is a dictionary whose values are sets.

    The `__contains__`, `__iter__`, and `__len__` methods work
    differently than for ordinary dictionaries. If `d` is a `dictofsets`
    object, then `(k,v) in d` is equivalent to `v in d[k]`. The
    `__iter__` method returns an iterator over all key-value pairs. To
    iterate over keys, use the `keys` method. And `len(d)` is the total
    number of key-value pairs.

    The `__getitem__` method returns a frozen set, so key-value pairs
    can only be added with `d[k] = v`. The syntax `d[k].add(v)` will not
    work.

    A `dictofsets` object also has a `discard` method, so that
    `d.discard((k, v))` removes `v` from the set `d[k]`, if it is
    present.

    The `dictofsets` class does not implement the `inverse` property.

    """

    # pylint: disable=abstract-method

    def __init__(self):
        self._dict = defaultdict(set)

    def _contains(self, key, val):
        return val in self._dict[key]

    def __iter__(self):
        for key in self._dict:
            for val in self._dict[key]:
                yield key, val

    def __len__(self):
        return sum(len(val) for val in self._dict.values())

    def _discard(self, key, val):
        """Removes the given key-value pair from the `dictofsets`, if
        present.
        """
        self._dict[key].discard(val)
        if not self._dict[key]:
            del self._dict[key]

    def __getitem__(self, key):
        if key not in self._dict:
            raise KeyError(key)
        return frozenset(self._dict[key])

    def __setitem__(self, key, val):
        self._dict[key].add(val)

    def __delitem__(self, key):
        del self._dict[key]

    def keys(self):
        """Returns an iterable over the keys of `dictofsets`."""
        return self._dict.keys()

    def __repr__(self):
        return 'dictofsets(' + repr(dict(self._dict)) + ')'

class multidict(MultiMapping): # pylint: disable=invalid-name
    """A more robust multi-valued dictionary that is easily inverted.

    It is a multi-mapping of immutables to immutables, implemented by
    embedding both a dictionary of sets, and a set of key-value pairs. A
    reversed dictionary and a reversed set are also embedded to
    implement the inverse mapping.

    """
    def __init__(self):
        """The constructor takes no arguments and creates an empty
        `multidict` object.

        """
        self._forward = dictofsets()
        self._backward = dictofsets()
        self._set = set()
        self._rset = set()

    def _contains(self, key, val):
        return (key, val) in self._set

    def __iter__(self):
        return self._set.__iter__()

    def __len__(self):
        return len(self._set)

    def _discard(self, key, val):
        """Removes the given key-value pair, if present.

        """
        if (key, val) in self:
            self._forward.discard((key, val))
            self._backward.discard((val, key))
            self._set.discard((key, val))
            self._rset.discard((val, key))

    def __getitem__(self, key):
        return self._forward[key]

    def __setitem__(self, key, val):
        self._forward[key] = val
        self._backward[val] = key
        self._set.add((key, val))
        self._rset.add((val, key))

    def __delitem__(self, key):
        if key not in self._forward.keys():
            raise KeyError(key)
        for val in self._forward[key]:
            self.discard((key, val))

    def keys(self):
        """Returns an iterator over the keys in the `multidict`.

        """
        return self._forward.keys()

    def __inverse__(self):
        inverse = multidict()
        return self._inverseinit(inverse)

    def _inverseinit(self, inverse):
        # pylint: disable=protected-access
        inverse._forward = self._backward
        inverse._backward = self._forward
        inverse._set = self._rset
        inverse._rset = self._set
        return inverse

    def copy(self):
        """Creates and returns a copy of the multidict object."""
        new = multidict()
        return self._fillcopy(new)

    def _fillcopy(self, new):
        for pair in self:
            new.add(pair)
        return new

    def __repr__(self):
        return 'multidict(' + repr(dict(self._forward._dict)) + ')'

class inversedict(multidict): # pylint: disable=invalid-name
    """A `multidict` whose values are disjoint sets.

    Its inverse can be represented as a dictionary and is implemented as
    an `invertibledict` object.

    """
    def __init__(self):
        """The constructor takes no arguments and creates an empty
        `inversedict` object.

        """
        multidict.__init__(self)
        self._backward = dictplus()

    def __setitem__(self, key, val):
        if val in self._backward.keys():
            raise ValueError(val)
        multidict.__setitem__(self, key, val)

    def __inverse__(self):
        inverse = invertibledict()
        return self._inverseinit(inverse)

    def copy(self):
        """Creates and returns a copy of the `inversedict` object.

        """
        new = inversedict()
        return self._fillcopy(new)

    def __repr__(self):
        return 'inversedict(' + repr(dict(self._forward._dict)) + ')'

class invertibledict(multidict): # pylint: disable=invalid-name
    """A more robust dictionary that is easily inverted.

    Its inverse is implemented as an `inversedict` object.

    """
    def __init__(self):
        """The constructor takes no arguments and creates an empty
        `invertibledict` object.

        """
        multidict.__init__(self)
        self._forward = dictplus()

    def __delitem__(self, key):
        if key not in self._forward.keys():
            raise KeyError(key)
        val = self._forward[key]
        self.discard((key, val))

    def __inverse__(self):
        inverse = inversedict()
        return self._inverseinit(inverse)

    def copy(self):
        """Creates and returns a copy of the `invertibledict` object.

        """
        new = invertibledict()
        return self._fillcopy(new)

    def __repr__(self):
        return 'invertibledict(' + repr(self._forward) + ')'
