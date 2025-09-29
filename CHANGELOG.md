# Changelog
## [1.1.0] - 2025-09-28
### Added
- spaCy leveraged in binary pipeline normalization; HLX endpoints retained
- VM execution guards (EP_MAX_OPS/EP_MAX_MS) and default-disabled networking (EP_ENABLE_NET=1 to enable)
- LIST_POP support; FOR_EACH execution; improved LIST_APPEND deterministic behavior
- Compiler phrases: "length of X store in Y", "pop from list X store in Y"
- Disassembler now shows byte offsets and jump targets
- Algorithms: LRUCache, Trie (prefix, suggest), topo_sort_full_order, merge_sorted_arrays
- Tests for algorithms and VM list operations

### Fixed
- Reduced warnings for common list and loop constructs

## 0.1.0
- Unified compiler+VM with optional spaCy NLP (auto-detect).
- Bytecode/VM: variables, arithmetic (ADD/SUB/MUL/DIV), strings (CONCAT, STRUPPER/STRLOWER/STRTRIM), lists/dicts, IF/ELSE, functions, PRINT.
- File I/O: WRITEFILE/READ/APPENDFILE.
- HTTP: HTTPGET, HTTPPOST, HTTPSETHEADER.
- JSON: JSONPARSE/JSONSTRINGIFY/JSONGET/JSONKEYS/JSONVALUES.
- Regex: REGEXMATCH/REGEXCAPTURE/REGEXREPLACE.
- Dates: NOW, DATEFORMAT.
- OOP (native): CLASS_START/END, METHOD_START/ENDMETHOD, CREATE_OBJECT, CALL_METHOD/CALL_METHODR, CALL_SUPER/CALL_SUPERR, GET/SET_PROPERTY.
- Modules: IMPORTURL via secure PackageManager (https/file), compile to .nlc.
- Web playground: run/lint, save+load snippets.
- VS Code: syntax, format (english-format) and lint (english-lint) commands.
- IR + optimizer (constant folding; conservative DCE off by default).
- CI workflow and comprehensive tests.


## NLBC v1.0
- Spec documented at docs/nlbc_spec_v1.md
- Verifier stack/type rules aligned with interpreter semantics.

