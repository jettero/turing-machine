#!/usr/bin/env python
# coding: utf-8

class TransitionFunction:
    def __init__(self, states=None):
        if isinstance(states, dict):
            self.states = dict(states)
        elif states is not None:
            raise ValueError("states argument should either be None or a dict")
        else:
            self.states = dict()

    def clear(self):
        self.states.clear()

    def add(self, cur_state, next_state):
        self.states[cur_state] = next_state

    def get(self, cur_state, default=None):
        if default is None:
            default = cur_state
        return self.states.get(cur_state, default)

    __setitem__ = add
    __call__    = __getitem__ = get

    def __iter__(self):
        for k,v in self.states.items():
            yield k,v

    def __repr__(self, indent=''):
        lines = [ indent + 'Transition Function:' ]
        for k,v in self:
            lines.append(indent + f'  {k!r} → {v!r}')
        return '\n'.join(lines) + '\n'
