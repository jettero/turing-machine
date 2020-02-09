#!/usr/bin/env python
# coding: utf-8

LEFT  = ('L', '-1', '-', '-1', '<', '←', '<-')
RIGHT = ('R', '1', '+', '+1', '>', '→', '->')

class StateList:
    def __init__(self, *args):
        self.items = set()
        self.add(*args)

    def add(self, *args):
        for item in args:
            if isinstance(item, (list,tuple)):
                self.add(*item)
            else:
                self.items.add(State(item))

    def __iter__(self):
        for item in self.items:
            yield item

    def __repr__(self, indent=''):
        lines = [ indent + repr(x) for x in self.items ]
        return '\n'.join(lines) + '\n'

class State:
    name = tval = action = None

    def __init__(self, name, tval=None, action=None):
        if isinstance(name, State):
            (name,tval,action) = (name.name, name.tval, name.action)

        self.name = name
        self.tval = tval if tval is None else str(tval)
        self.action = action

    @property
    def is_left(self):
        return self.action in LEFT

    @property
    def is_right(self):
        return self.action in RIGHT

    def new_pos(self, old_pos):
        return old_pos + (1 if self.is_right else -1 if self.is_left else 0)

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
