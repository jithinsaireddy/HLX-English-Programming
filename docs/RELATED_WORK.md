# Related Work and Positioning

This document situates HLX‑English‑Programming among nearby efforts.

## Inform 7
- English‑like language focused on interactive fiction
- Compiles to VM bytecode (e.g., Z‑machine/Glulx)
- Scope limited to narrative/IF; not aimed at IoT/real‑time systems
- Our difference: general computation + NLBC/VM + HLX multi‑target IoT outputs (Rust/FreeRTOS, edge manifests, WoT TD)

## Controlled English for Specs/Tests (Attempto, Gherkin)
- English for formal specs or test scenarios
- Generates tests/specifications, not executable multi‑target artifacts
- Our difference: deterministic compiler to NLBC and deployable HLX artifacts

## LLM Code Generation
- Probabilistic mapping from prompts to code
- No stable bytecode/VM contract; reproducibility varies
- Our difference: deterministic compiler with a defined bytecode (NLBC) and NLVM runtime

## Wolfram “Natural Language” Interfaces
- NL front‑end mapped onto Wolfram Language
- Not a separate deterministic compiler/VM stack with IoT codegen

## Summary
- HLX‑English‑Programming = controlled English → NLBC binary → NLVM, + HLX → multi‑target IoT outputs
- Focus on determinism, auditability, and real‑time/IoT portability rather than interactive fiction or probabilistic codegen
