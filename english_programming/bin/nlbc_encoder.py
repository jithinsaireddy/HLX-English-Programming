from struct import pack
from english_programming.bin.uleb128 import write_uleb128, write_sleb128

MAGIC = b"NLBC"
VER_MAJOR = 1
VER_MINOR = 0

SEC_CONSTANTS = 1
SEC_SYMBOLS   = 2
SEC_CODE      = 3
SEC_FUNCS     = 4
SEC_CLASSES   = 5
SEC_DEBUG     = 6  # optional: source mapping by instruction ordinal

# opcodes
OP_LOAD_CONST   = 0x01
OP_LOAD_NAME    = 0x02
OP_STORE_NAME   = 0x03
OP_ADD          = 0x04
OP_PRINT        = 0x05
OP_BUILD_LIST   = 0x06
OP_INDEX        = 0x07
OP_BUILD_MAP    = 0x08
OP_GET_ATTR     = 0x09
OP_JUMP         = 0x0A
OP_JUMP_IF_FALSE= 0x0B
OP_JUMP_BACK    = 0xAD
OP_CALL         = 0x0C
OP_RETURN       = 0x0D
OP_LT           = 0x0E
OP_SUB          = 0x0F
OP_MUL          = 0x10
OP_DIV          = 0x11
OP_CONCAT       = 0x12
OP_LEN          = 0x13
OP_EQ           = 0x14
OP_LE           = 0x15
OP_GE           = 0x16
OP_MOD          = 0x17

OP_WRITEFILE    = 0x20
OP_READFILE     = 0x21
OP_APPENDFILE   = 0x22
OP_DELETEFILE   = 0x23
OP_HTTPGET      = 0x40
OP_HTTPPOST     = 0x41
OP_IMPORTURL    = 0x50

OP_NEW          = 0x30
OP_GETFIELD     = 0x31
OP_SETFIELD     = 0x32
OP_CALL_METHOD  = 0x33
OP_SETUP_CATCH  = 0x61
OP_END_TRY      = 0x62
OP_THROW        = 0x63
OP_AWAIT        = 0x70
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
OP_WRAP_VALUE     = 0xA5
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

# const tags
CT_INT   = 0
CT_FLOAT = 1
CT_STR   = 2


def encode_constants(constants):
    body = bytearray()
    body += write_uleb128(len(constants))
    for tag, val in constants:
        body.append(tag)
        if tag == CT_INT:
            body += write_sleb128(int(val))
        elif tag == CT_FLOAT:
            body += pack("<d", float(val))
        elif tag == CT_STR:
            b = val.encode("utf-8")
            body += write_uleb128(len(b)) + b
        else:
            raise ValueError("bad const tag")
    return bytes([SEC_CONSTANTS]) + write_uleb128(len(body)) + body


def encode_symbols(symbols):
    body = bytearray()
    body += write_uleb128(len(symbols))
    for s in symbols:
        b = s.encode("utf-8")
        body += write_uleb128(len(b)) + b
    return bytes([SEC_SYMBOLS]) + write_uleb128(len(body)) + body


def encode_code(code_bytes: bytes):
    return bytes([SEC_CODE]) + write_uleb128(len(code_bytes)) + code_bytes


