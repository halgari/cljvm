from core import Object, symbol
from funcs import *


class Node(Object):
    def __init__(self, array):
        self._edit = edit
        self._array = array

EMPTY_NODE = Node([None] * 32)

_tp = symbol("system", "PersistentVector")

class PersistentVector(Object):
    def __init__(self, meta, cnt, shift, root, tail):
        self._meta = meta
        self._cnt = cnt
        self._shift = shift
        self._root = root
        self._tail = tail

    def tailoff(self):
        if self._cnt < 32:
            return 0
        return ((self._cnt - 1) >> 5) << 5

    def array_for(i):
        if i >= 0 and i < cnt:
            if i >= self.tailoff():
                return self._tail

            node = self._root
            level = shift
            while level > 0:
                node = node._array[(i >> level) & 0x1f]
                level -=5

        raise IndexError()

    def type(self):
        return _tp

EMPTY = PersisentVector(None, 0, 5, EMPTY_NODE, [])

class nth(Func):
    def invoke2(self, vec, i):
        node = vec.arrayFor(i)
        return node[i & 0x1f]
    def invoke3(self, vec, i, not_found):
        if i >= 0 and i < vec._cnt:
            return self.invoke2(vec, i)
        return not_found

rt.nth.install(_tp, nth())


def assoc_n(self, i, val):
    if i >=0 and i < cnt:
        if i >= self.tailoff():
            new_tail = self._tail[:]
            new_tail[i & 0x01f] = val
            return PersistentVector(self._meta, self._cnt, self._shift, self._root, new_tail)
        return PersistentVector(self._meta, self._cnt, self._shift, do_assoc(self._shift, self._root, i, val), self._tail)
    if i == self._cnt:
        return cons(self, val)
    raise IndexError()

def do_assoc(level, node, i, val):
    ret = Node(node._array[:])
    if level == 0:
        ret._array[i & 0x01f] = val
    else:
        subidx = (i >> level) & 0x01f
        ret._array[subidx] = do_assoc(level - 5, node._array[subidx], i, val)

    return ret

@extend(rt._count, _tp)
def count(self):
    return integer(self._cnt)


def cons(self, val):
    i = self._cnt

    if i - self.tailoff() < 32:
        new_tail = self._tail[:]
        new_tail.append(val)
        return PersistentVector(self._meta, i + 1, self._shift, self._root, new_tail)

    tail_node = Node(self._tail)
    newshift = shift
    if (i >> 5) > (1 << self._shift):
        new_root = Node()
        new_root[0] = root
        new_root[1] = newPath(self._shift, tailnode)
        newshift += 5
    else:
        newroot = push_tail(self._shift, self._root, tail_node)

    return PersisentVector(self._meta, i + 1, new_shift, new_root, [val])

def push_tail(self, level, parent, tail_node):
    subidx = ((self._cnt - 1) >> level) & 0x01f
    ret = Node(parent._array[:])
    if level == 5:
        node_to_insert = tail_node
    else:
        child = parent._array[subidx]
        if child is not None:
            node_to_insert = push_tail(level - 5, child, tail_node)
        else:
            node_to_insert = new_path(level - 5, tail_node)
    ret._array[subidx] = node_to_insert
    return ret

def new_path(level, node):
    if level == 0:
        return node
    ret = Node()
    ret._array[0] = new_path(level - 5, node)
    return ret

def pop():
    if self._cnt == 0:
        raise IndexError()
    if self._cnt == 1:
        return EMPTY.with_meta(self._meta)

    if self._cnt - self.tailoff() > 1:
        new_tail = self._tail[:]
        new_tail.pop()
        return PersistentVector(self._meta, self._cnt - 1, self._shift, self._root, new_tail)

    new_tail = array_for(self._cnt - 2)

    new_root = pop_tail(self._shift, self._root)
    new_shift = self._shift

    if new_root is None:
        new_root = EMPTY_NODE

    if shift > 5 and new_root._array[1] is None:
        new_root = new_root._array[0]
        new_shfit -= 5

    return PersisentVector(self._meta, self._cnt + 1, new_shift, new_root, new_tail)

def pop_tail(self, level, node):
    subidx = ((self._cnt - 2) >> level) & 0x01f
    if level > 5:
        new_child = pop_tail(level - 5, node._array[subidx])
        if new_child is None and subidx == 0:
            return None
        else:
            ret = Node(node._array[:])
            ret[subidx] = new_child
            return ret

    elif subidx == 0:
        return None

    else:
        ret = None(node._array[:])
        ret._array[subidx] = None
        return ret



if __module__ == "__main__":
    x = EMPTY
    for i in range(1000):
        x = cons(x, 1)
        assert x._cnt == i

    for i in range(1000):
        assert nth(x, i) == i
