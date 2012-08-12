
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
"JUMP_IF_FALSE",
"IS_EQ",
"JUMP",
"CUR_FUNC"]


for x in range(len(bytecodes)):
    globals()[bytecodes[x]] = x


bytecodes_with_arg = {LOAD_ARG: 1, LOAD_CONST : 1, CALL_FUNCTION :1 , TAIL_CALL :1, JUMP_IF_FALSE :1, JUMP :1}