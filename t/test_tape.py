#!/usr/bin/env python
# coding: utf-8

import logging
import pytest

from turing.tape import BLANK_SYMBOL

log = logging.getLogger(__name__)

def _low_high_mstr(a_tape):
    low = 0
    high = len(a_tape)-1
    for item in a_tape.access_map:
        if isinstance(item.idx, slice) and item.idx.start < low:
            low = item.idx.start
        elif isinstance(item.idx, int) and item.idx < low:
            low = item.idx
    mstr = (' ' * abs(low)) + 'test'
    return low,high,mstr

def test_basic_get(a_tape):
    low,high,mstr = _low_high_mstr(a_tape)

    assert len(a_tape) == len(mstr)
    assert a_tape[0] == 't'
    assert a_tape[1] == 'e'
    assert a_tape == mstr

def test_automagic_get_expansion(a_tape):
    low,high,mstr = _low_high_mstr(a_tape)

    assert a_tape[5] == BLANK_SYMBOL
    assert len(a_tape) == len(mstr) + 2
    assert a_tape == mstr + (BLANK_SYMBOL*2)

    assert a_tape[27] == BLANK_SYMBOL
    assert len(a_tape) == len(mstr) + (28-4)
    assert a_tape == mstr + (BLANK_SYMBOL * (28-4))

def test_automagic_get_negspansion(a_tape):
    low,high,mstr = _low_high_mstr(a_tape)

    if low > -1:
        low = -1
        mstr = ' ' + mstr

    assert a_tape[-1] == BLANK_SYMBOL
    assert a_tape[0] == 't'
    assert a_tape == mstr

    if low > -3:
        d = abs(-3 + abs(low))
        low = -3
        mstr = (' ' * d) + mstr

    assert a_tape[-3] == BLANK_SYMBOL
    assert a_tape[0] == 't'
    assert a_tape == mstr

def test_range_0_to_4(a_tape):
    assert a_tape[0:4] == 'test'

def test_range_start_to_4(a_tape):
    assert a_tape[:4].strip() == 'test'

def test_range_0_to_end(a_tape):
    assert a_tape[0:].strip() == 'test'

def test_range_neg20_to_end(a_tape):
    assert a_tape[-20:].rstrip() == (BLANK_SYMBOL * 20) + 'test'

def test_range_neg20_to_pls20(a_tape):
    assert a_tape[-20:20] == (BLANK_SYMBOL * 20) + 'test' + (BLANK_SYMBOL * 16)

def test_range_neg12_to_neg7(a_tape):
    assert a_tape[-12:-7] == BLANK_SYMBOL * 5

def test_range_start_to_neg7(a_tape):
    assert a_tape[-20] == BLANK_SYMBOL
    assert a_tape[:-7] == BLANK_SYMBOL * 13

def test_range_start_to_neg1(a_tape):
    assert a_tape[-20] == BLANK_SYMBOL
    assert a_tape[:-1] == BLANK_SYMBOL * 19

def test_range_neg1_to_end(a_tape):
    assert a_tape[-1:].rstrip() == ' test'

def test_range_neg2_to_pls2(a_tape):
    assert a_tape[-2:2] == '  te'

def test_write_to_tape(a_tape):
    low,high,mstr = _low_high_mstr(a_tape)

    a_tape[2] = 'X'
    assert a_tape == mstr.replace('test', 'teXt')

    a_tape[2] = 'XX'
    assert a_tape == mstr.replace('test', 'teXXt')

    a_tape[1:3] = 'YY'
    assert a_tape == mstr.replace('test', 'tYYXt')

def test_write_to_tape_at_neg1(a_tape):
    low,high,mstr = _low_high_mstr(a_tape)

    a_tape[-1] = 'Z'
    assert a_tape == mstr.replace('test', 'Ztest').replace(' Ztest', 'Ztest')

def test_write_to_tape_at_neg4_1(a_tape):
    low,high,mstr = _low_high_mstr(a_tape)

    # suppose we have this string
    # "     test"
    #  ⁵⁴³²¹0123  # pretend tape indexes (superscript being negative)
    #  012345678  # actual tape indexes

    # if our write is a_tape[-4:-1] = "zoot suit":
    # then our pretend to actual conversion is:
    # -4:-1 -> 1:4
    #
    # The text we need to keep from before the range is:
    # before = [:1] = " "
    #
    # and the text we keep after the range is:
    #   after = [4:] = " test"

    for i in range(3,-1,-1):
        j = (' ' * i) + ' test'
        if j in mstr:
            pstr = mstr
            mstr = mstr.replace(j, 'zoot suit test')
            log.debug('i=%d j="%s" mstr="%s" -> "%s"', i, j, pstr, mstr)
            break

    a_tape[-4:-1] = 'zoot suit'
    assert a_tape == mstr

def test_write_0123(a_tape):
    for i in range(4):
        a_tape[i] = str(i)
    assert str(a_tape).strip() == '0123'

def test_read_write(a_tape):
    assert a_tape == 'test'
    assert a_tape.read() == 'test'
    a_tape.seek(0)
    a_tape.write('this is a test')
    assert a_tape.read() == ''
    a_tape.seek(0)
    assert a_tape.read() == 'this is a test'
