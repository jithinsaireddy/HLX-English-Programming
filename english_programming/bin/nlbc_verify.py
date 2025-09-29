from english_programming.bin.uleb128 import read_uleb128
from typing import List

OP_LOAD_CONST  = 0x01
OP_LOAD_NAME   = 0x02
OP_STORE_NAME  = 0x03
OP_ADD         = 0x04
OP_PRINT       = 0x05
OP_BUILD_LIST  = 0x06
OP_INDEX       = 0x07
OP_BUILD_MAP   = 0x08
OP_GET_ATTR    = 0x09
OP_JUMP        = 0x0A
OP_JUMP_IF_FALSE=0x0B
OP_CALL        = 0x0C
OP_RETURN      = 0x0D
OP_LT          = 0x0E
OP_SUB         = 0x0F
OP_MUL         = 0x10
OP_DIV         = 0x11
OP_CONCAT      = 0x12
OP_LEN         = 0x13
OP_EQ          = 0x14
OP_LE          = 0x15
OP_GE          = 0x16

OP_WRITEFILE   = 0x20
OP_READFILE    = 0x21
OP_APPENDFILE  = 0x22
OP_DELETEFILE  = 0x23
OP_HTTPGET     = 0x40
OP_HTTPPOST    = 0x41
OP_IMPORTURL   = 0x50
OP_NEW         = 0x30
OP_GETFIELD    = 0x31
OP_SETFIELD    = 0x32
OP_CALL_METHOD = 0x33
OP_SETUP_CATCH = 0x61
OP_END_TRY     = 0x62
OP_THROW       = 0x63
OP_AWAIT       = 0x70
OP_ASYNC_READFILE = 0x71
OP_ASYNC_HTTPGET  = 0x72
OP_SCHEDULE       = 0x73
OP_RUN_TASKS      = 0x74
OP_THROW_T        = 0x75
OP_SETUP_CATCH_T  = 0x76
OP_SET_NEW        = 0x80
OP_SET_ADD        = 0x81
OP_SET_CONTAINS   = 0x82
OP_CSV_PARSE      = 0x90
OP_YAML_PARSE     = 0x91
OP_CSV_STRINGIFY  = 0x92
OP_YAML_STRINGIFY = 0x93
OP_ANNOTATE_FUNC  = 0xB0
OP_ITER_NEW       = 0xA0
OP_ITER_NEXT      = 0xA1
OP_ITER_HAS_NEXT  = 0xA2
OP_ASYNC_SLEEP    = 0x78
OP_ASYNC_CONNECT  = 0x79
OP_ASYNC_SEND     = 0x7A
OP_ASYNC_RECV     = 0x7B
OP_STRUPPER       = 0xA6
OP_STRLOWER       = 0xA7
OP_STRTRIM        = 0xA8
OP_LIST_APPEND    = 0xA9
OP_LIST_POP       = 0xAA
OP_MAP_PUT        = 0xAB
OP_MAP_GET        = 0xAC


