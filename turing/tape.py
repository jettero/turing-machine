#!/usr/bin/env python
# coding: utf-8

import re
import logging

log = logging.getLogger(__name__)

NULL = '\x00'

START_OF_TEXT = STX = '\x02'
END_OF_TEXT = ETX = '\x03'

FILE_SEPARATOR = FS = '\x1c'
GROUP_SEPARATOR = GS = '\x1d'
RECORD_SEPARATOR = RS = '\x1e'
UNIT_SEPARATOR = US = '\x1f'

# NOTE: thought about using NULL or RS or something, but settled on ' ' like
# the example -- it's just easier to read
BLANK_SYMBOL = ' '

PRINTABLE = bytearray(range(0x20, 0x7e+1)).decode() \
          + '«»'

class Tape:
    offset = 0

    @classmethod
    def read_file(cls, fh, bs=1024):
        tape = ''
        if 'b' in fh.mode:
            _read = lambda: fh.read(bs).decode()
        else:
            _read = lambda: fh.read(bs)
        r = _read()
        while r:
            tape += r
            r = _read()
        return cls(tape)

    def __init__(self, symbols=''):
        if isinstance(symbols, Tape):
            self.tape = symbols.tape
            self.offset = symbols.offset
        else:
            self.tape = symbols
        self.io_pos = 0

    def __str__(self):
        return self.tape

    def __repr__(self):
        ret = self.tape
        to_fix = set(re.findall(r' {8,}', ret))
        for t in sorted(to_fix, key=lambda x: -len(x)):
            ret = ret.replace(t, f"«{len(t)}»")
        to_fix = set(re.findall(r'[^'+PRINTABLE+']', ret))
        for t in to_fix:
            ret = ret.replace(t, f'\\x{ord(t):02x}')
        return f'##TAPE:{self.offset}##{ret}##'

    def __eq__(self, other):
        return self.tape == other

    def __len__(self):
        return len(self.tape)

    def _offset_idx(self, idx):
        orig = idx
        if isinstance(idx, slice):
            nstart = 0 if idx.start is None else idx.start + self.offset
            nstop  = len(self.tape) if idx.stop is None else idx.stop + self.offset
            idx = slice(nstart, nstop, idx.step)
            log.debug('_offset_idx (%s+%s or 0):(%s+%s or %d) -> %s',
                orig.start, self.offset,
                orig.stop , self.offset,
                len(self.tape),
                repr(idx)
            )

        else:
            idx += self.offset
            idx = slice(idx, idx+1, None)
            log.debug('_offset_idx %d+%d -> %s',
                orig, self.offset,
                repr(idx)
            )
        return idx

    def __getitem__(self, idx, crash_if_recurse=False, already_offset=False):
        input_idx = idx

        if not already_offset:
            idx = self._offset_idx(idx)

        extended_tape = False
        if idx.stop > len(self.tape):
            d = (idx.stop - len(self.tape))
            self.tape += BLANK_SYMBOL * d
            log.debug('__getitem__0 idx.stop > len(self.tape); extended tape: %s', self)
            extended_tape = True

        if idx.start < 0:
            adx = abs(idx.start)
            self.tape = (BLANK_SYMBOL * adx) + self.tape
            self.offset += adx
            log.debug('__getitem__1 idx.start < 0; extended tape: %s', self)
            extended_tape = True

        if extended_tape:
            if crash_if_recurse:
                raise Exception('internal error (probably): recursion shoud not happen here')
            return self.__getitem__(input_idx, crash_if_recurse=True)

        log.debug('__getitem__F %s[%s] --> "%s"', repr(self), repr(input_idx), self.tape[idx])
        return self.tape[idx]

    def __setitem__(self, idx, symbols):
        log.debug('__setitem__0 %s[%s] <= %s', repr(self), repr(idx), symbols)

        got = self[idx] # potentially expand tape
        log.debug('__setitem__1 got="%s" for [%s]', got, repr(idx))

        idx = self._offset_idx(idx)
        if idx.start < 0:
            by = abs(idx.start)
            log.debug('__setitem__2 extend tape by=%d', by)
            self.offset += by
            self.tape = symbols + self.tape

        else:
            before = self.tape[:idx.start]
            after  = self.tape[idx.stop:]
            log.debug('__setitem__3 before="%s" + symbols="%s" + after="%s"', before, symbols, after)
            self.tape = before + symbols + after

        log.debug('__setitem__F %s', repr(self))

    def strip(self, *a, **kw):
        return self.tape.strip(*a, **kw)

    def rstrip(self, *a, **kw):
        return self.tape.rstrip(*a, **kw)

    def lstrip(self, *a, **kw):
        return self.tape.lstrip(*a, **kw)

    def read(self, bs=-1):
        """ read from the tape as if it was a filehandle, including a 'bs' (blocksize) param

        if blocksize is negative, read will use the length of the tape for bs instead
        """
        start = self.io_pos
        end = len(self.tape) if bs < 0 else self.io_pos + bs
        ret = self.tape[start:end]
        self.io_pos += len(ret)
        return ret

    def tell(self):
        """ tell() the position in the tape as if it was a file handle """
        return self.io_pos

    def seek(self, pos, whence=0):
        """ attempt to emulate fh.seek(pos, whence=0), particularly this bit:

        * 0 -- start of stream (the default); offset should be zero or positive
        * 1 -- current stream position; offset may be negative
        * 2 -- end of stream; offset is usually negative

        """
        if whence == 0:
            self.io_pos = pos
        elif whence == 1:
            self.io_pos += pos
        elif whence == 2:
            self.io_pos = len(self.tape) + pos

    def write(self, blah):
        """ write to the tape as if it was some ordinary filehandle """

        before = self.tape[:self.io_pos]
        after  = self.tape[self.io_pos+len(blah):]
        self.tape = before + blah + after
        self.io_pos += len(blah)

    def replace(self, pattern, replacement):
        """ replace pattern with replacement in the internal tape and re-adjust
            the offset appropriately
        """

        # create silly string
        mark = NULL + "xXx" + NULL
        if mark in self.tape:
            raise ValueError('unexpected silly string')

        self[0:0] = mark
        tmp = self.tape.replace(pattern, replacement)
        self.offset = tmp.index(mark)
        self.tape = tmp.replace(mark, '')

