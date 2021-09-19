"""Custom abstract base classes to extend `collections.abc`.

Includes `BiMapping` (a one-to-one mapping), `RelSet` and
`MutableRelSet` (relational sets that omits set operations), and
`MultiMapping` (a mapping whose keys can have multiple values).

"""

from collections.abc import MutableMapping, Collection

__all__ = ['ordPair', 'BiMapping', 'RelSet', 'MutableRelSet', 'MultiMapping']

def ordPair(obj):
    """Checks if the given object is a 2-tuple. Returns `False` if it
    is not. Returns the 2-tuple itself if it is.

    Args:
        elem (obj): The object to check.

    Returns:
        bool: `True` if the object is a 2-tuple.

    """
    return isinstance(obj, tuple) and len(obj) == 2

class BiMapping(MutableMapping):
    """An abstract base class for one-to-one mappings.

    Subclasses should implement `__getitem__`, `__delitem__`,
    `__iter__`, and `__len__` from the `dict` type. They should also
    implement two methods unique to the `BiMapping` base class. The
    first is `__setfreeval__`. This is the same as `__setitem__` from
    the `dict` type, but it is called only after the `BiMapping` object
    has verified that the given value is free to assign (i.e. not
    already assigned to a different key). The second is `__inverse__`.
    This method should create and return the inverse mapping, which
    should also be a `BiMapping` object. The inverse object is accessed
    with the `inverse` property and is used by the underlying
    `__setitem__` method to check that the given value is free.

    `BiMapping` objects raise a `ValueError` when trying to set a value
    that is already assigned to a different key.

    """
    @property
    def inverse(self):
        """The inverse `BiMapping` object."""
        try:
            return self._inverse
        except AttributeError:
            # pylint: disable=protected-access, attribute-defined-outside-init
            self._inverse = self.__inverse__()
            self._inverse._inverse = self
            return self._inverse

    def __setitem__(self, key, val):
        if (val in self.inverse
            and (key not in self or self[key] != val)
        ):
            raise ValueError(val)
        self.__setfreeval__(key, val)

    def __getitem__(self, key):
        raise NotImplementedError

    def __delitem__(self, key):
        raise NotImplementedError

    def __iter__(self):
        raise NotImplementedError

    def __len__(self):
        raise NotImplementedError

    def __setfreeval__(self, key, val):
        raise NotImplementedError

    def __inverse__(self):
        raise NotImplementedError

class RelSet(Collection):
    """A relational set.

    It differs from the `Set` abstract base class in `collections.abc`
    in that subclasses only inherit set relations, not set operations.
    Subclasses do not need to provide iterator-based construction
    methods.

    Subclasses must implement `__contains__`, `__iter__`, and
    `__len__`, and will inherit `__le__`, `__ge__`, `__eq__`, `__ne__`,
    `__lt__`, `__gt__`, and `isdisjoint`.

    """
    def __contains__(self, elem):
        raise NotImplementedError

    def __iter__(self):
        raise NotImplementedError

    def __len__(self):
        raise NotImplementedError

    def __le__(self, other):
        return all(elem in other for elem in self)

    def __ge__(self, other):
        return other <= self

    def __eq__(self, other):
        return self <= other <= self

    def __ne__(self, other):
        return not self == other

    def __lt__(self, other):
        return self <= other and self != other

    def __gt__(self, other):
        return other < self

    def isdisjoint(self, other):
        """Returns `True` if self and other are disjoint."""
        return all(elem not in other for elem in self)

