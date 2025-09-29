from struct import unpack
from english_programming.bin.uleb128 import read_uleb128, read_sleb128

OPCODES = {
    0x01: 'LOAD_CONST', 0x02: 'LOAD_NAME', 0x03: 'STORE_NAME', 0x04: 'ADD', 0x05: 'PRINT',
    0x06: 'BUILD_LIST', 0x07: 'INDEX', 0x08: 'BUILD_MAP', 0x09: 'GET_ATTR',
    0x0A: 'JUMP', 0x0B: 'JUMP_IF_FALSE', 0x0C: 'CALL', 0x0D: 'RETURN', 0x0E: 'LT',
    0x0F: 'SUB', 0x10: 'MUL', 0x11: 'DIV', 0x12: 'CONCAT', 0x13: 'LEN', 0x14: 'EQ', 0x15: 'LE', 0x16: 'GE',
    0x20: 'WRITEFILE', 0x21: 'READFILE', 0x22: 'APPENDFILE', 0x23: 'DELETEFILE',
    0x30: 'NEW', 0x31: 'GETFIELD', 0x32: 'SETFIELD', 0x33: 'CALL_METHOD',
    0xA6: 'STRUPPER', 0xA7: 'STRLOWER', 0xA8: 'STRTRIM', 0xA9: 'LIST_APPEND', 0xAA: 'LIST_POP', 0xAB: 'MAP_PUT', 0xAC: 'MAP_GET'
}

def disassemble(buf: bytes) -> str:
    assert buf[:4] == b"NLBC"
    i = 9
    out = []
    consts, syms, code, funcs, classes = [], [], b"", [], []
    while i < len(buf):
        sid = buf[i]; i += 1
        slen, i = read_uleb128(buf, i)
        sec = buf[i:i+slen]; i += slen
        if sid == 1:
            j = 0
            count, j = read_uleb128(sec, j)
            for _ in range(count):
                tag = sec[j]; j += 1
                if tag == 0:
                    v, j = read_sleb128(sec, j); consts.append(v)
                elif tag == 1:
                    v = unpack("<d", sec[j:j+8])[0]; j += 8; consts.append(v)
                elif tag == 2:
                    ln, j = read_uleb128(sec, j); consts.append(sec[j:j+ln].decode()); j += ln
        elif sid == 2:
            j = 0
            count, j = read_uleb128(sec, j)
            for _ in range(count):
                ln, j = read_uleb128(sec, j); syms.append(sec[j:j+ln].decode()); j += ln
        elif sid == 3:
            code = sec
        elif sid == 4:
            j = 0
            count, j = read_uleb128(sec, j)
            for _ in range(count):
                name_idx, j = read_uleb128(sec, j)
                pcount, j = read_uleb128(sec, j)
                params = []
                for _ in range(pcount):
                    p, j = read_uleb128(sec, j); params.append(p)
                ln, j = read_uleb128(sec, j)
                code_b = sec[j:j+ln]; j += ln
                funcs.append((name_idx, params, code_b))
        elif sid == 5:
            j = 0
            count, j = read_uleb128(sec, j)
            for _ in range(count):
                class_idx, j = read_uleb128(sec, j)
                base_idx, j = read_uleb128(sec, j)
                fcount, j = read_uleb128(sec, j)
                field_syms = []
                for _ in range(fcount):
                    fs, j = read_uleb128(sec, j); field_syms.append(fs)
                mcount, j = read_uleb128(sec, j)
                methods = []
                for _ in range(mcount):
                    mname_idx, j = read_uleb128(sec, j)
                    pcount, j = read_uleb128(sec, j)
                    params = []
                    for _ in range(pcount):
                        p, j = read_uleb128(sec, j); params.append(p)
                    ln, j = read_uleb128(sec, j)
                    code_b = sec[j:j+ln]; j += ln
                    methods.append((mname_idx, params, code_b))
                classes.append((class_idx, base_idx, field_syms, methods))

    def dis_code(code_bytes):
        k = 0; lines = []
        while k < len(code_bytes):
            op = code_bytes[k]; k += 1
            name = OPCODES.get(op, f'OP_{op:02x}')
            offset_str = f"@{k-1:04x}"
            if name in ('LOAD_CONST','LOAD_NAME','STORE_NAME','BUILD_LIST','BUILD_MAP','GET_ATTR','JUMP','JUMP_IF_FALSE','CALL','NEW','GETFIELD','SETFIELD','CALL_METHOD'):
                a, k = read_uleb128(code_bytes, k)
                if name in ('JUMP','JUMP_IF_FALSE'):
                    target = k + a
                    lines.append(f"{offset_str} {name} +{a} -> @{target:04x}")
                elif name == 'CALL' or name == 'CALL_METHOD':
                    argc, k = read_uleb128(code_bytes, k)
                    lines.append(f"{offset_str} {name} sym={a} argc={argc}")
                else:
                    lines.append(f"{offset_str} {name} {a}")
            else:
                lines.append(f"{offset_str} {name}")
        return lines

    out.append('== CONSTANTS ==')
    for idx, c in enumerate(consts):
        out.append(f"[{idx}] {c!r}")
    out.append('== SYMBOLS ==')
    for idx, s in enumerate(syms):
        out.append(f"[{idx}] {s}")
    out.append('== CODE ==')
    out += dis_code(code)
    if funcs:
        out.append('== FUNCS ==')
        for name_idx, params, code_b in funcs:
            pnames = ', '.join(syms[p] for p in params)
            out.append(f"func {syms[name_idx]}({pnames})")
            out += ['  ' + ln for ln in dis_code(code_b)]
    if classes:
        out.append('== CLASSES ==')
        for class_idx, base_idx, field_syms, methods in classes:
            cname = syms[class_idx]
            base = 'None' if base_idx == 0 else syms[base_idx - 1]
            fields = ', '.join(syms[f] for f in field_syms)
            out.append(f"class {cname} extends {base} fields [{fields}]")
            for mname_idx, params, code_b in methods:
                pnames = ', '.join(syms[p] for p in params)
                out.append(f"  def {syms[mname_idx]}({pnames})")
                out += ['    ' + ln for ln in dis_code(code_b)]
    return '\n'.join(out)


if __name__ == '__main__':
    import sys
    data = open(sys.argv[1], 'rb').read()
    print(disassemble(data))

