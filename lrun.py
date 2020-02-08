#!/usr/bin/env python
# encoding: utf-8

import logging
import argparse

from turing.tape import Tape as T, BLANK_SYMBOL
from turing.state import State as S
from turing.machine import TuringMachine as TM

def main(args):
    tape = T('010011')
    init = 'init'
    final= 'final'
    trans = {
        S('init', 0): S('init', 1, 'R'),
        S('init', 1): S('init', 0, 'R'),
        S('init', BLANK_SYMBOL): S('final', BLANK_SYMBOL, 'N')
    }
    tm = TM(tape=tape, initial_state=init, final_states=final, transition_function=trans)

    print('Input on Tape:')
    print(f' {tape}')
    print('')

    step_no = 0
    while not tm.final:
        step_no += 1
        print(f'step-{step_no}')
        tm.step()
        if args.max_steps > 0 and step_no >= args.max_steps:
            print(' ... max steps, break')
            break

    print('')
    print('Result of the Turing machine computation:')
    print(f' {tm.tape}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser( # description='this program',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('-m', '--max-steps', type=int, default=50)

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.ERROR)

    try: main(args)
    except KeyboardInterrupt: pass
