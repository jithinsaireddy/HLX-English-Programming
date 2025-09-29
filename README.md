# HLX-English-Programming

English Programming is a research-grade system that compiles controlled English into executable artifacts across edge, cloud, and embedded targets. The stack includes a natural-language front‑end, an intermediate representation (IR), a bytecode virtual machine (NLVM), and HLX, a domain-specific controlled-English layer for real‑time IoT and cyber‑physical systems. In short: write intentions in English, obtain verified, runnable code and artifacts.

## Vision and Scope

- Express complex programs in precise English while preserving formal semantics.
- Compile to multiple targets: NLVM bytecode for rapid execution, Rust/FreeRTOS scaffolds for embedded MCUs, edge container manifests for gateways, and interoperable W3C WoT Thing Descriptions.
- Integrate real-time data streams, stateful policies, and safety envelopes for industrial, healthcare, and smart‑city deployments.

## End‑to‑End Architecture

```
English spec → Parsing + Semantic Normalization → IR →
  (a) Bytecode → NLVM execution
  (b) HLX backends → Rust/FreeRTOS, Edge manifests, WoT TD → downstream binary builds
```

- **English Front‑End**: Deterministic parser with optional NLP assistance (spaCy) to normalize English into a typed, explicit IR with disambiguation and constraints.
- **IR**: A compact, SSA‑like instruction set tailored for control flow, data flow, and side‑effect boundaries.
- **Bytecode + NLVM**: The IR lowers to bytecode executed by NLVM, providing deterministic evaluation, sandboxed I/O, and introspection for debugging/testing.
- **Binary Code Conversion (via HLX toolchain)**: HLX specifications generate Rust/FreeRTOS skeletons and edge manifests that are compiled downstream to machine binaries and deployable images. This bridges natural language to hardware‑level executables without sacrificing verifiability.

## HLX: Controlled‑English for Real‑Time IoT/Edge

HLX models sensors, actuators, timing constraints, and policies in strict English with a well‑defined grammar.

- Outputs:
  - `hlx_out/rtos.rs`: Rust/FreeRTOS skeleton for MCU tasks, timers, and ISR-safe queues
  - `hlx_out/edge_manifest.json`: Edge module/container manifest for gateway deployment
  - `hlx_out/thing_description.json`: W3C WoT Thing Description for interoperability
- Runtime integrations:
  - Local simulation and policy testing
  - MQTT/CoAP connectors for real‑time telemetry and command/control
  - Deterministic scheduling hints and rate‑monotonic patterns for control loops

See the dedicated HLX README under `english_programming/hlx/README.md` for grammar, timing, and safety details.

## Real‑Time Data and Streaming

- Ingestion: MQTT/CoAP/Web sockets to NLVM or HLX edge modules
- Semantics: event‑time vs processing‑time distinction, windowing, and stateful policies in English
- Safety: bounds checks, rate limits, dead‑man switches, and fail‑safe modes expressed in controlled English
- Observability: structured logs, execution traces, and testable scenarios from natural language specifications

## Representative Use Cases

- Industrial automation (process control, predictive maintenance)
- Healthcare monitoring (alarm policies, privacy‑aware streaming)
- Smart cities (traffic policies, energy optimization, incident response)
- Robotics and drones (mission plans, safety corridors)
- Finance and ops (natural‑language runbooks with auditable execution)

## Quick Start

Run an English program end‑to‑end (compile → execute):

```bash
python integrated_test_runner.py english_programming/examples/basic_operations.nl
```

Generate HLX artifacts and run a demo:

```bash
python -m english_programming.hlx.cli english_programming/examples/boiler_a.hlx --out hlx_out
python -m english_programming.hlx.run_demo english_programming/examples/boiler_a.hlx
```

Optional MQTT edge module (if broker available):

```bash
python -m english_programming.hlx.edge_module --spec english_programming/examples/boiler_a.hlx --endpoint mqtt://localhost
```

## Repository Map

- `english_programming/src`: compiler, NLVM, interfaces, and extensions
- `english_programming/hlx`: HLX grammar, CLI, edge module, and generators
- `english_programming/examples`: example `.nl` and `.hlx` programs
- `hlx_out/`: generated outputs (ignored by VCS)
- `ui/english-ui`: experimental React/TypeScript UI

## Open Source and Governance

- License: MIT (see `LICENSE`)
- Contributing: see `CONTRIBUTING.md`
- Code of Conduct: see `CODE_OF_CONDUCT.md`
- Security: see `SECURITY.md` for vulnerability reporting

## Citation

If you use this project in academic work, please cite it as “HLX‑English‑Programming (2025)”.