def _save_state(state):
    state = tuple( str(x) for x in state if x is not None )
    return US.join(state) + US

def save_to_tape(initial, transitions, final, debug_control_codes=False):
    """
        STX and ETX are meant to indicat the start and stop of some text
        stream.  Apparently Data link Layer uses it along with Data Link
        Escape (DLE) to mark frames.  Here, we use it as a kind of frame
        header for our state table on tape

        The file separator (FS) is meant to separate files in a serial format
        (like a tape) we use this as part of our footer.

        The group separator (GS) is meant to separate database tables on
        tapes (or other serial formats). We use this to separate init and
        final state areas.

        The record separator (RS) might be used between rows of table data.
        We use it to separate states

        The unit separator (US) was meant to separate fields in a row, which
        we use to sparate fields in a state (iff there's more than one)

        overall, our format is:
        STX
          initial_state
        GS
          cur_state0 RS next_state0 RS
          cur_state1 RS next_state2 RS
          cur_state… RS next_state…
        GS
          final_state0 RS
          final_state1 RS
          final_state…
        ETX

        Again, states are stored like this

        State(init) -> init
        State(init, 1) -> init US 1
        State(init, 1, L) -> init US 1 US L
    """

    ret = Tape()
    ret.write(STX)

    # write init state
    ret.write( _save_state(initial) )
    ret.write(GS)

    # write transitions
    ret.write(RS.join([ RS.join([ _save_state(x) for x in item ])
        for item in transitions.items() ]))
    ret.write(GS)

    # write final states
    ret.write( RS.join([ _save_state(x) for x in final ]) )
    ret.write(ETX)

    if debug_control_codes:
        ret = \
        ret.replace(STX, '<STX>') \
           .replace(ETX, '<ETX>') \
           .replace(GS,  '<GS>') \
           .replace(RS,  '<RS>') \
           .replace(US,  '<US>')

    return ret
