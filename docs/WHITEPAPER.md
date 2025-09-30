# HLX‑English‑Programming: A Deterministic English Runtime with Multi‑Target IoT Code Generation

## 1. Introduction
- Motivation: English as an executable medium; limitations of syntax‑first languages and probabilistic code generation
- Contributions: (1) Deterministic English→NLBC→NLVM pipeline; (2) spaCy‑driven normalization; (3) HLX multi‑target generation; (4) real‑time/safety semantics

## 2. Background and Related Work
- Natural‑language programming attempts; Inform 7; Attempto/Gherkin; Wolfram; LLM codegen
- Why prior work fails to offer a native bytecode/VM with real‑time deployments

## 3. Language Design (Controlled English)
- Core constructs; typing discipline; effect/capability model; ambiguity mitigation
- spaCy normalization: lemmatization, synonym canonicalization, comparative expressions

## 4. Intermediate Representation and NLBC
- IR role (internal), NLBC module format (constants, symbols, code, functions, classes)
- Disassembly; invariants; versioning and compatibility

## 5. NLVM Runtime
- Determinism; instruction semantics; capability‑gated I/O; operation/time guards
- Observability: tracing, debugging, reproducibility

## 6. HLX for Real‑Time/IoT
- Grammar and constructs (sensors, actuators, timing, policies)
- Outputs: Rust/FreeRTOS scaffolds, edge manifests, WoT TD
- Safety: watchdogs, unit checks, bounded ISRs; scheduling hints

## 7. Implementations and Case Studies
- Industrial overpressure; HVAC hysteresis; leak detection; hospital CO₂ monitoring
- End‑to‑end artifact generation; deployment notes

## 8. Evaluation
- Determinism and reproducibility metrics
- Micro‑benchmarks for VM throughput; latency/jitter in HLX loops (methodology)
- Developer productivity vs syntax‑first languages (qualitative)

## 9. Limitations and Future Work
- Grammar coverage and extensibility; formal verification; board HAL library
- Standardization: NLBC spec, conformance test suite, reference implementations

## 10. Conclusion
- HLX‑English‑Programming as a foundation for a Human Language OS: compiler+VM+IoT codegen

## Appendix A: NLBC Instruction Reference (to be populated)
## Appendix B: HLX Grammar Reference (to be populated)
