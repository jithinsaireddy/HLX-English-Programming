# NLBC v1.0 Specification

This document describes the Natural Language ByteCode (NLBC) version 1.0 format and execution model as implemented in this repository.

## File Header
- Magic: `NLBC` (ASCII bytes 4E 4C 42 43)
- Version: `ver_major=1`, `ver_minor=0` (little-endian u16 each)
- Flags: u8 (reserved; 0 for now)

## Sections
Each section is encoded as: `section_id (u8)` + `section_length (ULEB128)` + `payload (bytes)`.

- 1: CONSTANTS
  - Payload: `const_count (ULEB128)`, then entries:
    - `tag (u8)` + payload
      - 0=int: `SLEB128` value
      - 1=float64: 8 bytes IEEE754 little-endian
      - 2=string: `strlen (ULEB128)` + UTF‑8 bytes

- 2: SYMBOLS
  - Payload: `sym_count (ULEB128)`, then each: `namelen (ULEB128)` + UTF‑8 bytes

- 3: CODE (module main)
  - Payload: flat bytecode stream (u8 opcodes with ULEB128 operands)

- 4: FUNCS
  - Payload: `func_count (ULEB128)` entries:
    - `name_sym_idx (ULEB128)`
    - `param_count (ULEB128)` + `param_sym_idx[...]`
    - `code_len (ULEB128)` + `code_bytes`

- 5: CLASSES
  - Payload: `class_count (ULEB128)` entries:
    - `class_sym_idx (ULEB128)`
    - `base_offset (ULEB128)` where 0=None, else `base_sym_idx+1`
    - `field_count (ULEB128)` + `field_sym_idx[...]`
    - `method_count (ULEB128)` + method entries:
      - `method_sym_idx (ULEB128)`
      - `param_count (ULEB128)` + `param_sym_idx[...]`
      - `code_len (ULEB128)` + `code_bytes`

## Opcode Set (u8) and Stack Effects
- LOAD_CONST cidx: push const
- LOAD_NAME sidx: push env[name]
- STORE_NAME sidx: pop → env[name]
- ADD/SUB/MUL/DIV: pop b, pop a, push a op b
- CONCAT: pop b, pop a, push str(a)+str(b)
- LEN: pop a, push len(a)
- EQ/LE/GE/LT: pop b, pop a, push compare
- PRINT: pop and print
- BUILD_LIST n: pop n, push list
- INDEX: pop idx, pop seq, push seq[idx]
- BUILD_MAP k: pop 2k (k,v pairs), push map
- GET_ATTR sidx: pop obj, push obj[name]
- JUMP off: ip += off
- JUMP_IF_FALSE off: pop cond; if not cond: ip += off
- CALL fidx argc: pop argc args; call; push return
- RETURN: pop and return
- WRITEFILE/READFILE/APPENDFILE/DELETEFILE
- HTTPGET/HTTPPOST
- IMPORTURL: pop url; push content (subject to sandbox)
- Exceptions: SETUP_CATCH off, END_TRY, THROW; typed: SETUP_CATCH_T sym off, THROW_T
- Async: AWAIT, ASYNC_READFILE, ASYNC_HTTPGET, SCHEDULE, RUN_TASKS, ASYNC_SLEEP ms, ASYNC_CONNECT host_sym port, ASYNC_SEND, ASYNC_RECV
- Sets/CSV/YAML: SET_NEW, SET_ADD, SET_CONTAINS; CSV_PARSE/CSV_STRINGIFY; YAML_PARSE/YAML_STRINGIFY
- Iterators/Annotations: ITER_NEW/ITER_HAS_NEXT/ITER_NEXT; ANNOTATE_FUNC

## Verifier Rules (Deterministic Safety)
- Bounds: Constant/symbol indices must be in-range.
- Jumps: Targets must fall within the code section (0..len(code)).
- Stack: No underflow; enforce per-op stack effects exactly.
- Types (best-effort):
  - Arithmetic requires numbers (int/float); result numeric.
  - CONCAT requires strings; result string.
  - LEN requires list/str/map; result int.
  - INDEX requires list/str with int index; result unknown.
  - Sets: SET_ADD/SET_CONTAINS require a set on stack.
- Functions/classes: Symbol indices for names/params/fields/methods must be valid.

## Encoding Notes
- ULEB128/SLEB128 variable-length integers.
- Labels assembled via iterative fix-up to accommodate ULEB128 size changes in branch offsets.

## Forward Compatibility
- Unknown sections must be ignored.
- New opcodes extend the set; verifier must be updated to add stack/type rules.

## References
- Implementation: `english_programming/bin/nlbc_encoder.py`, `nlvm_bin.py`, `nlbc_verify.py`.
- Disassembler: `english_programming/bin/nlbc_disassembler.py`.
