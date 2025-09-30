# English Programming: NLBC/NLVM Core and HLX Backends (Technical Overview)

## Summary
This package provides the English→NLBC compiler pipeline, the NLVM deterministic bytecode virtual machine, and HLX generators for real‑time IoT/edge targets. spaCy (en_core_web_sm) is mandatory and automatically managed.

## Front‑End and Normalization
- Controlled English with spaCy normalization (lemmatization, synonym canonicalization)
- Entity resolution, type inference under constraints, capability tracking for effects
- Internal IR for analysis; public primary artifact is NLBC (binary)

## NLBC Module Format (High‑level)
- Sections: constants, symbols, main code, functions, classes
- Disassembler available at `english_programming/bin/nlbc_disassembler.py`

## NLVM Execution Model
- Deterministic evaluation; capability‑gated I/O; operation/time guards
- Tracing/disassembly for observability and debugging

## HLX Generators
- `hlx_out/rtos.rs` (Rust/FreeRTOS skeleton)
- `hlx_out/edge_manifest.json` (edge container manifest)
- `hlx_out/thing_description.json` (W3C WoT TD)

## Developer Workflow
```bash
python -m english_programming.run_english ../examples/basic_operations.nl
python -m english_programming.hlx.cli ../examples/boiler_a.hlx --out ../../hlx_out
python -m english_programming.hlx.run_demo ../examples/boiler_a.hlx
python -m english_programming.hlx.edge_module --spec ../examples/boiler_a.hlx --endpoint mqtt://localhost
```

## spaCy (Mandatory)
```bash
pip install -r ../../requirements.txt
make -C ../.. nlp-model
```
- Auto‑download and load; fails fast if missing
- Improves robustness for nested conditions and variant phrasings

## References
- Compiler (binary): `english_programming/bin/nlp_compiler_bin.py`
- Disassembler: `english_programming/bin/nlbc_disassembler.py`
- VM: `english_programming/src/vm/improved_nlvm.py`
- HLX grammar/safety: `english_programming/hlx/README.md`

## Governance
- MIT License (root `LICENSE`), `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`
