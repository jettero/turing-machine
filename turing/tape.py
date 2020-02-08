#!/usr/bin/env python
# coding: utf-8

import re
import logging

log = logging.getLogger(__name__)

NULL = '\x00'
START_OF_TEXT = STX = '\x02'
END_OF_TEXT = ETX = '\x03'
FILE_SEPARATOR = FS = '\x1c'
RECORD_SEPARATOR = RS = '\x1e'

# NOTE: thought about using NULL or RS or something, but settled on ' ' like
# the example -- it's just easier to read
BLANK_SYMBOL = ' '

class Tape:
    offset = 0

    @classmethod
    def read_file(cls, fh, bs=1024):
        tape = ''
        r = fh.read(bs)
        while r:
            tape += r
            r = fh.read(bs)
        return cls(tape)

    def __init__(self, symbols=''):
        if isinstance(symbols, Tape):
            self.tape = symbols.tape
            self.offset = symbols.offset
        else:
            self.tape = symbols

    def __str__(self):
        return self.tape

    def __repr__(self):
        ret = self.tape
        to_fix = set(re.findall(r' {8,}', ret))
        for t in sorted(to_fix, key=lambda x: -len(x)):
            ret = ret.replace(t, f"«{len(t)}»")
        to_fix = set(re.findall(r'[^\w\d \t_-]', ret))
        for t in to_fix:
            ret = ret.replace(t, f'\\x{ord(t):02x}')
        return f'##TAPE:{self.offset}##{ret}##'

    def __eq__(self, other):
        return self.tape == other

    def __len__(self):
        return len(self.tape)

    def _offset_idx(self, idx):
        log.debug('_offset_idx %s idx=%s [input]', repr(self), repr(idx))
        if isinstance(idx, slice):
            nstart = 0 if idx.start is None else idx.start + self.offset
            nstop  = len(self.tape) if idx.stop is None else idx.stop + self.offset
            idx = slice(nstart, nstop, idx.step)
        else:
            idx += self.offset
            idx = slice(idx, idx+1, None)
        log.debug('_offset_idx %s idx=%s [offset]', repr(self), repr(idx))
        return idx

    def __getitem__(self, idx, crash_if_recurse=False, already_offset=False):
        input_idx = idx

        if not already_offset:
            idx = self._offset_idx(idx)

        extended_tape = False
        if idx.stop > len(self.tape):
            d = (idx.stop - len(self.tape))
            self.tape += BLANK_SYMBOL * d
            log.debug('__getitem__ idx.stop > len(self.tape); extended tape: %s', self)
            extended_tape = True

        if idx.start < 0:
            adx = abs(idx.start)
            self.tape = (BLANK_SYMBOL * adx) + self.tape
            self.offset += adx
            log.debug('__getitem__ idx.start < 0; extended tape: %s', self)
            extended_tape = True

        if extended_tape:
            if crash_if_recurse:
                raise Exception('internal error (probably): recursion shoud not happen here')
            return self.__getitem__(input_idx, crash_if_recurse=True)

        log.debug('__getitem__ fin(%s)', self.tape[idx])
        return self.tape[idx]

    def __setitem__(self, idx, symbols):
        log.debug('__setitem__ %s [%s] <= %s', repr(self), repr(idx), symbols)

        self.__getitem__(idx)
        idx = self._offset_idx(idx)

        before = self.tape[:idx.start]
        after  = self.tape[idx.stop:]

        log.debug('__setitem__ %s [%d:%d] => "%s" + "%s" + "%s"',
            repr(self), idx.start, idx.stop, before, symbols, after)

        self.tape = before + symbols + after

        log.debug('__setitem__ fin(%s)', repr(self))
