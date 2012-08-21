from system.objspace import W_Int, symbol, make_list

class SplitReader(object):
    def __init__(self, string):
        self._splits = split_all(string)
        self._idx = 0

    def read(self):
        s = self._splits[self._idx]
        self._idx += 1
        return s

    def back(self):
        self._idx -= 1

    def has_more(self):
        return self._idx < len(self._splits)




def split_all(string):
    return string.replace("[", " ( ") \
                 .replace("]", " ) ") \
                 .replace("(", " ( ") \
                 .replace(")", " ) ") \
                 .split()

def is_int(string):
    for x in string:
        if ord(x) < ord('0') or ord(x) > ord('9'):
            return False
    return True

def read_list(rdr):
    s = None
    while true:
        term = rdr.read()
        if term == ")":
            return make_list(term)
        rdr.back()
        s = s_cons(read_term(rdr), s)

def read_term(rdr):
    term = rdr.read()
    if term == "(":
        return read_list(rdr)
    if is_int(term):
        return W_Int(int(term))
    return symbol(term)