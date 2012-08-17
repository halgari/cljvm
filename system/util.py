from objspace import W_Int, nil, s_cons, w_false, w_true, Symbol

def tuple_to_app(form):
    lst = nil
    for x in range(len(form) - 1, -1, -1):
        lst = s_cons(data_to_app(form[x]), lst)
    return lst

def symbol_to_app(sym):
    return sym

def bool_to_app(b):
    return w_true if b else w_false

def data_to_app(form):
    tp = type(form)
    return mappers[tp](form)





mappers = {int: W_Int,
           tuple: tuple_to_app,
           Symbol: symbol_to_app,
           bool: bool_to_app}
