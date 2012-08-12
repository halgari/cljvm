__author__ = 'tim'
from consts import *
from objspace import W_Int

def dis(func, ip = 0, exit = False, args_w = None):
    s = []
    while ip < len(func._bcode):
        s.append(str(ip))
        bc = ord(func._bcode[ip])
        s.append(bytecodes[bc])

        arg = -1
        if bc in bytecodes_with_arg:
            ip += 1
            arg = ord(func._bcode[ip])
            s.append(str(arg))

        if bc == LOAD_CONST:
            s.append(func._consts[arg].toString())

        if bc == LOAD_ARG and args_w is not None:
            s.append(args_w.getNth(W_Int(arg)).toString())

        ip += 1
        if exit:
            break
    return "\t".join(s)

def trace(func, ip, args_w):
    return dis(func, ip, True, args_w)