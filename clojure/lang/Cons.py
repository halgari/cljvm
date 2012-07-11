from system.objspace import *


@typedef
def Cons(first, next, _meta):
    return PersistentObject(types["Cons"], [first, next, _meta])

@extend(Cons, "ISeq")
def first(obj):
    return s_fget(obj, "first")

@extend(Cons, "ISeq")
def next(obj):
    return s_fget(obj, "next")

@extend(Cons, "ISeq")
def meta(obj):
    return s_fget(obj, "_meta")

@extend(Cons, "ISeq")
def with_meta(obj, w_meta):
    return s_with(obj, "_meta", w_meta)
