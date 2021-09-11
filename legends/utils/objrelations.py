"""Custom dictionary-like classes that can handle mutable objects.

Support for all relation types (one-to-one, many-to-many, many-to-one,
and one-to-many) is provided. All objects stored as keys or values in
any of these relations must be instances of the Managed class. The
Managed class tracks objects by their id.

"""

from types import MethodType
from legends.utils.customabcs import BiMapping, MultiMapping
from legends.utils.relations import (
    bidict, multidict, inversedict, invertibledict
)

__all__ = ['Managed', 'OneToOne', 'ManyToMany', 'ManyToOne', 'OneToMany']

class Managed(): # pylint: disable=too-few-public-methods
    """A class whose instances are tracked by ID number.

    Class attributes:
        _m_objects (dict of int:obj): A dictionary mapping the id of
            each instance to the instance itself.

    """

    _m_objects = {}

    def __new__(cls, *args, **kargs): # pylint: disable=unused-argument
        obj = object.__new__(cls)
        Managed._m_objects[id(obj)] = obj
        return obj

class OneToOne(BiMapping, Managed):
    """A one-to-one relation mapping objects to objects.

    All objects in the relation need to be Managed objects, but
    otherwise, a OneToOne object functions just like a bidict object.

    The OneToOne class is meant to be subclassed. Subclasses may wish to
    override the `validate` method to provide restrictions on adding a
    pair to the relation. The `validate` method is called whenever
    `__setitem__` is called. If `validate` returns True, the
    `__setitem__` method proceeds normally. Otherwise, `__setitem__`
    simply returns None. If the subclass wishes to raise an error when
    validation fails, the error should be raised from within the
    `validate` method.

    Attributes:
        map (bidict of int:int): The relation is stored under the
            hood as a bidict mapping IDs to IDs, where the IDs are
            provided by the common Manager object.

    """

    def __init__(self):
        self.map = bidict()

    def __getitem__(self, key):
        try:
            valID = self.map[id(key)]
        except KeyError as ex:
            raise KeyError(key) from ex
        return Managed._m_objects[valID]

    def __delitem__(self, key):
        try:
            del self.map[id(key)]
        except KeyError as ex:
            raise KeyError(key) from ex

    def __iter__(self):
        return (Managed._m_objects[keyID] for keyID in self.map)

    def __len__(self):
        return len(self.map)

    def __setfreeval__(self, key, val):
        if self.validate(key, val): # pylint: disable=not-callable
            self.map[id(key)] = id(val)

    def __inverse__(self):
        inverse = OneToOne()
        inverse.map = self.map.inverse
        def validate(slf, key, val):
            return slf.inverse.validate(val, key)
        inverse.validate = MethodType(validate, inverse)
        return inverse

    # pylint: disable-next=method-hidden, unused-argument, no-self-use
    def validate(self, key, val):
        """Checks if the given key-value pair may be added to the
        relation. As implemented here, the method always returns True.
        Subclasses should override this method to produce custom
        behavior.

        Args:
            key (obj): The key to validate.
            val (obj): The value to validate.

        Returns:
            bool: True if the key-value pair may be added, False
                otherwise.

        """
        return True

    def __repr__(self):
        disp = 'OneToOne({'
        for key, val in self.items():
            disp += repr(key) + ': ' + repr(val) + ',\n '
        return disp + '})'

