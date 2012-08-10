from system.objspace import s_unwrap_int
from StringIO import StringIO
from consts import *
from array import array
from objspace import *
from pypy.rlib.jit import JitDriver

jitdriver = JitDriver(greens=['ip', 'code', 'args', 'func'], reds=['stack'])



class Interpreter(object):
    def __init__(self, f = None):
        self._bcode = f._bcode
        self._ip = 0
        self._stack = []
        self._call_stack = [f]
        self._arg_stack = []
        self._ip_stack = []

    def get_bcode(self):
        c = ord(self.top_func()._bcode[self._ip])
        self._ip += 1
        return c
    
    def LOAD_LOCAL(self):
        frame = self.get_bcode()
        slot = self.get_bcode()
        val = self._frame.get_slot(frame, slot)
        self._stack.append(val)

    def push(self, val):
        self._stack.append(val)

    def pop(self):
        return self._stack.pop()

    def top_func(self):
        return self._call_stack[len(self._call_stack) - 1]

    def make_arg_stack(self, f, alen):
        args = []
        assert alen == len(f._args)
        args = [None] * alen
        for x in range(alen -1, -1, -1):
            args[x] = self.pop()
        self._arg_stack.append(args)

    def cur_arg_stack(self):
        return self._arg_stack[len(self._arg_stack) - 1]

    def get_arg(self, offset):
        return self.cur_arg_stack()[offset]

    def remove_stack_frame(self, f, alen):
        return self._arg_stack.pop()


    def main_loop(self, *args):
        args = list(args)
        for x in range(len(args)):
            self.push(args[x])

        self.make_arg_stack(self.top_func(), len(args))

        #import disassembler
        #disassembler.dis(self.top_func())

        while True:
            #print self.cur_arg_stack
            while self._ip < len(self.top_func()._bcode):
                #disassembler.trace(self.top_func(), self._ip, self.cur_arg_stack())

                jitdriver.jit_merge_point(ip = self._ip,
                                          code = self.top_func()._bcode,
                                          args = self.cur_arg_stack(),
                                          func = self.top_func(),
                                          stack = self._stack)

                b = self.get_bcode()
                if b == BINARY_ADD:
                    self.push(s_add(self.pop(), self.pop()))
                elif b == BINARY_SUB:
                    self.push(s_sub(self.pop(), self.pop()))
                elif b == LOAD_CONST:
                    c = self.get_bcode()
                    self.push(self.top_func()._consts[c])
                elif b == LOAD_ARG:
                    c = self.get_bcode()
                    self.push(self.get_arg(c))
                elif b == CALL_FUNCTION:
                    args = self.get_bcode()
                    func = self.pop()
                    self._call_stack.append(func)
                    self._ip_stack.append(self._ip)
                    self._ip = 0
                    self.make_arg_stack(self.top_func(), args)
                elif b == TAIL_CALL:
                    args = self.get_bcode()
                    func = self.pop()
                    self._call_stack.pop()
                    self._call_stack.append(func)
                    self._ip = 0
                    self._arg_stack.pop()
                    self.make_arg_stack(self.top_func(), args)
                elif b == IS_EQ:
                    self.push(s_eq(self.pop(), self.pop()))
                elif b == JUMP_IF_FALSE:
                    offset = self.get_bcode()
                    a = self.pop()
                    if isinstance(a, W_Bool) and not s_unwrap_bool(a):
                        self._ip += offset
                elif b == JUMP:
                    offset = self.get_bcode()
                    self._ip += offset
                elif b == CUR_FUNC:
                    self.push(self.top_func())
    
                #else:
                #    raise Exception("Unknown bytecode " + ord(b))

            self._arg_stack.pop()
            if len(self._arg_stack) == 0: 
                assert len(self._stack) == 1
                return self.pop()
            else: #jump back to caller
                self._call_stack.pop()
                self._ip = self._ip_stack.pop()

class Function(Object):
    """Defines a native function"""
    def __init__(self, bcode, args = None, consts = None):
        self._bcode = bcode
        self._args = args
        self._consts = consts
    def toString(self):
        return "Function"




def to_stack(*stk):
    stk = Stack(list(stk))
    return stk

def to_bcode(*lst):
    """
     Converts a list of bytecodes to a bytestream
    """
    arr = []
    for x in lst:
        arr.append(x)

    return arr