def assemble_code(instrs):
    m = {
        'LOAD_CONST': OP_LOAD_CONST, 'LOAD_NAME': OP_LOAD_NAME, 'STORE_NAME': OP_STORE_NAME,
        'ADD': OP_ADD, 'PRINT': OP_PRINT, 'BUILD_LIST': OP_BUILD_LIST,
        'INDEX': OP_INDEX, 'BUILD_MAP': OP_BUILD_MAP, 'GET_ATTR': OP_GET_ATTR,
        'JUMP': OP_JUMP, 'JUMP_IF_FALSE': OP_JUMP_IF_FALSE, 'CALL': OP_CALL, 'RETURN': OP_RETURN,
        'LT': OP_LT, 'SUB': OP_SUB, 'MUL': OP_MUL, 'DIV': OP_DIV, 'CONCAT': OP_CONCAT, 'MOD': OP_MOD,
        'LEN': OP_LEN, 'EQ': OP_EQ, 'LE': OP_LE, 'GE': OP_GE,
        'WRITEFILE': OP_WRITEFILE, 'READFILE': OP_READFILE, 'APPENDFILE': OP_APPENDFILE, 'DELETEFILE': OP_DELETEFILE,
        'HTTPGET': OP_HTTPGET, 'HTTPPOST': OP_HTTPPOST, 'IMPORTURL': OP_IMPORTURL,
        'NEW': OP_NEW, 'GETFIELD': OP_GETFIELD, 'SETFIELD': OP_SETFIELD, 'CALL_METHOD': OP_CALL_METHOD,
        'SETUP_CATCH': OP_SETUP_CATCH, 'END_TRY': OP_END_TRY, 'THROW': OP_THROW,
        'AWAIT': OP_AWAIT, 'ASYNC_READFILE': OP_ASYNC_READFILE, 'ASYNC_HTTPGET': OP_ASYNC_HTTPGET,
        'SCHEDULE': OP_SCHEDULE, 'RUN_TASKS': OP_RUN_TASKS,
        'THROW_T': OP_THROW_T, 'SETUP_CATCH_T': OP_SETUP_CATCH_T,
        'SET_NEW': OP_SET_NEW, 'SET_ADD': OP_SET_ADD, 'SET_CONTAINS': OP_SET_CONTAINS,
        'CSV_PARSE': OP_CSV_PARSE, 'YAML_PARSE': OP_YAML_PARSE, 'CSV_STRINGIFY': OP_CSV_STRINGIFY, 'YAML_STRINGIFY': OP_YAML_STRINGIFY,
        'ANNOTATE_FUNC': OP_ANNOTATE_FUNC,
        'ITER_NEW': OP_ITER_NEW, 'ITER_NEXT': OP_ITER_NEXT, 'ITER_HAS_NEXT': OP_ITER_HAS_NEXT,
        'WRAP_VALUE': OP_WRAP_VALUE, 'ASYNC_SLEEP': OP_ASYNC_SLEEP,
        'ASYNC_CONNECT': OP_ASYNC_CONNECT, 'ASYNC_SEND': OP_ASYNC_SEND, 'ASYNC_RECV': OP_ASYNC_RECV
        , 'STRUPPER': OP_STRUPPER, 'STRLOWER': OP_STRLOWER, 'STRTRIM': OP_STRTRIM
        , 'LIST_APPEND': OP_LIST_APPEND, 'LIST_POP': OP_LIST_POP, 'MAP_PUT': OP_MAP_PUT, 'MAP_GET': OP_MAP_GET
    }
    out = bytearray()
    def _is_labelled(ins):
        if ins[0] in ('JUMP','JUMP_IF_FALSE','SETUP_CATCH') and len(ins) > 1 and isinstance(ins[1], str):
            return True
        if ins[0] == 'SETUP_CATCH_T' and len(ins) > 2 and isinstance(ins[2], str):
            return True
        return False

    has_labels = any(_is_labelled(x) for x in instrs) or any(x[0] == 'LABEL' for x in instrs)
    if not has_labels:
        for ins in instrs:
            op = ins[0]; out.append(m[op])
            for operand in ins[1:]:
                out += write_uleb128(int(operand))
        return bytes(out)

    # Label-aware assembly with iterative fix-up of ULEB128 jump sizes
    # Identify jump instructions
    jump_indices = []  # indices into instrs for label-bearing ops
    for idx, ins in enumerate(instrs):
        if _is_labelled(ins):
            jump_indices.append(idx)
    # initial assumption: 1-byte encoded offset, unsigned kind
    jump_len = {idx: 1 for idx in jump_indices}
    jump_kind = {idx: 'unsigned' for idx in jump_indices}  # 'unsigned' for JUMP/JUMP_IF_FALSE/SETUP_CATCH(_T), 'signed' for backward

    def compute_layout():
        pc = 0
        label_pos = {}
        pcs = {}
        for idx, ins in enumerate(instrs):
            if ins[0] == 'LABEL':
                label_pos[ins[1]] = pc
                continue
            pcs[idx] = pc
            op = ins[0]
            pc += 1  # opcode
            if _is_labelled(ins):
                # add assumed length for the label operand only
                if op == 'SETUP_CATCH_T':
                    # first numeric (type sym), then label offset
                    # account for numeric operand size (approx by encoding now)
                    pc += len(write_uleb128(int(ins[1])))
                pc += jump_len[idx]
            else:
                for operand in ins[1:]:
                    pc += len(write_uleb128(int(operand)))
        return pcs, label_pos

    changed = True
    while changed:
        changed = False
        pcs, label_pos = compute_layout()
        for idx in jump_indices:
            ins = instrs[idx]
            op = ins[0]
            # determine label token position
            label = ins[2] if op == 'SETUP_CATCH_T' else ins[1]
            origin = pcs[idx]
            assumed = jump_len[idx]
            # ip is at start of op; after reading opcode and operand, ip moves by (1 + assumed)
            if op == 'SETUP_CATCH_T':
                # account for encoded type sym operand as well
                type_sym = int(ins[1])
                ip_after_operand = origin + 1 + len(write_uleb128(type_sym)) + assumed
            else:
                ip_after_operand = origin + 1 + assumed
            target = label_pos[label]
            off = target - ip_after_operand
            # choose encoding based on sign
            if off < 0:
                needed = len(write_sleb128(off))
                kind = 'signed'
            else:
                needed = len(write_uleb128(off))
                kind = 'unsigned'
            if needed != assumed or kind != jump_kind[idx]:
                jump_len[idx] = needed
                jump_kind[idx] = kind
                changed = True

    # Emit with final sizes
    out = bytearray()
    for idx, ins in enumerate(instrs):
        if ins[0] == 'LABEL':
            continue
        op = ins[0]
        # determine opcode byte (handle backward jumps specially)
        opcode_byte = m[op]
        if _is_labelled(ins):
            # compute final offset
            pcs, label_pos = compute_layout()
            origin = pcs[idx]
            assumed = jump_len[idx]
            if op == 'SETUP_CATCH_T':
                type_sym = int(ins[1])
                ip_after_operand = origin + 1 + len(write_uleb128(type_sym)) + assumed
                label_key = ins[2]
            else:
                ip_after_operand = origin + 1 + assumed
                label_key = ins[1]
            target = label_pos[label_key]
            off = target - ip_after_operand
            if op == 'JUMP' and off < 0:
                # emit backward jump with signed offset
                opcode_byte = OP_JUMP_BACK
            # write opcode first
            out.append(opcode_byte)
            # then write extra operands
            if op == 'SETUP_CATCH_T':
                type_sym = int(ins[1])
                out += write_uleb128(type_sym)
            if op == 'JUMP' and off < 0:
                out += write_sleb128(off)
            elif op in ('JUMP','JUMP_IF_FALSE','SETUP_CATCH'):
                out += write_uleb128(max(0, off))
            elif op == 'SETUP_CATCH_T':
                out += write_uleb128(max(0, off))
            else:
                # default
                out += write_uleb128(max(0, off))
        else:
            out.append(opcode_byte)
            for operand in ins[1:]:
                out += write_uleb128(int(operand))
    return bytes(out)