def verify_code(consts, syms, code):
    i = 0
    n = len(code)
    # simple stack effect tracker (approximate)
    stack = 0
    def need(k):
        if stack < k:
            raise ValueError("Stack underflow")
    while i < n:
        op = code[i]; i += 1
        if op == OP_LOAD_CONST:
            idx, i = read_uleb128(code, i)
            if idx >= len(consts):
                raise ValueError("LOAD_CONST out of range")
            stack += 1
        elif op == OP_LOAD_NAME:
            sidx, i = read_uleb128(code, i)
            if sidx >= len(syms):
                raise ValueError("LOAD_NAME sym out of range")
            stack += 1
        elif op == OP_STORE_NAME:
            sidx, i = read_uleb128(code, i)
            if sidx >= len(syms):
                raise ValueError("STORE_NAME sym out of range")
            need(1); stack -= 1
        elif op == OP_ADD:
            need(2); stack -= 1
        elif op == OP_SUB:
            need(2); stack -= 1
        elif op == OP_MUL:
            need(2); stack -= 1
        elif op == OP_DIV:
            need(2); stack -= 1
        elif op == OP_CONCAT:
            need(2); stack -= 1
        elif op == OP_LEN:
            need(1); stack += 0  # pop then push -> net 0
        elif op == OP_EQ or op == OP_LE or op == OP_GE:
            need(2); stack -= 1
        elif op == OP_PRINT:
            need(1); stack -= 1
        elif op == OP_SET_NEW:
            stack += 1
        elif op == OP_SET_ADD:
            need(2); stack -= 1
        elif op == OP_SET_CONTAINS:
            need(2); stack -= 1
        elif op == OP_BUILD_LIST:
            count, i = read_uleb128(code, i)
            need(count); stack -= count; stack += 1
        elif op == OP_INDEX:
            need(2); stack -= 1
        elif op == OP_BUILD_MAP:
            pairs, i = read_uleb128(code, i)
            need(pairs * 2); stack -= (pairs * 2); stack += 1
        elif op == OP_GET_ATTR:
            name_idx, i = read_uleb128(code, i)
            if name_idx >= len(syms):
                raise ValueError("GET_ATTR sym out of range")
            need(1)
        elif op == OP_JUMP:
            off, i = read_uleb128(code, i)
            tgt = i + off
            if not (0 <= tgt <= n):
                raise ValueError("JUMP target out of code bounds")
        elif op == OP_JUMP_IF_FALSE:
            off, i = read_uleb128(code, i)
            need(1); stack -= 1
            tgt = i + off
            if not (0 <= tgt <= n):
                raise ValueError("JUMP_IF_FALSE target out of code bounds")
        elif op == OP_CALL:
            fidx, i = read_uleb128(code, i)
            argc, i = read_uleb128(code, i)
            if fidx >= len(syms):
                raise ValueError("CALL function sym out of range")
            need(argc); stack -= argc; stack += 1
        elif op == OP_RETURN:
            # allow empty return as None
            if stack > 0:
                stack -= 1
            # after return code following is dead; no need to continue
            return True
        elif op == OP_LT:
            need(2); stack -= 1
        elif op == OP_WRITEFILE:
            need(2); stack -= 2
        elif op == OP_READFILE:
            need(1); stack -= 1; stack += 1
        elif op == OP_APPENDFILE:
            need(2); stack -= 2
        elif op == OP_DELETEFILE:
            need(1); stack -= 1
        elif op == OP_HTTPGET:
            need(1); stack -= 1; stack += 1
        elif op == OP_HTTPPOST:
            need(2); stack -= 2; stack += 1
        elif op == OP_IMPORTURL:
            need(1); stack -= 1; stack += 1
        elif op == OP_AWAIT:
            need(1); # pop future-like, push result
        elif op == OP_ASYNC_READFILE:
            need(1); stack -= 1; stack += 1
        elif op == OP_ASYNC_HTTPGET:
            need(1); stack -= 1; stack += 1
        elif op == OP_ASYNC_SLEEP:
            # has operand; pushes future-like
            ms, i = read_uleb128(code, i); stack += 1
        elif op == OP_ASYNC_CONNECT:
            host_idx, i = read_uleb128(code, i); port, i = read_uleb128(code, i); stack += 1
        elif op == OP_ASYNC_SEND:
            need(2); stack -= 1
        elif op == OP_ASYNC_RECV:
            need(1); stack += 1
        elif op == OP_SCHEDULE:
            need(1); stack -= 1
        elif op == OP_RUN_TASKS:
            # pushes results list
            stack += 1
        elif op == OP_NEW:
            idx, i = read_uleb128(code, i)
            stack += 1
        elif op == OP_GETFIELD:
            idx, i = read_uleb128(code, i)
            need(1)
        elif op == OP_SETFIELD:
            idx, i = read_uleb128(code, i)
            need(2); stack -= 2
        elif op == OP_CALL_METHOD:
            midx, i = read_uleb128(code, i)
            argc, i = read_uleb128(code, i)
            need(argc + 1); stack -= argc; stack += 1
        elif op == OP_SET_NEW:
            stack += 1
        elif op == OP_SET_ADD:
            need(2); stack -= 1  # pop set and val, push set back
        elif op == OP_SET_CONTAINS:
            need(2); stack -= 1  # pop set and val, push bool
        elif op == OP_CSV_PARSE:
            need(1); stack -= 1; stack += 1
        elif op == OP_CSV_STRINGIFY:
            need(1); stack -= 1; stack += 1
        elif op == OP_YAML_PARSE:
            need(1); stack -= 1; stack += 1
        elif op == OP_YAML_STRINGIFY:
            need(1); stack -= 1; stack += 1
        elif op == OP_ANNOTATE_FUNC:
            fidx, i = read_uleb128(code, i); argc, i = read_uleb128(code, i)
            for _ in range(argc): need(1); stack.pop()
        elif op == OP_ITER_NEW:
            need(1); stack.pop(); stack.append('iter')
        elif op == OP_ITER_HAS_NEXT:
            need(1); stack.pop(); stack.append('bool')
        elif op == OP_ITER_NEXT:
            need(1); stack.pop(); stack.append('unknown')
        elif op in (OP_STRUPPER, OP_STRLOWER, OP_STRTRIM):
            need(1); # pop then push
        elif op == OP_LIST_APPEND:
            need(2); stack -= 1
        elif op == OP_LIST_POP:
            need(1); # pop lst, push item
        elif op == OP_MAP_PUT:
            need(3); stack -= 2
        elif op == OP_MAP_GET:
            need(2); stack -= 1
        else:
            raise ValueError(f"Unknown opcode {op}")
    return True


