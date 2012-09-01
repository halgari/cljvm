
from system.core import Object
from system.rt import *

class Atom(Object):
    def __init__(self, w_initval):
        self._w_initval = w_initval

def atom_deref(self):
    return self._w_initval