class ManyToMany(MultiMapping, Managed):
    """A many-to-many relation mapping objects to objects.

    All objects in the relation need to be Managed objects, but
    otherwise, a ManyToMany object functions just like a multidict
    object.

    The ManyToMany class is meant to be subclassed. Subclasses may wish
    to override the `validate` method to provide restrictions on adding
    a pair to the relation. The `validate` method is called whenever
    `__setitem__` is called. If `validate` returns True, the
    `__setitem__` method proceeds normally. Otherwise, `__setitem__`
    simply returns None. If the subclass wishes to raise an error when
    validation fails, the error should be raised from within the
    `validate` method.

    Attributes:
        map (multidict of int:int): The relation is stored under the
            hood as a multidict mapping IDs to IDs, where the IDs are
            provided by the common Manager object.

    """

    def __init__(self):
        self.map = multidict()

    def _contains(self, key, val):
        return id(key), id(val) in self.map

    def __iter__(self):
        return (
            (Managed._m_objects[keyID], Managed._m_objects[valID])
            for keyID, valID in self.map
        )

    def __len__(self):
        return len(self.map)

    def _discard(self, key, val):
        """Removes the given key-value pair from the relation, if
        present.
        """
        self.map.discard((id(key), id(val)))

    def __getitem__(self, key):
        try:
            return tuple(
                Managed._m_objects[valID] for valID in self.map[id(key)]
            )
        except KeyError as ex:
            raise KeyError(key) from ex

    def __setitem__(self, key, val):
        if self.validate(key, val):
            self.map[id(key)] = id(val)

    def __delitem__(self, key):
        try:
            del self.map[id(key)]
        except KeyError as ex:
            raise KeyError(key) from ex

    def keys(self):
        return (Managed._m_objects[keyID] for keyID in self.map.keys())

    def __inverse__(self):
        inverse = ManyToMany()
        return self._inverseinit(inverse)

    def _inverseinit(self, inverse):
        inverse.map = self.map.inverse
        def validate(slf, key, val):
            return slf.inverse.validate(val, key)
        inverse.validate = MethodType(validate, inverse)
        return inverse

    # pylint: disable=unused-argument, no-self-use
    def validate(self, key, val):
        """Checks if the given key-value pair may be added to the
        relation. As implemented here, the method always returns True.
        Subclasses should override this method to produce custom
        behavior.

        Args:
            key (obj): The key to validate.
            val (obj): The value to validate.

        Returns:
            bool: True if the key-value pair may be added, False
                otherwise.

        """
        return True

    def __repr__(self):
        # pylint: disable=consider-using-dict-items
        disp = 'ManyToMany({'
        for key in self.keys():
            disp += repr(key) + ': ' + repr(self[key]) + ',\n '
        return disp + '})'

class ManyToOne(ManyToMany):
    """A many-to-one relation mapping objects to objects.

    All objects in the relation need to be Managed objects, but
    otherwise, a ManyToOne object functions just like an invertibledict
    object.

    The ManyToOne class is meant to be subclassed. Subclasses may wish
    to override the `validate` method to provide restrictions on adding
    a pair to the relation. The `validate` method is called whenever
    `__setitem__` is called. If `validate` returns True, the
    `__setitem__` method proceeds normally. Otherwise, `__setitem__`
    simply returns None. If the subclass wishes to raise an error when
    validation fails, the error should be raised from within the
    `validate` method.

    Attributes:
        map (invertibledict of int:int): The relation is stored under
            the hood as a multidict mapping IDs to IDs, where the IDs
            are provided by the common Manager object.

    """

    def __init__(self):
        ManyToMany.__init__(self)
        self.map = invertibledict()

    def __inverse__(self):
        inverse = OneToMany()
        return self._inverseinit(inverse)

    def __getitem__(self, key):
        try:
            valID = self.map[id(key)]
        except KeyError as ex:
            raise KeyError(key) from ex
        return Managed._m_objects[valID]

    def __repr__(self):
        # pylint: disable=consider-using-dict-items
        disp = 'ManyToOne({'
        for key in self.keys():
            disp += repr(key) + ': ' + repr(self[key]) + ',\n '
        return disp + '})'

class OneToMany(ManyToMany):
    """A one-to-many relation mapping objects to objects.

    All objects in the relation need to be Managed objects, but
    otherwise, a OneToMany object functions just like an inversedict
    object.

    The OneToMany class is meant to be subclassed. Subclasses may wish
    to override the `validate` method to provide restrictions on adding
    a pair to the relation. The `validate` method is called whenever
    `__setitem__` is called. If `validate` returns True, the
    `__setitem__` method proceeds normally. Otherwise, `__setitem__`
    simply returns None. If the subclass wishes to raise an error when
    validation fails, the error should be raised from within the
    `validate` method.

    Attributes:
        map (inversedict of int:int): The relation is stored under the
            hood as a multidict mapping IDs to IDs, where the IDs are
            provided by the common Manager object.

    """

    def __init__(self):
        ManyToMany.__init__(self)
        self.map = inversedict()

    def __inverse__(self):
        inverse = ManyToOne()
        return self._inverseinit(inverse)

    def __repr__(self):
        # pylint: disable=consider-using-dict-items
        disp = 'OneToMany({'
        for key in self.keys():
            disp += repr(key) + ': ' + repr(self[key]) + ',\n '
        return disp + '})'
