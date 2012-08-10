
bytecodes = [
"BINARY_ADD",
"BINARY_SUB",
"BINARY_MUL",
"BINARY_DIV",
"BINARY_MOD",
"LOAD_ARG",
"LOAD_CONST",
"CALL_FUNCTION",
"TAIL_CALL",
"JUMP_IF_TRUE",
"IS_EQ"]


for x in range(len(bytecodes)):
    globals()[bytecodes[x]] = x