def _type_of_const(consts, idx):
    v = consts[idx]
    if isinstance(v, bool):
        return 'bool'
    if isinstance(v, int):
        return 'int'
    if isinstance(v, float):
        return 'float'
    if isinstance(v, str):
        return 'str'
    if isinstance(v, list):
        return 'list'
    if isinstance(v, dict):
        return 'map'
    return 'unknown'


def verify_code_types(consts, syms, code):
    # Best-effort type simulation; Unknown types pass, concrete contradictions raise
    i = 0
    n = len(code)
    stack: List[str] = []
    sym_types = {}
    def need(k):
        if len(stack) < k:
            raise ValueError("Type stack underflow")
    while i < n:
        op = code[i]; i += 1
        if op == OP_LOAD_CONST:
            idx, i = read_uleb128(code, i)
            stack.append(_type_of_const(consts, idx))
        elif op == OP_LOAD_NAME:
            sidx, i = read_uleb128(code, i)
            t = sym_types.get(syms[sidx], 'unknown')
            stack.append(t)
        elif op == OP_STORE_NAME:
            sidx, i = read_uleb128(code, i)
            need(1); t = stack.pop(); sym_types[syms[sidx]] = t
        elif op in (OP_ADD, OP_SUB, OP_MUL, OP_DIV, OP_LT, OP_LE, OP_GE, OP_EQ):
            need(2); b = stack.pop(); a = stack.pop()
            # Allow unknowns; else require numeric for arithmetic, comparable for comparisons
            if op in (OP_ADD, OP_SUB, OP_MUL, OP_DIV):
                if a != 'unknown' and b != 'unknown' and not (a in ('int','float') and b in ('int','float')):
                    raise ValueError("Type error: arithmetic on non-numbers")
                stack.append('float' if 'float' in (a,b) else 'int')
            else:
                stack.append('bool')
        elif op == OP_CONCAT:
            need(2); b = stack.pop(); a = stack.pop()
            if a != 'unknown' and b != 'unknown' and not (a == 'str' and b == 'str'):
                raise ValueError("Type error: CONCAT requires strings")
            stack.append('str')
        elif op == OP_LEN:
            need(1); a = stack.pop();
            if a != 'unknown' and a not in ('list','str','map'):
                raise ValueError("Type error: LEN requires list/str/map")
            stack.append('int')
        elif op in (OP_STRUPPER, OP_STRLOWER, OP_STRTRIM):
            need(1); a = stack.pop();
            if a != 'unknown' and a not in ('str',):
                raise ValueError("Type error: string op requires str")
            stack.append('str')
        elif op == OP_BUILD_LIST:
            count, i = read_uleb128(code, i)
            for _ in range(count): need(1); stack.pop()
            stack.append('list')
        elif op == OP_BUILD_MAP:
            pairs, i = read_uleb128(code, i)
            for _ in range(pairs * 2): need(1); stack.pop()
            stack.append('map')
        elif op == OP_INDEX:
            need(2); idx_t = stack.pop(); seq_t = stack.pop();
            if seq_t != 'unknown' and seq_t not in ('list','str'):
                raise ValueError("Type error: INDEX requires list/str")
            if idx_t != 'unknown' and idx_t not in ('int',):
                raise ValueError("Type error: INDEX requires int index")
            stack.append('unknown')
        elif op in (OP_WRITEFILE, OP_APPENDFILE, OP_DELETEFILE):
            # pop 2 or 1
            if op in (OP_WRITEFILE, OP_APPENDFILE):
                need(2); stack.pop(); stack.pop()
            else:
                need(1); stack.pop()
        elif op in (OP_READFILE, OP_HTTPGET, OP_HTTPPOST, OP_IMPORTURL, OP_ASYNC_READFILE, OP_ASYNC_HTTPGET):
            # they push a string or callable; we generalize to unknown/str
            # READFILE consumes 1, pushes str
            if op == OP_READFILE:
                need(1); stack.pop(); stack.append('str')
            elif op == OP_HTTPGET:
                need(1); stack.pop(); stack.append('str')
            elif op == OP_HTTPPOST:
                need(2); stack.pop(); stack.pop(); stack.append('str')
            elif op == OP_IMPORTURL:
                need(1); stack.pop(); stack.append('str')
            else:
                need(1); stack.pop(); stack.append('unknown')
        elif op == OP_SET_NEW:
            stack.append('set')
        elif op == OP_SET_ADD:
            need(2); v = stack.pop(); s = stack.pop();
            if s != 'unknown' and s != 'set':
                raise ValueError("Type error: SET_ADD requires set")
            stack.append('set')
        elif op == OP_SET_CONTAINS:
            need(2); v = stack.pop(); s = stack.pop();
            if s != 'unknown' and s != 'set':
                raise ValueError("Type error: SET_CONTAINS requires set")
            stack.append('bool')
        elif op in (OP_CSV_PARSE, OP_YAML_PARSE):
            need(1); stack.pop(); stack.append('list' if op == OP_CSV_PARSE else 'map')
        elif op in (OP_CSV_STRINGIFY, OP_YAML_STRINGIFY):
            need(1); stack.pop(); stack.append('str')
        elif op == OP_AWAIT:
            need(1); stack.pop(); stack.append('unknown')
        elif op == OP_PRINT:
            need(1); stack.pop()
        elif op in (OP_JUMP, OP_JUMP_IF_FALSE, OP_RETURN, OP_SETUP_CATCH, OP_END_TRY, OP_THROW, OP_NEW, OP_GETFIELD, OP_SETFIELD, OP_CALL, OP_CALL_METHOD, OP_ANNOTATE_FUNC, OP_ITER_NEW, OP_ITER_HAS_NEXT, OP_ITER_NEXT):
            # skip for type purposes for these ops; handle arg pops if needed
            if op == OP_JUMP:
                off, i = read_uleb128(code, i)
            elif op == OP_JUMP_IF_FALSE:
                off, i = read_uleb128(code, i); need(1); stack.pop()
            elif op == OP_RETURN:
                if stack: stack.pop()
            elif op in (OP_CALL,):
                fidx, i = read_uleb128(code, i); argc, i = read_uleb128(code, i)
                for _ in range(argc): need(1); stack.pop()
                stack.append('unknown')
            elif op in (OP_CALL_METHOD,):
                midx, i = read_uleb128(code, i); argc, i = read_uleb128(code, i)
                for _ in range(argc): need(1); stack.pop()
                need(1); stack.pop(); stack.append('unknown')
            elif op in (OP_NEW, OP_GETFIELD, OP_SETFIELD):
                if op == OP_NEW:
                    idx, i = read_uleb128(code, i); stack.append('object')
                elif op == OP_GETFIELD:
                    idx, i = read_uleb128(code, i); need(1); stack.pop(); stack.append('unknown')
                else:
                    idx, i = read_uleb128(code, i); need(2); stack.pop(); stack.pop()
            elif op in (OP_SETUP_CATCH, OP_END_TRY, OP_THROW):
                if op == OP_SETUP_CATCH:
                    off, i = read_uleb128(code, i)
                elif op == OP_THROW:
                    need(1); stack.pop()
            elif op == OP_ANNOTATE_FUNC:
                fidx, i = read_uleb128(code, i); argc, i = read_uleb128(code, i)
                for _ in range(argc): need(1); stack.pop()
            elif op == OP_ITER_NEW:
                need(1); stack.pop(); stack.append('iter')
            elif op == OP_ITER_HAS_NEXT:
                need(1); stack.pop(); stack.append('bool')
            elif op == OP_ITER_NEXT:
                need(1); stack.pop(); stack.append('unknown')
        elif op == OP_LIST_APPEND:
            need(2); stack.pop(); stack.pop(); stack.append('list')
        elif op == OP_LIST_POP:
            need(1); stack.pop(); stack.append('unknown')
        elif op == OP_MAP_PUT:
            need(3); stack.pop(); stack.pop(); stack.pop(); stack.append('map')
        elif op == OP_MAP_GET:
            need(2); stack.pop(); stack.pop(); stack.append('unknown')
        else:
            # Unknown opcode treated as non-type affecting
            pass
    return True


def verify_module(consts, syms, main_code, funcs, classes=None):
    verify_code(consts, syms, main_code)
    verify_code_types(consts, syms, main_code)
    for name_idx, params, code in funcs:
        if name_idx >= len(syms):
            raise ValueError("Function name sym out of range")
        for p in params:
            if p >= len(syms):
                raise ValueError("Function param sym out of range")
        verify_code(consts, syms, code)
        verify_code_types(consts, syms, code)
    if classes:
        for class_idx, base_idx, field_syms, methods in classes:
            if class_idx >= len(syms):
                raise ValueError("Class name sym out of range")
            # base index already offset-encoded at binary level; upstream parsers decode
            for fs in field_syms:
                if fs >= len(syms):
                    raise ValueError("Class field sym out of range")
            for mname_idx, params, code in methods:
                if mname_idx >= len(syms):
                    raise ValueError("Method name sym out of range")
                for p in params:
                    if p >= len(syms):
                        raise ValueError("Method param sym out of range")
                verify_code(consts, syms, code)
                verify_code_types(consts, syms, code)
    return True

