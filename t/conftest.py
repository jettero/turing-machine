#!/usr/bin/env python
# coding: utf-8

from collections import OrderedDict

import logging
import pytest

from turing.tape import Tape, BLANK_SYMBOL

log = logging.getLogger(__name__)

class AccessMapItem:
    """ A container to describe a tape access.

        tape = Tape('test')

        AccessMapItem(2, 's')
          means: access tape at idx 2
            and expect to see symbol 's'

        AccessMapItem(2, 4, 'st')
        AccessMapItem(slice(2,4), 'st') [equiv]
          means: access the tape at idx slice(2,4)
            and expect to see symbols 'st'
    """
    def __init__(self, *a):
        if len(a) == 3:
            self.idx = slice(*a[0:2])
            self.sym = a[2]
        elif len(a) == 2:
            self.idx, self.sym = a
        else:
            raise ValueError('AccessMapItem(idx,sym) or AccessMapItem(start,stop,sym)')

    def __str__(self):
        if isinstance(self.idx, slice):
            ret = [ '' if x is None else str(x) for x in (self.idx.start, self.idx.stop) ]
            ret = ':'.join(ret)
        else:
            ret = str(self.idx)
        return f'AMI<Tape[{ret}] => "{self.sym}">'

class AccessMapList(list):
    def __init__(self, *a):
        for item in a:
            if not isinstance(item, AccessMapItem):
                raise ValueError('items must be AccessMapItems')
        super().__init__(a)

ACCESS_MAP = OrderedDict()
ACCESS_MAP['boring tape']   = AccessMapList()
ACCESS_MAP['accessed tape'] = AccessMapList( AccessMapItem(2, 's') )
ACCESS_MAP['sliced tape']   = AccessMapList( AccessMapItem(2,4, 'st') )
ACCESS_MAP['backwards1']    = AccessMapList( AccessMapItem(-2, ' ') )
ACCESS_MAP['backwards2']    = AccessMapList( AccessMapItem(-5, -2, '   ') )

@pytest.fixture(scope='function', params=ACCESS_MAP.values(), ids=ACCESS_MAP.keys())
def a_tape(request):
    tape = Tape('test')
    tape.access_map = request.param
    log.debug("created a tape %s", repr(tape))
    for item in request.param:
        log.debug('fixture factory tape access %s', item)
        assert tape[item.idx] == item.sym
    log.debug("returning fixture %s", repr(tape))
    return tape
