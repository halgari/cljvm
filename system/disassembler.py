__author__ = 'tim'
from consts import *

def dis(func):
    ip = 0
    while ip < len(func._bcode):
        print ip,
        bc = ord(func._bcode[ip])
        print bytecodes[bc],

        if bc in bytecodes_with_arg:
            ip += 1
            arg = ord(func._bcode[ip])
            print arg,

        if bc == LOAD_CONST:
            print func._consts[arg].toString(),

        print
        ip += 1