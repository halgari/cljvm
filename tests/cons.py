def run(self):
    from system.objspace import W_Int, s_type, Integer, s_unwrap_int
    from clojure.lang.Cons import Cons
    from clojure.rt import first, next
    c = Cons(W_Int(1), None, None)
    f = first(c)
    tp = s_type(f)
    assert(tp is Integer)

    for x in range(10):
        c = Cons(W_Int(x), c, None)

    for x in range(10):
        self.assertEqual(s_unwrap_int(first(c)), 9-x)
        c = next(c)



    assert(s_type(first(c)) is Integer)

