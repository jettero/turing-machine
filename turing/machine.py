#!/usr/bin/env python
# coding: utf-8

import logging

from .tape import Tape
from .state import State

log = logging.getLogger(__name__)

class TuringMachine:
    def __init__(self, tape='', initial_state='init', final_states='final', transition_function=None):
        self.stepno = 0
        self.tape = Tape(tape)
        self.pos = 0
        self.transition_function = transition_function
        if isinstance(final_states, (list,tuple)):
            self.final_states = set(State(x) for x in final_states)
        elif final_states:
            self.final_states = set([ final_states ])
        else:
            self.final_states = set()
        self.initial_state = State(initial_state)
        self.state = self.initial_state

        log.debug('init( %s )', self)

    @property
    def read(self):
        val = self.tape[ self.pos ]
        log.debug('read %s[ %d ] -> %s', repr(self.tape), self.pos, repr(val))
        return val

    @read.setter
    def write(self, val):
        log.debug('write %s[ %d ] <- %s', repr(self.tape), self.pos, repr(val))
        self.tape[ self.pos ] = val

    @property
    def state(self):
        ns = self._state.with_new_tval(self.read)
        log.debug('get-state: %s', repr(ns))
        return ns

    @state.setter
    def state(self, val):
        if not isinstance(val, State):
            raise ValueError('new state should be a State')
        self._state = ns = State(val.name)
        log.debug('set-state: %s', repr(ns))

    def step(self):
        step = self.stepno
        self.stepno += 1
        log.debug('step(%d)', step)
        if self.transition_function is None:
            log.debug('step(%d) null-transition', step)
            return

        if isinstance(self.transition_function, dict):
            # more of a table really …
            cur_state = self.state
            next_state = self.transition_function.get(cur_state, cur_state)

            log.debug('step(%d) cur-state: %s; next-state: %s; pos: %d',
                step, repr(cur_state), repr(next_state), self.pos)

            self.write = next_state.tval

            if next_state.action in ('R', '1', '+', '+1', '>', '→', '->'):
                self.pos += 1
                log.debug('step(%d) move right, new-pos: %d', step, self.pos)

            elif next_state.action in ('L', '-1', '-', '-1', '<', '←', '<-'):
                self.pos -= 1
                log.debug('step(%d) move left, new-pos: %d', step, self.pos)

            self.state = next_state

    @property
    def done(self):
        s = self.state
        log.debug('done? state=%s', s)
        for fs in self.final_states:
            if s == fs:
                log.debug('done? state=%s == fs=%s => done', s, fs)
                return True
            log.debug('done? state=%s != fs=%s => not done', s, fs)
        log.debug('done? not done')
    final = done
