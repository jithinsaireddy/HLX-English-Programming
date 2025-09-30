# HLX‑English‑Programming: Deterministic English Compilation to NLBC/NLVM with HLX Multi‑Target Codegen

## Abstract
HLX‑English‑Programming treats controlled English as a first‑class programming language with a compiler and runtime. English programs compile to a binary bytecode (NLBC) executed by a deterministic virtual machine (NLVM). For real‑time and IoT/edge systems, HLX (Human Language eXecution) lifts English specifications into deployable artifacts: Rust/FreeRTOS scaffolds for MCUs, edge container manifests, and W3C Web of Things Thing Descriptions. spaCy‑driven normalization is mandatory, enabling robust, flexible phrasing while preserving determinism.

## Key Contributions (What is path‑breaking)
- Deterministic English→NLBC→NLVM pipeline: not prompt‑to‑code, but a stable, reproducible compiler/runtime contract.
- Mandatory spaCy normalization (en_core_web_sm): controlled English enriched by lemmatization and synonym canonicalization to handle complex, natural phrasing before compilation.
- HLX multi‑target generation: one English source produces MCU/edge/standards artifacts, aligning natural language intent with deployable software/hardware targets.
- Real‑time semantics and safety envelopes: timing, watchdogs, rate‑limits, and unit‑aware checks expressed directly in controlled English.

## System Architecture
```
English (.nl) ──► spaCy normalization ──► parsing & semantic checks ──► IR ──► NLBC (binary)
                                                                     └─► HLX generators ► {rtos.rs, edge_manifest.json, thing_description.json}
NLBC (binary) ──► NLVM deterministic execution (capability‑gated I/O, op/time guards)
```
- English Front‑End: controlled English with spaCy normalization for resilient phrasing.
- IR (secondary, internal): used for analysis/transformations; public artifact is NLBC.
- NLBC (primary binary): compact module format with constants, symbols, code, functions, and classes; viewable via disassembler.
- NLVM (primary runtime): executes NLBC deterministically; observability via traces and disassembly.
- HLX Generators: produce Rust/FreeRTOS scaffolds, edge manifests, and WoT TDs for deployment.

## spaCy in the Pipeline (Mandatory)
- Install: `pip install -r requirements.txt && make nlp-model`
- Role: lemmatization/synonym canonicalization, normalization of nested conditions and variants; improves robustness without adding runtime nondeterminism.
- Enforcement: the toolchain auto‑loads (or one‑time downloads) `en_core_web_sm`; compilation fails fast if unavailable.

## Primary Pipeline (English → NLBC → NLVM)
- Compile and run end‑to‑end:
```bash
python integrated_test_runner.py english_programming/examples/basic_operations.nl
```
- Disassemble an NLBC module:
```bash
python -m english_programming.bin.nlbc_disassembler path/to/program.nlbc
```

## HLX: Controlled‑English for Real‑Time IoT/Edge
- Outputs:
  - `hlx_out/rtos.rs`: Rust/FreeRTOS skeleton for MCU tasks/timers/queues
  - `hlx_out/edge_manifest.json`: container manifest for gateways
  - `hlx_out/thing_description.json`: W3C WoT TD for interoperability
- Runtime integrations: local simulation, MQTT/CoAP connectors, deterministic scheduling hints.
- See root `README-HLX.md` and `english_programming/hlx/README.md`.

## What You Can Express (Complexity at a glance)
- EPL (general): variables, lists/maps/sets, nested conditionals, loops, file I/O, HTTP, async, OOP sketches.
- HLX (IoT/edge): sensors, actuators, timing (period/deadline/jitter), hysteresis/cooldown, windowed storage, multi‑sensor correlation, event vs processing time.
- The web UI (`ui/english-ui/src/App.tsx`) includes HLX examples (overpressure, HVAC hysteresis, leak detection, hospital CO₂) and EPL examples (BFS, Kahn topological sort sketches, CSV/YAML round‑trip, OOP).

## Positioning
- Unique: a deterministic compiler + VM for English, plus HLX multi‑target generation. Most alternatives either translate to a different language or rely on probabilistic LLMs.
- Overlap exists: English‑like systems (Inform 7, specs like Attempto/Gherkin) and LLM codegen. They either constrain English into domain‑specific niches or don’t define a native bytecode/VM contract.
- Hard problem: ambiguity in natural language. We mitigate with controlled English, spaCy normalization, explicit errors, and deterministic semantics.
- Honest reality: NLBC is VM bytecode (not native machine code). Native MCU binaries arise downstream when compiling HLX Rust scaffolds with board HALs.
- If done right: this is genuinely paradigm‑shifting—an “English JVM” with real‑time reach.

## Limitations and Roadmap
- Formalization: publish NLBC spec and conformance tests.
- Hardware: provide reference HAL bindings for 1–2 MCU boards (see `english_programming/hlx/README_boards.md`).
- Evidence: add micro‑benchmarks, case studies, timing/jitter evaluations for HLX loops.
- Semantics: extend formal grammar and unit/contract checks (HLX safety model).

## Repository Map
- `english_programming/src`: compiler, NLVM, interfaces, extensions
- `english_programming/hlx`: HLX grammar, CLI, edge module, generators
- `english_programming/examples`: `.nl` and `.hlx` examples
- `hlx_out/`: generated outputs
- `ui/english-ui`: web playground

## Install & Run
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
make nlp-model
python integrated_test_runner.py english_programming/examples/basic_operations.nl
python -m english_programming.hlx.cli english_programming/examples/boiler_a.hlx --out hlx_out
```

## Related Work
See `docs/RELATED_WORK.md` for specific comparisons (Inform 7; Attempto/Gherkin; Wolfram; LLM codegen).

## License, Governance, Security
- License: MIT (`LICENSE`)
- Contributing: `CONTRIBUTING.md`
- Code of Conduct: `CODE_OF_CONDUCT.md`
- Security: `SECURITY.md`

## Citation
If you use this project in academic work, please cite it as “HLX‑English‑Programming (2025)”.