class MutableRelSet(RelSet):
    """A mutable relational set.

    It differs from the `MutableSet` abstract base class in
    `collections.abc` in that subclasses only inherit set relations, not
    set operations. Subclasses do not need to provide iterator-based
    construction methods.

    Subclasses must implement `__contains__`, `__iter__`, `__len__`,
    `add`, and `discard`, and will inherit all the `RelSet` methods, as
    well as `pop`, `clear`, `remove`, `update`, and `difference_update`.

    """
    def __contains__(self, elem):
        raise NotImplementedError

    def __iter__(self):
        raise NotImplementedError

    def __len__(self):
        raise NotImplementedError

    def add(self, elem):
        """Adds the given element to the set."""
        raise NotImplementedError

    def discard(self, elem):
        """Removes the given element from the set if present."""
        raise NotImplementedError

    def pop(self):
        """Removes an element from the set and returns it."""
        elem = next(self.__iter__())
        self.discard(elem)
        return elem

    def clear(self):
        """Removes all elements from the set."""
        while len(self) > 0:
            self.pop()

    def remove(self, elem):
        """Removes the given element from the set. Raises a `ValueError`
        if the element is not present.
        """
        if elem not in self:
            raise ValueError(elem)
        self.discard(elem)

    def update(self, *others):
        """Adds all elements from the given sets."""
        for other in others:
            for elem in other:
                self.add(elem)

    def difference_update(self, *others): # pylint: disable=invalid-name
        """Discards all elements from the given sets."""
        for other in others:
            for elem in other:
                self.discard(elem)

class MultiMapping(MutableRelSet):
    """A dictionary-like object whose keys can have multiple values.

    A `MultiMapping` is an object that can function as both a dictionary
    of sets, or as a single set of key-value pairs. To use this abstract
    base class, you must implement nine methods: four set-like methods,
    four dictionary-like methods, and one method unique to the
    `MultiMapping` base class.

    The set-like methods you must implement are `_contains`,
    `__iter__`, `__len__`, and `_discard`. The methods, `_contains` and
    `_discard`, are just like the `__contains__` and `discard` method of
    the `set` type, except they take two arguments (a key and a value)
    rather than one. You do not need to implement `add`, since this is
    built automatically from the `__setitem__` method below. Also,
    `__iter__` should iterate over the key-value pairs.

    The dictionary-like methods you must implement are `__getitem__`,
    `__setitem__`, `__delitem__`, and `keys`. The `__setitem__` method
    should add a new value to a key's current set of values.

    Finally, you should implement `__inverse__`, which builds and
    returns the inverse multi-mapping object.

    A `MultiMapping` object inherits the following set-like methods:
    `__le__`, `__lt__`, `__eq__`, `__ne__`, `__gt__`, `__ge__`,
    `isdisjoint`, `add`, `discard`, `clear`, `pop`, `remove`, `update`,
    and `difference_update`.

    The only strictly dictionary-like method it inherits is `values`,
    although `clear` and `update` are also used for dictionaries and
    function the same.

    Finally, a `MultiMapping` object inherits the `inverse` property,
    which returns the inverse object built by the `__inverse__` method.

    """

    @property
    def inverse(self):
        """The inverse `MultiMapping` object."""
        try:
            return self._inverse
        except AttributeError:
            # pylint: disable=protected-access, attribute-defined-outside-init
            self._inverse = self.__inverse__()
            self._inverse._inverse = self
            return self._inverse

    def __contains__(self, elem):
        if ordPair(elem):
            return self._contains(*elem)
        return False

    def _contains(self, key, val):
        raise NotImplementedError

    def __iter__(self):
        raise NotImplementedError

    def __len__(self):
        raise NotImplementedError

    def discard(self, elem):
        """Removes the given key-value pair, if present. Does nothing if
        `elem` if not a 2-tuple.

        Args:
            elem (tuple): (`key`, `value`) The key-value pair to remove.

        """
        if ordPair(elem):
            self._discard(*elem)

    def _discard(self, key, val):
        raise NotImplementedError

    def __getitem__(self, key):
        raise NotImplementedError

    def __setitem__(self, key, val):
        raise NotImplementedError

    def __delitem__(self, key):
        raise NotImplementedError

    def keys(self):
        """Returns an iterator over the keys of the `MultiMapping`
        instance.

        """
        raise NotImplementedError

    def __inverse__(self):
        raise NotImplementedError

    def add(self, elem):
        """`m.add((key, val))` is equivalent to `m[key] = val`.

        Args:
            elem (tuple): (`key`, `value`) The key-value pair to add.

        Raises:
            ValueError: If `elem` is not a 2-tuple.

        """
        if not isinstance(elem, tuple) or len(elem) != 2:
            raise ValueError(elem)
        key, val = elem
        self.__setitem__(key, val)

    def values(self):
        """`m.values()` is equivalent to `m.inverse.keys()`.

        Returns:
            iterable: An iterable over the values of the `MultiMapping`
                instance.

        """
        return self.inverse.keys()
