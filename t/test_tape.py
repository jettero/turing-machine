#!/usr/bin/env python
# coding: utf-8

import logging
import pytest

from turing.tape import BLANK_SYMBOL

log = logging.getLogger(__name__)

def test_basic_get(a_tape):
    assert len(a_tape) == 4
    assert a_tape[0] == 't'
    assert a_tape[1] == 'e'
    assert a_tape == 'test'

def test_automagic_get_expansion(a_tape):
    assert a_tape[5] == BLANK_SYMBOL
    assert len(a_tape) == 6
    assert a_tape == 'test' + (BLANK_SYMBOL*2)

    assert a_tape[27] == BLANK_SYMBOL
    assert len(a_tape) == 28
    assert a_tape == 'test' + (BLANK_SYMBOL * 24)

def test_automagic_get_negspansion(a_tape):
    assert a_tape[-1] == BLANK_SYMBOL
    assert a_tape[0] == 't'
    assert a_tape == (BLANK_SYMBOL*1) + 'test'

    assert a_tape[-3] == BLANK_SYMBOL
    assert a_tape[0] == 't'
    assert a_tape == (BLANK_SYMBOL*3) + 'test'

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
    a_tape[2] = 'X'
    assert a_tape == 'teXt'

    a_tape[2] = 'XX'
    assert a_tape == 'teXXt'

    a_tape[1:3] = 'YY'
    assert a_tape == 'tYYXt'

def test_write_to_tape_at_neg1(a_tape):
    a_tape[-1] = 'Z'
    assert a_tape == 'Ztest'

def test_write_to_tape_at_neg1(a_tape):
    a_tape[-4:-1] = 'zoot suit'
    assert a_tape == 'zoot suit test'

def test_write_0123(a_tape):
    for i in range(4):
        a_tape[i] = str(i)
    assert str(a_tape).strip() == '0123'
