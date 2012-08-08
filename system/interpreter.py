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
            
class Stack(object):
    def __init__(self, init = None, size = 64):
        self.size = size
        self.stack_w = [None] * size if init is None else init
        self.ptr = -1 if init is None else len(self.stack_w)

    def __len__(self):
        return self.ptr
        
    def append(self, obj):

        if self.ptr > len(self.stack_w):
            self.stack_w.extend([None] * 64)
            
        self.stack_w[self.ptr] = obj
        self.ptr += 1


    def pop(self):
        self.ptr -= 1
        val = self.stack_w[self.ptr]
        self.stack_w[self.ptr] = None
        assert self.ptr >= -1
        return val
    
    def tos(self):
        assert self.ptr >= 0
        return self.stack_w[self.ptr]
        
    def tos1(self):
        assert self.ptr >= 1
        return self.stack_w[self.ptr - 1]

    def tos2(self):
        assert self.ptr >= 2
        return self.stack_w[self.ptr - 2]

    def tos3(self):
        assert self.ptr >= 3
        return self.stack_w[self.ptr - 3]

class Interpreter(object):
    def __init__(self, bcode = None, stack = None, ip = 0, frame = None):
        self._bcode = array("H", bcode)
        self._ip = ip
        self._stack = Stack(size = 64) if stack is None else stack
        self._frame = frame

    def get_bcode(self):
        c = self._bcode[self._ip]
        self._ip += 1
        return c
    
    def LOAD_LOCAL(self):
        frame = self.get_bcode()
        slot = self.get_bcode()
        val = self._frame.get_slot(frame, slot)
        self._stack.append(val)


    def main_loop(self):
        stack = self._stack
        while self._ip < len(self._bcode):
            b = self.get_bcode()
            print b
            if b == BINARY_ADD:
                stack.append(s_add(stack.pop(), stack.pop()))
            if b == BINARY_SUB:
                stack.append(s_sub(stack.pop(), stack.pop()))

        print len(stack)
        assert len(stack) == 1
        return stack.pop()


def to_stack(*stk):
    stk = list(reversed(stk))
    return Stack(stk)

def to_bcode(*lst):
    """
     Converts a list of bytecodes to a bytestream
    """
    from struct import pack
    io = StringIO()
    for x in lst:
        io.write(pack("=H", x))

    return io.getvalue()





