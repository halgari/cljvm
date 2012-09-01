

class Object(object):
    _immutable_fields_ = ["int_value", "_w_head", "_w_tail", "_count", "_w_meta",
                          "_name", "_ns"]


def symbol(ns, name = None):
    if name is None:
        name = ns
        ns = None
    from symbol import W_Symbol
    return W_Symbol(ns, name)

def type(a):
    if a is None:
        return symbol("system", "Nil")
    return a.type()

def integer(i):
    from system.integer import W_Integer
    return W_Integer(i)
