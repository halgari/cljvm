__author__ = 'tim'
from consts import *

def dis(func, ip = 0, exit = False, args_w = None):
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

        if bc == LOAD_ARG and args_w:
            print args_w[arg].toString(),

        print
        ip += 1
        if exit:
            break

def trace(func, ip, args_w):
    dis(func, ip, True, args_w)