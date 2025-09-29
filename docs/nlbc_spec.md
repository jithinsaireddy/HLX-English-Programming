# NLBC v1 – Natural Language ByteCode (Binary) Spec

## File header

offset  size  field
0       4     magic = "NLBC"   ; ASCII 4E 4C 42 43
4       2     version_major (u16 LE)
6       2     version_minor (u16 LE)
8       1     flags (bitfield; for now 0)
9..     ?     section table (variable)

## Sections (sequence)
Each section = section_id (u8) + section_length (ULEB128) + payload.

Recommended order:
- 1 = CONSTANTS
- 2 = SYMBOLS
- 3 = CODE
- 4 = FUNCS (reserved)

### CONSTANTS (id=1)
```
const_count (ULEB128)
repeat const_entry:
  tag (u8): 0=int, 1=float64, 2=utf8-string
  payload:
    if tag=0: int_value (SLEB128)
    if tag=1: float64 (IEEE754, LE)
    if tag=2: strlen (ULEB128) + bytes
```

### SYMBOLS (id=2)
```
sym_count (ULEB128)
repeat:
  namelen (ULEB128) + UTF-8 name bytes
```

### CODE (id=3)
A flat bytecode stream executed at startup. Encoding: opcode (u8) then operands as ULEB128 indices.

### Minimal v1 opcode set (stack-based)

Mnemonic | Val | Stack effect | Operands
-|-|-|-
OP_LOAD_CONST | 0x01 | push const | const_idx
OP_LOAD_NAME  | 0x02 | push value of name | sym_idx
OP_STORE_NAME | 0x03 | pop → name | sym_idx
OP_ADD        | 0x04 | pop b, pop a, push a+b | –
OP_PRINT      | 0x05 | pop → print | –
OP_BUILD_LIST | 0x06 | pop N items → push list | count
OP_INDEX      | 0x07 | pop idx, pop seq → push seq[idx] | –
OP_BUILD_MAP  | 0x08 | pop 2*N (k,v) → push map | pairs_count
OP_GET_ATTR   | 0x09 | pop obj → push obj[name] | name_sym_idx

## Rationale
- Magic/version like JVM/WASM.
- ULEB128/SLEB128 compact integers like WASM/DWARF.
- Stack VM mirrors JVM/CPython simplicity.
- Sections + constant pool ease extension.

## Roadmap
- Control flow (JUMP/IF), functions (CALL/RETURN), verifier, binary constant lists/maps, disassembler.

