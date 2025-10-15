from english_programming.bin.uleb128 import read_uleb128, write_uleb128


# opcodes
OP_LOAD_CONST  = 0x01
OP_LOAD_NAME   = 0x02
OP_STORE_NAME  = 0x03
OP_ADD         = 0x04
OP_PRINT       = 0x05
OP_SUB         = 0x0F
OP_MUL         = 0x10
OP_DIV         = 0x11
OP_CONCAT      = 0x12
OP_MOD         = 0x17


def _fold_binary(op, a, b):
    try:
        if op == OP_ADD:
            return a + b
        if op == OP_SUB:
            return a - b
        if op == OP_MUL:
            return a * b
        if op == OP_DIV:
            return a / b
        if op == OP_CONCAT:
            return str(a) + str(b)
        if op == OP_MOD:
            return a % b
    except Exception:
        return None
    return None


def optimize_code(consts, code_bytes):
    # Very small peephole: LOAD_CONST i, LOAD_CONST j, BINOP -> LOAD_CONST k
    i = 0
    out = bytearray()
    n = len(code_bytes)
    while i < n:
        op = code_bytes[i]; i += 1
        # pattern match
        if op == OP_LOAD_CONST:
            i1, pos_after_i1 = read_uleb128(code_bytes, i)
            # lookahead without consuming main i
            if pos_after_i1 < n and code_bytes[pos_after_i1] == OP_LOAD_CONST:
                j = pos_after_i1 + 1
                i2, j = read_uleb128(code_bytes, j)
                if j < n and code_bytes[j] in (OP_ADD, OP_SUB, OP_MUL, OP_DIV, OP_CONCAT, OP_MOD):
                    binop = code_bytes[j]
                    a = consts[i1]; b = consts[i2]
                    res = _fold_binary(binop, a, b)
                    if res is not None:
                        out.append(OP_LOAD_CONST)
                        try:
                            idx = consts.index(res)
                        except ValueError:
                            consts.append(res)
                            idx = len(consts) - 1
                        out += write_uleb128(idx)
                        i = j + 1  # consume both loads and binop
                        continue
            # no pattern: emit original first load and advance to pos_after_i1
            out.append(OP_LOAD_CONST); out += write_uleb128(i1)
            i = pos_after_i1
            continue
        else:
            out.append(op)
            # copy operands if any
            if op in (OP_LOAD_NAME, OP_STORE_NAME):
                idx, i = read_uleb128(code_bytes, i); out += write_uleb128(idx)
            elif op in (OP_PRINT, OP_ADD, OP_SUB, OP_MUL, OP_DIV, OP_CONCAT):
                pass
            else:
                # conservative: pass through following ULEB128 if present is unknown; this keeps most ops unchanged
                # For safety, we try to decode one operand for ops that usually have one
                # But unknown ops here are minimal as optimizer is peephole on small set
                pass
    return consts, bytes(out)


def optimize_module(consts, syms, main_code, funcs):
    consts, main_code = optimize_code(consts, main_code)
    new_funcs = []
    for name_idx, params, code in funcs:
        c_consts = consts  # share for simplicity
        _, code2 = optimize_code(c_consts, code)
        new_funcs.append((name_idx, params, code2))
    return consts, syms, main_code, new_funcs


