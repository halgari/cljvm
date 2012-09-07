
from system.core import Object, symbol
from system.rt import extend
import system.rt as rt
from system.bool import w_true, w_false
from system.util import intern

_tp = symbol("system", "Keyword")

class Keyword(Object):
    def __init__(self, ns, name):
        self._ns = ns
        self._name = name

    def type(self):
        return _tp



@extend(rt.equals, _tp)
def keword_equals(self, other):
    if self is other:
        return w_true
    return w_false


class KeywordCache(object):
    def __init__(self):
        self._cache = {}

    def intern(self, ns, name):
        ns = intern(ns)
        name = intern(name)

        if ns not in self._cache:
            self._cache[ns] = {}

        if name not in self._cache[ns][name]:
            self._cache[ns][name] = Keyword(ns, name)

        return self._cache[ns][name]


keyword_cache = KeywordCache()


def keyword(ns, name):
    return keyword_cache.intern(ns, name)
