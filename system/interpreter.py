from system.objspace import s_unwrap_int
from StringIO import StringIO
from consts import *
from array import array
from objspace import *

class SlotFrame(object):
    def __init__(self, w_slots, prev = None):
        self._prev = prev
        self._slots = [None] * s_unwrap_int(w_slots)
        
    def set_slot(self, slot, w_value):
        """
        Sets the value of a slot

        >>> from objspace import *
        >>> s = SlotFrame(W_Int(2))
        >>> s.set_slot(0, W_Int(42))
        >>> s_unwrap_int(s._slots[0])
        42
        """

        assert self._slots[slot] is None
        
        self._slots[slot] = w_value
        
    def get_slot_fast(self, slot):
        """
        Gets the value of a slot

        >>> from objspace import *
        >>> s = SlotFrame(W_Int(2))
        >>> s.set_slot(0, W_Int(21))
        >>> s_unwrap_int(s.get_slot_fast(0))
        21
        """
        assert slot >= 0 and slot < len(self._slots)
        return self._slots[slot]
        
    def get_slot(self, level, slot):
        """
        Gets the value of a slot

        >>> from objspace import *
        >>> s = SlotFrame(W_Int(2))
        >>> s2 = SlotFrame(W_Int(2), s)
        >>> s.set_slot(0, W_Int(21))
        >>> s2.set_slot(1, W_Int(42))
        >>> s_unwrap_int(s2.get_slot(1, 0))
        21
        >>> s_unwrap_int(s2.get_slot(0, 1))
        42
        """
        if level == 0:
            return self._slots[slot]
            
        assert level > 0
        assert self._prev is not None
        return self._prev.get_slot(level - 1, slot)


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
        for x in range(alen):
            args.append(self.pop())
        self._arg_stack.append(args)

    def cur_arg_stack(self):
        return self._arg_stack[len(self._arg_stack) - 1]

    def get_arg(self, offset):
        return self.cur_arg_stack()[offset]

    def remove_stack_frame(self, f, alen):
        return self._arg_stack.pop()


    def main_loop(self, *args):
        for x in range(len(args) - 1, -1, -1):
            self.push(args[x])

        self.make_arg_stack(self.top_func(), len(args))

        while True:
            while self._ip < len(self.top_func()._bcode):
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
                elif b == JUMP_IF_TRUE:
                    offset = self.get_bcode()
                    a = self.pop()
                    if isinstance(a, W_Bool) and s_unwrap_bool(a):
                        self._ip += offset
    
                else:
                    raise Exception("Unknown bytecode " + ord(b))

            self._arg_stack.pop()
            if len(self._arg_stack) == 0: 
                assert len(self._stack) == 1
                return self.pop()
            else: #jump back to caller
                self._call_stack.pop()
                self._ip = self._ip_stack.pop()

class Function(object):
    """Defines a native function"""
    def __init__(self, bcode, args = None, consts = None):
        self._bcode = bcode
        self._args = args
        self._consts = consts




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





