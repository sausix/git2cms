from collections.abc import Iterable

# TODO implement other set functions to SetOfMutable


class SetOfMutable:
    # Just uses id to "hash" mutable items
    # Allows to add a dict only one, for example.

    def __init__(self, seq=()):
        self.data = {id(item): item for item in seq}
        self.testset = set()

    def add(self, element):
        """
        Add an element to a set.

        This has no effect if the element is already present.
        """
        key = id(element)
        if key in self.data:
            return

        self.data[key] = element

    def clear(self, *args, **kwargs): # real signature unknown
        """ Remove all elements from this set. """
        self.data.clear()

    def copy(self, *args, **kwargs): # real signature unknown
        """ Return a shallow copy of a set. """
        return SetOfMutable(self.data.values())

    def difference(self, *args, **kwargs): # real signature unknown
        """
        Return the difference of two or more sets as a new set.

        (i.e. all elements that are in this set but not the others.)
        """
        pass

    def difference_update(self, *args, **kwargs): # real signature unknown
        """ Remove all elements of another set from this set. """
        pass

    def discard(self, element):
        """
        Remove an element from a set if it is a member.

        If the element is not a member, do nothing.
        """
        key = id(element)
        if key in self.data:
            self.data.pop(key)

    def intersection(self, *args, **kwargs): # real signature unknown
        """
        Return the intersection of two sets as a new set.

        (i.e. all elements that are in both sets.)
        """
        pass

    def intersection_update(self, *args, **kwargs): # real signature unknown
        """ Update a set with the intersection of itself and another. """
        pass

    def isdisjoint(self, *args, **kwargs): # real signature unknown
        """ Return True if two sets have a null intersection. """
        pass

    def issubset(self, *args, **kwargs): # real signature unknown
        """ Report whether another set contains this set. """
        pass

    def issuperset(self, *args, **kwargs): # real signature unknown
        """ Report whether this set contains another set. """
        pass

    def pop(self):
        """
        Remove and return an arbitrary set element.
        Raises KeyError if the set is empty.
        """
        if len(self.data) == 0:
            raise KeyError("pop from an empty set")

        return self.data.pop(next(iter(self.data.keys())))

    def remove(self, element):
        """
        Remove an element from a set; it must be a member.

        If the element is not a member, raise a KeyError.
        """
        key = id(element)

        if key not in self.data:
            raise KeyError(repr(element))

        self.data.pop(key)

    def symmetric_difference(self, *args, **kwargs): # real signature unknown
        """
        Return the symmetric difference of two sets as a new set.

        (i.e. all elements that are in exactly one of the sets.)
        """
        pass

    def symmetric_difference_update(self, *args, **kwargs): # real signature unknown
        """ Update a set with the symmetric difference of itself and another. """
        pass

    def union(self, *args, **kwargs): # real signature unknown
        """
        Return the union of sets as a new set.

        (i.e. all elements that are in either set.)
        """
        pass

    def update(self, iterable):
        """ Update a set with the union of itself and others. """
        if isinstance(iterable, Iterable):
            self.data.update({id(element): element for element in iterable})
        else:
            raise TypeError("{} object is not iterable.".format(type(iterable).__name__))

    def __contains__(self, y): # real signature unknown; restored from __doc__
        """ x.__contains__(y) <==> y in x. """
        return id(y) in self.data

    def __iter__(self, *args, **kwargs):
        """ Implement iter(self). """
        return iter(self.data.values())

    def __len__(self, *args, **kwargs):
        """ Return len(self). """
        return len(self.data)

    def __repr__(self, *args, **kwargs):
        """ Return repr(self). """
        return "SetOfMutable({})".format(", ".join(repr(item) for item in self.data.values()))

    __hash__ = None
