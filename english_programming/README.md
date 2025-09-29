# English Programming: Compiler, IR, NLVM, and HLX Backends

This package contains the core compiler pipeline, intermediate representation (IR), the NLVM bytecode virtual machine, and HLX tooling for real‑time IoT/edge targets.

## Technical Overview

### Front‑End and Semantic Normalization

- Deterministic parsing of controlled English with optional NLP aids (spaCy)
- Entity resolution, type inference under constraints, and effect tracking
- Normalization to a typed IR with explicit control/data flow

### Intermediate Representation (IR)

- Structured control flow (blocks, branches, joins)
- Side‑effect boundaries (I/O, network, filesystem) carried as capabilities
- Lowerable to: (a) NLVM bytecode, (b) HLX generators

### NLVM Execution Model

- Register‑like bytecode with deterministic evaluation
- Sandboxed runtime with capability‑gated I/O
- Tracing hooks for test runners and step‑through debugging

### Binary Code Conversion via HLX

- HLX specifications generate target artifacts:
  - Rust/FreeRTOS task skeletons for MCU binaries (compiled downstream)
  - Edge container manifests for gateway deployment
  - W3C WoT Thing Descriptions for interoperability

## Real‑Time and Streaming

- Event‑time vs processing‑time semantics, windowing, and rate controls
- MQTT/CoAP connectors in `hlx.edge_module` for telemetry and command/control
- Safety envelopes: bounds checks, watchdogs, and fail‑safe transitions

## Developer Workflow

Compile and execute an English program:

```bash
python ../../integrated_test_runner.py ../examples/basic_operations.nl
```

Generate HLX artifacts and simulate:

```bash
python -m english_programming.hlx.cli ../examples/boiler_a.hlx --out ../../hlx_out
python -m english_programming.hlx.run_demo ../examples/boiler_a.hlx
```

Run an MQTT‑backed edge module (optional broker):

```bash
python -m english_programming.hlx.edge_module --spec ../examples/boiler_a.hlx --endpoint mqtt://localhost
```

## Extensibility

- Extension APIs under `src/extensions` for HTTP, files, and custom domains
- Add IR passes for optimization or static analysis
- Add HLX verbs for domain‑specific actions (publish/subscribe/actuate)

## References

- See root `README.md` for a system overview and use cases
- See `english_programming/hlx/README.md` for HLX grammar and safety model

## License and Governance

- MIT License (root `LICENSE`)
- Contributing: `CONTRIBUTING.md`
- Code of Conduct: `CODE_OF_CONDUCT.md`
