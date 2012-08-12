from system.objspace import s_unwrap_int
from StringIO import StringIO
from consts import *
from array import array
from objspace import *
from pypy.rlib.jit import JitDriver




def get_location(ip, func, interp):
    import consts
    cc = ord(func._bcode[ip])
    s = []
    s.append(str(ip))

    s.append(consts.bytecodes[cc])

    #if cc in consts.bytecodes_with_arg:
    #    s.append(str(ord(func._bcode[ip + 1])))

    #if cc == LOAD_ARG:
    #    s.append(interp.cur_arg().getNth(W_Int(ord(func._bcode[ip + 1]))).toString())

    return "\t".join(s)


jitdriver = JitDriver(greens=['ip', 'func', 'interp'],
                      reds=['stack', 'args'],
                      get_printable_location = get_location
)

@elidable
def get_bcode_at(func, ip):
    return ord(func._bcode[ip])


class Interpreter(object):
    def __init__(self, f = None):
        self._ip = 0
        self._call_stack = W_InternalList(f, nil)
        self._arg_stack = nil
        self._ip_stack = nil
        self._sp = 0
        self._stack = [None] * 64

    def get_bcode(self):
        c = get_bcode_at(self.top_func(), self._ip)
        self._ip += 1
        return c
    
    def push(self, val):
        #self._stack = s_cons(val, self._stack)
        self._stack[self._sp] = val
        self._sp += 1

    def pop(self):
        #val = self._stack.getFirst()
        #self._stack = self._stack.getNext()
        self._sp -= 1
        val = self._stack[self._sp]
        self._stack[self._sp] = None
        return val

    def top_func(self):
        return self._call_stack.getFirst()

    def push_arg_stack(self, f, alen):
        args = []
        assert alen == len(f._args)
        args = [None] * alen
        for x in range(alen -1, -1, -1):
            args[x] = self.pop()
        self._arg_stack = s_cons(W_Array(args), self._arg_stack)

    def cur_arg_stack(self):
        return self._arg_stack.getFirst()

    def get_arg(self, offset):
        return self.cur_arg_stack().getNth(W_Int(offset))

    def pop_arg_stack(self):
        self._arg_stack = self._arg_stack.getNext()

    def push_ip(self, ip):
        self._ip_stack = s_cons(W_Int(ip), self._ip_stack)

    def pop_ip(self, ip):
        ip = s_unwrap_int(self._ip_stack.getFirst())
        self._ip_stack = self._ip_stack.getNext()
        return ip

    def push_call_stack(self, cf):
        self._call_stack = s_cons(cf, self._call_stack)

    def pop_call_stack(self):
        self._call_stack = self._call_stack.getNext()

    def cur_arg(self):
        return W_Array([]) if self._arg_stack is nil else self._arg_stack.getFirst()

    def tos(self):
        return self._stack[self._sp - 1]



    def main_loop(self, *args):
        args = list(args)
        for x in range(len(args)):
            self.push(args[x])

        self.push_arg_stack(self.top_func(), len(args))

        import disassembler
        #disassembler.dis(self.top_func())

        while True:
            #print self.cur_arg_stack
            while self._ip < len(self.top_func()._bcode):
                #print get_location(self._ip, self.top_func(), self)
                jitdriver.jit_merge_point(ip = self._ip,
                                          func = self.top_func(),
                                          args = self.cur_arg(),
                                          stack = self._sp,
                                          interp = self)

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
                    self.push_call_stack(func)
                    self.push_ip(self._ip)
                    self._ip = 0
                    self.push_arg_stack(self.top_func(), args)
                elif b == TAIL_CALL:
                    args = self.get_bcode()
                    func = self.pop()
                    self.pop_call_stack()
                    self.push_call_stack(func)
                    self._ip = 0
                    self.pop_arg_stack()
                    self.push_arg_stack(self.top_func(), args)
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

            self.pop_arg_stack()
            if self._arg_stack is nil:
                return self.pop()
            #else: #jump back to caller
            #    self._call_stack.pop()
            #    self._ip = self._ip_stack.pop()

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





