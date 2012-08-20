
print "WARNING: FAKING JIT...."


def elidable(f):
    return f

def promote(f):
    return f

def unroll_safe(f):
    return f

class JitDriver(object):
    def __init__(self, **kw):
        self.loc = kw["get_printable_location"]
        pass
    def jit_merge_point(self, **kw):
        print self.loc(kw["can_tail_call"], kw["form"])
        pass
    def can_enter_jit(self, **kw):
        print self.loc(kw["can_tail_call"], kw["form"])
