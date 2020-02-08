#!/usr/bin/env python
# coding: utf-8

from turing.state import State

def test_state():
    s1 = State('one')
    assert str(s1) == 'one'

    s2 = State('one', 0)
    assert str(s2) == 'one, 0'

    # s1 should equal s2
    # but they should not hash the same
    assert s1 == s2
    for s in s1,s2:
        assert s in (s, )
        assert s in {s: True}

    assert s1 in (s2, )
    assert s1 not in {s2: True}

    assert s2 in (s1, )
    assert s2 not in {s1: True}