def write_module(filepath, constants, symbols, instrs):
    header = bytearray()
    header += MAGIC
    header += pack("<H", VER_MAJOR)
    header += pack("<H", VER_MINOR)
    header += bytes([0])  # flags

    code_bytes = assemble_code(instrs)
    blob  = header
    blob += encode_constants(constants)
    blob += encode_symbols(symbols)
    blob += encode_code(code_bytes)
    with open(filepath, "wb") as f:
        f.write(blob)


def encode_funcs(func_table):
    """func_table: list of tuples (name_sym_idx, param_sym_indices, code_bytes)"""
    body = bytearray()
    body += write_uleb128(len(func_table))
    for name_idx, params, code in func_table:
        body += write_uleb128(int(name_idx))
        # params
        body += write_uleb128(len(params))
        for p in params:
            body += write_uleb128(int(p))
        # code
        body += write_uleb128(len(code))
        body += code
    return bytes([SEC_FUNCS]) + write_uleb128(len(body)) + body


def write_module_with_funcs(filepath, constants, symbols, main_instrs, funcs):
    header = bytearray()
    header += MAGIC
    header += pack("<H", VER_MAJOR)
    header += pack("<H", VER_MINOR)
    header += bytes([0])

    main_code = assemble_code(main_instrs)

    blob  = header
    blob += encode_constants(constants)
    blob += encode_symbols(symbols)
    blob += encode_code(main_code)
    # funcs: list of (sym_idx, param_sym_indices, instrs)
    func_bytes = []
    for sym_idx, params, instrs in funcs:
        func_bytes.append((sym_idx, params, assemble_code(instrs)))
    blob += encode_funcs(func_bytes)
    with open(filepath, 'wb') as f:
        f.write(blob)


