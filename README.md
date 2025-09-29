# HLX-English-Programming

English Programming is a research-grade system that compiles controlled English into executable artifacts across edge, cloud, and embedded targets. The stack includes a natural-language front‑end, an intermediate representation (IR), a bytecode virtual machine (NLVM), and HLX, a domain-specific controlled-English layer for real‑time IoT and cyber‑physical systems. In short: write intentions in English, obtain verified, runnable code and artifacts.

## Vision and Scope

- Express complex programs in precise English while preserving formal semantics.
- Compile to multiple targets: NLVM bytecode for rapid execution, Rust/FreeRTOS scaffolds for embedded MCUs, edge container manifests for gateways, and interoperable W3C WoT Thing Descriptions.
- Integrate real-time data streams, stateful policies, and safety envelopes for industrial, healthcare, and smart‑city deployments.

## Primary Pipeline (English → NLBC Binary → NLVM)

```
English program (.nl) → Compiler → NLBC binary (.nlc) → NLVM execution

HLX spec (.hlx) → HLX generators → Rust/FreeRTOS, Edge manifests, WoT TD → downstream target binaries
```

- **English→NLBC Compiler (primary)**: Translates controlled English directly to NLBC, a compact binary bytecode. See `english_programming/run_english.py` for CLI flags including disassembly.
- **NLVM (primary runtime)**: Executes NLBC deterministically with capability‑gated I/O and execution guards. See `english_programming/src/vm/improved_nlvm.py`.
- **IR (secondary, internal)**: We maintain an internal IR to support analysis/transformations. It is not the primary public artifact; the public contract is NLBC and HLX outputs.
- **HLX Generators**: Produce deployable artifacts for embedded and edge: Rust/FreeRTOS skeletons, gateway manifests, and W3C WoT TDs.

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

## Real‑Time Data, Streaming, and Binary Execution Advantages

- Direct binary execution via NLBC minimizes interpretive overhead and enables tight execution guards.
- Ingestion: MQTT/CoAP/WebSockets into NLVM/HLX edge modules with deterministic handlers.
- Semantics: event‑time vs processing‑time, windowing, and stateful English policies.
- Safety: bounds checks, rate limits, watchdogs, and fail‑safe transitions expressed in controlled English.
- Observability: structured logs, disassembly tooling, traces tied back to English source.

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

## Differentiation and Impact

- Unlike ML code generators (e.g., prompt-to-code), our compiler is deterministic and produces a verifiable binary (NLBC) with a stable VM contract.
- Unlike natural-language DSLs that target a single environment, HLX produces multi‑target artifacts (MCU Rust/FreeRTOS, edge manifests, WoT TD) from one source of truth.
- Compared to historical natural-language languages (e.g., domain‑specific or interactive notebooks), this system offers end‑to‑end compilation to binary, real‑time semantics, and cross‑domain safety constructs.

## Open Source and Governance

- License: MIT (see `LICENSE`)
- Contributing: see `CONTRIBUTING.md`
- Code of Conduct: see `CODE_OF_CONDUCT.md`
- Security: see `SECURITY.md` for vulnerability reporting

## Citation

If you use this project in academic work, please cite it as “HLX‑English‑Programming (2025)”.
