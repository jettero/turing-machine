#!/usr/bin/env python
# coding: utf-8

class State:
    name = tval = action = None

    def __init__(self, name, tval=None, action=None):
        if isinstance(name, State):
            (name,tval,action) = (name.name, name.tval, name.action)

        self.name = name
        self.tval = tval if tval is None else str(tval)
        self.action = action

    def with_new_tval(self, tval):
        name, _, action = self
        return self.__class__(name, tval, action)

    def __eq__(self, other):
        if isinstance(other, State):
            return self.name == other.name
        return self.name == other

    def __hash__(self):
        return hash( (self.name, self.tval) )

    def __iter__(self):
        for i in self.name, self.tval, self.action:
            yield i

    def as_str(self):
        return ', '.join([ repr(x) if x.startswith(' ') or x.endswith(' ') else x
            for x in self if x is not None ])
    __str__ = as_str

    def __repr__(self):
        return f'S({self.as_str()})'
