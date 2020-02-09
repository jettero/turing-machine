#!/usr/bin/env python
# coding: utf-8

import logging

from .tape import Tape
from .state import State, StateList
from .transition import TransitionFunction

log = logging.getLogger(__name__)

class TuringMachine:
    def __init__(self, tape='', initial_state='init', final_states='final', transition_function=None):
        if isinstance(transition_function, dict):
            transition_function = TransitionFunction(transition_function)

        self.stepno = 0
        self.tape = Tape(tape)
        self.pos = 0
        self.transition_function = transition_function
        self.state = self.initial_state = State(initial_state)
        self.final_states = StateList(final_states)
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

        cur_state = self.state
        next_state = self.transition_function(cur_state)

        log.debug('step(%d) cur-state: %s; next-state: %s; pos: %d',
            step, repr(cur_state), repr(next_state), self.pos)

        self.write = next_state.tval

        log.debug('step(%d) next_state.new_pos(%d)', self.pos)
        self.pos = next_state.new_pos(self.pos)
        log.debug('step(%d)     --> %d', self.pos)

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