def encode_classes(classes_table):
    """classes_table: list of (class_sym_idx, base_sym_idx_or_-1, field_sym_indices, methods)
    where methods = list of (method_sym_idx, param_sym_indices, code_bytes)
    """
    body = bytearray()
    body += write_uleb128(len(classes_table))
    for class_idx, base_idx, field_syms, methods in classes_table:
        body += write_uleb128(int(class_idx))
        body += write_uleb128(int(base_idx if base_idx is not None else -1))
        body += write_uleb128(len(field_syms))
        for fs in field_syms:
            body += write_uleb128(int(fs))
        body += write_uleb128(len(methods))
        for mname_idx, params, code in methods:
            body += write_uleb128(int(mname_idx))
            body += write_uleb128(len(params))
            for p in params:
                body += write_uleb128(int(p))
            body += write_uleb128(len(code))
            body += code
    return bytes([SEC_CLASSES]) + write_uleb128(len(body)) + body


def write_module_full(filepath, constants, symbols, main_instrs, funcs, classes):
    header = bytearray()
    header += MAGIC
    header += pack("<H", VER_MAJOR)
    header += pack("<H", VER_MINOR)
    header += bytes([0])

    main_code = assemble_code(main_instrs)

    blob  = header
    blob += encode_constants(constants)
    blob += encode_symbols(symbols)
    blob += encode_code(main_code)
    func_bytes = []
    for sym_idx, params, instrs in funcs:
        func_bytes.append((sym_idx, params, assemble_code(instrs)))
    blob += encode_funcs(func_bytes)
    class_bytes = []
    for class_sym_idx, base_idx, field_syms, methods in classes:
        compiled_methods = []
        for mname_idx, mparams, minst in methods:
            compiled_methods.append((mname_idx, mparams, assemble_code(minst)))
        # Encode base index using offset scheme to avoid negative ULEB128:
        # None -> 0, otherwise base_idx + 1
        encoded_base = 0 if base_idx is None else (base_idx + 1)
        class_bytes.append((class_sym_idx, encoded_base, field_syms, compiled_methods))
    blob += encode_classes(class_bytes)
    with open(filepath, 'wb') as f:
        f.write(blob)


def encode_debug(main_line_map, func_line_maps):
    """Encode optional source mapping by instruction ordinal.

    main_line_map: List[int] mapping instruction index -> 1-based source line (0 for unknown)
    func_line_maps: List[List[int]] per function in same order as funcs table
    """
    body = bytearray()
    # Tag 1 = main, then count and entries
    body += bytes([1])
    body += write_uleb128(len(main_line_map))
    for ln in main_line_map:
        body += write_uleb128(int(max(0, ln)))
    # Tag 2 = functions, count and then for each: func_index, count, entries
    body += bytes([2])
    body += write_uleb128(len(func_line_maps))
    for idx, fmap in enumerate(func_line_maps or []):
        body += write_uleb128(int(idx))
        body += write_uleb128(len(fmap))
        for ln in fmap:
            body += write_uleb128(int(max(0, ln)))
    return bytes([SEC_DEBUG]) + write_uleb128(len(body)) + body


def write_module_full_with_debug(filepath, constants, symbols, main_instrs, funcs, classes, main_line_map, func_line_maps):
    """Write full module and append optional debug section."""
    header = bytearray()
    header += MAGIC
    header += pack("<H", VER_MAJOR)
    header += pack("<H", VER_MINOR)
    header += bytes([0])

    main_code = assemble_code(main_instrs)

    blob  = header
    blob += encode_constants(constants)
    blob += encode_symbols(symbols)
    blob += encode_code(main_code)
    func_bytes = []
    for sym_idx, params, instrs in funcs:
        func_bytes.append((sym_idx, params, assemble_code(instrs)))
    blob += encode_funcs(func_bytes)
    class_bytes = []
    for class_sym_idx, base_idx, field_syms, methods in classes:
        compiled_methods = []
        for mname_idx, mparams, minst in methods:
            compiled_methods.append((mname_idx, mparams, assemble_code(minst)))
        encoded_base = 0 if base_idx is None else (base_idx + 1)
        class_bytes.append((class_sym_idx, encoded_base, field_syms, compiled_methods))
    blob += encode_classes(class_bytes)
    # Append debug section
    try:
        blob += encode_debug(main_line_map or [], func_line_maps or [])
    except Exception:
        # Do not fail module writing if debug encoding fails
        pass
    with open(filepath, 'wb') as f:
        f.write(blob)

